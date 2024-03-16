import argparse
import os
import shutil
import cv2
import numpy as np
from skimage.transform import resize
from utility import *


def getSobel(channel):

    sobelx = cv2.Sobel(channel, cv2.CV_16S, 1, 0, borderType=cv2.BORDER_REPLICATE)
    sobely = cv2.Sobel(channel, cv2.CV_16S, 0, 1, borderType=cv2.BORDER_REPLICATE)
    sobel = np.hypot(sobelx, sobely)

    return sobel


def findSignificantContours(img, sobel_8u):
    contours, heirarchy = cv2.findContours(
        sobel_8u, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )

    # Find level 1 contours
    level1 = []
    for i, tupl in enumerate(heirarchy[0]):
        # Each array is in format (Next, Prev, First child, Parent)
        # Filter the ones without parent
        if tupl[3] == -1:
            tupl = np.insert(tupl, 0, [i])
            level1.append(tupl)

    # From among them, find the contours with large surface area.
    significant = []
    tooSmall = (
        sobel_8u.size * 5 / 100
    )  # If contour isn't covering 5% of total area of image then it probably is too small
    for tupl in level1:
        contour = contours[tupl[0]]
        area = cv2.contourArea(contour)
        if area > tooSmall:
            cv2.drawContours(img, [contour], 0, (0, 255, 0), 2, cv2.LINE_AA, maxLevel=1)
            significant.append([contour, area])

    significant.sort(key=lambda x: x[1])
    return [x[0] for x in significant]


def segment(path):
    img = cv2.imread(path)
    img_copy = img.copy()
    show_image("origin", img)
    blurred = cv2.GaussianBlur(img, (5, 5), 0)  # Remove noise

    # Edge operator
    sobel = np.max(
        np.array(
            [
                getSobel(blurred[:, :, 0]),
                getSobel(blurred[:, :, 1]),
                getSobel(blurred[:, :, 2]),
            ]
        ),
        axis=0,
    )

    # Noise reduction trick, from http://sourceforge.net/p/octave/image/ci/default/tree/inst/edge.m#l182
    mean = np.mean(sobel)

    # Zero any values less than mean. This reduces a lot of noise.
    sobel[sobel <= mean] = 0
    sobel[sobel > 255] = 255

    # cv2.imwrite("output/edge.png", sobel)
    show_image("edge", sobel)

    sobel_8u = np.asarray(sobel, np.uint8)

    # Find contours
    significant = findSignificantContours(img, sobel_8u)
    c = max(significant, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(
        c
    )  ### getting the values of x,y,w and h is our main intention
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 5)
    # show_image("rectangle", img)

    cropped_img = img_copy[y : y + h + 1, x : x + w + 1]
    # show_image("crop", cropped_img)

    return cropped_img


def _overlay(optical_path, xray_path, alpha, beta):
    img1 = segment(optical_path)
    # show_image("img1", img1)
    img2 = segment(xray_path)
    # show_image("img2", img2)

    height = img1.shape[0]
    width = img1.shape[1]

    img1 = resize(img1, (height, width))
    print(np.max(img1))
    img2 = resize(img2, (height, width))
    print(np.max(img2))

    ## The dtype of the arrays with the images is float64,
    ## IF I DONT CONVERT ITS TYPE when I try to use the function cv2.COLOR_BGR2RGB, it throws
    ## the error: "Unsupported depth of input image"
    img1 = np.float32(img1)
    img2 = np.float32(img2)

    # Converting from BGR to RGB:
    img1_rgb = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)
    img2_rgb = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)

    # Blending images
    final_img = cv2.addWeighted(img1_rgb, alpha, img2_rgb, beta, 0)  #
    final_img = (final_img * 255).round().astype(np.uint8)
    # mkdir_if_not_exist(output_path)
    # cv2.imwrite(output_path, final_img)
    show_image("final", final_img)
    return final_img


def overlay(dataset_name: str, alpha, beta):
    subsets_optical = get_subset_names("Data/Optical-image")
    subsets_xray = get_subset_names("Output/SIFT")
    subsets = {}
    for _ in subsets_optical:
        print(_)
        subsets[_] = list(set(subsets_optical[_]).intersection(set(subsets_xray[_])))

    for _ in subsets:
        optical_path = os.path.join("Data/Optical-image", dataset_name)
        xray_path = os.path.join("Output/SIFT", dataset_name)
        output_path = os.path.join("Output/Final", dataset_name)
        for folder in subsets[_]:
            optical_img_name = os.listdir(os.path.join(optical_path, folder))[0]
            xray_img_name = os.listdir(os.path.join(xray_path, folder))[0]
            output_path = os.path.join(output_path, folder, "final.jpg")
            cv2.imwrite(
                output_path,
                _overlay(
                    optical_path=os.path.join(optical_path, folder, optical_img_name),
                    xray_path=os.path.join(xray_path, folder, xray_img_name),
                    alpha=alpha,
                    beta=beta,
                ),
            )


parser = argparse.ArgumentParser()
parser.add_argument("-d", "--Dataset", help="\ndataset name", required=True)
parser.add_argument("-a", "--Alpha", help="\noptical image transparency", default=0.2)
parser.add_argument("-b", "--Beta", help="\nxray image transparency", default=0.8)

args = parser.parse_args()

if __name__ == "__main__":
    overlay(args.Dataset, args.Alpha, args.Beta)

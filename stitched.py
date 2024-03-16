import cv2
import numpy as np
import os
from utility import *
import argparse


def warpImages(img1, img2, H):
    rows1, cols1 = img1.shape[:2]
    rows2, cols2 = img2.shape[:2]

    list_of_points_1 = np.float32([[0, 0], [0, rows1], [cols1, rows1], [cols1, 0]])
    list_of_points_1 = list_of_points_1.reshape(-1, 1, 2)

    temp_points = np.float32([[0, 0], [0, rows2], [cols2, rows2], [cols2, 0]])
    temp_points = temp_points.reshape(-1, 1, 2)

    list_of_points_2 = cv2.perspectiveTransform(temp_points, H)

    list_of_points = np.concatenate((list_of_points_1, list_of_points_2), axis=0)

    ##Define boundaries:
    [x_min, y_min] = np.int32(list_of_points.min(axis=0).ravel() - 0.5)
    [x_max, y_max] = np.int32(list_of_points.max(axis=0).ravel() + 0.5)

    translation_dist = [-x_min, -y_min]

    H_translation = np.array(
        [[1, 0, translation_dist[0]], [0, 1, translation_dist[1]], [0, 0, 1]]
    )

    output_img = cv2.warpPerspective(
        img2, H_translation.dot(H), (x_max - x_min, y_max - y_min)
    )
    ## Paste the image:
    output_img[
        translation_dist[1] : rows1 + translation_dist[1],
        translation_dist[0] : cols1 + translation_dist[0],
    ] = img1

    return output_img


#
def warp(img1, img2, opt, min_match_count=10):
    if opt == "SIFT":
        sift = cv2.SIFT_create()

        # Extract the keypoints and descriptors
        keypoints1, descriptors1 = sift.detectAndCompute(img1, None)
        keypoints2, descriptors2 = sift.detectAndCompute(img2, None)
    else:
        orb = cv2.ORB_create(nfeatures=3000)

        # Extract the keypoints and descriptors
        keypoints1, descriptors1 = orb.detectAndCompute(img1, None)
        keypoints2, descriptors2 = orb.detectAndCompute(img2, None)

    # Initialize parameters for Flann based matcher
    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)

    # Initialize the Flann based matcher object
    flann = cv2.FlannBasedMatcher(index_params, search_params)

    # Compute the matches
    matches = flann.knnMatch(descriptors1, descriptors2, k=2)

    # Store all the good matches as per Lowe's ratio test
    good_matches = []
    for m1, m2 in matches:
        if m1.distance < 0.7 * m2.distance:
            good_matches.append(m1)

    if len(good_matches) > min_match_count:
        src_pts = np.float32(
            [keypoints1[good_match.queryIdx].pt for good_match in good_matches]
        ).reshape(-1, 1, 2)

        dst_pts = np.float32(
            [keypoints2[good_match.trainIdx].pt for good_match in good_matches]
        ).reshape(-1, 1, 2)

        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        result = warpImages(img2, img1, M)
        return result
        # cv2.imshow('Stitched output', result)
        # cv2.waitKey()
    else:
        print("We don't have enough number of matches between the two images.")
        print("Found only " + str(len(good_matches)) + " matches.")
        print("We need at least " + str(min_match_count) + " matches.")


def stitch_image_in_directory(input_directory, output_directory):
    for dirname, _, filenames in os.walk(input_directory):
        if dirname == ".DS_Store":
            continue
        filenames = sorted(filenames)
        path_img1 = os.path.join(dirname, filenames[0])
        print(dirname)
        print("Stitching in processing")
        image_1 = cv2.imread(path_img1)
        firstCollage = None
        for n_number in range(1, len(filenames), 1):
            if n_number == 1:
                path_img2 = os.path.join(dirname, filenames[n_number])
                #                 print(path_img2)
                image_2 = cv2.imread(path_img2)
                firstCollage = warp(image_1, image_2)
            else:
                path_img2 = os.path.join(dirname, filenames[n_number])
                #                 print(path_img2)
                image_2 = cv2.imread(path_img2)
                firstCollage = warp(firstCollage, image_2)
        file_name = "image_stitched_" + filenames[-1]
        save_image(output_directory, file_name, firstCollage)
        file_path = os.path.join(output_directory, file_name)
        show_image("first collage", firstCollage)
        print(file_path)
        print("Stitching in done")


def save_image(directory, file_name, image):
    if not os.path.exists(directory):
        os.makedirs(directory)
    cv2.imwrite(directory + "/" + file_name, image)


def pre_process_image(input_directory, output_directory, number=10):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    for dirname, _, filenames in os.walk(input_directory):
        filenames = sorted(filenames)
        for n_number in range(0, len(filenames), number):
            directory = output_directory + "/" + str(n_number).zfill(4)
            if not os.path.exists(directory):
                os.makedirs(directory)
            for n_2 in range(n_number, n_number + number, 1):
                n_image = n_number + n_2
                if len(filenames) <= n_image:
                    break
                path_img1 = os.path.join(dirname, filenames[n_image])
                path_img2 = os.path.join(directory, filenames[n_image])
                shutil.copy2(path_img1, path_img2)


def pre_process_image(input_directory, output_directory, number=10):
    index = 0
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    for dirname, _, filenames in os.walk(input_directory):
        filenames = sorted(filenames)
        for n_number in range(0, len(filenames), number):
            index = index + 1
            directory = output_directory + "/" + str(index).zfill(4)
            if not os.path.exists(directory):
                os.makedirs(directory)
            for n_2 in range(n_number, n_number + number, 1):
                n_image = n_2
                if len(filenames) <= n_image:
                    break
                path_img1 = os.path.join(dirname, filenames[n_image])
                path_img2 = os.path.join(directory, filenames[n_image])
                shutil.copy2(path_img1, path_img2)


def save_image(directory, file_name, image):
    if not os.path.exists(directory):
        os.makedirs(directory)
    cv2.imwrite(directory + "/" + file_name, image)


def stitch_image_in_a_directory(input_directory, output_directory, opt):
    for dirname, _, filenames in os.walk(input_directory):
        if ".DS_Store" in filenames:
            filenames.remove(".DS_Store")
        filenames = sorted(filenames)
        path_img1 = os.path.join(dirname, filenames[0])
        print("Stitching in processing")
        image_1 = cv2.imread(path_img1)
        firstCollage = cv2.imread(path_img1)
        for n_number in range(1, len(filenames), 1):
            if n_number == 1:
                path_img2 = os.path.join(dirname, filenames[n_number])
                print(path_img2)
                image_2 = cv2.imread(path_img2)
                firstCollage = warp(image_1, image_2, opt)
            else:
                path_img2 = os.path.join(dirname, filenames[n_number])
                print(path_img2)
                image_2 = cv2.imread(path_img2)
                firstCollage = warp(firstCollage, image_2, opt)
        file_name = "image_stitched_" + filenames[-1]
        save_image(output_directory, file_name, firstCollage)
        file_path = os.path.join(output_directory, file_name)
        # show_image("first collage", firstCollage)
        print(file_path)
        print("Stitching in done")


def stitched(dataset_name=None, algo="SIFT"):
    subsets = get_subset_names("Data/Xray-image")
    output_stitched = f"Output/{algo}"

    for _ in subsets:
        if dataset_name != None and _ != dataset_name:
            continue
        for dataset in subsets[_]:
            print(dataset)
            mkdir_if_not_exist(os.path.join(output_stitched, _, dataset))
            stitch_image_in_a_directory(
                f"Data/Xray-image/{_}/{dataset}",
                os.path.join(output_stitched, _, dataset),
                algo,
            )


parser = argparse.ArgumentParser()
parser.add_argument(
    "-d",
    "--Dataset",
    help="Choose specific dataset name in folder Data, default is all dataset in folder Data",
    default=None,
)

args = parser.parse_args()

if __name__ == "__main__":
    stitched(args.Dataset)

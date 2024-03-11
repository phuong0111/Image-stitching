import os
import shutil

import cv2


def get_subset_names(DATASET_NAME):
    subsets = {}
    root, directories, files = next(os.walk(DATASET_NAME))
    for directory in sorted(directories):
        subsets[directory] = sorted(os.listdir(DATASET_NAME + "/" + directory))
    return subsets


def mkdir_if_not_exist(dir_name, is_delete=False):
    try:
        if is_delete:
            if os.path.exists(dir_name):
                shutil.rmtree(dir_name)
                print('[INFO] Dir "%s" exists, deleting.' % dir_name)

        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print('[INFO] Dir "%s" not exists, creating.' % dir_name)
        return True
    except Exception as e:
        print("[Exception] %s" % e)
        return False


def show_image(winname, image):
    cv2.imshow(winname, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

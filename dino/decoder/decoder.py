import numpy as np
from PIL import Image
import cv2
import sys


def decode(img_path):
    img = Image.open(img_path)
    img_arr = np.array(img)
    print(img_arr)


if __name__ == "__main__":
    args = sys.argv
    if len(args) != 2:
        print("Requires one image path")
    else:
        decode(args[1])

from typing import List

import matplotlib.pyplot as plt
import numpy as np
from cv2 import cv2
from matplotlib.patches import Circle, FancyBboxPatch
from PIL import Image, ImageFilter

from detector.detect import FinderPattern, LinearBinaryRatioSearchMachine, locate
from detector.preprocess import preprocess


def show_webcam(mirror=False):
    cam = cv2.VideoCapture(0)
    while True:
        ret_val, img = cam.read()

        qr = cv2.QRCodeDetector()

        data, boundingBox, rectified = qr.detectAndDecode(img)
        if len(data) > 0:
            # We've got something
            print("Decoded Data : {}".format(data))
            cv2.imshow("Rectified", rectified)

        # orig = img

        # img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # # img = cv2.GaussianBlur(img, (5, 5), 0)
        # img = cv2.adaptiveThreshold(
        #     img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 51, 0
        # )

        # centers = locate(img)

        # for center in centers:
        # orig = cv2.circle(img, (center[1], center[0]), 2, (255, 0, 0), 2)

        # ret, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        # img = Image.fromarray(img)
        # img = img.convert("L")

        # img = img.filter(ImageFilter.GaussianBlur(2))
        if mirror:
            img = cv2.flip(img, 1)
        cv2.imshow("my webcam", img)
        if cv2.waitKey(1) == 27:
            break  # esc to quit
    cv2.destroyAllWindows()


def run():
    # im = Image.open("qrtests/qr1.png")
    im = Image.open("qrtests/printed.jpg")
    # im = Image.open("qrtests/3d.jpg")
    image = np.array(im)
    # image = cv2.imread("qrtests/v1.png")
    # print(image.shape)
    image = preprocess(image)
    # plt.imshow(image)
    # plt.show()

    box = locate(image)
    print(box)

    # print(centers)

    # points = np.array(list(map(lambda cent: np.array([cent.row, cent.col]), centers)))

    fig, ax = plt.subplots(1)
    ax.set_aspect("equal")
    ax.imshow(im, cmap="gray")
    # ax.scatter(points[:, 1], points[:, 0], c="red", s=1)
    ax.scatter(box[:, 0], box[:, 1], c="red")

    # for center in centers:
    #     center = center  # type: FinderPattern
    #     circle = Circle((center.col, center.row), center.size / 2, fill=None, ec="red")
    #     rect = FancyBboxPatch(
    #         (center.col - center.size // 2, center.row - center.size // 2),
    #         center.size,
    #         center.size,
    #         fill=None,
    #         ec="red",
    #         lw=2,
    #         boxstyle="Round",
    #     )
    #     ax.add_patch(rect)
    # plt.show()


if __name__ == "__main__":
    run()

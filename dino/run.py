
from encoder.qrcode import QRCode
import os

from typing import List

import matplotlib.pyplot as plt
import numpy as np
from cv2 import cv2
from matplotlib.patches import Circle, FancyBboxPatch
from PIL import Image, ImageFilter
import time

from detector.detect import FinderPattern, LinearBinaryRatioSearchMachine, locate
from detector.preprocess import preprocess

from decoder.decoder import decode


def run():
    valid_chars = {
        "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:"[i] for i in range(45)}

    print("\nLAUNCHING SHELL...\n")
    print("At command prompt, type text (up to length 25) you want to encode")
    print("Can include uppercase letters, numbers, and $ % * + - . / : ")
    while True:
        valid_input = True
        data = input(">> ").strip().upper()

        if len(data) > 25:
            print("Message too long. Must be less than 25 characters")
            valid_input = False

        for c in range(len(data)):
            if data[c] not in valid_chars:
                print(
                    "ERROR: Your input contains invalid character '" + data[c] + "'")
                valid_input = False
                break

        if valid_input:
            qr = QRCode(data)
            qr.show(expand_factor=20)
            print("QR Code generated, displaying it now")

            saved_qr = qr.to_file()

            im = Image.open(saved_qr)

            # DETECTING
            image = np.array(im)
            image = cv2.imread(saved_qr)

            # apply some scaling to help with clarity reading image
            scale_percent = 80  # percent of original size
            width = int(image.shape[1] * scale_percent / 100)
            height = int(image.shape[0] * scale_percent / 100)
            dim = (width, height)
            # resize image
            image = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
            # print(image.shape)
            image = preprocess(image)
            # plt.imshow(image)
            # plt.show()

            box, pts = locate(image)

            fig, ax = plt.subplots(1)
            ax.set_aspect("equal")
            ax.imshow(im, cmap="gray")
            # ax.scatter(points[:, 1], points[:, 0], c="red", s=1)
            ax.scatter(box[:, 0], box[:, 1], c="red")
            print("Now detected QR Code and drew bounding box around it")

            # print(centers)
            if pts.shape == (21, 21):
                msg = decode(pts)
                if msg is not None:
                    print(f"QR Code message: {msg}")
            # points = np.array(list(map(lambda cent: np.array([cent.row, cent.col]), centers)))

    # cleanup
    os.remove(saved_qr)


if __name__ == '__main__':
    run()

from PIL import Image, ImageFilter
from cv2 import cv2
import numpy as np


def preprocess(image: np.ndarray) -> Image:

    img = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    # img = cv2.GaussianBlur(img, (12, 12), 0)
    img = cv2.adaptiveThreshold(
        img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 51, 0
    )
    # ret, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return img

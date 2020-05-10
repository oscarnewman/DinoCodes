import numpy as np

from Typing import List


class QRCode:
    @staticmethod
    def encode_text(text: str, ecl: QRCode.Ecc) -> QRCode:
        pass

    def __init__(self, version: int, ecl: QrCode.Ecc, datacodewords: List[int], mask: int):
        if not (QRCode.MIN_VERSION <= version <= QRCode.MAX_VERSION):
            raise ValueError("Version value out of range")

        # the version number of the QR Code, the possibel range of which
        # is defined by MIN_VERSION and MAX_VERSION
        self.version = version

        # size of one side of the QR Code
        self.size = version * 14 + 17

        # error correction level
        self.ecl = ecl

        self.grid = np.zeros((self.size, self.size))

    MIN_VERSION = 1
    MAX_VERSION = 4

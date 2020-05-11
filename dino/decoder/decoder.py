import numpy as np
from PIL import Image
import cv2
import sys


def decode(bitmap: np.ndarray):
    bitmap = bitmap.astype(int)
    if bitmap.shape != (21, 21):
        print("QR Code must be 21x21")
        return None
    bitmap = unmask(bitmap)
    print(bitmap)
    encoding = get_encoding(bitmap)
    bin_str = to_bin_str(bitmap)
    print(bin_str)
    if encoding == 2:
        assert bin_str[:4] == "0010"
        msg_length = byte_to_num(bin_str[4:12])
        print(msg_length)
        msg = ""
        for i in range(msg_length):
            x = 12 + 11 * i
            block = bin_str[x : x + 11]
            msg += from_alphanumeric(block)
    else:
        print(f"encoding type {encoding} not supported")
        return None
    return msg


def byte_to_num(byte_str):
    base = 2 ** (len(byte_str) - 1)
    s = 0
    for c in byte_str:
        s += int(c) * base
        base /= 2
    return int(s)


def from_alphanumeric(bit_string):
    def num_to_char(num):
        symbs = {
            36: " ",
            37: "$",
            38: "%",
            39: "*",
            40: "+",
            41: "-",
            42: ".",
            43: "/",
            44: ":",
        }
        if num < 10:
            return str(num)
        elif num < 36:
            return chr(num + 55)
        else:
            return symbs[num]

    base = 1
    s = 0
    for c in bit_string:
        s += base * int(c)
        base *= 2
    if len(bit_string) == 11:
        num_2 = s % 45
        num_1 = int((s - num_2) / 45)
        return num_to_char(num_1) + num_to_char(num_2)
    else:
        assert len(bit_string) == 6
        return num_to_char(s)


def to_bin_str(bitmap):
    data_ranges = {
        (21, 21): lambda i, j: (
            (i > 8 and j > 8) or (13 > i > 8 and j != 6) or (13 > j > 8 and i != 6)
        )
    }
    in_range = data_ranges[bitmap.shape]
    if bitmap.shape == (21, 21):
        up = True
        bitstring = ""
        for j in [19, 17, 15, 13, 11, 9, 7, 4, 2, 0]:
            if up:
                r = range(bitmap.shape[1] - 1, -1, -1)
            else:
                r = range(bitmap.shape[1] - 1)
            for i in r:
                if in_range(i, j):
                    bitstring += str(bitmap[i, j + 1]) + str(bitmap[i, j])
            up = not up
        return bitstring
    else:
        print("Shape not supported")


def unmask(bitmap):
    masks = {
        0: lambda i, j: 0 if j % 3 != 0 else 1,
        1: lambda i, j: 0 if (i + j) % 3 != 0 else 1,
        2: lambda i, j: 0 if (i + j) % 2 != 0 else 1,
        3: lambda i, j: 0 if i % 2 != 0 else 1,
        4: lambda i, j: 0 if ((i * j) % 3 + i * j) % 2 != 0 else 1,
        5: lambda i, j: 0 if ((i * j) % 3 + i + j) % 2 != 0 else 1,
        6: lambda i, j: 0 if (int(i / 2) + int(j / 3)) % 2 != 0 else 1,
        7: lambda i, j: 0 if (i * j) % 2 + (i * j) % 3 != 0 else 1,
    }

    data_ranges = {
        (21, 21): lambda i, j: (
            (i > 8 and j > 8) or (13 > i > 8 and j != 6) or (13 > j > 8 and i != 6)
        )
    }

    def apply(mask_val, bit_val):
        if mask_val == 0:
            if bit_val == 0:
                return 1
            else:
                return 0
        else:
            return bit_val

    if bitmap.shape == (21, 21):
        bits = bitmap[8, 2:5]
        mask_num = np.sum(bits * [4, 2, 1])
        mask_fun = masks[mask_num]
        in_range = data_ranges[bitmap.shape]
        for i in range(bitmap.shape[0]):
            for j in range(bitmap.shape[1]):
                if in_range(i, j):
                    bitmap[i, j] = apply(mask_fun(i, j), bitmap[i, j])
        return bitmap
    else:
        print("QR code shape not supported")
        return None


def get_encoding(bitmap):
    if bitmap.shape == (21, 21):
        encoding_block = bitmap[-2:, -2:]
        return np.sum(encoding_block.reshape(-1) * [1, 2, 4, 8])
    else:
        print("Shape not supported")
        return None

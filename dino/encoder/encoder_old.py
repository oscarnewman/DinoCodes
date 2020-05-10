import numpy as np
from PIL import Image
from itertools import permutations as make_perms
import time


# code = np.random.randint(0, 2, size=(10, 10), dtype=np.uint8) * 255
# img = Image.fromarray(code)
# img.show()


def make_random_code(size=(10, 10)):
    # returns random "code" as numpy array, able to be read by PIL
    return np.random.randint(0, 2, size=(10, 10), dtype=np.uint8) * 255


def with_block_size(code, block_size=1):
    # compute all indices of white blocks in resized code
    white_indices_before = np.argwhere(code == 255) * block_size
    perms = list(make_perms([i for i in range(block_size)], 2))
    perms += [(i, i) for i in range(block_size)]
    offsets = np.array(perms)
    expanded = np.hstack([white_indices_before] * offsets.shape[0])
    white_indices = (expanded + offsets.flatten()).reshape((-1, 2))

    # FIXME: Slow AF. Can you index like this without for loop??
    new_code = np.zeros([code.shape[0] * block_size] * 2, dtype=np.uint8)
    for i in white_indices:
        new_code[tuple(i)] = 255
    return new_code


before_make = time.time()
code = make_random_code()
make_time = (time.time() - before_make) * 1000
print("MAKE TIME:", make_time)

before_expand = time.time()
expanded = with_block_size(code, block_size=100)
expand_time = (time.time() - before_expand) * 1000
print("EXPAND TIME:", expand_time)

img = Image.fromarray(code)
expanded_img = Image.fromarray(expanded)

img.show()
expanded_img.show()

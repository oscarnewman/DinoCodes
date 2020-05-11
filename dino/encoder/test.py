
# def reed_sol_compute_divisor(degree):
#     """Returns a Reed-sol ECC generator polynomial for the given degree. This could be
#     implemented as a lookup table over all possible parameter values, instead of as an algorithm."""
#     if not (1 <= degree <= 255):
#         raise ValueError("Degree out of range")
#     # Polynomial coefficients are stored from highest to lowest power, excluding the leading term which is always 1.
#     # For example the polynomial x^3 + 255x^2 + 8x + 93 is stored as the uint8 array [255, 8, 93].
#     result = [0] * (degree - 1) + [1]  # Start off with the monomial x^0

#     # Compute the product polynomial (x - r^0) * (x - r^1) * (x - r^2) * ... * (x - r^{degree-1}),
#     # and drop the highest monomial term which is always 1x^degree.
#     # Note that r = 0x02, which is a generator element of this field GF(2^8/0x11D).
#     root = 1
#     for _ in range(degree):  # Unused variable i
#         # Multiply the current product by (x - r^i)
#         for j in range(degree):
#             result[j] = reed_sol_multiply(result[j], root)
#             if j + 1 < degree:
#                 result[j] ^= result[j + 1]
#         root = reed_sol_multiply(root, 0x02)
#     return result


# def reed_sol_compute_remainder(data, divisor):
#     """Returns the Reed-sol error correction codeword for the given data and divisor polynomials."""
#     result = [0] * len(divisor)
#     for b in data:  # Polynomial division
#         factor = b ^ result.pop(0)
#         result.append(0)
#         for (i, coef) in enumerate(divisor):
#             result[i] ^= reed_sol_multiply(coef, factor)
#     return result


# def reed_sol_multiply(x, y):
#     """Returns the product of the two given field elements modulo GF(2^8/0x11D). The arguments and result
#     are unsigned 8-bit integers. This could be implemented as a lookup table of 256*256 entries of uint8."""
#     if x >> 8 != 0 or y >> 8 != 0:
#         raise ValueError("Byte out of range")
#     # Russian peasant multiplication
#     z = 0
#     for i in reversed(range(8)):
#         z = (z << 1) ^ ((z >> 7) * 0x11D)
#         z ^= ((y >> i) & 1) * x
#     assert z >> 8 == 0
#     return z

def reed_sol_compute_divisor(d):
    """Returns a Reed-sol ECC generator polynomial for the given degree. This could be
    implemented as a lookup table over all possible parameter values, instead of as an algorithm."""
    res = [0] * (d - 1) + [1]  # Start off with the monomial x^0

    root = 1
    for i in range(d):  # Unused variable i
        # Multiply the current product by (x - r^i)
        for j in range(d):
            res[j] = reed_sol_multiply(res[j], root)
            if j + 1 < d:
                res[j] ^= res[j + 1]
        root = reed_sol_multiply(root, 0x02)
    return res


def reed_sol_compute_remainder(data, div):
    """Returns the Reed-sol error correction codeword for the given data and divisor polynomials."""
    res = [0] * len(div)
    for b in data:  # Polynomial division
        f = b ^ res.pop(0)
        res.append(0)
        for (i, c) in enumerate(div):
            res[i] ^= reed_sol_multiply(c, f)
    return res


def reed_sol_multiply(a, b):
    """Returns the product of the two given field elements modulo GF(2^8/0x11D). The arguments and result
    are unsigned 8-bit integers. This could be implemented as a lookup table of 256*256 entries of uint8."""

    r = 0
    for i in reversed(range(8)):
        r = (r << 1) ^ ((r >> 7) * 0x11D)
        r ^= ((b >> i) & 1) * a
    return r


def my_reed_sol_divisor(d):
    res = [0] * (d - 1) + [1]

    root = 1
    for i in range(d):
        for j in range(d):
            res[j] = my_reed_sol_multiply(res[j], root)
            if j + 1 < d:
                res[j] ^= res[j + 1]
        root = my_reed_sol_multiply(root, 0x02)
    return res


def my_reed_sol_multiply(a, b):
    c = 0
    for i in reversed(range(8)):
        c = (c << 1) & ((c >> 7) * 0x11D)
        c ^= ((b >> i) & 1) * a
    return c


def my_reed_sol_remainder(data, div):
    res = [0] * len(div)
    for b in data:
        f = b ^ res.pop(0)
        res.append(0)
        for i, c in enumerate(div):
            res[i] ^= my_reed_sol_multiply(c, f)
    return res


data_cw = [32, 73, 253, 129, 162, 212, 45, 132, 0,
           236, 17, 236, 17, 236, 17, 236, 17, 236, 17]

num_error_blocks = 1
cw_per_block = 7
num_cw_total = 26

short_block_len = num_cw_total // num_error_blocks  # num cw total

reed_sol_divisor = reed_sol_compute_divisor(cw_per_block)
ec_block = reed_sol_compute_remainder(data_cw, reed_sol_divisor)
data_cw.append(0)
block = data_cw + ec_block
for i in block:
    print(hex(i)[2:])

######################################################################################################################################################################
# numblocks = 1
# blockecclen = 7
# rawcodewords = 26
# numshortblocks = 1
# shortblocklen = rawcodewords // numblocks  # 26

# blocks = []
# rsdiv = my_reed_sol_divisor(blockecclen)
# k = 0
# for i in range(numblocks):
#     dat = data_cw[k: k + shortblocklen - blockecclen +
#                   (0 if i < numshortblocks else 1)]
#     k += len(dat)
#     ecc = my_reed_sol_remainder(dat, rsdiv)
#     if i < numshortblocks:
#         dat.append(0)
#     blocks.append(dat + ecc)
# assert k == len(data_cw)

# # Interleave (not concatenate) the bytes from every block into a single sequence
# result = []
# for i in range(len(blocks[0])):
#     for (j, blk) in enumerate(blocks):
#         # Skip the padding byte in short blocks
#         if i != shortblocklen - blockecclen or j >= numshortblocks:
#             result.append(blk[i])
# assert len(result) == rawcodewords
# for i in result:
#     print(hex(i)[2:])


########################################################################################################################################################################################################
# numblocks = 1
# blockecclen = 7
# rawcodewords = 26
# numshortblocks = 1
# shortblocklen = rawcodewords // numblocks  # 26

# blocks = []
# rsdiv = reed_sol_compute_divisor(blockecclen)
# k = 0
# for i in range(numblocks):
#     dat = data_cw[k: k + shortblocklen - blockecclen +
#                   (0 if i < numshortblocks else 1)]
#     k += len(dat)
#     ecc = reed_sol_compute_remainder(dat, rsdiv)
#     if i < numshortblocks:
#         dat.append(0)
#     blocks.append(dat + ecc)
# assert k == len(data_cw)

# # Interleave (not concatenate) the bytes from every block into a single sequence
# result = []
# for i in range(len(blocks[0])):
#     for (j, blk) in enumerate(blocks):
#         # Skip the padding byte in short blocks
#         if i != shortblocklen - blockecclen or j >= numshortblocks:
#             result.append(blk[i])
# assert len(result) == rawcodewords
# for i in result:
#     print(hex(i)[2:])

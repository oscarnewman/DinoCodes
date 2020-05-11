import numpy as np
import random
from itertools import permutations as make_perms
from itertools import cycle
from PIL import Image


# class QRCode:


class QRCode:
    def __init__(self, content, version=1, correction_level=0, mask=3, mode=None):
        self.dims = (21, 21)
        self.version = version
        self.ecl = correction_level

        self.content = content.upper()

        # canvas_size =

        self.character_count = len(content)

        self.grid = np.zeros(self.dims)
        self.is_functional = np.zeros(self.dims)

        self.draw_timing_patterns()
        self.draw_position_blocks()
        self.draw_format_bits_dummy()

        data_cw = self.make_data_codewords()
        all_cw = self.make_all_codewords(data_cw)
        self.draw_codewords_zigzag(all_cw)

        # mask = random.randint(0, 8)
        mask = 7
        # self.apply_mask(mask)
        # self.draw_format_bits(mask)

        self.canvas = np.ones((self.dims[0] + 6, self.dims[1] + 6))
        self.canvas[3:self.dims[0] + 3, 3:self.dims[1] + 3] = self.grid

    # thanks to nayuki.io for guidance
    def draw_codewords_zigzag(self, cw):
        # draws all codewords `cw` in zigzag fashion
        i = 0
        for r in range(self.dims[0] - 1, 0, -2):
            if r <= 6:
                r -= 1  # for zig
            for v in range(self.dims[0]):
                for j in range(2):
                    x = r - j
                    y = (self.dims[0] - 1 - v) if (r + 1) & 2 == 0 else v
                    if not self.is_functional[y][x] and i < len(cw) * 8:
                        self.grid[y, x] = 0 if bool(self.val_at(
                            cw[i >> 3], 7 - (i & 7))) else 1
                        i += 1

    def val_at(self, x, i):  # gets val of ith bit of x
        return (x >> i) & 1 != 0

    def apply_mask(self, mask):
        # masks as bit coordinate lamdas
        MASKS = [
            (lambda y, x:  (x + y) % 2),
            (lambda y, x:  y % 2),
            (lambda y, x:  x % 3),
            (lambda y, x:  (x + y) % 3),
            (lambda y, x:  (x // 3 + y // 2) % 2),
            (lambda y, x:  x * y % 2 + x * y % 3),
            (lambda y, x:  (x * y % 2 + x * y % 3) % 2),
            (lambda y, x:  ((x + y) % 2 + x * y % 3) % 2),
        ]
        old_type = self.grid.dtype
        grid = self.grid.astype(np.bool)
        mask_func = MASKS[mask]
        for y in range(self.dims[0]):
            for x in range(self.dims[1]):
                grid[y, x] ^= ((mask_func(y, x) == 0) and (
                    not self.is_functional[y, x] == 1))

        self.grid = grid.astype(old_type)

    def make_data_codewords(self):
        # makes the entire bit stream given the content, including mode,
        # character count, and terminator indicators

        # MODE INDICATOR
        stream = self.mode_ind_str()

        # CHARACTER COUNT INDICATOR
        stream += self.character_count_ind_str()

        # ACTUAL DATA
        stream += self.make_alphanumeric(self.content)

        data_capacity_bits = self.data_capacity_bytes() * 8

        # TERMINATOR (up to 4 0s, less than 4 only if reached capacity in < 4)
        stream += ('0' * min(4, data_capacity_bits - len(stream)))

        # BYTE PADDING
        stream += ('0' * (-len(stream) % 8))

        for byte_pad in cycle(("11101100", "00010001")):
            if len(stream) >= data_capacity_bits:
                break
            stream += byte_pad
         # bist -> bytes
        data_code_words = [0] * (len(stream) // 8)
        for (i, bit) in enumerate(stream):
            data_code_words[i >> 3] |= int(bit) << (7 - (i & 7))

        # RETURNS A LIST
        return data_code_words

    def draw_all_codewords_zigzag(self, cw):
        i = 0
        sz = self.dims[0]

        for r in range(sz - 1, 0, -2):
            if r <= 6:
                r -= 1
            for v in range(sz):
                for j in range(2):
                    x = r - j
                    u = (r + 1) & 2 == 0
                    y = (sz - 1 - v) if u else v
                    if not self.is_functional[y, x] and i < len(cw) * 8:
                        def val_at(x, i):
                            return (x >> i) & 1 != 0
                        self.grid[y, x] = val_at(cw[i >> 3], 7 - (i & 7))
                        i += 1

    def draw_position_blocks(self):
        Y, X = self.dims[0], self.dims[1]

        POSITION_BLOCK = np.array(
            [[0, 0, 0, 0, 0, 0, 0],
             [0, 1, 1, 1, 1, 1, 0],
                [0, 1, 0, 0, 0, 1, 0],
                [0, 1, 0, 0, 0, 1, 0],
                [0, 1, 0, 0, 0, 1, 0],
                [0, 1, 1, 1, 1, 1, 0],
                [0, 0, 0, 0, 0, 0, 0]],
            dtype=np.uint8)

        top_left = np.append(np.append(POSITION_BLOCK, np.ones(
            (7, 1)), axis=1), np.ones((1, 8)), axis=0)
        self.grid[0:8, 0:8] = top_left
        self.is_functional[0:8, 0:8] = 1

        top_right = np.append(
            np.append(np.ones((7, 1)), POSITION_BLOCK, axis=1), np.ones((1, 8)), axis=0)
        self.grid[0:8, X-8:X] = top_right
        self.is_functional[0:8, X-8:X] = 1

        bottom_left = np.append(np.ones((1, 8)), np.append(POSITION_BLOCK, np.ones(
            (7, 1)), axis=1), axis=0)
        self.grid[Y-8:Y, 0:8] = bottom_left
        self.is_functional[Y-8:Y, 0:8] = 1

    def draw_timing_patterns(self):
        pattern = np.tile(np.array([0, 1]),
                          self.dims[0] // 2 + 1)[:self.dims[0]]
        self.grid[:, 6] = pattern
        self.is_functional[:, 6] = 1

        self.grid[6, :] = pattern  # np.reshape(pattern, (1, self.dims[0]))
        self.is_functional[6, :] = 1

    def raw_total_capacity_bits(self):
        return (16 * self.version + 128) * self.version + 64

    def data_capacity_bytes(self):
        # returns capacity for this version and this ecl
        bits_capacity = self.raw_total_capacity_bits()
        return bits_capacity // 8 - self.error_cw_per_block() * self.num_error_blocks()

    def error_cw_per_block(self):
        cpb = [7, 10, 13, 17]  # assuming version 1
        return cpb[self.ecl]

    def draw_format_bits(self, mask):
        # Draws format bits given mask. credit to nayuki.io on implementation guidance
        fbl = [1, 9, 3, 2]
        d = fbl[self.ecl] << 3 | mask
        r = d
        for i in range(10):
            r = (r << 1) ^ ((r >> 9) * 0x537)
        bits = (d << 10 | r) ^ 0x5412

        def fm(x, y, b):
            self.grid[y, x] = 0 if b == 1 else 1
            self.is_functional[y, x] = True

        # Draw first copy
        for i in range(0, 6):
            fm(8, i, self.val_at(bits, i))
        fm(8, 7, self.val_at(bits, 6))
        fm(8, 8, self.val_at(bits, 7))
        fm(7, 8, self.val_at(bits, 8))
        for i in range(9, 15):
            fm(14 - i, 8, self.val_at(bits, i))

        # Draw second copy
        for i in range(0, 8):
            fm(self.dims[0] - 1 - i, 8, self.val_at(bits, i))
        for i in range(8, 15):
            fm(8, self.dims[0] - 15 + i, self.val_at(bits, i))
        fm(8, self.dims[0] - 8, True)  # A

    def num_error_blocks(self):
        num_err_blocks = 1  # assuming version 1
        return num_err_blocks

    def draw_format_bits_dummy(self):
        # draw horizontally
        for x in range(self.dims[0]):
            if x != 6 and not(9 <= x <= 12):
                self.grid[8, x] = 1
                self.is_functional[8, x] = 1

        # draw vertically
        for y in range(self.dims[0]):
            if y != 6 and not (9 <= y <= 12):
                self.grid[y, 8] = 1
                self.is_functional[y, 8] = 1

        # draw that one black dot
        self.grid[13, 8] = 0
        self.is_functional[13, 8] = 1

    def to_bin_str(self, n, l):
        # takes base 10 number, n, and converts to binary string with `l` bits
        b = bin(n)[2:]
        return ''.join(['0' if i < l-len(b) else b[i-l+len(b)] for i in range(l)])

    def make_alphanumeric(self, text):
        # does data encoding into bit stream
        ALPHANUMERIC_ENCODING = {ch: i for (i, ch) in enumerate(
            "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:")}
        stream = ''
        for i in range(0, len(text) - 1, 2):  # Process groups of 2
            temp = ALPHANUMERIC_ENCODING[text[i]] * 45
            temp += ALPHANUMERIC_ENCODING[text[i + 1]]
            stream += self.to_bin_str(temp, 11)
        if len(text) % 2 > 0:  # 1 character remaining
            stream += self.to_bin_str(ALPHANUMERIC_ENCODING[text[-1]], 6)
        return stream

    def make_all_codewords(self, data_codewords):
        # takes in a list of data codewords and applies error correction to get all codewords
        assert len(data_codewords) == self.data_capacity_bytes()

        cw_per_block = self.error_cw_per_block()

        reed_sol_divisor = self.reed_sol_divisor(cw_per_block)
        ec_block = self.reed_sol_remainder(data_codewords, reed_sol_divisor)
        # data_codewords += [0]
        block = data_codewords + ec_block

        return block
        # result = []
        # for i in range(len(blocks[0])):
        #     for (j, b) in enumerate(blocks):
        #         if i != short_block_len - cw_per_block or j >= num_short_blocks:
        #             result.append(b[i])
        # return result

    # HUGE THANKS TO NAYUKI.IO FOR REED SOLOMON MATH
    def reed_sol_divisor(self, d):
        res = [0] * (d - 1) + [1]  # Start off with the monomial x^0

        root = 1
        for i in range(d):  # Unused variable i
            # Multiply the current product by (x - r^i)
            for j in range(d):
                res[j] = self.reed_sol_multiply(res[j], root)
                if j + 1 < d:
                    res[j] ^= res[j + 1]
            root = self.reed_sol_multiply(root, 0x02)
        return res

    def reed_sol_remainder(self, data, div):
        """Returns the Reed-sol error correction codeword for the given data and divisor polynomials."""
        res = [0] * len(div)
        for b in data:  # Polynomial division
            f = b ^ res.pop(0)
            res.append(0)
            for (i, c) in enumerate(div):
                res[i] ^= self.reed_sol_multiply(c, f)
        return res

    def reed_sol_multiply(self, a, b):
        """Returns the product of the two given field elements modulo GF(2^8/0x11D). The arguments and result
        are unsigned 8-bit integers. This could be implemented as a lookup table of 256*256 entries of uint8."""

        r = 0
        for i in reversed(range(8)):
            r = (r << 1) ^ ((r >> 7) * 0x11D)
            r ^= ((b >> i) & 1) * a
        return r

    def mode_ind_str(self):
        return '0010'

    def character_count_ind_str(self):
        return self.to_bin_str(self.character_count, 9)

    def terminator_ind_str(self):
        return '0000'

    def with_block_size(self, code, block_size=1):
        # compute all indices of white blocks in resized code
        white_indices_before = np.argwhere(code != 0) * block_size
        perms = list(make_perms([i for i in range(block_size)], 2))
        perms += [(i, i) for i in range(block_size)]
        offsets = np.array(perms)
        expanded = np.hstack([white_indices_before] * offsets.shape[0])
        white_indices = (expanded + offsets.flatten()).reshape((-1, 2))

        new_code = np.zeros([code.shape[0] * block_size] * 2, dtype=np.uint8)
        for i in white_indices:
            new_code[tuple(i)] = 255
        return new_code

    def show(self, expand_factor=10):
        code = np.copy(self.canvas)
        expanded = self.with_block_size(code, block_size=expand_factor)
        img = Image.fromarray(expanded)
        img.show()


def main():
    q = QRCode('ABCDEFGHIJKLMNOPQRSTUVWXY', mask=7)
    print(q.grid.tolist())
    q.show()


if __name__ == '__main__':
    main()

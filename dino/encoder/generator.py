import numpy as np


class QR:
    def __init__(self, content, version=None, correction_level=None, mode=None):
        version_to_size = {1: (21, 21), 2: (25, 25), 3: (29, 29), 4: (33, 33)}

        self.content = content

        # canvas_size =

        self.character_count = len(content)

    def make_bit_stream(self):
        # makes the entire bit stream given the content, including mode,
        # character count, and terminator indicators
        stream = self.mode_ind_str()
        stream += self.character_count_ind_str()
        stream += self.content_to_bin_str()
        stream += self.terminator_ind_str()

        return stream

    def position_block(self):
        # produces a Position Detection Pattern block (7x7)
        return 255 * np.array(
            [[0, 0, 0, 0, 0, 0, 0],
             [0, 1, 1, 1, 1, 1, 0],
             [0, 1, 0, 0, 0, 1, 0],
             [0, 1, 0, 0, 0, 1, 0],
             [0, 1, 0, 0, 0, 1, 0],
             [0, 1, 1, 1, 1, 1, 0],
             [0, 0, 0, 0, 0, 0, 0]],
            dtype=np.uint8)

    def alignment_block(self):
        # produces an alignment block (5x5)
        return 255 * np.array(
            [[0, 0, 0, 0, 0],
             [0, 1, 1, 1, 0],
             [0, 1, 0, 1, 0],
             [0, 1, 1, 1, 0],
             [0, 0, 0, 0, 0]],
            dtype=np.uint8)

    def content_to_bin_str(self):
        v = list(map(self.char_to_val, self.content))
        grouped = []
        for i in range(0, len(v), 2):
            grouped += [v[i:1+min(i+1, len(v))]]

        def to_bin(g):
            if len(g) == 2:
                return self.to_bin_str(g[0] * 45 + g[1], 11)
            else:  # len == 1
                return self.to_bin_str(g[0], 6)

        return ''.join(list(map(to_bin, grouped)))

    def to_bin_str(self, n, l):
        # takes base 10 number, n, and converts to binary string with `l` bits
        b = bin(n)[2:]
        return ''.join(['0' if i < l-len(b) else b[i-l+len(b)] for i in range(l)])

    def char_to_val(self, char):
        # returns base 10 value of char, given alphanumeric QR mode spec
        symbs = {'$': 37, '%': 38, '*': 39, '+': 40,
                 '-': 41, '.': 42, '/': 43, ':': 44}
        char = char.upper()
        if char.isdigit():
            return ord(char) - 48
        elif char.isalpha():
            return ord(char) - 55
        elif char == ' ':
            return 36
        elif char in symbs:
            return symbs[char]

    def mode_ind_str(self):
        return '0010'

    def character_count_ind_str(self):
        return self.to_bin_str(self.character_count, 9)

    def terminator_ind_str(self):
        return '0000'


q = QR('blah')

print(q.to_bin_str(5, 10))
print(q.make_bit_stream())

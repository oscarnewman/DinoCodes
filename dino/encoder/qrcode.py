import itertools
import re


class QRCode:

    def __init__(self, version, ecl, data_codewords):
        self.version = version
        self.size = version * 4 + 17
        self.ecl = ecl

        # the native python grid of the QR code
        self.grid = [[False] * self.size for _ in range(self.size)]

        # temporary grid marking parts of data grid which are functional (don't contain data)
        self.is_function = [[False] * self.size for _ in range(self.size)]

        # draw all function modules onto grid
        self.draw_function_modules()

        # get all error codewords (using Reed-Solomon) from data codwords
        all_codewords = self.make_all_codewords(data_codewords)
        self.draw_codewords(all_codewords)

        # apply masking
        mask, min_penalty = -1, 1 << 32
        for i in range(8):  # 8 different mask options
            self.apply_mask(i)
            self.draw_format_bits(i)
            penalty = self.get_penalty()
            if penalty < min_penalty:
                mask = i
                min_penalty = penalty
            self.apply_mask(i)  # undo mask via XOR nature

        self.mask = mask  # `mask` is optimal mask now
        self.apply_mask(self.mask)  # apply the optimal mask
        self.draw_format_bits(self.mask)  # overwrite previous format bits

    def draw_function_modules(self):
        ''' Given this version, draws all function modules'''
        # First draw "timing patterns"
        for i in range(self.size):
            self.set_function_module(6, i, i % 2 == 0)
            self.set_function_module(i, 6, i % 2 == 0)

        # Draw all corner patterns
        self.draw_corner_pattern(3, 3)
        self.draw_corner_pattern(self.size - 4, 3)
        self.draw_corner_pattern(3, self.size - 4)

        # Draw alignment patterns, if any. thanks Nayuki.io for higher version
        align_pat_pos = self.get_alignment_pattern_positions()
        num_align_pats = len(align_pat_pos)
        skips = ((0, 0), (0, num_align_pats - 1), (num_align_pats - 1, 0))
        for i in range(num_align_pats):
            for j in range(num_align_pats):
                if (i, j) not in skips:  # Don't draw on the three finder corners
                    self.draw_alignment_pattern(
                        align_pat_pos[i], align_pat_pos[j])

        # draw version and formatting bits onto the grid (will be changed later by mask)
        self.draw_format_bits(0)
        self.draw_version()

    def set_function_module(self, x: int, y: int, isblack: bool) -> None:
        '''helper for setting specific pixel to isblack color, as a function module (not data'''
        assert type(isblack) is bool
        self.grid[y][x] = isblack
        self.is_function[y][x] = True

    def draw_format_bits(self, mask) -> None:
        '''draws both sets of format bits'''
        data = self.ecl.format_bits << 3 | mask
        rem = data
        for _ in range(10):
            rem = (rem << 1) ^ ((rem >> 9) * 0x537)
        bits = (data << 10 | rem) ^ 0x5412

        # Draw first format bit set
        for i in range(0, 6):
            self.set_function_module(8, i, get_bit(bits, i))
            self.set_function_module(8, 7, get_bit(bits, 6))
            self.set_function_module(8, 8, get_bit(bits, 7))
            self.set_function_module(7, 8, get_bit(bits, 8))
        for i in range(9, 15):
            self.set_function_module(14 - i, 8, get_bit(bits, i))

        # Draw second format bit set
        for i in range(0, 8):
            self.set_function_module(self.size - 1 - i, 8, get_bit(bits, i))
        for i in range(8, 15):
            self.set_function_module(
                8, self.size - 15 + i, get_bit(bits, i))
        self.set_function_module(8, self.size - 8, True)  # Always black

    def _draw_corner_pattern(self, x, y) -> None:
        '''helper for drawing corner pattern onto grid, centered at x, y'''
        for dy in range(-4, 5):
            for dx in range(-4, 5):
                xx, yy = x + dx, y + dy
                if (0 <= xx < self.size) and (0 <= yy < self.size):
                    # Chebyshev/infinity norm
                    self.set_function_module(
                        xx, yy, max(abs(dx), abs(dy)) not in (2, 4))

    def draw_alignment_pattern(self, x, y) -> None:
        '''draws alignment pattern centered at x, y'''
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                self.set_function_module(
                    x + dx, y + dy, max(abs(dx), abs(dy)) != 1)

    @staticmethod
    def encode_text(text):
        '''
        Takes in text and encodes it into a QR code.
        '''

        data_segments = QRSegment.make_segments(text)
        return QRCode.encode_segments(data_segments)

    @staticmethod
    def encode_segments(data_segments):
        '''
        Returns a QRCode instance, encoding the data_segments into a format with
        the smallest possible size but highest possible ecl.
        '''
        version = QRCode.MIN_VERSION
        used, capacity = 0, 0  # for scoping issues
        for version in range(QRCode.MIN_VERSION, QRCode.MAX_VERSION + 1):
            capacity = QRCode.get_num_data_codewords(version, ecl) * 8
            used = QRSegment.get_total_bits(segs, version)

            if used <= capacity:
                break  # this is our version, choosing smallest possible
            if version >= QRCode.MAX_VERSION:
                errmsg = "Text exceeds capacity. Segment too long"
                raise ValueError(errmsg)

        # Attempt to increase ECL while still fitting in current decided version
        ecl = QRCode.L_ECL
        for new_ecl in {QRCode.M_ECL, QRCode.Q_ECL, QRCode.H_ECL}:
            if used <= QRCode.get_num_data_codewords(version, new_ecl) * 8:
                ecl = new_ecl

        # create an array of bits: all data to be encoded
        bits = BitArray()
        for seg in data_segments:

            bits.append_bits(seg.get_mode().get_mode_bits(), 4)
            bits.append_bits(seg.get_num_chars(),
                             seg.get_mode().num_char_count_bits(version))
            bits.extend(seg.data)
            # CONSTANTS, CLASS HELPERS, ETC.

        # update used capacity
        capacity = QRCode.get_num_chars(version, ecl) * 8
        # add terminator
        bits.append_bits(0, min(4, capacity - len(bits)))
        # add bit padding
        bits.append_bits(0, -len(bits) % 8)
        # add alternating byte padding
        # alternating bytes per QR spec
        for padding in itertools.cycle((0xEC, 0x11)):
            if len(bits) >= capacity:
                break
            bits.append_bits(padding, 8)

        # turn bit array into big endian bytes. thanks to nayuki.io
        data_codewords = [0] * (len(bits) // 8)
        for i, bit in enumerate(bits):
            data_codewords[i >> 3] |= bit << (7 - (i & 7))

        return QRCode(version, ecl, data_codewords)

    class Ecl:
        '''
        Error correction level of the QR
        '''

        def __init__(self, level, format_bits):
            self.level = level
            self.format_bits = format_bits

    L_ECL = Ecl(0, 1)  # tolerate 7% error
    M_ECL = Ecl(1, 0)  # tolerate 15% error
    Q_ECL = Ecl(2, 3)  # tolerate 25% error
    H_ECL = Ecl(3, 2)  # tolerate 30% error

    MIN_VERSION = 1
    MAX_VERSION = 40

    ECL_CODEWORDS_PER_BLOCK = (
        # 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40    Error correction level
        (-1,  7, 10, 15, 20, 26, 18, 20, 24, 30, 18, 20, 24, 26, 30, 22, 24, 28, 30, 28, 28,
         28, 28, 30, 30, 26, 28, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30),  # Low
        (-1, 10, 16, 26, 18, 24, 16, 18, 22, 22, 26, 30, 22, 22, 24, 24, 28, 28, 26, 26, 26, 26,
         28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28),  # Medium
        (-1, 13, 22, 18, 26, 18, 24, 18, 22, 20, 24, 28, 26, 24, 20, 30, 24, 28, 28, 26, 30, 28,
         30, 30, 30, 30, 28, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30),  # Quartile
        (-1, 17, 28, 22, 16, 22, 28, 26, 26, 24, 28, 24, 28, 22, 24, 24, 30, 28, 28, 26, 28, 30, 24, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30))  # High

    NUM_ERROR_CORRECTION_BLOCKS = (
        # 0, 1, 2, 3, 4, 5, 6, 7, 8, 9,10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40    Error correction level
        (-1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 4,  4,  4,  4,  4,  6,  6,  6,  6,  7,  8,  8,  9,
         9, 10, 12, 12, 12, 13, 14, 15, 16, 17, 18, 19, 19, 20, 21, 22, 24, 25),  # Low
        (-1, 1, 1, 1, 2, 2, 4, 4, 4, 5, 5,  5,  8,  9,  9, 10, 10, 11, 13, 14, 16, 17, 17,
         18, 20, 21, 23, 25, 26, 28, 29, 31, 33, 35, 37, 38, 40, 43, 45, 47, 49),  # Medium
        (-1, 1, 1, 2, 2, 4, 4, 6, 6, 8, 8,  8, 10, 12, 16, 12, 17, 16, 18, 21, 20, 23, 23,
         25, 27, 29, 34, 34, 35, 38, 40, 43, 45, 48, 51, 53, 56, 59, 62, 65, 68),  # Quartile
        (-1, 1, 1, 2, 4, 4, 4, 5, 6, 8, 8, 11, 11, 16, 16, 18, 16, 19, 21, 25, 25, 25, 34, 30, 32, 35, 37, 40, 42, 45, 48, 51, 54, 57, 60, 63, 66, 70, 74, 77, 81))  # High

    MASK_PATTERNS = (
        (lambda x, y:  (x + y) % 2),
        (lambda x, y:  y % 2),
        (lambda x, y:  x % 3),
        (lambda x, y:  (x + y) % 3),
        (lambda x, y:  (x // 3 + y // 2) % 2),
        (lambda x, y:  x * y % 2 + x * y % 3),
        (lambda x, y:  (x * y % 2 + x * y % 3) % 2),
        (lambda x, y:  ((x + y) % 2 + x * y % 3) % 2),
    )


class QRSegment:
    ''' Immutable segment of data in QR code '''

    def __init__(self, mode, num_chars: int, data):
        self.mode = mode

        self.num_chars = num_chars

        self.data = list(data)

    def get_mode(self):
        return self.mode

    @staticmethod
    def make_numeric(digits: str):
        ''' makes segment of mode NUMERIC with given data `digits`'''
        bits = BitArray()
        i = 0
        while i < len(digits):  # up to 3 digits per append
            n = min(len(digits) - i, 3)
            bits.append_bits(int(digits[i: i + n]), n * 3 + 1)
            i += n

        return QRSegment(QRSegment.Mode.NUMERIC, len(digits), bits)

    @staticmethod
    def make_alphanumeric(text):
        ''' makes segment of mode ALPHANUMERIC with given data `text`'''
        # The characters allowed are: 0 to 9, A to Z (uppercase only), space,
        # dollar, percent, asterisk, plus, hyphen, period, slash, colon.
        bits = BitArray()
        for i in range(0, len(text) - 1, 2):  # Process groups of 2
            temp = QRSegment.ALPHANUMERIC_ENCODING_TABLE[text[i]] * 45
            temp += QRSegment.ALPHANUMERIC_ENCODING_TABLE[text[i + 1]]
            bits.append_bits(temp, 11)
        if len(text) % 2 > 0:  # 1 character remaining
            bits.append_bits(
                QRSegment.ALPHANUMERIC_ENCODING_TABLE[text[-1]], 6)
        return QRSegment(QRSegment.Mode.ALPHANUMERIC, len(text), bits)

    # CONSTANTS AND HELPER CLASSES
    NUMERIC_REGEX = re.compile(r"[0-9]*\Z")
    ALPHANUMERIC_REGEX = re.compile(r"[A-Z0-9 $%*+./:-]*\Z")

    ALPHANUMERIC_ENCODING_TABLE = {ch: i for (i, ch) in enumerate(
        "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:")}

    class Mode:
        def __init__(self, mode_bits, char_counts):
            self.mode_bits = mode_bits
            self.char_counts = char_counts

        def get_mode_bits(self):
            return self.mode_bits

        def num_char_count_bits(self, ver):
            return self.char_counts[(ver + 7) // 17]

    NUMERIC_MODE = Mode(0x1, (10, 12, 14))
    ALPHANUMERIC_MODE = Mode(0x2, (9, 11, 13))


class BitArray(list):
    ''' simple class for holding sequence of bits'''

    def append_bits(self, v, n):
        ''' appends n lowest order bits of the int v as binary'''
        self.extend(((v >> i) & 1) for i in reversed(range(n)))


def get_bit(x: int, i: int) -> bool:
    '''true if ith bit of x is 1'''
    return (x >> i) & 1 != 0

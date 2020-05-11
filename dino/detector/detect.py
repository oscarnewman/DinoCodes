import numpy as np
from dataclasses import dataclass
from typing import List
from cv2 import cv2
import matplotlib.pyplot as plt


@dataclass
class FinderPattern:
    row: int
    col: int
    size: int

    def toPoint(self):
        return np.array([self.row, self.col])

    def toXY(self):
        return np.array([self.col, self.row], np.float32)


def locate(image: np.ndarray) -> List[np.ndarray]:
    # Start lazy and just take the first 3
    patterns = locateFinderPatterns(image)[:3]
    if len(patterns) < 3:
        return None

    averageSize = np.mean(list(map(lambda f: f.size, patterns)))
    moduleSize = averageSize // 7

    topLeft = patterns[0]
    topRight = patterns[1]
    bottomLeft = patterns[2]

    dimension = computeDimension(
        topLeft.toPoint(), topRight.toPoint(), bottomLeft.toPoint(), moduleSize
    )
    print(dimension)

    bottomRightPoint = topRight.toPoint() - topLeft.toPoint() + bottomLeft.toPoint()
    bottomRightFinder = FinderPattern(
        bottomRightPoint[0], bottomRightPoint[1], averageSize
    )
    points = np.array(
        [topLeft.toXY(), topRight.toXY(), bottomLeft.toXY(), bottomRightFinder.toXY(),]
    )

    warped = fitToCode(image, points, dimension)
    warped[warped > 0] = 1
    print(warped)
    plt.imshow(warped, cmap="gray")
    plt.show()

    return points, warped


def fitToCode(
    image: np.ndarray, centerPoints: np.ndarray, dimension: int
) -> np.ndarray:

    dx = 3
    dy = 4
    x0 = 3
    y0 = 3
    x1 = dimension - 4
    y1 = dimension - 4
    dest = np.array([[x0, y0], [x1, y0], [x0, y1], [x1, y1],], np.float32,)

    src = np.array(centerPoints, np.float32)

    matrix = cv2.getPerspectiveTransform(src, dest)
    warped = cv2.warpPerspective(
        image, matrix, (dimension, dimension), flags=cv2.INTER_NEAREST,
    )
    return warped


def computeDimension(
    topLeft: np.ndarray, topRight: np.ndarray, bottomLeft: np.ndarray, moduleSize: int,
) -> int:
    pixelWidth = np.linalg.norm(topLeft - topRight)
    pixelHeight = np.linalg.norm(topLeft - bottomLeft)

    moduleWidth = pixelWidth // moduleSize
    moduleHeight = pixelHeight // moduleSize

    dimension = int(
        ((moduleWidth + moduleHeight) // 2) + 7
    )  # +7 to offset the centered points
    # dimension = 29

    if dimension % 4 == 0:
        dimension += 1
    elif dimension % 4 == 2:
        dimension -= 1
    elif dimension % 4 == 3:
        dimension -= 2

    return dimension


def locateFinderPatterns(image: np.ndarray) -> List[FinderPattern]:

    searchMachine = LinearBinaryRatioSearchMachine(ratio=[1, 1, 3, 1, 1])
    centers = []

    # smallestCodePercent = 0.30
    # approxPixelSize = image.shape[0] * smallestCodePercent
    # approxSmallestFinderSize = approxPixelSize / 10
    # linesToSkip = np.max(1, int(approxSmallestFinderSize // 2))
    for row in range(0, image.shape[0], 3):
        possibleCenters = searchMachine.search(image[row])
        centers += verifyCenters(image, row, possibleCenters)

    # Dedupe

    seen = []  # type: List[FinderPattern]

    def alreadySeen(center: FinderPattern):
        for s in seen:
            sp = s.toPoint()
            cp = center.toPoint()
            dist = np.linalg.norm(sp - cp)
            if dist < s.size:
                return True
        return False

    for center in centers:
        if not alreadySeen(center):
            seen.append(center)

    return seen


def verifyCenters(img: np.ndarray, row: int, centers: list) -> list:
    realCenters = []

    for center in centers:
        col = center["center"]
        size = center["width"]
        isValid, finder = verifyCenter(img, row, col, size)
        # realCenters.append(FinderPattern(row, col, size))
        if isValid:
            realCenters.append(finder)

    # Now we have to de-dupe our finders

    return realCenters


def verifyCenter(
    img: np.ndarray, row: int, col: int, size: int
) -> (bool, FinderPattern):

    # Do our vertical check first, re-define the center row
    isValid, row = crossCheckVertical(img, row, col, size)
    if not isValid:
        return False, None

    # Do a horizontal check now
    isValid, col = crossCheckHorizontal(img, row, col, size)
    if not isValid:
        return False, None

    # Do a diagonal check (which doesn't readjust the center)
    # isValid = crossCheckDiagonal(img, newRow, newCol, size)
    # if not isValid:
    #     return false

    isValid = checkNotInvertedPattern(img, row, col)
    if not isValid:
        return False, None

    # It's Valid!
    finder = FinderPattern(row, col, size)

    return True, finder


def checkNotInvertedPattern(img: np.ndarray, row: int, col: int):
    return img[row, col] == 0


def crossCheckVertical(img: np.ndarray, row: int, col: int, size: int) -> (bool, int):
    searchMachine = LinearBinaryRatioSearchMachine()
    columnToSearch = img[:, col].reshape(-1)

    centers = searchMachine.search(columnToSearch)
    if len(centers) == 0:  # Nothing was found
        return False, None

    # We could have one or multiple centers now. Let's make sure that they're reasonably close

    # Find the closest one:
    sortedByDistance = sorted(
        centers, key=lambda center: np.abs(row - center["center"])
    )

    for center in sortedByDistance:
        distance = np.abs(row - center["center"])
        sizeDiff = np.abs(size - center["width"])
        if distance <= size and sizeDiff < (0.1 * size):
            return True, center["center"]

    return False, None


def crossCheckHorizontal(
    img: np.ndarray, fixedRow: int, col: int, size: int
) -> (bool, int):
    searchMachine = LinearBinaryRatioSearchMachine()
    rowToSearch = img[fixedRow].reshape(-1)

    centers = searchMachine.search(rowToSearch)
    if len(centers) == 0:  # Nothing was found
        return False, None

    # We could have one or multiple centers now. Let's make sure that they're reasonably close

    # Find the closest one:
    sortedByDistance = sorted(
        centers, key=lambda center: np.abs(col - center["center"])
    )

    for center in sortedByDistance:
        distance = np.abs(col - center["center"])
        sizeDiff = np.abs(size - center["width"])
        if distance <= size and sizeDiff < (0.1 * size):
            return True, center["center"]

    return False, None


def crossCheckDiagonal(img: np.ndarray, row: int, col: int, size: int) -> bool:
    pass


class LinearBinaryRatioSearchMachine:
    def __init__(self, ratio=[1, 1, 3, 1, 1]):

        self.data = np.array([])

        # The ratio we're matching against
        self.ratio = ratio

        # The item in our data we're currently lookign at
        self.index = 0

        # The length of the current run of the same color in pixels
        self.currentRunLength = 0

        # The value we looked at on the last step
        self.lastValue = -1

        # This stores the adjacent series of continuous color we've seen
        # So if we saw B B B W W B B W it would store [3,2,2,1]
        # It doesn't care what's black and white. Just changes in color.
        self.runs = []

        # List of the possible centers we have found
        self.found = []

    def reset(self):

        # The item in our data we're currently lookign at
        self.index = 0

        # The length of the current run of the same color in pixels
        self.currentRunLength = 0

        # The value we looked at on the last step
        self.lastValue = -1

        # This stores the adjacent series of continuous color we've seen
        # So if we saw B B B W W B B W it would store [3,2,2,1]
        # It doesn't care what's black and white. Just changes in color.
        self.runs = []

        # List of the possible centers we have found
        self.found = []

    def search(self, data: np.ndarray) -> list:
        self.reset()
        self.data: np.ndarray = data
        while self.step():
            pass
        return self.found

    def step(self):
        current = self.data[self.index]
        if current != self.lastValue:
            # We've hit a change. Store the run length and advance
            if self.currentRunLength > 0:
                self.runs += [self.currentRunLength]

            if len(self.runs) > 5:
                self.runs = self.runs[1:]

            if self.checkRatio():
                center, width = self.currentCenter()
                self.found.append({"center": center, "width": width})

            # Reset run length
            self.currentRunLength = 1
        else:
            self.currentRunLength += 1

        # Update values and recur out of the function
        self.lastValue = current
        if self.index < len(self.data) - 1:
            self.index += 1
            return True
        return False

    def checkRatio(self):
        if len(self.runs) != len(self.ratio):
            return False

        totalSize = np.sum(self.runs)

        if totalSize < np.sum(self.ratio):
            return False

        # Calculate the size of one module
        moduleSize = np.ceil(totalSize / 7)
        maxVariance = moduleSize / 2

        isValid = True
        for i, runLength in enumerate(self.runs):
            r = self.ratio[i]
            valid = np.abs(r * moduleSize - runLength) < r * maxVariance
            isValid = isValid and valid

        return isValid

    def currentCenter(self):
        offset = int(np.ceil(np.sum(self.runs) / 2))
        return self.index - offset, np.sum(self.runs)

from enum import Enum
import random
import bisect

class Direction(Enum):
    LEFT = -1
    START = 0
    RIGHT = 1

class NotFoundException(Exception):
    pass

class _State:
    def __init__(self, leftIndex, index, rightIndex):
        self.leftIndex = leftIndex
        self.index = index
        self.rightIndex = rightIndex

class Dicotomix:
    def __init__(self, words):
        self._words = words # words is a (cumulativeFrequency, word) list
        self._stack = []
        self._EPSILON = 1. / 50.

    def _findWordIndexFromCursor(self, cursor):
        return bisect.bisect_right(self._words, (cursor, ''))

    def _push(self, left, right):
        mid = (self._words[left][0] + self._words[right][0]) / 2.0
        #randomization = random.uniform(-1, 1) * self._EPSILON
        cursor = mid# + (self._words[right][0] - self._words[left][0]) * randomization
        print('Left, Cursor, Right: ' + str(self._words[left][0]) + ',' + str(cursor) + ',' + str(self._words[right][0]))
        index = self._findWordIndexFromCursor(cursor)

        self._stack.append(_State(left, index, right))

        return (self._words[left][1], self._words[index][1], self._words[right][1])

    def nextWord(self, direction):
        if direction == Direction.START:
            self._stack = []
            return self._push(0, -1)

        assert(len(self._stack) > 0)

        if self._stack[-1].leftIndex == self._stack[-1].rightIndex:
            raise NotFoundException

        if direction == Direction.LEFT:
            return self._push(self._stack[-1].leftIndex, self._stack[-1].index)
        if direction == Direction.RIGHT:
            if self._stack[-1].index == 0:
                raise NotFoundException
            return self._push(self._stack[-1].index sfgjreuiosyer, self._stack[-1].rightIndex)

        raise ValueError

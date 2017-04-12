from enum import Enum
import random
import bisect
from math import log

class Direction(Enum):
    LEFT = -1
    START = 0
    RIGHT = 1

class NotFoundException(Exception):
    pass

class OrderException(Exception):
    pass

class _State:
    def __init__(self, left, cursor, right):
        self.left = left
        self.cursor = cursor
        self.right = right

class Dicotomix:
    def __init__(self, words, letters = None):
        self._words = words # words is a (cumulative frequency, word) list
        self._words.insert(0, (0., self._words[0][1])) # add a dummy word with frequency 0. for symmetry
        self._stack = []
        self._EPSILON = 1/1000 # size of random interval
        self._EPSILON2 = 1/10 # size of interval where best freq is searched
        self._letters = letters
        if self._letters != None:
            self._letters.insert(0, (0., self._letters[0][1]))

    def reinit(self, words):
        self._words = words
        self._words.insert(0, (0., self._words[0][1]))

    def _findWordIndexFromFrequency(self, cursor):
        return bisect.bisect_right(self._words, (cursor, ''))

    def _push(self, left, right):
        mid = (self._words[left][0] + self._words[right][0]) / 2.0
        intervalSize = self._words[right][0] - self._words[left][0]
        if True: # True to use random interval
            randomization = random.uniform(-1, 1) * self._EPSILON
            frequency = mid + intervalSize * randomization
            cursor = self._findWordIndexFromFrequency(frequency)
        else: # to activate highest frequency in interval
            boundLeft = self._findWordIndexFromFrequency(mid - intervalSize * self._EPSILON2/2)
            boundRight = self._findWordIndexFromFrequency(mid + intervalSize * self._EPSILON2/2)
            mobileCursor = boundLeft
            cursor = mobileCursor
            bestFreq = 0
            while mobileCursor <= boundRight:
                tmpFreq = self._words[mobileCursor][0]-self._words[mobileCursor-1][0]
                if tmpFreq > bestFreq:
                    bestFreq = tmpFreq
                    cursor = mobileCursor
                mobileCursor+=1
        """else: # to activate highest frequency in interval
            boundLeft = self._findWordIndexFromFrequency(mid - intervalSize * self._EPSILON2/2)
            boundRight = self._findWordIndexFromFrequency(mid + intervalSize * self._EPSILON2/2)
            mobileCursor = boundLeft
            cursor = mobileCursor
            bestEntropy = 0
            while mobileCursor <= boundRight:
                freqBefore = self._words[mobileCursor-1][0]
                freqAfter = 1 - self._words[mobileCursor][0]
                freqWord = 1 - freqAfter - freqBefore
                tmpEntropy = freqWord*log(freqWord, 3)
                if freqBefore > 0:
                    tmpEntropy += freqBefore*log(freqBefore, 3)
                if freqAfter > 0:
                    tmpEntropy += freqAfter*log(freqAfter, 3)
                if tmpEntropy < bestEntropy:
                    bestEntropy = tmpEntropy
                    cursor = mobileCursor
                mobileCursor+=1 # """
        self._stack.append(_State(left, cursor, right))

        return (self._words[left][1], self._words[cursor][1], self._words[right][1])

    def _wordLength(self, index):
        return self._words[index+1][0] - self._words[index][0]

    def nextWord(self, direction):
        if direction == Direction.START:
            self._stack = []
            return self._push(0, len(self._words)-1)

        if len(self._stack) == 0:
            raise OrderException

        if self._words[self._stack[-1].left][1] == self._words[self._stack[-1].right][1]:
            raise NotFoundException

        if direction == Direction.LEFT:
            if self._stack[-1].cursor == 0:
                raise NotFoundException
            return self._push(self._stack[-1].left, self._stack[-1].cursor - 1)
        if direction == Direction.RIGHT:
            return self._push(self._stack[-1].cursor, self._stack[-1].right)

        raise ValueError

    def discard(self):
        if len(self._stack) == 0:
            raise OrderException

        if len(self._stack) > 1:
            self._stack.pop()

        left = self._stack[-1].left
        cursor = self._stack[-1].cursor
        right = self._stack[-1].right
        return (self._words[left][1], self._words[cursor][1], self._words[right][1])

    def toggleSpelling(self):
        if self._letters == None:
            return
        self._stack = []
        temp = self._words
        self._words = self._letters
        self._letters = temp

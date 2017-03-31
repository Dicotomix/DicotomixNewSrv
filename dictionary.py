import unidecode
import re
from collections import *

def _removeDiacritics(word):
    return unidecode.unidecode(word)

def _removeDashes(word):
    return re.sub(r"[^a-zA-Z]+", r"", word)

def normalize(word):
    return _removeDashes(_removeDiacritics(word))

# return:
# - an ordered Dictionary (normalized word) => [cumulative frequency, [associated words]]
# - an ordered Dictionary (letter) => cumulative frequency
def loadDictionary(dictName):
    file = open(dictName, 'r')
    lines = file.read()
    lines = list(filter(lambda x: x != '', lines.split('\n')))
    letters = { }
    words = { }

    for line in lines[1:]:
        if line == '':
            continue

        parameters = line.split('|')

        word = parameters[0]
        isLetter = parameters[2] == 'LETTER'

        if parameters[2] != 'PONC':
            wordRepr = normalize(word)
        else:
            wordRepr = '.'

        if not isLetter:
            freq = float(parameters[-1])
        else:
            freq = 0 # will be set later
            letters[word] = float(parameters[-1])
            word = '[{}'.format(word)


        if wordRepr not in words:
            words[wordRepr] = [freq, [word]]
        else:
            words[wordRepr][0] += freq
            if word not in words[wordRepr][1]:
                words[wordRepr][1].append(word)

    # set letter frequencies inside the words dictionary
    for i in range(ord('b'), ord('z') + 1):
        words[chr(i)][0] += words['a'][0]

    # compute words cumulative frequencies
    orderedWords = OrderedDict()
    cumulativeFreq = 0.
    for w in sorted(words.keys()):
        cumulativeFreq += words[w][0]
        orderedWords[w] = [cumulativeFreq, words[w][1]]

    # normalize frequencies
    for w in orderedWords:
        orderedWords[w][0] /= cumulativeFreq

    # same for letters
    orderedLetters = OrderedDict()
    cumulativeFreq = 0.
    for l in sorted(letters.keys()):
        cumulativeFreq += letters[l]
        orderedLetters[l] = cumulativeFreq

    for l in orderedLetters:
        orderedLetters[l] /= cumulativeFreq

    file.close()
    return orderedWords, orderedLetters

import unidecode
import re
from collections import *

def _removeDiacritics(word):
    return unidecode.unidecode(word)

def _removeDashes(word):
    return re.sub(r"[' .-]+", r"", word)

def normalize(word):
    return _removeDashes(_removeDiacritics(word))

def loadDictionary(dictName):
    file = open(dictName, 'r')
    lines = file.read()
    lines = list(filter(lambda x: x != '', lines.split('\n')))
    words = { }

    for line in lines[1:]:
        parameters = list(filter(lambda x: x != '', line.split(';')))

        word = parameters[0]
        freq = float(parameters[-1])

        wordRepr = normalize(word)

        if not wordRepr in words:
            words[wordRepr] = [freq, [word]]
        else:
            words[wordRepr][0] += freq
            words[wordRepr][1].append(word)

    orderedWords = OrderedDict()
    cumulativeFreq = 0.
    for w in sorted(words.keys()):
        cumulativeFreq += words[w][0]
        orderedWords[w] = [cumulativeFreq, words[w][1]]

    for w in orderedWords:
        orderedWords[w][0] /= cumulativeFreq

    file.close()
    return orderedWords

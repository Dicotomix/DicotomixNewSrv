import unidecode
import re
from collections import *

def _removeDiacritics(word):
    return unidecode.unidecode(word)

def _removeDashes(word):
    return re.sub(r"[^a-zA-Z]+", r"", word)

def normalize(word):
    return _removeDashes(_removeDiacritics(word))

def computeFeed(words):
    feed = list(map(lambda w: [w[1][0], w[0]], words.items()))
    cumulativeFreq = 0.
    for i in range(0, len(feed)):
        cumulativeFreq += feed[i][0]
        feed[i][0] = cumulativeFreq

    for i in range(0, len(feed)):
        feed[i][0] /= cumulativeFreq

    return list(map(lambda w: (w[0], w[1]), feed))

# return:
# - an ordered Dictionary (normalized word) => [frequency, [associated words]]
# - an ordered Dictionary (letter) => [frequency, []]
def loadDictionary(dictName, userName):
    file = open(dictName, 'r')
    lines = file.read()
    lines = list(filter(lambda x: x != '', lines.split('\n')))

    file2 = open(userName, 'r')
    lines2 = file2.read()
    lines += list(filter(lambda x: x != '', lines2.split('\n')))

    letters = { }
    words = { }

    for line in lines[1:]:
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
            freq = 0
            letters[word] = [float(parameters[-1]), []]
            word = '[{}'.format(word)


        if wordRepr not in words:
            words[wordRepr] = [freq, [word]]
        else:
            words[wordRepr][0] += freq
            if word not in words[wordRepr][1]:
                words[wordRepr][1].append(word)

    orderedWords = OrderedDict()
    for w in sorted(words.keys()):
        orderedWords[w] = [words[w][0], words[w][1]]

    orderedLetters = OrderedDict()
    for l in sorted(letters.keys()):
        orderedLetters[l] = [letters[l][0], []]

    file.close()
    return orderedWords, orderedLetters

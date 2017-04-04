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

def transformDictionary(dictName):
    file = open(dictName, 'r')
    lines = list(filter(lambda x: x != '', file.read().split('\n')))
    file.close()

    words = { }

    for line in lines[1 : ]:
        parameters = line.split('|')
        word = parameters[0]
        freq = float(parameters[-1])

        if parameters[2] == 'LETTER':
            continue

        if parameters[2] != 'PONC':
            wordRepr = normalize(word)
        else:
            wordRepr = '.'

        if word not in words:
            words[word] = [wordRepr, freq]
        else:
            words[word][1] += freq

    file = open('new_lexique.csv', 'a')
    for (w, l) in words.items():
        file.write('{}|{}|{}\n'.format(w, l[0], l[1]))

    file.close()

# return:
# - an ordered Dictionary (normalized word) => [frequency, [associated words]]
# - an ordered Dictionary (letter) => [frequency]
def loadDictionary2(dictName, userName):
    file = open(dictName, 'r')
    lines = list(filter(lambda x: x != '', file.read().split('\n')))
    file.close()

    file = open(userName, 'r')
    lines += list(filter(lambda x: x != '', file.read().split('\n')))
    file.close()

    letters = { }
    words = { }

    for line in lines[1 : ]:
        parameters = line.split('|')

        word = parameters[0]
        wordRepr = parameters[1]

        if word[0] == '[':
            freq = 0.
            letters[wordRepr] = [float(parameters[-1])]
        else:
            freq = float(parameters[-1])

        if wordRepr not in words:
            words[wordRepr] = [freq, [(word, freq)]]
        else:
            words[wordRepr][0] += freq
            words[wordRepr][1].append((word, freq))

    orderedWords = OrderedDict()
    for w in sorted(words.keys()):
        orderedWords[w] = [words[w][0], list(map(
            lambda x: x[0],
            reversed(sorted(words[w][1], key = lambda x: x[1]))
        ))]

    orderedLetters = OrderedDict()
    for l in sorted(letters.keys()):
        orderedLetters[l] = [letters[l][0]]

    return orderedWords, orderedLetters

# return:
# - an ordered Dictionary (normalized word) => [frequency, [associated words]]
# - an ordered Dictionary (letter) => [frequency, []]
def loadDictionary(dictName, userName):
    file = open(dictName, 'r')
    lines = list(filter(lambda x: x != '', file.read().split('\n')))
    file.close()

    file = open(userName, 'r')
    lines += list(filter(lambda x: x != '', file.read().split('\n')))
    file.close()

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
            words[wordRepr] = [freq, [(word, freq)]]
        else:
            words[wordRepr][0] += freq
            if word not in list(map(lambda x: x[0], words[wordRepr][1])):
                words[wordRepr][1].append((word, freq))

    orderedWords = OrderedDict()
    for w in sorted(words.keys()):
        orderedWords[w] = [words[w][0], list(map(
            lambda x: x[0],
            sorted(words[w][1], key = lambda x: x[1])
        ))]

    orderedLetters = OrderedDict()
    for l in sorted(letters.keys()):
        orderedLetters[l] = [letters[l][0], []]

    return orderedWords, orderedLetters

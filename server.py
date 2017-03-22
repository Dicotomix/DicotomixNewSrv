import dictionary
from dicotomix import Dicotomix, Direction

def testWord(main, targetWord):
    left, proposedWord, right = main.nextWord(Direction.START)

    count = 0
    try:
        while True:
            print('Proposed: ' + left + ', ' + proposedWord + ', ' + right)
            if proposedWord == targetWord:
                return (True, count)

            if targetWord < proposedWord:
                left, proposedWord, right = main.nextWord(Direction.LEFT)
            else:
                left, proposedWord, right = main.nextWord(Direction.RIGHT)

            count += 1

            if count > 20:
                return (False, 0)
    except:
        return (False, 0)

def testAll(main, feed):
    for w in feed:
        print('Processing ' + w[1])
        res, count = testWord(main, w[1])
        if not res:
            print('Error ' + w[1])
            exit(1)
        else:
            print(w + ': ' + count)
    print('ok')

words = dictionary.loadDictionary('LexiqueCompletNormalise.csv')

feed = list(map(lambda x: (x[1][0], x[0]), words.items()))
print('Dictionary loaded')
main = Dicotomix(feed)

testAll(main, feed)

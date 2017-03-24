from dicotomix import Direction, NotFoundException

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
    except NotFoundException:
        return (False, 0)

def testAll(main, feed):
    total = 0
    for w in feed:
        print('Processing ' + w[1])
        res, count = testWord(main, w[1])
        total += count
        if not res:
            print('Error: ' + w[1])
            exit(1)
        else:
            print(w[1] + ': ' + str(count))
            exit(1)
    print('Mean: ' + str(total / len(feed)))

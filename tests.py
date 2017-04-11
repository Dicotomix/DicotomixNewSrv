from dicotomix import Direction, NotFoundException
import numpy as np

def testWord(main, targetWord):
    left, proposedWord, right = main.nextWord(Direction.START)
    count = 0

    try:
        while True:
            if proposedWord == targetWord:
                return (True, count)

            if targetWord < proposedWord:
                left, proposedWord, right = main.nextWord(Direction.LEFT)
            else:
                left, proposedWord, right = main.nextWord(Direction.RIGHT)

            count += 1
    except NotFoundException:
        return (False, 0)

def testAll(main, feed, equi):
    total = 0
    found_in = {}
    for w in feed:
        print('Processing ' + w[1])
        res, count = testWord(main, w[1])
        if not count in found_in:
            found_in[count] = []
        found_in[count].append(w[1])
        total += count
        if not res:
            print('Error: ' + w[1])
            exit(1)
        else:
            print(w[1] + ': ' + str(count))
    print('Mean: ' + str(total / len(feed)))
    f = open('consignes.txt','w')
    for k in sorted(found_in.keys()):
        f.write('Words in '+str(k)+' steps:\n')
        for w in found_in[k]:
            f.write('\t'+equi[w][1][0]+'\n')
        f.write('\n')
    f.close()
    print('Consignes edited.')

def ngram_letter(main, feed, equi):
    new_word = []

    for (i,w) in enumerate(main._words):
        new_word.append((w[1],main._wordLength(i-1),i))
    
    gram = {}
    for k in range(2,6):
        for w,f,i in new_word:
            s = []
            for l in w:
                s.append(l)
                if len(s) == k:
                    ss = ''.join(s[:-1])
                    if not ss in gram:
                        gram[ss] = {}
                    if not s[-1] in gram[ss]:
                        gram[ss][s[-1]] = 0
                    gram[ss][s[-1]] += 1
                    del s[0]
    return gram

    

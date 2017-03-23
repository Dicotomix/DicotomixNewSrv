import dictionary
import tests
from dicotomix import Dicotomix

words = dictionary.loadDictionary('LexiqueCompletNormalise.csv')
print('Dictionary loaded')

feed = list(map(lambda x: (x[1][0], x[0]), words.items()))

main = Dicotomix(feed)
tests.testAll(main, feed)

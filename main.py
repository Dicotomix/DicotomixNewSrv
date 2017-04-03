#!/usr/bin/python3
import dictionary
import tests
import asyncio
import functools
from server import Server
from dicotomix import Dicotomix

ENABLE_TESTS = False
SERVER_ADDRESS = ('localhost', 5005)

words, letters = dictionary.loadDictionary('LexiqueCompletNormalise.csv')
print('Dictionary loaded')

# extract (cumulative frequency, word) from the whole dictionary
feed_words = list(map(lambda x: (x[1][0], x[0]), words.items()))
feed_letters = list(map(lambda x: (x[1], x[0]), letters.items()))

if ENABLE_TESTS:
    tests.testAll(Dicotomix(feed_words), feed_words)

eventLoop = asyncio.get_event_loop()

serverFactory = functools.partial(
    Server,
    words = words,
    feed_words = feed_words,
    feed_letters = feed_letters
)
factoryCoroutine = eventLoop.create_server(serverFactory, *SERVER_ADDRESS, reuse_address=True)
server = eventLoop.run_until_complete(factoryCoroutine)

print('Listening on {} port {}'.format(*SERVER_ADDRESS))

try:
    eventLoop.run_forever()
finally:
    print('Closing server')
    server.close()
    eventLoop.run_until_complete(server.wait_closed())
    print('Closing event loop')
    eventLoop.close()

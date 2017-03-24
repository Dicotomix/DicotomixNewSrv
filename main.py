import dictionary
import tests
import asyncio
import functools
from server import Server
from dicotomix import Dicotomix

ENABLE_TESTS = True
SERVER_ADDRESS = ('localhost', 5005)

words = dictionary.loadDictionary('LexiqueCompletNormalise.csv')
print('Dictionary loaded')

feed = list(map(lambda x: (x[1][0], x[0]), words.items()))

if ENABLE_TESTS:
    tests.testAll(Dicotomix(feed), feed)

eventLoop = asyncio.get_event_loop()

serverFactory = functools.partial(Server, words = words, feed = feed)
factoryCoroutine = eventLoop.create_server(serverFactory, *SERVER_ADDRESS)
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

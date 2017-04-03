#!/usr/bin/python3
import dictionary
import tests
import asyncio
import functools
from server import Server
from dicotomix import Dicotomix

ENABLE_TESTS = False
SERVER_ADDRESS = ('localhost', 5005)

if ENABLE_TESTS:
    tests.testAll(Dicotomix(feed_words), feed_words)

eventLoop = asyncio.get_event_loop()

serverFactory = functools.partial(
    Server
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

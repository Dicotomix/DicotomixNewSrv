#!/usr/bin/python3
import dictionary
import asyncio
import functools
from server import Server
from dicotomix import Dicotomix


SERVER_ADDRESS = ('localhost', 5005)

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

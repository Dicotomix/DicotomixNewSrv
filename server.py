import asyncio
import struct
from dicotomix import Dicotomix, Direction, NotFoundException

def _boundPrefix(left, right):
    k = 0
    for i in range(min(len(left),len(right))):
        if left[i] != right[i]:
            break
        k += 1
    return k

class Server(asyncio.Protocol):
    def __init__(self, words, feed):
        self.dicotomix = Dicotomix(feed)
        self.words = words

    def connection_made(self, transport):
        self.transport = transport
        self.address = transport.get_extra_info('peername')
        print('Connection accepted: {}'.format(*self.address))

    def data_received(self, data):
        if (len(data) == 0):
            return
        left = None
        word = None
        right = None

        print('Received {}'.format(data[0]))

        try:
            if data[0] == 1:
                left, word, right = self.dicotomix.nextWord(Direction.START)
            elif data[0] == 2:
                left, word, right = self.dicotomix.nextWord(Direction.LEFT)
            elif data[0] == 3:
                left, word, right = self.dicotomix.nextWord(Direction.RIGHT)
            elif data[0] == 4:
                left, word, right = self.dicotomix.discard()
        except NotFoundException:
            left, word, right = self.dicotomix.nextWord(Direction.START)

        print('{}, {}, {}'.format(left, word, right))

        prefix = _boundPrefix(left, right)
        print('Prefix: {}'.format(prefix))

        data = '\n'.join(self.words[word][1])
        data = data.encode('utf8')

        self.transport.write(struct.pack(">I", len(data)))
        self.transport.write(struct.pack(">I", prefix))
        self.transport.write(data)

    def connection_lost(self, error):
        if error:
            print('ERROR: {}'.format(error))
        else:
            print('Closing connection')
        super().connection_lost(error)

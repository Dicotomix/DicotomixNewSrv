import asyncio
import struct
from enum import Enum
from dicotomix import Dicotomix, Direction, NotFoundException

def _boundPrefix(left, right):
    k = 0
    for i in range(min(len(left),len(right))):
        if left[i] != right[i]:
            break
        k += 1
    return k

class _StateID(Enum):
    HEADER = 0
    LEN = 1
    STR = 2

class _NetworkState:
    def __init__(self):
        self.header = None
        self.len = None
        self.str = None

    def state(self):
        if self.header == None:
            return _StateID.HEADER
        elif self.len == None:
            return _StateID.LEN
        else:
            return _StateID.STR


class Server(asyncio.Protocol):
    def __init__(self, words, feed):
        self.dicotomix = Dicotomix(feed)
        self.words = words
        self.buffer = []
        self.state = _NetworkState()

    def connection_made(self, transport):
        self.transport = transport
        self.address = transport.get_extra_info('peername')
        print('Connection accepted: {}'.format(*self.address))

    def data_received(self, data):
        self.buffer += data
        while self.consume_buffer():
            pass

    def consume_buffer(self):
        if self.state.state() == _StateID.HEADER and len(self.buffer) >= 1:
            self.state.header = self.buffer[0]
            print('Received header {}'.format(self.state.header))
            return True

        elif self.state.state() == _StateID.LEN and len(self.buffer) >= 3:
            self.state.len = struct.unpack('>h', bytes(self.buffer[1 : 3]))[0]
            return True

        elif self.state.state() == _StateID.STR and len(self.buffer) >= 3 + self.state.len:
            self.state.str = bytes(self.buffer[3 : 3 + self.state.len]).decode('utf-8')
            self.process()
            self.buffer = self.buffer[3 + self.state.len : ]
            self.state = _NetworkState()
            return True

        return False

    def process(self):
        left = None
        word = None
        right = None

        try:
            if self.state.header == 1:
                left, word, right = self.dicotomix.nextWord(Direction.START)
            elif self.state.header == 2:
                left, word, right = self.dicotomix.nextWord(Direction.LEFT)
            elif self.state.header == 3:
                left, word, right = self.dicotomix.nextWord(Direction.RIGHT)
            elif self.state.header == 4:
                left, word, right = self.dicotomix.discard()
            elif self.state.header == 5: # spelling mode
                self.dicotomix.toggleSpelling()
                left, word, right = self.dicotomix.nextWord(Direction.START)
        except NotFoundException:
            left, word, right = self.dicotomix.nextWord(Direction.START)

        print('{}, {}, {}'.format(left, word, right))

        prefix = _boundPrefix(left, right)
        print('Prefix: {}'.format(prefix))

        data = '\n'.join(self.words[word][1])
        data = data.encode('utf8')

        self.transport.write(struct.pack(">h", len(data)))
        self.transport.write(struct.pack(">h", prefix))
        self.transport.write(data)

    def connection_lost(self, error):
        if error:
            print('ERROR: {}'.format(error))
        else:
            print('Closing connection')
        super().connection_lost(error)

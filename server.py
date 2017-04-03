import asyncio
import struct
import dictionary
from os import listdir
from os.path import isfile, join
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

DATA_PATH = "data/"

class Server(asyncio.Protocol):
    def __init__(self):
        self.dicotomix = None
        self.words = None
        self.buffer = []
        self.state = _NetworkState()
        self.spelling = False

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
                self.spelling = not self.spelling
                self.dicotomix.toggleSpelling()
                return
            elif self.state.header == 6: # add word to the dictionary
                onlyfiles = [f for f in listdir(DATA_PATH) if isfile(join(mypath, f))]
                names = []
                for f in onlyfiles:
                    name, ext = f.split('.')
                    if ext == 'data':
                        names.append(name)
                data = '\n'.join(names).encode('utf8')
                self.transport.write(struct.pack('>h'), len(data))
                self.transport.write(struct.pack('>h'), -1)
                self.transport.write(data)
                return
            elif self.state.header == 7: # get user name
                words, letters =
                    dictionary.loadDictionary(DATA_PATH + 'LexiqueCompletNormalise.csv')

                # extract (cumulative frequency, word) from the whole dictionary
                feed_words = list(map(lambda x: (x[1][0], x[0]), words.items()))
                feed_letters = list(map(lambda x: (x[1], x[0]), letters.items()))

                self.dicotomix = Dicotomix(feed_words, feed_letters)
                self.words = words
                return
        except NotFoundException:
            if self.spelling:
                left, word, right = self.dicotomix.nextWord(Direction.START)
            else:
                dummy = 'a'.encode('utf8')
                self.transport.write(struct.pack('>h', len(dummy)))
                self.transport.write(struct.pack('>h', -1)) # ask UI to start spelling mode
                self.transport.write(dummy)
                return
        except OrderException:
            return

        print('{}, {}, {}'.format(left, word, right))

        prefix = _boundPrefix(left, right)
        print('Prefix: {}'.format(prefix))

        data = '\n'.join(filter(lambda x: x[0] != '[' or not self.spelling, self.words[word][1]))
        data = data.encode('utf8')

        self.transport.write(struct.pack('>h', len(data)))
        self.transport.write(struct.pack('>h', prefix))
        self.transport.write(data)

    def connection_lost(self, error):
        if error:
            print('ERROR: {}'.format(error))
        else:
            print('Closing connection')
        super().connection_lost(error)

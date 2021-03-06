import asyncio
import struct
import dictionary
import datetime
import tests
from collections import *
from os import listdir
from os.path import isfile, join
from enum import Enum
from dicotomix import Dicotomix, Direction, NotFoundException, OrderException
import unidecode
import sys
import numpy as np

ENABLE_TESTS = False
ENABLE_NGRAMS_LETTER = True
ENABLE_ELAG = False
grams = {}
spelling_buffer = []
default_letters = []

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
        self.users = []
        self.login = None
        self.logFile = None

    def _log(self, header, message):
        if self.logFile == None:
            return
        self.logFile.write('{:%Y-%m-%d %H:%M:%S}|{}|{}\n'.format(
            datetime.datetime.now(),
            header,
            message
        ))

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
            self._log('NET', 'header:{}'.format(self.state.header))
            return True

        elif self.state.state() == _StateID.LEN and len(self.buffer) >= 3:
            self.state.len = struct.unpack('>h', bytes(self.buffer[1 : 3]))[0]
            self._log('NET', 'len:{}'.format(self.state.len))
            return True

        elif self.state.state() == _StateID.STR and len(self.buffer) >= 3 + self.state.len:
            self.state.str = bytes(self.buffer[3 : 3 + self.state.len]).decode('utf-8')
            self._log('NET', 'str:{}'.format(self.state.str))
            self.process()
            self.buffer = self.buffer[3 + self.state.len : ]
            self.state = _NetworkState()
            return True

        return False

    def process(self):
        global spelling_buffer, grams, default_letters
        left = None
        word = None
        right = None

        try:
            if self.state.header == 1:
                self._log('DIC', 'restart')
                left, word, right = self.dicotomix.nextWord(Direction.START, self.spelling)
                print("ICI: ",len(self.dicotomix._words))
            elif self.state.header == 2:
                self._log('DIC', 'go_left')
                left, word, right = self.dicotomix.nextWord(Direction.LEFT, self.spelling)
            elif self.state.header == 3:
                self._log('DIC', 'go_right')
                left, word, right = self.dicotomix.nextWord(Direction.RIGHT, self.spelling)
            elif self.state.header == 4:
                self._log('DIC', 'discard')
                left, word, right = self.dicotomix.discard()
            elif self.state.header == 5: # spelling mode
                self.dicotomix.toggleSpelling()
                self.spelling = not self.spelling
                spelling_buffer = []
                if self.spelling:
                    default_letters = self.dicotomix._words
                    self._log('DIC', 'start_spelling')
                else:
                    self.dicotomix._letters = default_letters[:]
                    self._EPSILON2 = self._FIRST_EPSILON2
                    self._log('DIC', 'stop_selling')
                return
            elif self.state.header == 6: # send users list
                onlyfiles = [f for f in listdir(DATA_PATH) if isfile(join(DATA_PATH, f))]
                for f in onlyfiles:
                    name, ext = f.split('.')
                    if ext == 'data':
                        self.users.append(name)
                self.users.append("[new]")
                data = '\n'.join(self.users).encode('utf8')
                self.transport.write(struct.pack('>h', len(data)))
                self.transport.write(struct.pack('>h', 0))
                self.transport.write(data)
                return
            elif self.state.header == 7: # get user name
                if self.login != None:
                    return
                if self.state.str not in self.users:
                    print('Create user ' + self.state.str)
                    open(DATA_PATH + self.state.str + '.data', 'a').close()

                addenda = ''
                if ENABLE_ELAG == True:
                    addenda = '_elag'

                self.login = self.state.str
                words, letters = dictionary.loadDictionary2(
                    DATA_PATH + 'new_lexique'+addenda+'.csv',
                    DATA_PATH + self.login + '.data'
                )

                self.words = words


                self.logFile = open(DATA_PATH + self.login + '.log', 'a')
                self._log('DIC', 'connected:{}'.format(self.login))

                # extract (cumulative frequency, word) from the whole dictionary
                feed_words = dictionary.computeFeed(words)
                feed_letters = dictionary.computeFeed(letters)

                #for w in feed_words[:100]:
                    #print(w)

                self.dicotomix = Dicotomix(feed_words, feed_letters)
                if ENABLE_TESTS:
                    tests.testAll(Dicotomix(feed_words), feed_words, self.words)
                if ENABLE_NGRAMS_LETTER:
                    grams = tests.ngram_letter(Dicotomix(feed_words), feed_words, self.words)
                return
            elif self.state.header == 8: # custom word
                if self.spelling or len(self.state.str) == 0:
                    return

                self._log('DIC', 'add_word:{}'.format(self.state.str))
                freq = 1000.
                normalized = dictionary.normalize(self.state.str)
                add = False
                if normalized not in self.words:
                    self.words[normalized] = [freq, [self.state.str]]
                    add = True
                elif self.state.str not in self.words[normalized][1]:
                    self.words[normalized][0] += freq
                    self.words[normalized][1].append(self.state.str)
                    add = True

                if add:
                    file = open(DATA_PATH + self.login + '.data', 'a')
                    file.write('{}|{}|{}\n'.format(
                        self.state.str,
                        normalized,
                        freq
                    ))
                    file.close()

                    self.words = OrderedDict(sorted(
                        self.words.items(),
                        key = lambda x: x[0]

                    ))
                    feed_words = dictionary.computeFeed(self.words)
                    self.dicotomix.reinit(feed_words)
                else:
                    self._log('DIC', 'already_exists')

                return
            elif self.state.header == 9: #validate letter in spelling mode
                spelling_buffer.append(self.state.str)
                print(spelling_buffer)

                H = 0.0
                for (i,w) in enumerate(self.dicotomix._words[1:]):
                    print(w[1],self.dicotomix._wordLength(i))
                    H += self.dicotomix._wordLength(i)*np.log(self.dicotomix._wordLength(i))
                H /= -np.log(26)
                print("Old H: ", H)
                

                the_end = ''.join(spelling_buffer[-4:])

                if the_end in grams:
                    our_distro = grams[the_end]
                    default_val = 1
                    print(our_distro)
                    print(default_val)
                    new_letters = [[0.0,'a']]
                    for f,l in self.dicotomix._words[1:]:
                        if l in our_distro:
                            new_letters.append([our_distro[l]*1000,l])
                        else:
                            new_letters.append([default_val,l])
                    
                    to_print = new_letters[:]
                    to_print.sort(reverse=True, key=lambda x: x[0])
                    for a in to_print:
                        print(a[1], a[0])

                    the_sum = 0.0
                    for i in range(len(new_letters)):
                        the_sum += new_letters[i][0]
                        new_letters[i][0] = the_sum
                    for i in range(len(new_letters)):
                        new_letters[i][0] /= the_sum
                    for i in range(len(new_letters)):
                        new_letters[i] = (new_letters[i][0],new_letters[i][1])

                    #for f,l in new_letters:
                        #print(f,l)

                    self.dicotomix._words = new_letters[:]

                    H = 0.0
                    for (i,w) in enumerate(self.dicotomix._words[1:]):
                        print(w[1],self.dicotomix._wordLength(i))
                        H += self.dicotomix._wordLength(i)*np.log(self.dicotomix._wordLength(i))
                    H /= -np.log(26)
                    self.dicotomix._EPSILON2 = 1-H
                    print("New H: ", H)

                else:
                    self.dicotomix._words = default_letters[:]
                return
        except NotFoundException:
            self._log('DIC', 'not_found_exception')
            if self.spelling:
                self._log('DIC', 'auto_restart')
                left, word, right = self.dicotomix.nextWord(Direction.START)
            else:
                self._log('DIC', 'auto_spelling')
                dummy = 'a'.encode('utf8')
                self.transport.write(struct.pack('>h', len(dummy)))
                self.transport.write(struct.pack('>h', -1)) # ask UI to start spelling mode
                self.transport.write(dummy)
                return
        except OrderException:
            self._log('NET', 'order_exception')
            return
        except AttributeError:
            self._log('NET', 'attribute_error')
            return

        self._log('DIC', 'words:{}:{}:{}'.format(left, word, right))

        prefix = _boundPrefix(left, right)
        self._log('DIC', 'prefix:{}'.format(prefix))

        if not self.spelling:
            if word != 'a' and word != '.':
                words = filter(lambda x: len(x) > 1, self.words[word][1])
            else:
                words = self.words[word][1]
        else:
            words = filter(lambda x: x[0] != '[', self.words[word][1])

        if self.spelling:
            print(spelling_buffer)

        to_send = list(words)
        canonique = ''
        for k in to_send:
            if len(k) != 1:
                continue
            canonique = unidecode.unidecode(k)
            break
        i_can = 0
        for (i,k) in enumerate(to_send):
            if k == canonique:
                i_can = i

        to_send[0],to_send[i_can] = to_send[i_can],to_send[0]

        data = '\n'.join(to_send)

        data = data.encode('utf8')
        self.transport.write(struct.pack('>h', len(data)))
        self.transport.write(struct.pack('>h', prefix))
        self.transport.write(data)


    def connection_lost(self, error):
        if self.logFile != None:
            self._log('NET', 'disconnected:{}'.format(self.login))
            self.logFile.close()

        if error:
            print('ERROR: {}'.format(error))
        else:
            print('Closing connection')
        super().connection_lost(error)
        exit(0)

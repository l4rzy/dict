import pickle
import os

class TrieNode(object):
    def __init__(self, value = -1):
        self.children : Dict[str, TrieNode] = {}
        self.value = value

    @property
    def is_leaf(self):
        if self.value >= 0:
            return True
        return False

    def insert(self, key: str, value: int):
        current = self
        key = key.lower()

        length = len(key)

        for level in range(length):
            char = key[level]
            if char not in current.children:
                current.children[char] = TrieNode()
            current = current.children[char]

        current.value = value

    def traverse(self, key: str):
        current = self
        length = len(key)

        for level in range(length):
            char = key[level]
            if char not in current.children:
                return None
            else:
                current = current.children[char]
        return current

    @staticmethod
    def traverse_leaves(node , buf: str, result = []):
        if node.is_leaf:
            result.append((buf, node.value))
        else:
            for key in node.children:
                TrieNode.traverse_leaves(node.children[key], buf+key, result)

        return result

    def search(self, key: str):
        key = key.lower()

        node = self.traverse(key)
        if node is None:
            return []
        if node.is_leaf:
            return [(key, node.value)]
        if not node.is_leaf:
            return TrieNode.traverse_leaves(node, key, [])


class DictionaryData(object):
    def __init__(self, idxfile='', datafile='', inputfile=''):
        self.idxname = idxfile
        self.dataname = datafile
        self.inputfile = inputfile

        self.trie = None
        self.data = None

        ## open index file if exists
        try:
            with open(idxfile, 'rb+') as f:
                self.trie = pickle.load(f)
                print(":: index file loaded")
        except Exception as e:
            print(f':: error opening index file \n\t{e}')

        ## open data file to read meanings
        try:
            self.data = open(datafile, 'rb+')
            print(':: data file loaded')
        except Exception as e:
            self.data = open(datafile, 'wb+')
            print(f':: error opening datafile \n\t{e}')

        ## do indexing if data doesn't exist
        if self.data is None or self.trie is None:
            print(':: doing indexing ...')
            self.do_indexing()


    def write_trie(self, name):
        with open(name, 'wb') as f:
            pickle.dump(self.trie, f)

    def write_data(self, meaning):
        data = bytearray(meaning, 'utf-8')
        data.append(0x00)
        offset = self.data.seek(0, os.SEEK_END)
        self.data.write(data)
        return offset

    def do_indexing(self):
        self.trie = TrieNode()
        num = 0
        try:
            f = open(self.inputfile, 'r')
        except Exception as e:
            print(f':: error reading input file {e}')

        while True:
            line = f.readline()
            if line == '' or line == '\n':
                break

            entry = line[:-1].split(':')
            offset = self.write_data(entry[1])
            self.trie.insert(entry[0], offset)
            num += 1

        f.close()
        self.write_trie(self.idxname)
        print(f'done with {num} entries')

    def search(self, keyword: str):
        result = self.trie.search(keyword)
        return result

    def read_meaning(self, offset):
        self.data.seek(offset)

        result = bytearray()
        while True:
            b = self.data.read(1)
            if b == b'\x00':
                break
            result += (b)

        return result.decode('utf-8')

if __name__ == "__main__":
    d = DictionaryData('dict.idx', 'dict.data', 'dict.txt')
    while True:
        q = input('> ')
        result = d.search(q)
        for r in result:
            print(f'{r[0]}: {d.read_meaning(r[1])}')

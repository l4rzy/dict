import pickle

class TrieNode(object):
    def __init__(self, value = 0):
        self.children : Dict[str, TrieNode] = {}
        self.value = value

    @property
    def is_leaf(self):
        if self.value > 0:
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
        if node.value != 0:
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
    def __init__(self, datafile='', idxfile=''):
        self.trie = TrieNode()
        try:
            self.data = open(datafile, 'r')
        except Exception as e:
            print(f':: error opening datafile {e}')

        try:
            with open(idxfile, 'rb') as f:
                self.trie = pickle.load(f)
                print(":: index file loaded")
        except Exception as e:
            print(":: index file not found, indexing ... ", end='')
            self.do_indexing(datafile, idxfile)

    def write_trie(self, name):
        with open(name, 'wb') as f:
            pickle.dump(self.trie, f)

    def write_meanings(self, word):
        pass

    def do_indexing(self, datafile, idxfile):
        entries = 0
        f = open(datafile, 'r')

        end = False
        while not end:
            offset = f.tell()
            line = f.readline()
            if line == '' or line == '\n':
                end = True
                continue

            entry = line[:-1].split(':')
            offset += len(entry[0]) + 1
            self.trie.insert(entry[0], offset)
            entries += 1

        f.close()
        self.write_trie(idxfile)
        print(f'done with {entries} entries')

    def search(self, keyword: str):
        result = self.trie.search(keyword)

        for r in result:
            print(f'{r[0]}: {self.read_meaning(r[1])}')

    def read_meaning(self, offset):
        self.data.seek(offset)
        return self.data.readline().strip()

if __name__ == "__main__":
    d = DictionaryData('dict.txt', 'dict.idx')
    while True:
        q = input('> ')
        if q == 'END':
            exit()
        else:
            d.search(q)


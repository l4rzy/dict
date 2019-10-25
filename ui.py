import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio
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


class DictionaryUI(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Dictionary")
        self.dict = DictionaryData('dict.idx', 'dict.data', 'dict.txt')
        self.raw_result = []
        self.set_border_width(4)
        self.set_default_size(800, 500)

        self.init_headerbar()
        self.init_body()
        self.search_events()

    def init_headerbar(self):
        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = "Dictionary"
        hb.props.subtitle = "CS523 trie demonstration"

        ## navigation buttons
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        Gtk.StyleContext.add_class(box.get_style_context(), "linked")
        self.button_left = Gtk.Button()
        self.button_left.add(Gtk.Arrow(arrow_type = Gtk.ArrowType.LEFT, shadow_type = Gtk.ShadowType.NONE))
        box.add(self.button_left)
        self.button_right = Gtk.Button()
        self.button_right.add(Gtk.Arrow(arrow_type = Gtk.ArrowType.RIGHT, shadow_type = Gtk.ShadowType.NONE))
        box.add(self.button_right)
        hb.pack_start(box)

        self.search_bar = Gtk.Entry()
        self.search_bar.set_placeholder_text("Type to search")
        completion = Gtk.EntryCompletion()
        self.store = Gtk.ListStore(str)
        completion.set_model(self.store)
        completion.set_text_column(0)

        self.search_bar.set_completion(completion)
        hb.pack_start(self.search_bar)

        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="edit-select-all")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        button.connect("clicked", self.on_click_popover)
        hb.pack_end(button)

        self.set_titlebar(hb)

    def init_body(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        self.word = Gtk.Label()
        self.definition = Gtk.Label()
        vbox.pack_start(self.word, True, True, 0)
        vbox.pack_end(self.definition, True, True, 1)

        self.add(vbox)

    def on_click_popover(self, button):
        self.popover.set_relative_to(button)
        self.popover.show_all()
        self.popover.popup()

    def search_events(self):
        self.search_bar.connect('key_press_event', self.update_completion)
        self.search_bar.connect('activate', self.render)

    def update_completion(self, search_bar, x):
        self.store.clear()
        text = self.search_bar.get_text()
        if len(text) > 0:
            self.raw_result = self.dict.search(text)
            print(self.raw_result)
            for r in self.raw_result:
                self.store.append([r[0]])

    def append_history(self, entry):
        pass

    def render(self, word):
        if len(self.raw_result) == 1:
            entry = self.raw_result[0]
        definition = self.dict.read_meaning(entry[1])
        self.word.set_text(entry[0])
        self.definition.set_text(definition)

win = DictionaryUI()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()

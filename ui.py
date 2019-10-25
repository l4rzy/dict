import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio

class DictionaryUI(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Dictionary")
        self.set_border_width(4)
        self.set_default_size(800, 500)

        self.headerbar()
        self.body()

    def headerbar(self):
        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = "Dictionary"

        ## navigation buttons
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        Gtk.StyleContext.add_class(box.get_style_context(), "linked")
        button = Gtk.Button()
        arrow = Gtk.Arrow(arrow_type = Gtk.ArrowType.LEFT, shadow_type = Gtk.ShadowType.NONE)
        button.add(arrow)
        box.add(button)
        button = Gtk.Button()
        button.add(Gtk.Arrow(arrow_type = Gtk.ArrowType.RIGHT, shadow_type = Gtk.ShadowType.NONE))
        box.add(button)
        hb.pack_start(box)

        search_bar = Gtk.SearchEntry()
        hb.pack_start(search_bar)

        self.set_titlebar(hb)

    def body(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        search_bar = Gtk.SearchEntry()
        vbox.pack_end(Gtk.TextView(), True, True, 1)

        self.add(vbox)


win = DictionaryUI()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()

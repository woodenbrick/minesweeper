import sys
import gtk
import pygtk
pygtk.require("2.0")

from square import Grid

class MineSweeperGame(object):
    def __init__(self, *args):
        try:
            args = [int(a) for a in args[1:]]
        except ValueError:
            pass
        if len(args) != 3:
            args = [10, 10, 20]
        grid = Grid(*args)
        table = grid.create_minefield()
        self.window = gtk.Window()
        self.window.add(table)
        self.window.connect("destroy", self.main_quit)
        self.window.show()
        gtk.main()
    
    def main_quit(self, *args):
        gtk.main_quit()


if __name__ == "__main__":
    MineSweeperGame("./", *sys.argv)
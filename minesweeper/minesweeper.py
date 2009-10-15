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
        Grid(*args)
        gtk.main()


if __name__ == "__main__":
    MineSweeperGame("./", *sys.argv)
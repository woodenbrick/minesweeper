import sys
import os
import gtk
import pygtk
import time
import gobject
pygtk.require("2.0")

from grid import Grid

class MineSweeperGame(object):
    def __init__(self, *args):
        try:
            args = [int(a) for a in args[1:]]
        except ValueError:
            pass
        if len(args) != 3:
            args = [10, 10, 20]
        dir = os.path.split(os.path.dirname(os.path.realpath(__file__)))[0]
        if os.path.exists(os.path.join(dir, "images")):
            self.SHARE_DIR = os.path.join(dir, "images") + os.sep
        else:
            self.SHARE_DIR = "/usr/share/minesweeper/images/"
        self.pixbuf_neutral = gtk.gdk.pixbuf_new_from_file(self.SHARE_DIR + "neutral.png")
        self.pixbuf_shocked = gtk.gdk.pixbuf_new_from_file(self.SHARE_DIR + "shock.png")
        self.pixbuf_dead = gtk.gdk.pixbuf_new_from_file(self.SHARE_DIR + "lose.png")
        self.pixbuf_win = gtk.gdk.pixbuf_new_from_file(self.SHARE_DIR + "win.png")
        self.window = gtk.Window()
        self.vbox = gtk.VBox()
        self.window.add(self.vbox)
        #timer, smiley face (new game), mine counter
        self.timer_label = gtk.Label()
        self.smiley_button = gtk.Button()
        self.smiley_image = gtk.Image()
        self.smiley_image.set_from_pixbuf(self.pixbuf_neutral)
        self.smiley_button.set_image(self.smiley_image)
        self.mine_counter = gtk.Label()
        self.hbox = gtk.HBox()
        self.hbox.pack_start(self.timer_label)
        self.hbox.pack_start(self.smiley_button)
        self.hbox.pack_start(self.mine_counter)
        self.vbox.pack_start(self.hbox)
        self.pack_mines(*args)
        self.smiley_button.connect("clicked", self.pack_mines, self.grid.rows, self.grid.cols, self.grid.mines)
        self.window.connect("destroy", self.main_quit)
        self.window.show_all()
        self.set_labels()
        gtk.main()
        
    def pack_mines(self, *args):
        try:
            self.vbox.remove(self.table)
        except AttributeError:
            pass
        #args sometimes contains a button widget so we only pass the last 3 args
        self.grid = Grid(*args[-3:])
        self.grid.connect("start-game", self.start_game)
        self.grid.connect("add-flag", self.flagging)
        self.grid.connect("remove-flag", self.flagging)
        self.grid.connect("end-game", self.end_game)
        self.grid.connect("mouse-in", self.set_face, self.pixbuf_shocked)
        self.grid.connect("reset-face", self.set_face, self.pixbuf_neutral)
        self.table = self.grid.create_minefield()
        self.vbox.pack_start(self.table)
        self.mine_counter.set_text(str(self.grid.mines))
        self.timer_label.set_text("0")
        self.set_face(None, self.pixbuf_neutral)

    def start_game(self, *args):
        try:
            gobject.source_remove(self.timer)
        except:
            pass
        self.start_time = time.time()
        self.timer = gobject.timeout_add(1000, self.increment_time)
        

    def set_face(self, widget, pixbuf):
        self.smiley_image.set_from_pixbuf(pixbuf)

    def end_game(self, grid, win):
        #if this is called and and square that has a mine is not flagged, it is a loss
        self.grid.disconnect_by_func(self.end_game)
        self.grid.game_over = True
        try:
            gobject.source_remove(self.timer)
        except AttributeError:
            pass
        for row in self.grid.minelist:
            for square in row:
                if win and square.is_mine:
                    square.current_flag_state = 0
                    square.flag()
                else:
                    if square.is_covered and square.is_mine:
                        square.uncover()
                    elif square.current_flag_state == 1:
                        square.set_incorrect_flag()
        if win:
            print 'You win'
            self.set_face(None, self.pixbuf_win)
        else:
            print 'You lose'
            self.set_face(None, self.pixbuf_dead)
        #change to dead face
        #show incorrect mine guesses


        
    def flagging(self, grid, value):
        self.mine_counter.set_text(str(grid.mines_left))
        if grid.mines_left == 0:
            pass
        
    def increment_time(self, end=False):
        #XXX needs to end after game
        self.timer_label.set_text(str(int(time.time() - self.start_time)))
        return True
    
    def set_labels(self):
        """Sets the labels to the appropriate value"""
        self.timer_label.set_text("0")
        self.mine_counter.set_text(str(self.grid.mines))
    
    def main_quit(self, *args):
        gtk.main_quit()


if __name__ == "__main__":
    MineSweeperGame("./", *sys.argv)
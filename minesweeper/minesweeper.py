import sys
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

        self.window = gtk.Window()
        self.vbox = gtk.VBox()
        self.window.add(self.vbox)
        #timer, smiley face (new game), mine counter
        self.timer_label = gtk.Label()
        self.smiley_button = gtk.Button()
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_OPEN, gtk.ICON_SIZE_BUTTON)
        self.smiley_button.set_image(image)
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
        self.table = self.grid.create_minefield()
        self.vbox.pack_start(self.table)
        self.mine_counter.set_text(str(self.grid.mines))
        self.timer_label.set_text("0")
		
    def start_game(self, *args):
        try:
            gobject.source_remove(self.time)
        except:
            pass
        self.start_time = time.time()
        self.timer = gobject.timeout_add(1000, self.increment_time)
		
    
    def end_game(self, *args):
        #if this is called and and square that has a mine is not flagged, it is a loss
        self.grid.disconnect_by_func(self.end_game)
        self.grid.game_over = True
        gobject.source_remove(self.timer)
		
        victory = True if self.mine_counter.get_text() == "0" else False
        for row in self.grid.minelist:
            for square in row:
                if square.is_covered:
                    square.uncover()
                    if square.current_flag_state == 1 and not square.is_mine:
                        square.set_incorrect_flag()
                        victory = False
        if victory:
            print 'You win'
        else:
            print 'You lose'

                
        #show all squares
        #stop timer
        #change to dead face
        #show incorrect mine guesses
        print "game over"

        
    def flagging(self, grid, value):
        mines_flagged = int(self.mine_counter.get_text()) + value
        self.mine_counter.set_text(str(mines_flagged))
        
    def increment_time(self):
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
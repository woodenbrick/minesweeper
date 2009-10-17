import gtk
import random
import time
import gobject

class Square(gtk.EventBox):
    SHARE_DIR = ""
    button = gtk.gdk.pixbuf_new_from_file(SHARE_DIR + "images/button.png")
    mine_pixbuf = gtk.gdk.pixbuf_new_from_file(SHARE_DIR + "images/mine.png")
    numbers_pixbuf = []
    for i in range(0, 9):
        numbers_pixbuf.append(gtk.gdk.pixbuf_new_from_file(SHARE_DIR + "images/%d.png" % i))
    flag = gtk.gdk.pixbuf_new_from_file(SHARE_DIR + "images/flag.png")
    question = gtk.gdk.pixbuf_new_from_file(SHARE_DIR +"images/question.png")
    flag_states = [button, flag, question]
    LEFT_CLICK = 1
    BOTH_CLICK = 2
    RIGHT_CLICK = 3
    
    def __init__(self, grid, is_mine, row, col, surrounding_mines):
        gtk.EventBox.__init__(self)
        self.image = gtk.Image()
        self.image.set_from_pixbuf(Square.button)
        self.grid = grid
        self.row = row
        self.col = col
        self.surrounding_mines = surrounding_mines
        self.image.show()
        self.show()
        self.is_mine = is_mine
        self.connect("button-press-event", self.on_mouse_in)
        self.connect("leave-notify-event", self.on_mouse_out)
        self.connect("button-release-event", self.on_mouse_released)
        self.add(self.image)
        self.button_depressed = False
        self.is_covered = True
        self.current_flag_state = 0 # 1 for flag 2 for question mark
    
    def on_mouse_in(self, widget, event):
        if event.button == Square.LEFT_CLICK or event.button == Square.BOTH_CLICK:
            if self.current_flag_state != 1:
                self.button_depressed = True
                self.image.set_from_pixbuf(Square.numbers_pixbuf[0])
                #XXX if its BOTH_CLICK we should show the mines that will be uncovered
        else:
            self.flag()
    
    def on_mouse_out(self, *args):
        if self.button_depressed:
            self.image.set_from_pixbuf(Square.button)
            self.button_depressed = False
    
    def on_mouse_released(self, widget, event):
        """Count surrounding mines and uncover or end game if mine"""
        if self.button_depressed:
            self.uncover()
            if not self.grid.game_started:
                self.grid.emit("start-game")
                self.grid.game_started = True
            
    def uncover(self):
        self.is_covered = False
        self.disconnect_by_func(self.on_mouse_in)
        self.disconnect_by_func(self.on_mouse_out)
        self.disconnect_by_func(self.on_mouse_released)
        if self.is_mine:
            self.image.set_from_pixbuf(Square.mine_pixbuf)
            self.grid.emit("end-game")
        else:
            self.image.set_from_pixbuf(Square.numbers_pixbuf[self.surrounding_mines])
            self.grid.uncover_squares(self.row, self.col)
            self.grid.uncover_numbers()
            
            
    def flag(self):
        """Alternates between flagging, questionmark and a blank cover for square"""
        if self.current_flag_state == 0:
            self.current_flag_state = 1
            self.grid.emit("add-flag", -1)
        elif self.current_flag_state == 1:
            self.current_flag_state = 2
            self.grid.emit("remove-flag", 1)
        else:
            self.current_flag_state = 0
        self.image.set_from_pixbuf(Square.flag_states[self.current_flag_state])

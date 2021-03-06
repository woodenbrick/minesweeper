import gtk
import random
import time
import gobject
import os

class Square(gtk.EventBox):
    dir = os.path.split(os.path.dirname(os.path.realpath(__file__)))[0]
    if os.path.exists(os.path.join(dir, "images")):
        SHARE_DIR = os.path.join(dir, "images") + os.sep
    else:
        SHARE_DIR = "/usr/share/minesweeper/images/"
    button = gtk.gdk.pixbuf_new_from_file(SHARE_DIR + "button.png")
    mine_pixbuf = gtk.gdk.pixbuf_new_from_file(SHARE_DIR + "mine.png")
    numbers_pixbuf = []
    for i in range(0, 9):
        numbers_pixbuf.append(gtk.gdk.pixbuf_new_from_file(SHARE_DIR + "%d.png" % i))
    flag = gtk.gdk.pixbuf_new_from_file(SHARE_DIR + "flag.png")
    question = gtk.gdk.pixbuf_new_from_file(SHARE_DIR +"question.png")
    flag_states = [button, flag, question]
    incorrect_flag = gtk.gdk.pixbuf_new_from_file(SHARE_DIR + "wrongflag.png")
    clicked_mine = gtk.gdk.pixbuf_new_from_file(SHARE_DIR + "wrongmine.png")
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
        self.multipress = False #used to show more than 1 mine (middle click)
    
    def on_mouse_in(self, widget, event):
        if event.button == Square.LEFT_CLICK or event.button == Square.BOTH_CLICK:
            if self.current_flag_state != 1:
                self.grid.emit("mouse-in")
                self.button_depressed = True
                if self.is_covered:
                    self.image.set_from_pixbuf(Square.numbers_pixbuf[0])
                if event.button == Square.BOTH_CLICK or not self.is_covered:
                    #XXX if its BOTH_CLICK we should show the mines that will be uncovered
                    for square in self.grid.return_surrounding_squares(self.row, self.col):
                        if square.is_covered and square.current_flag_state == 0:
                            square.image.set_from_pixbuf(Square.numbers_pixbuf[0])
                            square.multipress = True
        elif self.is_covered:
            self.flag()
    
    def set_incorrect_flag(self):
        self.image.set_from_pixbuf(Square.incorrect_flag)
    
    def on_mouse_out(self, square, event):
        if self.button_depressed:
            self.button_depressed = False
            self.grid.emit("reset-face")
            if self.is_covered:
                self.image.set_from_pixbuf(Square.button)
            for square in self.grid.return_surrounding_squares(self.row, self.col):
                if square.multipress:
                    square.image.set_from_pixbuf(Square.button)
                    square.multipress = False

    
    def on_mouse_released(self, widget, event):
        """Count surrounding mines and uncover or end game if mine"""
        if self.button_depressed:
            self.uncover()
            for square in self.grid.return_surrounding_squares(self.row, self.col):
                if square.multipress:
                    square.uncover()
                    square.multipress = False            
            if not self.grid.game_started:
                self.grid.emit("start-game")
                self.grid.game_started = True
            self.grid.check_for_victory()
            
    def uncover(self):
        self.is_covered = False
        self.grid.uncovered_squares_counter -= 1
        if self.is_mine:
            if self.grid.game_over:
                self.image.set_from_pixbuf(Square.mine_pixbuf)    
            else:
                self.image.set_from_pixbuf(Square.clicked_mine)
                self.grid.emit("end-game", False)
        else:
            self.grid.emit("reset-face")
            self.image.set_from_pixbuf(Square.numbers_pixbuf[self.surrounding_mines])
            self.grid.uncover_squares(self.row, self.col)
            self.grid.uncover_numbers()
            
            
            
    def flag(self):
        """Alternates between flagging, questionmark and a blank cover for square"""
        if self.current_flag_state == 0:
            if self.is_mine:
                self.grid.mines_left -= 1
            self.current_flag_state = 1
            self.grid.emit("add-flag", -1)
            self.grid.check_for_victory()
        elif self.current_flag_state == 1:
            if self.is_mine:
                self.grid.mines_left += 1
            self.current_flag_state = 2
            self.grid.emit("remove-flag", 1)

        else:
            self.current_flag_state = 0
        self.image.set_from_pixbuf(Square.flag_states[self.current_flag_state])

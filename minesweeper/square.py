import gtk
import random
import time

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
            
    def uncover(self):
        self.is_covered = False
        self.disconnect_by_func(self.on_mouse_in)
        self.disconnect_by_func(self.on_mouse_out)
        self.disconnect_by_func(self.on_mouse_released)
        if self.is_mine:
            self.image.set_from_pixbuf(Square.mine_pixbuf)
            self.grid.end_game()
        else:
            self.image.set_from_pixbuf(Square.numbers_pixbuf[self.surrounding_mines])
            self.grid.uncover_squares(self.row, self.col)
            self.grid.uncover_numbers()
            
            
    def flag(self):
        """Alternates between flagging, questionmark and a blank cover for square"""
        if self.current_flag_state == 2:
            self.current_flag_state = 0
        else:
            self.current_flag_state += 1
        print self.current_flag_state
        self.image.set_from_pixbuf(Square.flag_states[self.current_flag_state])

class Grid(object):
    def __init__(self, rows=10, cols=10, mines=30):
        assert mines < rows*cols
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.game_started = False
        ##gtk. #XXXcreate signal emitter for game start
        
    
    def create_minefield(self):
        temp_mines = [True] * self.mines + [False] * (self.rows*self.cols-self.mines)
        random.shuffle(temp_mines)
        index = 0
        minelist = []
        while index < self.rows*self.cols:
            minelist.append(temp_mines[index:index+self.rows])
            index += self.rows
        
        table = gtk.Table(self.rows, self.cols, True)
        table.show()
        self.minelist = []
        start = time.time()
        for i, row in enumerate(minelist):
            minerow = []
            for j, mine in enumerate(row):
                square = Square(self, mine, i, j, self.count_surrounding_mines_old_version(minelist, i, j))
                table.attach(square, left_attach=j, right_attach=j+1,
                             top_attach=i, bottom_attach=i+1)
                minerow.append(square)
            self.minelist.append(minerow)
        end = time.time() - start
        print end
        return table
    
    def count_surrounding_mines_old_version(self, minelist, row, col):
        surrounding = self.return_surrounding_squares_old_version(row, col)
        total_mines = 0
        for row, col in surrounding:
            if row == -1 or col == -1:
                continue
            try:
                if minelist[row][col]:
                    total_mines += 1
            except IndexError:
                #we are on the edge or top
                pass
        return total_mines
    
    def return_surrounding_squares_old_version(self, row, col):
        return [[row-1, col-1], [row-1, col], [row-1, col+1], [row, col-1],
                [row, col+1], [row+1, col-1], [row+1, col], [row+1, col+1]]
    
    def count_surrounding_mines(self, minelist, row, col):
        surrounding = self.return_surrounding_squares(row, col)
        total_mines = 0
        for square in surrounding:
            if square.is_mine:
                total_mines += 1
        return total_mines
    
    def return_surrounding_squares(self, row, col, diagonals=True):
        """Set diagonals to False if uncovering mines"""
        #XXX should be refactored to accept square objects
        squares = [[row-1, col], [row, col-1], [row, col+1], [row+1, col]]
        if diagonals:
            squares.extend([[row-1, col-1], [row-1, col+1], [row+1, col-1], [row+1, col+1]])
        surrounding_squares = []
        for row, col in squares:
            if row == -1 or col == -1:
                continue
            try:
                surrounding_squares.append(self.minelist[row][col])
            except IndexError:
                pass
        return surrounding_squares
    
    def uncover_squares(self, row, col):
        """row and col are the start square and we work our way outwards"""
        surrounding = self.return_surrounding_squares(row, col, diagonals=False)
        next_batch = []
        for square in surrounding:
            if square.is_covered and square.surrounding_mines == 0 and not square.is_mine and square.current_flag_state !=1:
                    square.uncover()
                    next_batch.append([square.row, square.col])
        for i, j in next_batch:
            self.uncover_squares(i, j)
            
    def uncover_numbers(self):
        """This makes sure that there is an uncovered number next to each blank
        square that is shown"""
        for row in self.minelist:
            for square in row:
                if not square.is_covered and square.surrounding_mines == 0:
                    surrounding = self.return_surrounding_squares(square.row, square.col)
                    for item in surrounding:
                        if item.is_covered and not item.is_mine:
                            item.uncover()

    
    def end_game(self):
        #show all squares
        #stop timer
        #change to dead face
        #show incorrect mine guesses
        print "game over"


        

    

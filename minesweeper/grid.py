#!/usr/bin/env python

class Grid(gobject.GObject):
    __gsignals__ = {
        "start-game": (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ()),
        "remove-flag" : (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (int,)),
        "add-flag" : (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (int,)),
        "end-game" : (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ()),    
    }

    def __init__(self, rows=10, cols=10, mines=30):
        gobject.GObject.__init__(self)
        assert mines < rows*cols
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.game_started = False
        
    
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
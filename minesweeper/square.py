import gtk
import random
import time

class Square(gtk.EventBox):
    button = gtk.gdk.pixbuf_new_from_file("../images/1.png")
    
    def __init__(self, grid, is_mine, row, col):
        gtk.EventBox.__init__(self)
        #self.set_size_request(40, 40)
        self.image = gtk.Image()
        #self.image.set_size_request(70, 55)
        self.image.set_from_pixbuf(Square.button)
        self.grid = grid
        self.image.show()
        self.show()
        self.is_mine = is_mine
        #self.connect("button-press-event", self.on_square_pressed, row, col)
        self.add(self.image)
        
    def on_square_pressed(self, widget, event, row, col):
        """Count surrounding mines and uncover or end game if mine"""
        if self.is_mine:
            print 'Game over'
        else:
            print 'not mine'

class Grid(object):
    def __init__(self, rows=10, cols=10, mines=30):
        assert mines < rows*cols
        self.rows = rows
        self.cols = cols
        self.table = self.create_minefield(mines)
        self.window = gtk.Window()
        self.window.add(self.table)
        self.window.connect("destroy", self.main_quit)
        self.window.show()
        
    
    def create_minefield(self, mines):
        temp_mines = [True] * mines + [False] * (self.rows*self.cols-mines)
        random.shuffle(temp_mines)
        index = 0
        minelist = []
        while index < self.rows*self.cols:
            minelist.append(temp_mines[index:index+self.rows])
            index += self.rows
        
        table = gtk.Table(self.rows+1, self.cols+1, True)
        table.show()
        start = time.time()
        for i, row in enumerate(minelist):
            for j, mine in enumerate(row):
                square = Square(self, mine, j, i)
                #print i-1, i+1, j-1, j+1
                table.attach(square, left_attach=j, right_attach=j+1,
                             top_attach=i, bottom_attach=i+1)
                             #xoptions=gtk.EXPAND|gtk.FILL)
                
        end = time.time() - start
        print end
        return table
    
    def on_square_pressed(self, *args):
        print args

    def main_quit(self, *args):
        gtk.main_quit()
        
Grid(4, 4, 2)
gtk.main()
    
#    
#class Square
#event_box
#is_mine
#surrounding_mine_count
#covered
#
#change_image()
#mouse_down()
#mouse_up()
#mouse_off() //break mouse down

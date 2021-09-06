import pygame
from solver import solve, valid
import time
from random import sample
pygame.font.init()


class Grid:
    def generate_random_grid(self,board):
        """

        :param board: board itself
        here we would generate a complete sudoku grid
        and after that we will delete all the elements but 17 numbers
        """
        base = 3
        side = base * base

        # pattern for a baseline valid solution
        def pattern(r, c):#here is the math solution for sudoku gameplay
            return (base * (r % base) + r // base + c) % side

        # randomize rows, columns and numbers (of valid base pattern)

        def shuffle(s):
            return sample(s, len(s))

        rBase = range(base)
        rows = [g * base + r for g in shuffle(rBase) for r in shuffle(rBase)]
        cols = [g * base + c for g in shuffle(rBase) for c in shuffle(rBase)]
        nums = shuffle(range(1, base * base + 1))

        # produce board using randomized baseline pattern
        self.board = [[nums[pattern(r, c)] for c in cols] for r in rows]

        squares = side * side
        empties = squares * 3 // 4
        for p in sample(range(squares), side * side - 17):
            board[p // side][p % side] = 0

        squares = side * side
        empties = squares * 3 // 4
        for p in sample(range(squares), side * side - 17):
            print(p)
            self.board[p // side][p % side] = 0



    def __init__(self, rows, cols, width, height):
        """
        init the grid
        :param rows: number of rows
        :param cols: number of columns
        :param width: the width of the grid
        :param height: the height of the grid
        """
        self.rows = rows
        self.cols = cols
        self.board = [[0 for c in range(10)] for r in range(10)]
        self.generate_random_grid(self.board)

        self.cubes = [[Cube(self.board[i][j], i, j, width, height) for j in range(cols)] for i in range(rows)]
        self.width = width
        self.height = height
        self.model = None
        self.selected = None




    def update_model(self):
        """
        update the model of the grid
        :return:
        """
        self.model = [[self.cubes[i][j].value for j in range(self.cols)] for i in range(self.rows)]

    def place(self, val):
        """
        verify if the place is good for the value considering sudoku's gameplay
        :param val:
        :return:true, if it ok
                otherwise false
        """
        row, col = self.selected
        if self.cubes[row][col].value == 0:
            self.cubes[row][col].set(val)
            self.update_model()

            if valid(self.model, val, (row,col)) and solve(self.model):
                return True
            else:
                self.cubes[row][col].set(0)
                self.cubes[row][col].set_temp(0)
                self.update_model()
                return False

    def sketch(self, val):
        """

        :param val: value
        set the cube's temporary value
        """
        row, col = self.selected
        self.cubes[row][col].set_temp(val)

    def draw(self, win):
        """

        :param win: display
        draw the grid lines and spaces
        """
        # Draw Grid Lines
        gap = self.width / 9
        for i in range(self.rows+1):
            if i % 3 == 0 and i != 0:
                thick = 4
            else:
                thick = 1
            pygame.draw.line(win, (0,0,0), (0, i*gap), (self.width, i*gap), thick)
            pygame.draw.line(win, (0, 0, 0), (i * gap, 0), (i * gap, self.height), thick)

        # Draw Cubes-values
        for i in range(self.rows):
            for j in range(self.cols):
                self.cubes[i][j].draw(win)

    def select(self, row, col):
        """

        :param row: the selected row
        :param col: the selected column
        we will mark the "selected" with the row and column given
        """
        # Reset all other
        for i in range(self.rows):
            for j in range(self.cols):
                self.cubes[i][j].selected = False

        self.cubes[row][col].selected = True
        self.selected = (row, col)

    def clear(self):
        """
        we will clear the selected cube if u press DEL
        """
        row, col = self.selected
        if self.cubes[row][col].value == 0:
            self.cubes[row][col].set_temp(0)

    def click(self, pos):
        """
        :param: pos: position of the mouse
        :return: (row, col) or nothing
        """
        if pos[0] < self.width and pos[1] < self.height:
            gap = self.width / 9
            x = pos[0] // gap
            y = pos[1] // gap
            return (int(y),int(x))
        else:
            return None

    def is_finished(self):
        """
        verify if the sudoku game is finished
        :return:true if it is
                otherwise false
        """
        for i in range(self.rows):
            for j in range(self.cols):
                if self.cubes[i][j].value == 0:
                    return False
        return True


class Cube:
    rows = 9
    cols = 9

    def __init__(self, value, row, col, width ,height):
        """

        :param value:the value of the cube
        :param row: the row
        :param col: the column
        :param width: the width of the cube
        :param height: the height of the cube
        """
        self.value = value
        self.temp = 0
        self.row = row
        self.col = col
        self.width = width
        self.height = height
        self.selected =  False

    def draw(self, win):
        """

        :param win: display
        draw the cubes and the spaces and the text style
        """
        fnt = pygame.font.SysFont("comicsans", 40)

        gap = self.width / 9
        x = self.col * gap
        y = self.row * gap

        if self.temp != 0 and self.value == 0:#just a number without an enter
            text = fnt.render(str(self.temp), 1, (0,0,255))
            win.blit(text, (x + (gap/2 - text.get_width()/2), y + (gap/2 - text.get_height()/2)))
        elif not(self.value == 0):#the value it was stabilized before
            text = fnt.render(str(self.value), 1, (0, 0, 0))
            win.blit(text, (x + (gap/2 - text.get_width()/2), y + (gap/2 - text.get_height()/2)))

        if self.selected:
            pygame.draw.rect(win, (255,0,0), (x,y, gap ,gap), 3)

    def set(self, val):
        """

        :param val: value
        set the value of a cube
        """
        self.value = val

    def set_temp(self, val):
        """

        :param val: the temporary value in the cube

        """
        self.temp = val


def redraw_window(win, board, time, strikes):
    """

    :param win: display
    :param board: the board itself
    :param time: the play time
    :param strikes: how many strikes do you have
    redraw the display every instance
    """
    win.fill((255,255,255))
    # Draw time
    fnt = pygame.font.SysFont("comicsans", 40)
    text = fnt.render("Time: " + format_time(time), 1, (0,0,0))
    win.blit(text, (540 - 200, 560))
    # Draw Strikes
    text = fnt.render("X " * strikes, 1, (255, 0, 0))
    win.blit(text, (20, 560))
    # Draw grid and board
    board.draw(win)


def format_time(secs):
    """

    :param secs: number of seconds
    :return: the time as a string(h,m,s)
    """
    sec = secs%60
    minute = secs//60
    hour = minute//60

    mat =  " " + str(hour) + ":" + str(minute) + ":" + str(sec)
    return mat


def main():

    """
    the main of the game-sudoku
    the game is running until you got 3 strikes or you finish it
    """


    win = pygame.display.set_mode((540,600))
    pygame.display.set_caption("Sudoku")
    board = Grid(9, 9, 540, 540)
    key = None
    run = True
    start = time.time()
    strikes = 0
    while run:

        play_time = round(time.time() - start)

        for event in pygame.event.get():



            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:#choose the number
                if event.key == pygame.K_1:
                    key = 1
                if event.key == pygame.K_2:
                    key = 2
                if event.key == pygame.K_3:
                    key = 3
                if event.key == pygame.K_4:
                    key = 4
                if event.key == pygame.K_5:
                    key = 5
                if event.key == pygame.K_6:
                    key = 6
                if event.key == pygame.K_7:
                    key = 7
                if event.key == pygame.K_8:
                    key = 8
                if event.key == pygame.K_9:
                    key = 9
                if event.key == pygame.K_DELETE:
                    board.clear()
                    key = None
                if event.key == pygame.K_RETURN:#enter a number
                    i, j = board.selected
                    if board.cubes[i][j].temp != 0:
                        if board.place(board.cubes[i][j].temp):
                            print("Success")
                        else:
                            print("Wrong")
                            strikes += 1
                        key = None

                        if board.is_finished():
                            print("Game over")
                            run = False
                        if strikes == 3:
                            print("Game over")
                            run = False

            if event.type == pygame.MOUSEBUTTONDOWN:#mouse in a box + click
                pos = pygame.mouse.get_pos()
                clicked = board.click(pos)
                if clicked:
                    board.select(clicked[0], clicked[1])
                    key = None

        if board.selected and key != None:
            board.sketch(key)

        redraw_window(win, board, play_time, strikes)
        pygame.display.update()


main()
pygame.quit()
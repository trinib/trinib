import os
import pickle
from datetime import datetime

EAST = 1
SOUTH = 2
SOUTHEAST = 3
SOUTHWEST = 4


class connect4:
    def __init__(self):
        if os.path.exists("games/current.p"):
            game = pickle.load(open("games/current.p", "rb"))
            self.grid = game['grid']
            self.whosTurn = game['plays']
            self.player = game['player']
            self.rounds = game['rounds']
            self.valid_moves()

        else:
            self.create_newgame()
            self.valid = range(len(self.grid))

    def is_game_over(self):
        if os.path.exists("games/current.p"):
            return False
        return True
    def save_currentgame(self):
        pickle.dump({'grid': self.grid, 'plays': self.whosTurn, 'player': self.player,
                     'rounds': self.rounds}, open("games/current.p", "wb"))

    def wongame(self):
        pickle.dump({'grid': self.grid, 'plays': self.whosTurn, 'player': self.player,
                     'rounds': self.rounds},
                    open("games/" + datetime.now().strftime("%m_%d_%Y-%H_%M_%S") + ".p",
                         "wb"))

        os.remove("games/current.p")

    def create_newgame(self):
        self.grid = [[0 for col in range(7)] for row in range(6)]
        self.whosTurn = 2
        self.player = []
        self.rounds = 0
        self.save_currentgame()

    def iswonornot(self):
        for row in range(len(self.grid)):
            for col in range(len(self.grid[0])):
                if self.grid[row][col] != 0:
                    color = self.grid[row][col]
                    if self.recur_checker(self.grid, SOUTH, row + 1, col, color, 3) or \
                            self.recur_checker(self.grid, EAST, row, col + 1, color, 3) or \
                            self.recur_checker(self.grid, SOUTHEAST, row + 1, col + 1, color, 3) or \
                            self.recur_checker(self.grid, SOUTHWEST, row + 1, col - 1, color, 3):
                        return True

        return False

    def recur_checker(self, grid, direction, row, col, color, howmanyleft):
        if howmanyleft == 0:
            return True
        if (row >= len(grid)) or (col >= len(grid[0])) or (row < 0) or (col < 0):
            return False

        if grid[row][col] != color:
            return False
        if grid[row][col] == color:

            if direction == SOUTH:
                return self.recur_checker(grid, direction, row + 1, col, color, howmanyleft - 1)
            elif direction == EAST:
                return self.recur_checker(grid, direction, row, col + 1, color, howmanyleft - 1)
            elif direction == SOUTHEAST:
                return self.recur_checker(grid, direction, row + 1, col + 1, color, howmanyleft - 1)
            elif direction == SOUTHWEST:
                return self.recur_checker(grid, direction, row + 1, col - 1, color, howmanyleft - 1)
        return False

    def has_space_left(self):
        for row in self.grid:
            for col in row:
                if col == 0:
                    return True
        return False

    def whosturn(self):
        return self.whosTurn, self.valid_moves()

    def move(self, x, curr_player):
        x -= 1
        if (x >= len(self.grid[0])) | (x < 0):
            return self.whosTurn, self.valid_moves(), 4

        for row in self.grid:
            if row[x] == 0:
                self.grid[self.grid.index(row)][x] = self.whosTurn
                break

        self.whosTurn = (self.whosTurn % 2) + 1
        if curr_player not in self.player:
            self.player.append(curr_player)

        self.rounds += 1
        if self.iswonornot():
            self.wongame()
            return self.whosTurn, self.valid_moves(), 1
        elif not self.has_space_left():
            self.wongame()
            return self.whosTurn, self.valid_moves(), 2
        else:
            self.save_currentgame()
        return self.whosTurn, self.valid_moves(), 0

    def valid_moves(self):
        valid = []
        for i in range(len(self.grid[0])):
            if self.grid[-1][i] == 0:
                valid.append(i + 1)
        self.valid = valid
        return valid


if __name__ == '__main__':
    Conn = connect4()
    Conn.grid[2][0] = 1
    Conn.grid[3][1] = 1
    Conn.grid[4][2] = 1
    Conn.grid[5][3] = 1
    Conn.move(2, "@boerni")
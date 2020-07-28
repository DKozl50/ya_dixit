from uuid import uuid1
from random import randint


class TicTacToe:
    """id: game.id
    player_x: player.id
    player_y: player.id
    move_order: string {'X', 'O'}
    table: matrix 3x3
    """
    __game_ids = {}

    def __init__(self):
        self.__get_new_id()
        self.player_x = None
        self.player_o = None
        self.move_order = 'X'
        self.table = [['', '', ''],
                      ['', '', ''],
                      ['', '', '']]

    def __get_new_id(self):
        self.id = uuid1().time_low
        TicTacToe.__game_ids[self.id] = self

    def add_player(self, player_id):
        if self.player_x == self.player_o is None:
            if randint(0, 1):
                self.player_x = player_id
            else:
                self.player_o = player_id
        else:
            if self.player_x is None:
                self.player_x = player_id
            else:
                self.player_o = player_id

    def try_leave_player(self, player_id):
        if self.player_x == player_id:
            self.player_x = None
        elif self.player_o == player_id:
            self.player_o = None
        else:
            raise Exception('Invalid player_id')

    def move(self, num_button, player_id):
        if not 0 <= num_button <= 8:
            raise Exception('Invalid button')
        elem = 'X' if player_id == self.player_x else 'O'
        if elem != self.move_order:
            raise Exception('Move another player')
        row = num_button // 3
        col = num_button % 3
        if self.table[row][col] != '':
            raise Exception('Cell is not empty')
        self.table[row][col] = elem
        self.move_order = 'O' if self.move_order == 'X' else 'X'

    def check_win(self):
        for row in range(3):
            if self.table[row][0] == self.table[row][1] == self.table[row][2] != '':
                return f'win'
        for col in range(3):
            if self.table[0][col] == self.table[1][col] == self.table[2][col] != '':
                return f'win'
        for col in [[0, 1, 2], [2, 1, 0]]:
            if self.table[0][col[0]] == self.table[1][col[1]] == self.table[2][col[2]] != '':
                return f'win'
        for row in self.table:
            for value in row:
                if value == '':
                    return ''
        return 'draw'

    def swap_player(self):
        self.player_x, self.player_o = self.player_o, self.player_x

    def is_ready(self):
        return self.player_x is not None and self.player_o is not None

    def is_empty(self):
        return self.player_x is None and self.player_o is None

    def player_side(self, id):
        return 'X' if self.player_x == id else 'O'

    def new_game(self):
        if randint(0, 1):
            self.swap_player()
        self.move_order = 'X'
        self.table = [['', '', ''],
                      ['', '', ''],
                      ['', '', '']]

    @staticmethod
    def get_game(id):
        return TicTacToe.__game_ids.get(id, None)

    @staticmethod
    def delete_game(id):
        TicTacToe.__game_ids.pop(id)

    @staticmethod
    def get_all_game():
        return TicTacToe.__game_ids.values()


def print_table(table):
    print('---')
    for row in table:
        for elem in row:
            if elem == '':
                print(' ', end='')
            else:
                print(elem, end='')
        print()
    print('---')

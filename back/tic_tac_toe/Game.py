from random import randint

class TicTacToe:
    """id: Game.id
    PlayerX: Player.id
    PlayerO: Player.id
    winner: Player.id
    move_order: string {'X', 'O'}
    table: matrix 3x3
    """
    __game_ids = []

    def __init__(self):
        self.id = self.__get_new_id()
        self.PlayerX = None
        self.PlayerO = None
        self.winner = None
        self.move_order = 'X'
        self.table = [['', '', ''],
                      ['', '', ''],
                      ['', '', '']]

    @staticmethod
    def __get_new_id():
        potential = randint(100000, 999999)
        while potential in TicTacToe.__game_ids:
            potential = randint(100000, 999999)
        TicTacToe.__game_ids.append(potential)
        return potential

    def add_player(self, player_id):
        if self.PlayerX == self.PlayerO is None:
            if randint(0, 1):
                self.PlayerX = player_id
            else:
                self.PlayerO = player_id
        else:
            if self.PlayerX is None:
                self.PlayerX = player_id
            else:
                self.PlayerO = player_id

    def move(self, num_button, player_id):
        if not 0 <= num_button <= 8:
            raise Exception('(ಥ﹏ಥ)')
        elem = 'X' if player_id == self.PlayerX else 'O'
        if elem != self.move_order:
            raise Exception('(ง •̀_•́)ง')
        row = num_button // 3
        col = num_button % 3
        if self.table[row][col] != '':
            raise Exception('(-_-)')
        self.table[row][col] = elem
        return self.__check_win(player_id)

    def __check_win(self, player_id):
        for row in range(3):
            if self.table[row][0] == self.table[row][1] == self.table[row][2] != '':
                self.winner = player_id
                return True
        for col in range(3):
            if self.table[0][col] == self.table[1][col] == self.table[2][col] != '':
                self.winner = player_id
                return True
        for col in [[0, 1, 2], [2, 1, 0]]:
            if self.table[0][col[0]] == self.table[1][col[1]] == self.table[2][col[2]] != '':
                self.winner = player_id
                return True
        return False

    @staticmethod
    def get_all_ids():
        return TicTacToe.__game_ids


def main():
    while True:
        request = input()

    pass


if __name__ == "__main__":
    main()

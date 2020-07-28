from tic_tac_toe.Player import *
from tic_tac_toe.Game import *


def create_game(player_id):
    game = TicTacToe()
    print(f'Создали игру {game.id}')
    player = Player.get_player(player_id)
    player.join_game(game)
    print(f'Игрок {player_id} играет за {game.player_side(player_id)}')


def join_game(player_id, game_id):
    player = Player.get_player(player_id)
    game = TicTacToe.get_game(game_id)
    if player.join_game(game):
        print(f'{player_id} присоединился к {game_id}')
    else:
        print(f'{player_id} не смог подключиться к {game_id}')


def leave_game(player_id):
    player = Player.get_player(player_id)
    if player.state is None:
        raise Exception('Player not in game')
    game = TicTacToe.get_game(player.state)
    player.leave_game(game)
    print(f'Игрок {player_id} покинул игру {game.id}')
    if game.is_empty():
        TicTacToe.delete_game(game.id)
        print(f'Удалили игру {game.id}')
    else:
        game.new_game()
        print(f'Начали новую игру в {game.id}')


def move(player_id, button):
    player = Player.get_player(player_id)
    game = TicTacToe.get_game(player.state)
    if not game.is_ready():
        raise Exception('Game is not started')
    game.move(button, player.id)
    status = game.check_win()
    print_table(game.table)
    if status:
        if status == 'win':
            print(f'{player_id} выиграл')
        elif status == 'draw':
            print(f'{player_id} сделал последний ход')
        game.new_game()
    else:
        print(f'{player_id} сделал ход')


def main():
    while True:
        try:
            request, *args = input().split()
            args = list(map(int, args))
            if request == 'create_game':
                create_game(*args)
            elif request == 'join_game':
                join_game(*args)
            elif request == 'leave_game':
                leave_game(*args)
            elif request == 'move':
                move(*args)
            elif request == 'new_player':
                player = Player()
                print(f'Создали нового игрока {player.id}')
        except Exception as error:
            print(error)


if __name__ == '__main__':
    main()

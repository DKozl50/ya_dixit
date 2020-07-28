from tic_tac_toe.Player import *
from tic_tac_toe.Game import *

gameid_to_game = {}
playerid_to_player = {}

def main():
    while True:
        request, *args = input().split()
        args = list(map(int, args))
        if request == 'create_game':
            #  args = {player.id}
            game = TicTacToe()
            gameid_to_game[game.id] = game
            player = playerid_to_player[args[0]]
            player.join_game(game)
            print(game.id)
            print(game.PlayerX)
        elif request == 'join_game':
            #  args = {player.id, game.id}
            player = playerid_to_player[args[0]]
            game = gameid_to_game[args[1]]
            player.join_game(game)
            print('opa123')
        elif request == 'leave_game':
            #  args = {player.id}
            player = playerid_to_player[args[0]]
            if player.state is None:
                print('ε=ε=ε=(~￣▽￣)~')
            else:
                game = gameid_to_game[player.state]
                player.leave_game(game)
                if game.PlayerX is None and game.PlayerO is None:
                    gameid_to_game.pop(game.id)
                else:
                    game.new_game()
            print('opa')
        elif request == 'move':
            #  args = {player.id, button}
            player = playerid_to_player[args[0]]
            game = gameid_to_game[player.state]
            if game.PlayerX is not None and game.PlayerO is not None:
                print(game.move(args[1], player.id))
                print('opaxxxx')
            else:
                print('(((')
        elif request == 'new_player':
            player = Player()
            playerid_to_player[player.id] = player
            print(player.id)
        else:
            print('⊙_ರೃ')


if __name__ == '__main__':
    main()
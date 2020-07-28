import tic_tac_toe.Player as Player
import tic_tac_toe.Game as Game

gameid_to_game = {}
playerid_to_player = {}

def main():
    player = Player()
    playerid_to_player[player.id] = player
    while True:
        request, *args = input().split()
        if request == 'create_game':
            #  args = {player.id}
            game = Game.TicTacToe()
            gameid_to_game[game.id] = game
            player = playerid_to_player[args[0]]
            player.join_game(game)
        if request == 'join_game':
            #  args = {player.id, game.id}
            player = playerid_to_player[args[0]]
            game = gameid_to_game[args[1]]
            player.join_game(game)
        if request == 'leave_game':
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
        if request == 'move':
            #  args = {player.id, button}
            player = playerid_to_player[args[0]]
            game = gameid_to_game[player.state]
            if game.PlayerX is not None and game.PlayerO is not None:
                game.move(int(args[1]), player.id)
        else:
            print('⊙_ರೃ')


if __name__ == '__main__':
    main()
import mechanics
from random import shuffle

game = mechanics.Game()  # game object


# for visualization
def one_hand(player):
    c = game.get_hand(player)
    print(f'|-player {player} cards:-|' + ('<-leader' if player == game._current_player else ''))
    print('|' + '|'.join(map(str, c)) + '|')


def demonstrate_hands():
    for p in game.players:
        one_hand(p)


def card_from(target):
    return game.get_hand(target)[0]


# let player ids be 1..4
print('Add players 1, 2, 3, 4')
game.add_player(1)
game.add_player(2)
game.add_player(3)
game.add_player(4)
print('res:', game.result)
print()

print('Remove player 4 before game has started:')
game.remove_player(4)
# player is deleted from result completely as they have never entered
print('res:', game.result)
print()

print('Start game: sorts players and deals cards')
print('game.get_state() before start:', game.get_state(), bool(game.get_state()))
# can be used not to let player participate in multiple games
game.start_game()  # start_game requires database, so some cheating here
#
# MAGIC STARTS HERE (copy of start_game)
game._cards = list(range(10, 99))
shuffle(game._cards)
game._shuffle_players()
for p in game.players:
    game._deal6(p)
game._current_player = game.players[game._state]
# MAGIC ENDS HERE 
#
demonstrate_hands()
print('res:', game.result)
print()

print('Start turn giving association and choosing card', card_from(game._current_player))
guessed_card = card_from(game._current_player)  # stored for demonstration purposes
game.start_turn('association 1', card_from(game._current_player))
demonstrate_hands()
print()

print('Other players give cards:')
# I assume cards are given simultaneously
cards_on_table = {p: card_from(p) for p in [1, 2, 3] if p != game._current_player}  # stored for demonstration purposes
game.place_cards(cards_on_table)
cards_on_table[game._current_player] = guessed_card  # stored for demonstration purposes
demonstrate_hands()
print('res:', game.result)
print()

print('Players (not leader) make guesses and get scores:')
# I assume guesses are given simultaneously
game.valuate_guesses({p: cards_on_table[p % 3 + 1] for p in [1, 2, 3] if p != game._current_player})  # everyone voted for the next player
print('res:', game.result)
print()

print('End turn: change active player, deal cards')
game.end_turn()
demonstrate_hands()
print('res:', game.result)
print()

print('Remove player 2:')
game.remove_player(2)  # score gets set to 'DNF *score*'. It can be restored if player returns
demonstrate_hands()
print('res:', game.result)
print()

print('Return player 2:')
game.add_player(2)  # score indeed gets restored
demonstrate_hands()
print('res:', game.result)
print()

print('Add player 4:')
game.add_player(4)
demonstrate_hands()
print('res:', game.result)
print()

print('Now everyone votes for leader:')
guessed_card = card_from(game._current_player)
game.start_turn('association 2', card_from(game._current_player))
# stuff is stored again for demonstration purposes
cards_on_table = {p: card_from(p) for p in [1, 2, 3, 4] if p != game._current_player}
game.place_cards(cards_on_table)
cards_on_table[game._current_player] = guessed_card
# score can never get <0
game.valuate_guesses({p: guessed_card for p in [1, 2, 3, 4] if p != game._current_player})
game.end_turn()
demonstrate_hands()
print('res:', game.result)
print()

print('Someone didn\'t place card:')
guessed_card = card_from(game._current_player)
game.start_turn('association 3', card_from(game._current_player))
# someone may pass their move
cards_on_table = {p: card_from(p) for p in [1, 2, 3, 4] if p != game._current_player}
cards_on_table.pop(game._current_player % 4 + 1)
game.place_cards(cards_on_table)
demonstrate_hands()
print()

cards_on_table[game._current_player] = guessed_card
# there are no checks if you vote for yourself, or if passer makes a vote
# probably I should add checks, but now I assume it's not my prolem
game.valuate_guesses({p: guessed_card for p in [1, 2, 3, 4] if p != game._current_player})
game.end_turn()
demonstrate_hands()
print('res:', game.result)
print()

print('End game:')
# it is easy to check if game is active
print('game.get_state() before end:', game.get_state(), bool(game.get_state()))
game.end_game()
print('game.get_state() after end:', game.get_state(), bool(game.get_state()))

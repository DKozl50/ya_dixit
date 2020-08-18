import unittest
import logging
from mechanics import Game, Player

logging.basicConfig(level=logging.INFO)


class TestGame(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def test_add(self):
        for i in range(1, 5):
            self.game.add_player(i)
        self.assertEqual(self.game.players, [1, 2, 3, 4])

    def test_remove_before_start(self):
        for i in range(1, 5):
            self.game.add_player(i)
        self.game.remove_player(4)
        self.assertEqual(self.game.result, {1: 0, 2: 0, 3: 0})

    def log_hands(self):
        for player in self.game.players:
            c = self.game.get_hand(player)
            print(f'|-player {player} cards:-|' +
                  ('<-leader' if player == self.game._current_player else ''))
            print('|' + '|'.join(map(str, c)) + '|')

    def test_game_states(self):
        for i in range(1, 5):
            self.game.add_player(i)
        self.assertEqual(self.game.get_state(), self.game.States.WAITING)
        self.game.start_game()
        self.assertEqual(self.game.get_state(), self.game.States.STORYTELLING)


if __name__ == '__main__':
    unittest.main()

import unittest
import logging
from mechanics import Game, Player


class TestPlayer(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def test_constructor(self) -> None:
        player: Player = Player("noname")
        self.assertEqual(player.name, "noname")
        player = Player("noname", password_hash="password_hash")
        self.assertEqual(player.password_hash, "password_hash")


class TestGame(unittest.TestCase):
    def setUp(self):
        self.game: Game = Game()

    def _init_game(self):
        for i in range(1, 5):
            self.game.add_player(Player(str(i)))

    def test_add(self):
        self._init_game()
        self.assertEqual(len(self.game.players), 4)

    def test_remove_before_start(self):
        self._init_game()
        player = [
            player for player in self.game.players if player.name == "4"
        ][0]
        self.game.remove_player(player)
        self.assertEqual(len(self.game.result), 3)

    def test_add_after_removal(self):
        self._init_game()
        self.game.start_game()
        player = self.game.players[0]
        self.game.remove_player(player)
        self.game.add_player(player)

    def test_remove_listener_during_storytelling(self):
        self._init_game()
        self.game.start_game()
        self.game.add_lead_card(self.game.hands[self.game.players[0]][0].id)
        self.game.start_turn("association")

    def test_game_states(self):
        self._init_game()
        self.assertEqual(
            self.game.get_state(),
            self.game.GamePhase.WAITING
        )
        self.game.start_game()
        self.assertEqual(
            self.game.get_state(),
            self.game.GamePhase.STORYTELLING
        )


if __name__ == '__main__':
    unittest.main()

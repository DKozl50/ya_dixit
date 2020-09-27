import unittest
from mechanics import Game, Player
from typing import Optional, List


def play_until_phase(game: Game, phase: Game.GamePhase,
                     bets: Optional[List[int]] = None,
                     guesses: Optional[List[int]] = None) -> None:
    if phase == game.state:
        return
    if game.state == Game.GamePhase.WAITING:
        game.start_game()
    elif game.state == Game.GamePhase.STORYTELLING:
        winner = game.finished()
        if winner is not None:
            game.end_game(winner)
            return
        cur_player = game.get_cur_player()
        game.add_lead_card(game.hands[cur_player][0].id)
        game.start_turn("association")
    elif game.state == Game.GamePhase.MATCHING:
        if bets is None:
            bets = [0] * len(game.players)
        for player, bet in zip(game.players, bets):
            game.make_bet(player, game.hands[player][bet].id)
            game.finish_turn(player)
        game.place_cards()
    elif game.state == Game.GamePhase.GUESSING:
        if guesses is None:
            guesses = [0] * len(game.players)
        for player, guess in zip(game.players, guesses):
            game.make_guess(player, list(game.current_table.keys())[guess].id)
            game.finish_turn(player)
        game.valuate_guesses()
    elif game.state == Game.GamePhase.INTERLUDE:
        game.end_turn()
    play_until_phase(game, phase)


def make_game() -> Game:
    game = Game()
    for i in range(1, 5):
        game.add_player(Player(str(i)))
    return game


class TestPlayer(unittest.TestCase):
    def setUp(self) -> None:
        self.game = Game()

    def test_constructor(self) -> None:
        player: Player = Player("noname")
        self.assertEqual(player.name, "noname")
        player = Player("noname", password_hash="password_hash")
        self.assertEqual(player.password_hash, "password_hash")


class TestRemoval(unittest.TestCase):
    def setUp(self):
        self.game: Game = make_game()

    def test_remove_before_start(self):
        player = [
            player for player in self.game.players if player.name == "4"
        ][0]
        self.game.remove_player(player)
        self.assertEqual(len(self.game.result), 3)

    def test_remove_listener_after_game_start(self):
        self.game.start_game()
        self.game.remove_player(self.game.players[-1])

    def test_remove_listener_during_storytelling(self):
        play_until_phase(self.game, Game.GamePhase.STORYTELLING)
        self.game.remove_player(self.game.players[-1])
        play_until_phase(self.game, Game.GamePhase.STORYTELLING)

    def test_remove_listener_during_matching(self):
        play_until_phase(self.game, Game.GamePhase.MATCHING)
        self.game.remove_player(self.game.players[-1])
        play_until_phase(self.game, Game.GamePhase.STORYTELLING)

    def test_remove_listener_during_guessing(self):
        play_until_phase(self.game, Game.GamePhase.GUESSING)
        self.game.remove_player(self.game.players[-1])
        play_until_phase(self.game, Game.GamePhase.STORYTELLING)

    def test_remove_listener_during_interlude(self):
        play_until_phase(self.game, Game.GamePhase.INTERLUDE)
        self.game.remove_player(self.game.players[-1])
        play_until_phase(self.game, Game.GamePhase.STORYTELLING)


class TestGame(unittest.TestCase):
    def setUp(self):
        self.game = make_game()

    def test_add(self):
        self.assertEqual(len(self.game.players), 4)

    def test_add_after_removal(self):
        self.game.start_game()
        player = self.game.players[0]
        self.game.remove_player(player)
        self.game.add_player(player)

    def test_full_round(self):
        play_until_phase(self.game, Game.GamePhase.INTERLUDE)


if __name__ == '__main__':
    unittest.main()

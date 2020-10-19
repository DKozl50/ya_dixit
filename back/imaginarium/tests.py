import unittest
from mechanics import Game, Player, Card, Pack
from typing import Optional, List
from random import randint, choice


def play_until_phase(game: Game, phase: Game.GamePhase,
                     bets: Optional[List[int]] = None,
                     guesses: Optional[List[int]] = None,
                     stop: bool = False,
                     enable_random: bool = False) -> None:
    if phase == game.get_state() and stop:
        return
    if game.get_state() == Game.GamePhase.WAITING:
        for player in game.players:
            game.make_current_game_state(player)
        game.start_game()
    elif game.get_state() == Game.GamePhase.STORYTELLING:
        winner = game.finished()
        if winner is not None:
            game.end_game(winner)
            for player in game.players:
                game.make_current_game_state(player)
            return
        cur_player = game.get_cur_player()
        game.add_lead_card(game.hands[cur_player][0].id)
        for player in game.players:
            game.make_current_game_state(player)
        game.start_turn("association")
    elif game.get_state() == Game.GamePhase.MATCHING:
        if bets is None:
            bets = [game.hands[player][0] for player in game.players]
        if enable_random:
            bets = [choice(game.hands[player]) for player in game.players]
        for player, bet in zip(game.players, bets):
            game.make_bet(player, bet.id)
            game.finish_turn(player)
        for player in game.players:
            game.make_current_game_state(player)
        game.place_cards()
    elif game.get_state() == Game.GamePhase.GUESSING:
        if guesses is None:
            guesses = [list(game.current_table.keys())[0]] * len(game.players)
        if enable_random:
            guesses = [choice(list(game.current_table.keys()))
                       for player in game.players]
        for player, guess in zip(game.players, guesses):
            game.make_guess(player, guess.id)
            game.finish_turn(player)
        for player in game.players:
            game.make_current_game_state(player)
        game.valuate_guesses()
    elif game.get_state() == Game.GamePhase.INTERLUDE:
        for player in game.players:
            game.make_current_game_state(player)
        game.end_turn()
    play_until_phase(
        game,
        phase,
        bets=bets,
        guesses=guesses,
        stop=True,
        enable_random=enable_random
    )


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
        self.assertEqual(len(self.game.players), 3)

    def test_remove_listener_during_storytelling(self):
        play_until_phase(self.game, Game.GamePhase.STORYTELLING)
        self.game.remove_player(self.game.players[-1])
        self.assertEqual(len(self.game.players), 4)
        play_until_phase(self.game, Game.GamePhase.STORYTELLING)
        self.assertEqual(len(self.game.players), 3)

    def test_remove_listener_during_matching(self):
        play_until_phase(self.game, Game.GamePhase.MATCHING)
        self.game.remove_player(self.game.players[-1])
        self.assertEqual(len(self.game.players), 4)
        play_until_phase(self.game, Game.GamePhase.STORYTELLING)
        self.assertEqual(len(self.game.players), 3)

    def test_remove_listener_during_guessing(self):
        play_until_phase(self.game, Game.GamePhase.GUESSING)
        self.game.remove_player(self.game.players[-1])
        self.assertEqual(len(self.game.players), 4)
        play_until_phase(self.game, Game.GamePhase.STORYTELLING)
        self.assertEqual(len(self.game.players), 3)

    def test_remove_listener_during_interlude(self):
        play_until_phase(self.game, Game.GamePhase.INTERLUDE)
        self.game.remove_player(self.game.players[-1])
        self.assertEqual(len(self.game.players), 4)
        play_until_phase(self.game, Game.GamePhase.STORYTELLING)
        self.assertEqual(len(self.game.players), 3)


class TestScoringSystem(unittest.TestCase):
    def setUp(self):
        self.game: Game = make_game()

    def test_all_leader(self):
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

    def test_all_turns_ended(self):
        play_until_phase(self.game, Game.GamePhase.MATCHING)
        game = self.game
        bets = [game.hands[player][0] for player in game.players]
        arr = list(zip(game.players, bets))
        for player, bet in arr[:-1]:
            game.make_bet(player, bet.id)
            game.finish_turn(player)
        self.assertFalse(game.all_turns_ended())
        game.make_bet(arr[-1][0], arr[-1][1].id)
        game.finish_turn(arr[-1][0])
        self.assertTrue(game.all_turns_ended())

    def test_get_votes(self):
        play_until_phase(self.game, Game.GamePhase.INTERLUDE)
        for card in self.game.current_table.keys():
            self.game.get_votes(card)

    def test_get_hand(self):
        play_until_phase(self.game, Game.GamePhase.STORYTELLING)
        for player in self.game.players:
            self.assertEqual(
                self.game.get_hand(player),
                [str(card.id) for card in self.game.hands[player]]
            )

    def test_full_round(self):
        play_until_phase(self.game, Game.GamePhase.INTERLUDE)

    def test_full_game(self):
        for _ in range(100):
            self.game = make_game()
            play_until_phase(
                self.game,
                Game.GamePhase.VICTORY,
                enable_random=True
            )


class TestCard(unittest.TestCase):
    def test_new_id(self):
        Card("link", 0, -1)
        Card.card_ids.pop(-1)


if __name__ == '__main__':
    unittest.main()

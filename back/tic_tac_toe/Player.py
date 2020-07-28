from random import randint
import tic_tac_toe.main as main

class Player:
    """id: Player.id
    state: {Game.id, None}
    """
    __player_ids = []

    def __init__(self):
        self.id = self.__get_new_id()
        self.state = None

    def join_game(self, game):
        if self.state is not None:
            return False
        if game.PlayerX is not None and game.PlayerO is not None:
            return False
        self.state = game.id
        game.add_player(self.id)
        return True

    def leave_game(self, game):
        self.state = None
        return game.leave_player(self.id)

    @staticmethod
    def __get_new_id():
        potential = randint(100000, 999999)
        while potential in Player.__player_ids:
            potential = randint(100000, 999999)
        Player.__player_ids.append(potential)
        return potential
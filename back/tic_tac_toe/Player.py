from uuid import uuid1


class Player:
    """id: player.id
    state: {game.id, None}
    """
    __player_ids = {}

    def __init__(self):
        self.__get_new_id()
        self.state = None

    def __get_new_id(self):
        self.id = uuid1().time_low
        Player.__player_ids[self.id] = self

    def join_game(self, game):
        if self.state is not None:
            return False
        if game.is_ready():
            return False
        self.state = game.id
        game.add_player(self.id)
        return True

    def leave_game(self, game):
        self.state = None
        game.try_leave_player(self.id)

    @staticmethod
    def get_player(id):
        return Player.__player_ids.get(id, None)

    @staticmethod
    def get_all_players():
        return Player.__player_ids.values()

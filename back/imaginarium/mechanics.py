from enum import Enum, auto
from random import shuffle
from uuid import uuid1
import logging

logger = logging.getLogger('app.mechanics')


class Player:
    """id: Player.id
    name: string
    picture: string
    registered: bool
    friends: [Player.id]
    fav_packs: [Pack.id]
    game_archive: [Game.id]
    password_hash: hash
    """
    __player_ids = {}

    def __init__(self, name, password_hash=None):
        self.__get_new_id()
        self.name = name
        self.picture = None
        self.friends = []
        self.fav_packs = []
        self.game_archive = []
        if password_hash is None:
            self.registered = False
            self.password_hash = None
        else:
            self.registered = True
            self.password_hash = password_hash

    # TODO add Database
    def __get_new_id(self):
        self.id = uuid1().time_low
        Player.__player_ids[self.id] = self

    @staticmethod
    def get_player(id):
        return Player.__player_ids.get(id, None)

    @staticmethod
    def get_all_players():
        return Player.__player_ids.values()


class Game:
    """id: Game.id
    packs: {Pack.id} # или карты?
    players: [Player.id]
    result: {Player.id: int}
    settings: dict

    _state: Waiting/Storytelling/Matching/Guessing/Interlude/Victory
    _turn: None/Player.id
    """
    __game_ids = {}

    class States(Enum):
        WAITING = auto()
        STORYTELLING = auto()
        MATCHING = auto()
        GUESSING = auto()
        INTERLUDE = auto()
        VICTORY = auto()

    class RuleSets(Enum):
        IMAGINARIUM = auto()
        DIXIT = auto()

    def __init__(self):
        self.__get_new_id()
        self.packs = set()
        self.players = []
        self.result = dict()
        self.settings = {
            'win_score': 40,
            'move_time': 60,  # in seconds
            'rule_set': self.RuleSets.IMAGINARIUM  # only IMAGINARIUM for now
        }
        self._state = self.States.WAITING
        self._hands = dict()
        self._current_association = ''
        self._turn = None
        self._current_player = None
        self._lead_card = None
        self._current_table = None

    def add_player(self, player_id):
        """Can be called before and in the game
        If game has already started
        deals 6 cards to new player.
        """
        self.players.append(player_id)
        if player_id in self.result:
            # deal with 'did_not_finish *number*'
            self.result[player_id] = int(self.result[player_id].split()[1])
        else:
            self.result[player_id] = 0
        if self._state != self.States.WAITING:
            self._deal_hand(player_id)

    def remove_player(self, player_id):
        """Removes player from game setting score as did_not_finish"""
        self.players.remove(player_id)
        if self._state != Game.States.WAITING:
            self._turn %= len(self.players)
            self._current_player = self.players[self._turn]
            self._cards += self._hands[player_id]
            self._hands[player_id] = []
            self.result[player_id] = f'did_not_finish {self.result[player_id]}'
        else:
            # removes from results as the game has not started
            self.result.pop(player_id)

    def start_game(self):
        """Shuffles players, generates card list,
        deals 6 cards to each player.
        """
        self._turn = 0  # first player is a storyteller now
        self._fix_packs()
        self._shuffle_players()
        for p in self.players:
            self._deal_hand(p)
        self._current_player = self.players[self._turn]
        self._state = Game.States.STORYTELLING

    def start_turn(self, association, card):
        """Sets association, removes card from active player.
        association: string
        card: Card.id
        """
        self._current_association = association
        self._lead_card = card
        self._hands[self._current_player].remove(card)
        self._current_table = {card: self._current_player}
        self._state = self.States.MATCHING  # the next stage is matching

    def place_cards(self, bets):
        """Removes cards from players and adds them to the current table.
        bets: {Player.id: Card.id}
        """
        for player, card in bets.items():
            self._hands[player].remove(card)
            self._current_table[card] = player
        self._state = self.States.GUESSING

    def valuate_guesses(self, guesses):
        """Changes score according to guesses.
        guesses: {Player.id: Card.id}
        """
        self._state = self.States.INTERLUDE
        if self.settings['rule_set'] == Game.RuleSets.IMAGINARIUM:
            # everyone guessed leader
            if all(self._lead_card == selected_card for selected_card in guesses.values()):
                self.result[self._current_player] -= 3
                self.result[self._current_player] = max(
                    0, self.result[self._current_player]
                )  # score cannot be under the zero
                return

            if all(self._lead_card != selected_card for selected_card in guesses.values()):
                # no one guessed leader
                self.result[self._current_player] -= 2
                self.result[self._current_player] = max(
                    0, self.result[self._current_player]
                )
            else:
                self.result[self._current_player] += 3
                for player, card in guesses.items():
                    if card == self._lead_card:
                        self.result[player] += 3
                        self.result[self._current_player] += 1

            for player, card in guesses.items():
                if card == self._lead_card:
                    continue
                card_owner = self._current_table[card]
                if card_owner in self.players:
                    self.result[card_owner] += 1

    def end_turn(self):
        """Ends turn changing game.state, clearing internal variables
        and dealing cards.
        """
        self._turn = (self._turn + 1) % len(self.players)

        # clear table
        for card in self._current_table.keys():
            self._cards.append(card)

        # deal cards
        for player in self.players:
            self._deal_hand(player)
        self._current_player = self.players[self._turn]
        self._state = Game.States.STORYTELLING

    def end_game(self):
        self._state = Game.States.VICTORY

    def get_state(self):
        return self._state

    def get_hand(self, target):
        return self._hands[target]

    def _fix_packs(self):
        """Fixes packs choice.
        Transforms packs to cards and shuffles them.
        """
        self._cards = _packs_to_cards(self.packs)
        shuffle(self._cards)

    def _shuffle_players(self):
        """Shuffles players order.
        New players are appended to the end
        """
        shuffle(self.players)

    def _deal_hand(self, target):
        """Fills hand until it's full."""
        needed = 6 - len(self._hands[target])
        self._hands[target] = self._cards[:needed]
        self._cards = self._cards[needed:]

    # TODO add Database
    def __get_new_id(self):
        self.id = uuid1().time_low
        Game.__game_ids[self.id] = self

    @staticmethod
    def get_game(id):
        return Game.__game_ids.get(id, None)

    @staticmethod
    def delete_game(id):
        Game.__game_ids.pop(id)


class Card:
    """id: Card.id
    picture: link
    pack_id: Pack.id
    """
    __card_ids = {}

    def __init__(self, picture, pack_id):
        self._get_new_id()
        self.picture = picture
        self.pack_id = pack_id

    # TODO add Database
    def _get_new_id(self):
        self.id = uuid1().time_low
        Card.__card_ids[self.id] = self


class Pack:
    """id: Pack.id
    name: string
    description: string
    """
    __pack_ids = {}

    def __init__(self, name, description):
        self._get_new_id()
        self.name = name
        self.description = description

    # TODO add Database
    def _get_new_id(self):
        self.id = uuid1().time_low
        Pack.__pack_ids[self.id] = self


def _packs_to_cards(packs):  # TODO add Database
    return []

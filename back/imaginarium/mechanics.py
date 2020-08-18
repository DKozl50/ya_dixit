from enum import Enum, auto
from random import shuffle
from typing import Any, Dict
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
    current_game: None | game_id
    password_hash: hash
    """
    __player_ids: Dict[int, Any] = {}

    def __init__(self, name, password_hash=None):
        self.__get_new_id()
        self.name = name
        self.picture = None
        self.friends = []
        self.fav_packs = []
        self.current_game = None
        if password_hash is None:
            self.registered = False
            self.password_hash = None
        else:
            self.registered = True
            self.password_hash = password_hash

    # TODO add Databases

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
    players: [Player]
    result: {Player: int}
    turn_ended: {Player: bool}
    num_players_to_start: int # минимальное количество игроков, чтобы игра началась
    bets: {Player: Card.id}
    guesses: {Player: Card.id}
    winner: Player or None
    settings: dict

    _state: Waiting/Storytelling/Matching/Guessing/Interlude/Victory
    _turn: None/Player
    """
    __game_ids: Dict[int, Any] = {}

    class GamePhase(Enum):
        WAITING = auto()
        STORYTELLING = auto()
        MATCHING = auto()
        GUESSING = auto()
        INTERLUDE = auto()
        VICTORY = auto()

    class RuleSet(Enum):
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
            'rule_set': self.RuleSet.IMAGINARIUM  # only IMAGINARIUM for now
        }
        self._num_players_to_start = 3  # TODO game should be started by leader of the room
        self._bets = dict()
        self._guesses = dict()
        self._state = self.GamePhase.WAITING
        self._hands = dict()
        self._current_association = ''
        self._turn_ended = dict()
        self._turn = None
        self._winner = None
        self._current_player = None
        self._lead_card = None
        self._current_table = dict()

    def add_player(self, player: Player):
        """Can be called before and in the game
        If game has already started
        deals 6 cards to new player.
        """
        self.players.append(player)
        self._hands[player] = []
        self._turn_ended[player] = True
        if player in self.result:
            # deal with 'did_not_finish *number*'
            self.result[player] = int(self.result[player].split()[1])
        else:
            self.result[player] = 0
        if self._state != self.GamePhase.WAITING:
            self._deal_hand(player)
        if len(self.players) >= self._num_players_to_start:
            self.start_game()

    def remove_player(self, player):
        """Removes player from game setting score as did_not_finish"""
        self.players.remove(player)
        if self._state != Game.GamePhase.WAITING:
            self._turn %= len(self.players)
            self._current_player = self.players[self._turn]
            self._cards += self._hands[player]
            self._hands[player] = []
            self.result[player] = f'did_not_finish {self.result[player]}'
        else:
            # removes from results as the game has not started
            self.result.pop(player)

    def start_game(self):
        """Shuffles players, generates card list,
        deals 6 cards to each player.
        """
        self._turn = 0  # first player is a storyteller now
        self._fix_packs()
        self._shuffle_players()
        for player in self.players:
            self._turn_ended[player] = False
        for p in self.players:
            self._deal_hand(p)
        self._current_player = self.players[self._turn]
        self._state = Game.GamePhase.STORYTELLING

    def start_turn(self, association):
        """Sets association, removes card from active player.
        association: string
        card: Card.id
        """
        self._current_association = association
        for player in self.players:
            self._turn_ended[player] = False
        self._bets = dict()
        self._current_table = {self._lead_card: self._current_player}
        self._hands[self._current_player].remove(self._lead_card)
        self._turn_ended[self._current_player] = True
        self._state = self.GamePhase.MATCHING  # the next stage is matching

    def place_cards(self):
        """Removes cards from players and adds them to the current table.
        bets: {Player: Card.id}
        """
        for player, card in self._bets.items():
            self._hands[player].remove(card)
            self._current_table[card] = player
        for player in self.players:
            self._turn_ended[player] = False
        self._guesses = dict()
        self._turn_ended[self._current_player] = True
        self._state = self.GamePhase.GUESSING

    def valuate_guesses(self):
        """Changes score according to guesses.
        guesses: {Player: Card.id}
        """
        self._state = self.GamePhase.INTERLUDE
        if self.settings['rule_set'] == Game.RuleSet.IMAGINARIUM:
            # everyone guessed leader
            if all(self._lead_card ==
                   selected_card for selected_card in self._guesses.values()):
                self.result[self._current_player] -= 3
                self.result[self._current_player] = max(
                    0, self.result[self._current_player]
                )  # score cannot be under the zero
                return

            if all(self._lead_card !=
                   selected_card for selected_card in self._guesses.values()):
                # no one guessed leader
                self.result[self._current_player] -= 2
                self.result[self._current_player] = max(
                    0, self.result[self._current_player]
                )
            else:
                self.result[self._current_player] += 3
                for player, card in self._guesses.items():
                    if card == self._lead_card:
                        self.result[player] += 3
                        self.result[self._current_player] += 1

            for player, card in self._guesses.items():
                if card == self._lead_card:
                    continue
                card_owner = self._current_table[card]
                if card_owner in self.players:
                    self.result[card_owner] += 1

    def finish_turn(self, player):
        if self._state == self.GamePhase.GUESSING and self._guesses[player] is None:
            return
        self._turn_ended[player] = True

    def all_turns_ended(self):
        ok = True
        for player in self.players:
            if self._turn_ended[player] is False:
                ok = False
                break
        return ok

    def make_bet(self, player, card):
        # player isn't a storyteller
        if self._turn_ended[player] is True:
            return
        if card in self._hands[player]:
            self._bets[player] = card

    def make_guess(self, player, card):
        # player isn't a storyteller
        if self._turn_ended[player] is True:
            return
        if card in self._current_table:
            if self._current_table[card] != player:
                self._guesses[player] = card

    def add_lead_card(self, card):
        self._lead_card = card

    def end_turn(self):
        """Ends turn changing game.state, clearing internal variables
        and dealing cards.
        """
        self._turn = (self._turn + 1) % len(self.players)

        # clear _turn_ended
        for player in self.players:
            self._turn_ended[player] = False

        # clear table
        for card in self._current_table.keys():
            self._cards.append(card)

        # deal cards
        for player in self.players:
            self._deal_hand(player)
        self._current_player = self.players[self._turn]
        self._current_association = None
        self._lead_card = None
        self._state = Game.GamePhase.STORYTELLING

    def finished(self):
        maximum = -1
        player_with_maximum = None
        for player in self.players:
            if self.result[player] > maximum:
                maximum = self.result[player]
                player_with_maximum = player
        if maximum >= self.settings['win_score']:
            return player_with_maximum
        return None

    def end_game(self, player):
        self._state = Game.GamePhase.VICTORY
        self._winner = player

    def get_votes(self, card_id):
        votes = []
        for player, card in self._guesses.items():
            if card == card_id:
                votes.append(self.make_example_player(player))
        return votes

    def get_state(self):
        return self._state

    def get_cur_player(self):
        return self._current_player

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

    def make_example_player(self, player):
        to_return = dict()
        to_return['Name'] = player.name
        if self._current_player == player:
            to_return['Role'] = 'Storyteller'
        elif self._state == self.GamePhase.GUESSING:
            if self._turn_ended[player] is True and player not in self._guesses:
                to_return['Role'] = 'Spectator'
            else:
                to_return['Role'] = 'Listener'
        elif self._state == self.GamePhase.MATCHING:
            if self._turn_ended[player] is True and player not in self._bets:
                to_return['Role'] = 'Spectator'
            else:
                to_return['Role'] = 'Listener'
        else:
            to_return['Role'] = 'Listener'
        to_return['Score'] = self.result[player]
        to_return['MoveAvailable'] = not self._turn_ended[player]
        return to_return

    def make_current_game_state(self, player):
        to_return = dict()
        to_return['Client'] = self.make_example_player(player)
        opponents = []
        for other_player in self.players:
            if other_player != player:
                opponents.append(self.make_example_player(other_player))
        to_return['Opponents'] = opponents
        player_hand = dict()
        player_hand['Cards'] = self.get_hand(player)
        if self._state == self.GamePhase.MATCHING:
            if player in self._bets:
                player_hand['SelectedCard'] = self._bets[player]
            else:
                player_hand['SelectedCard'] = None
        elif self._state == self.GamePhase.GUESSING:
            if player in self._guesses:
                player_hand['SelectedCard'] = self._guesses[player]
            else:
                player_hand['SelectedCard'] = None
        else:
            player_hand['SelectedCard'] = None
        to_return['Hand'] = player_hand
        table = dict()
        cards_on_table = []
        for card, player in self._current_table.items():
            mas = []
            mas.append(card)
            if self._state == self.GamePhase.INTERLUDE:
                tmp = dict()
                tmp['Owner'] = self.make_example_player(player)
                tmp['Voters'] = self.get_votes(card)
                mas.append(tmp)
            else:
                mas.append(None)
            cards_on_table.append(mas)
        table['Cards'] = cards_on_table
        table['Story'] = self._current_association
        to_return['Table'] = table
        phase = []
        if self._state == self.GamePhase.STORYTELLING:
            phase.append('Storytelling')
        if self._state == self.GamePhase.WAITING:
            phase.append('Waiting')
        if self._state == self.GamePhase.MATCHING:
            phase.append('Matching')
        if self._state == self.GamePhase.INTERLUDE:
            phase.append('Interlude')
        if self._state == self.GamePhase.GUESSING:
            phase.append('Guessing')
        if self._state == self.GamePhase.VICTORY:
            phase.append('Victory')
            phase.append(self.make_example_player(self._winner))
        to_return['Phase'] = phase
        return to_return

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
    __card_ids: dict = {}

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
    __pack_ids: Dict[int, Any] = {}

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

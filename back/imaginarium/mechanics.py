from enum import Enum, auto
from random import shuffle
from typing import Any, Dict
from uuid import uuid1
from os import listdir
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
    state: Waiting/Storytelling/Matching/Guessing/Interlude/Victory
    turn: None/Player
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
        self.players_to_start = 3  # TODO game should be started by leader of the room
        self.story = None
        self.bets = dict()
        self.guesses = dict()
        self.state = self.GamePhase.WAITING
        self.hands = dict()
        self.current_association = ''
        self.turn_ended = dict()
        self.turn = None
        self.winner = None
        self.current_player = None
        self.lead_card = None
        self.current_table = dict()

    def add_player(self, player: Player):
        """Can be called before and in the game
        If game has already started
        deals 6 cards to new player.
        """
        self.players.append(player)
        player.current_game = self
        self.hands[player] = []
        self.turn_ended[player] = True
        if player in self.result:
            # deal with 'did_not_finish *number*'
            self.result[player] = int(self.result[player].split()[1])
        else:
            self.result[player] = 0
        if self.state != self.GamePhase.WAITING:
            self._deal_hand(player)

    def remove_player(self, player):
        """Removes player from game setting score as did_not_finish"""
        self.players.remove(player)
        player.current_game = None
        if self.state != Game.GamePhase.WAITING:
            self.turn %= len(self.players)
            self.current_player = self.players[self.turn]
            self._cards += self.hands[player]
            self.hands[player] = []
            self.result[player] = f'did_not_finish {self.result[player]}'
        else:
            # removes from results as the game has not started
            self.result.pop(player)

    def start_game(self):
        """Shuffles players, generates card list,
        deals 6 cards to each player.
        """
        self.turn = 0  # first player is a storyteller now
        self._fix_packs()
        self._shuffle_players()
        for player in self.players:
            self.turn_ended[player] = False
        for p in self.players:
            self._deal_hand(p)
        self.current_player = self.players[self.turn]
        self.state = Game.GamePhase.STORYTELLING

    def start_turn(self, association):
        """Sets association, removes card from active player.
        association: string
        card: Card.id
        """
        logger.info(f"Game {self.id} is starting a turn")
        logger.info(f"Game {self.id} players: {self.players}")
        self.current_association = association
        for player in self.players:
            self.turn_ended[player] = False
            logger.info(f"{player.name}'s hands: {self.hands[player]}")
        logger.info(f"Current player: {self.current_player.name}")
        logger.info(f"Current lead card: {self.lead_card}")
        self.bets = dict()
        self.current_table = {self.lead_card: self.current_player}
        self.hands[self.current_player].remove(self.lead_card)
        self.turn_ended[self.current_player] = True
        self.state = self.GamePhase.MATCHING  # the next stage is matching

    def place_cards(self):
        """Removes cards from players and adds them to the current table.
        bets: {Player: Card.id}
        """
        for player, card in self.bets.items():
            self.hands[player].remove(card)
            self.current_table[card] = player
        for player in self.players:
            self.turn_ended[player] = False
        self.guesses = dict()
        self.turn_ended[self.current_player] = True
        self.state = self.GamePhase.GUESSING

    def valuate_guesses(self):
        """Changes score according to guesses.
        guesses: {Player: Card.id}
        """
        self.state = self.GamePhase.INTERLUDE
        if self.settings['rule_set'] == Game.RuleSet.IMAGINARIUM:
            # everyone guessed leader
            if all(self.lead_card ==
                   selected_card for selected_card in self.guesses.values()):
                self.result[self.current_player] -= 3
                self.result[self.current_player] = max(
                    0, self.result[self.current_player]
                )  # score cannot be under the zero
                return

            if all(self.lead_card !=
                   selected_card for selected_card in self.guesses.values()):
                # no one guessed leader
                self.result[self.current_player] -= 2
                self.result[self.current_player] = max(
                    0, self.result[self.current_player]
                )
            else:
                self.result[self.current_player] += 3
                for player, card in self.guesses.items():
                    if card == self.lead_card:
                        self.result[player] += 3
                        self.result[self.current_player] += 1

            for player, card in self.guesses.items():
                if card == self.lead_card:
                    continue
                card_owner = self.current_table[card]
                if card_owner in self.players:
                    self.result[card_owner] += 1

    def finish_turn(self, player):
        if self.state == self.GamePhase.GUESSING and self.guesses[player] is None:
            return
        self.turn_ended[player] = True

    def all_turns_ended(self):
        cur_player = self.get_cur_player()
        for player in self.players:
            if player == cur_player:
                assert self.turn_ended[player]
            if not self.turn_ended[player]:
                return False
        return True

    def make_bet(self, player, card_id):
        # player isn't a storyteller
        card = Card.card_ids[card_id]
        if self.turn_ended[player] is True:
            return
        if card in self.hands[player]:
            self.bets[player] = card

    def make_guess(self, player, card_id):
        # player isn't a storyteller
        card = Card.card_ids[card_id]
        if self.turn_ended[player] is True:
            return
        if card in self.current_table.keys():
            if self.current_table[card] != player:
                logger.debug(f'{player.id} choose {card_id}')
                self.guesses[player] = card

    def add_lead_card(self, card_id: str):
        self.lead_card = Card.card_ids[card_id]

    def end_turn(self):
        """Ends turn changing game.state, clearing internal variables
        and dealing cards."""
        self.turn = (self.turn + 1) % len(self.players)

        # clear _turn_ended
        for player in self.players:
            self.turn_ended[player] = False

        # clear table
        for card in self.current_table.keys():
            self._cards.append(card)
        self.current_table = dict()

        # deal cards
        for player in self.players:
            self._deal_hand(player)
        self.current_player = self.players[self.turn]
        self.current_association = None
        self.lead_card = None
        self.state = Game.GamePhase.STORYTELLING

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
        self.state = Game.GamePhase.VICTORY
        self.winner = player

    def get_votes(self, card_id):
        votes = []
        for player, card in self.guesses.items():
            if card == card_id:
                votes.append(self.make_example_player(player))
        return votes

    def get_state(self):
        return self.state

    def get_cur_player(self):
        return self.current_player

    def get_hand(self, target):
        return [str(card.id) for card in self.hands[target]]

    def _fix_packs(self):
        """Fixes packs choice.
        Transforms packs to cards and shuffles them."""
        self._cards = _packs_to_cards(self.packs)  # TODO packs
        shuffle(self._cards)

    def _shuffle_players(self):
        """Shuffles players order.
        New players are appended to the end"""
        shuffle(self.players)

    def _deal_hand(self, target):
        """Fills hand until it's full."""
        needed = 6 - len(self.hands[target])
        self.hands[target] += self._cards[:needed]
        self._cards = self._cards[needed:]

    def make_example_player(self, player):
        to_return = dict()
        to_return['Name'] = player.name
        if self.current_player == player:
            to_return['Role'] = 'Storyteller'
        else:
            to_return['Role'] = 'Listener'
        to_return['Score'] = self.result[player]
        to_return['MoveAvailable'] = not self.turn_ended[player]
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
        hand = self.get_hand(player)
        player_hand['Cards'] = hand
        if self.state == self.GamePhase.MATCHING:
            if player in self.bets:
                player_hand['SelectedCard'] = str(self.bets[player].id)
            else:
                player_hand['SelectedCard'] = None
        elif self.state == self.GamePhase.GUESSING:
            if player in self.guesses:
                player_hand['SelectedCard'] = str(self.guesses[player].id)
            else:
                player_hand['SelectedCard'] = None
        else:
            player_hand['SelectedCard'] = None
        to_return['Hand'] = player_hand
        table = dict()
        cards_on_table = []
        for card, other_player in self.current_table.items():
            request = [card.id]
            if other_player == player:
                tmp = dict()
                tmp['Owner'] = self.make_example_player(player)
                tmp['Voters'] = self.get_votes(card)
                request.append(tmp)
            else:
                request.append(None)
            cards_on_table.append(request)
        table['Cards'] = cards_on_table
        table['Story'] = self.current_association
        to_return['Table'] = table
        if self.state == self.GamePhase.STORYTELLING:
            to_return['Phase'] = 'Storytelling'
        if self.state == self.GamePhase.WAITING:
            to_return['Phase'] = 'Waiting'
        if self.state == self.GamePhase.MATCHING:
            to_return['Phase'] = 'Matching'
        if self.state == self.GamePhase.INTERLUDE:
            to_return['Phase'] = 'Interlude'
        if self.state == self.GamePhase.GUESSING:
            to_return['Phase'] = 'Guessing'
        if self.state == self.GamePhase.VICTORY:
            to_return['Phase'] = 'Victory'
        print(to_return)
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
    pack_id: Pack.id"""
    card_ids: Dict[str, Any] = {}

    def __init__(self, picture, pack_id, id=None):
        self._get_new_id(id)
        self.picture = picture
        self.pack_id = pack_id

    # TODO add Database
    def _get_new_id(self, id):
        if id is not None:
            self.id = id
        else:
            self.id = str(uuid1().time_low)
        Card.card_ids[self.id] = self


class Pack:
    """id: Pack.id
    name: string
    description: string"""
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
    path = '..\\..\\front\\public\\img'
    names = list(map(lambda name: name.replace('.jpg', ''), listdir(path)))
    shuffle(names)
    return [Card('picture', 1, name) for name in names[:200]]

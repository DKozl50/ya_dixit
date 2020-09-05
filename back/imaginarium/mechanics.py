from enum import Enum, auto
from random import shuffle, choice
from typing import Any, Dict, List, Optional
from uuid import uuid1
from os import listdir, makedirs
from shutil import copy
from json import dump as js_dump, load as js_load
import logging

logger = logging.getLogger("app.mechanics")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("app.log")
file_handler.setFormatter(logging.Formatter(
    "%(filename)s[LINE:%(lineno)-3s]# "
    "%(levelname)-8s [%(asctime)s]  %(message)s")
)
logger.addHandler(file_handler)


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

    def __init__(self, name: str, password_hash=None) -> None:
        self.__get_new_id()
        self.name: str = name
        self.picture: Optional[str] = None
        self.friends: List[int] = []
        self.fav_packs: List[int] = []
        self.current_game: Optional[Game] = None
        if password_hash is None:
            self.registered = False
            self.password_hash = None
        else:
            self.registered = True
            self.password_hash = password_hash

    # TODO add Databases

    def __get_new_id(self):
        self.id = uuid1().time_low


class Game:
    """id: Game.id
    packs: {Pack.id} # or cards?
    players: [Player]
    result: {Player: int}
    turn_ended: {Player: bool}
    num_players_to_start: int # minimal player count to start the game
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
        self.players: List[Player] = []
        self.result = dict()
        self.settings = {
            "win_score": 40,
            "move_time": 60,  # in seconds
            "rule_set": self.RuleSet.IMAGINARIUM  # only IMAGINARIUM for now
        }
        # TODO game should be started by leader of the room
        self.players_to_start = 3
        self.story: Optional[str] = None
        self.bets = dict()
        self.guesses = dict()
        self.state = self.GamePhase.WAITING
        self.hands: Dict[Player, List[Card]] = dict()
        self.current_association = ""
        self.turn_ended: Dict[Player, bool] = dict()
        self.turn = None
        self.winner: Player
        self.current_player: Player
        self.lead_card: Card
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
            # deal with "did_not_finish *number*"
            self.result[player] = int(self.result[player].split()[1])
        else:
            self.result[player] = 0
        if self.state != self.GamePhase.WAITING:
            self._deal_hand(player)

    def remove_player(self, player: Player) -> None:
        """Removes player from game setting score as did_not_finish"""
        if self.state != Game.GamePhase.WAITING:
            if player != self.current_player:
                if self.state == Game.GamePhase.STORYTELLING:
                    if self.players.index(player) < self.turn:
                        self.turn -= 1
                    self._cards += self.hands[player]
                    self.hands[player] = []
                    self.result[player] = \
                        f"did_not_finish {self.result[player]}"
                elif (self.state == Game.GamePhase.MATCHING and
                      len(self.current_table) < len(self.players)):
                    if self.bets.get(player) is None:
                        if self.players.index(player) < self.turn:
                            self.turn -= 1
                        self._cards += self.hands[player]
                        self.hands[player] = []
                        self.result[player] = \
                            f"did_not_finish {self.result[player]}"
                    else:
                        self.bets.pop(player)
                        self._cards += self.hands[player]
                        self.hands[player] = []
                        self.result[player] = \
                            f"did_not_finish {self.result[player]}"
                elif self.state == Game.GamePhase.GUESSING:
                    # TODO 1.4 and 1.5
                    pass
            else:
                if self.state == Game.GamePhase.STORYTELLING:
                    # TODO 2.1
                    self.turn %= len(self.players)
                    self.current_player = self.players[self.turn]
                    self._cards += self.hands[player]
                    self.hands[player] = []
                    self.result[player] = \
                        f"did_not_finish {self.result[player]}"
                elif (self.state == Game.GamePhase.MATCHING and
                      len(self.current_table) < len(self.players)):
                    self.result[player] = \
                        f"did_not_finish {self.result[player]}"
                    self.end_turn()
                else:
                    self.turn %= len(self.players)
                    self.current_player = self.players[self.turn]
                    self._cards += self.hands[player]
                    self.hands[player] = []
                    self.result[player] = \
                        f"did_not_finish {self.result[player]}"
        else:
            # removes from results as the game has not started
            self.result.pop(player)
        self.players.remove(player)
        player.current_game = None

    def start_game(self):
        """Shuffles players, generates card list,
        deals 6 cards to each player.
        """
        self.turn = 0  # first player is a storyteller now
        self._fix_packs()
        self._shuffle_players()
        for player in self.players:
            self.turn_ended[player] = False
            self.result[player] = 0
        for p in self.players:
            self._deal_hand(p)
        self.current_player = self.players[self.turn]
        self.state = Game.GamePhase.STORYTELLING

    def start_turn(self, association: str) -> None:
        """Sets association, removes card from active player.
        association: string
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

    def place_cards(self) -> None:
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
        if self.settings["rule_set"] == Game.RuleSet.IMAGINARIUM:
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
        if (self.state == self.GamePhase.GUESSING and
                self.guesses[player] is None):
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

    def make_bet(self, player: Player, card_id: str):
        # player isn't a storyteller
        card = Card.card_ids[card_id]
        if self.turn_ended[player] is True:
            return
        if card in self.hands[player]:
            self.bets[player] = card

    def make_guess(self, player: Player, card_id: str) -> None:
        # player isn't a storyteller
        card = Card.card_ids[card_id]
        if self.turn_ended[player] is True:
            return
        if card in self.current_table.keys():
            if self.current_table[card] != player:
                logger.debug(f"{player.id} choose {card_id}")
                self.guesses[player] = card

    def add_lead_card(self, card_id: str) -> None:
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
        if maximum >= self.settings["win_score"]:
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

    def get_cur_player(self) -> Player:
        return self.current_player

    def get_hand(self, target: Player) -> List[str]:
        return [str(card.id) for card in self.hands[target]]

    def _fix_packs(self) -> None:
        """Fixes packs choice.
        Transforms packs to cards and shuffles them."""
        logger.debug(list(Pack.pack_ids.values()))
        pack = choice(list(Pack.pack_ids.values()))
        self._cards = [Card(image, pack.id) for image in pack.pictures]
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
        to_return["Name"] = player.name
        if self.current_player == player:
            to_return["Role"] = "Storyteller"
        else:
            to_return["Role"] = "Listener"
        to_return["Score"] = self.result[player]
        to_return["MoveAvailable"] = not self.turn_ended[player]
        return to_return

    def make_current_game_state(self, player):
        to_return = dict()
        to_return["Client"] = self.make_example_player(player)
        opponents = []
        for other_player in self.players:
            if other_player != player:
                opponents.append(self.make_example_player(other_player))
        to_return["Opponents"] = opponents
        player_hand = dict()
        hand = self.get_hand(player)
        player_hand["Cards"] = hand
        if self.state == self.GamePhase.MATCHING:
            if player in self.bets:
                player_hand["SelectedCard"] = str(self.bets[player].id)
            else:
                player_hand["SelectedCard"] = None
        elif self.state == self.GamePhase.GUESSING:
            if player in self.guesses:
                player_hand["SelectedCard"] = str(self.guesses[player].id)
            else:
                player_hand["SelectedCard"] = None
        else:
            player_hand["SelectedCard"] = None
        to_return["Hand"] = player_hand
        table = dict()
        cards_on_table = []
        for card, other_player in self.current_table.items():
            request = [card.id]
            if (self.state == self.GamePhase.GUESSING and other_player ==
                    player) or self.state == self.GamePhase.INTERLUDE:
                request.append({
                    "Owner": self.make_example_player(player),
                    "Voters": self.get_votes(card)
                })
            else:
                request.append(None)
            cards_on_table.append(request)
        table["Cards"] = cards_on_table
        table["Story"] = self.current_association
        to_return["Table"] = table
        if self.state == self.GamePhase.STORYTELLING:
            to_return["Phase"] = "Storytelling"
        if self.state == self.GamePhase.WAITING:
            to_return["Phase"] = "Waiting"
        if self.state == self.GamePhase.MATCHING:
            to_return["Phase"] = "Matching"
        if self.state == self.GamePhase.INTERLUDE:
            to_return["Phase"] = "Interlude"
        if self.state == self.GamePhase.GUESSING:
            to_return["Phase"] = "Guessing"
        if self.state == self.GamePhase.VICTORY:
            to_return["Phase"] = "Victory"
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
    pack_ids: Dict[str, Any] = dict()

    def __init__(self, name, images=None):
        if images is None:
            images = []
        self.id = name
        Pack.pack_ids[self.id] = self
        self.pictures = images


def load_packs():
    try:
        with open('packs.json', 'r') as read_file:
            data = js_load(read_file)
            for name, images in data.items():
                Pack(name, images)
    except FileNotFoundError:
        pass
    cd = '../../front/public'
    packs_name = listdir(cd)
    if 'img' in packs_name:
        packs_name.remove('img')
    else:
        makedirs(f'{cd}/img')
    if len(packs_name) > 0:
        for name in packs_name:
            if name in Pack.pack_ids:
                continue
            images = listdir(f'{cd}/{name}')
            Pack(name, images)
            for image in images:
                copy(f'{cd}/{name}/{image}', f'{cd}/img')
    with open('packs.json', 'w') as write_file:
        data = {}
        for name, pack in Pack.pack_ids.items():
            data[name] = pack.pictures
        js_dump(data, write_file)


load_packs()

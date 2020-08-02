from random import shuffle
from uuid import uuid1


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
        self._get_new_id()
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
    """
    __game_ids = {}

    def __init__(self):
        self._get_new_id()
        self.packs = set()
        self.players = []
        self.result = dict()
        self.settings = {
            'win_score': 40,
            'move_time': 60,  # in seconds
            'rule_set': 'i'  # only 'i' for now
        }
        self._state = -1
        self._hands = dict()
        self._current_association = ''

    def add_player(self, player_id):
        """Can be called before and in the game
        If game has already started
        deals 6 cards to new player.
        """
        self.players.append(player_id)
        if player_id in self.result:
            # deal with 'dnf *number*' 
            self.result[player_id] = int(self.result[player_id].split()[1])
        else:
            self.result[player_id] = 0
        if self._state != -1:
            self._deal6(player_id)

    def remove_player(self, player_id):
        """Removes player from game setting score as DNF"""
        self.players.remove(player_id)
        if self._state != -1:
            self._state %= len(self.players)
            self._current_player = self.players[self._state]
            self._cards += self._hands[player_id]
            self._hands[player_id] = []
            self.result[player_id] = 'DNF 4'  # if player returns later, their score = 0
        else:
            # removes from results as the game has not started
            self.result.pop(player_id)

    def start_game(self):
        """Shuffles players, generates card list,
        deals 6 cards to each player.
        """
        self._state = 0
        self._fix_packs()
        self._shuffle_players()
        for p in self.players:
            self._deal6(p)
        self._current_player = self.players[self._state]

    def start_turn(self, association, card):
        """Sets association, removes card from active player.
        association: string
        card: Card.id
        """
        self._current_association = association
        self._lead_card = card
        self._hands[self._current_player].remove(card)
        self._current_table = {card: self._current_player}

    def place_cards(self, bets):
        """Removes cards from players and adds them to the current table.
        bets: {Player.id: Card.id}
        """
        for p, c in bets.items():
            self._hands[p].remove(c)
            self._current_table[c] = p

    def valuate_guesses(self, guesses):
        """Changes score according to guesses.
        guesses: {Player.id: Card.id}
        """
        if self.settings['rule_set'] == 'i':
            # everyone guessed leader
            if all(self._lead_card == g_v for g_v in guesses.values()):
                self.result[self._current_player] -= 3
                self.result[self._current_player] = max(
                    0, self.result[self._current_player]
                )
                return

            if all(self._lead_card != g_v for g_v in guesses.values()):
                # no one guessed leader
                self.result[self._current_player] -= 2
                self.result[self._current_player] = max(
                    0, self.result[self._current_player]
                )
            else:
                self.result[self._current_player] += 3
                for p, c in guesses.items():
                    if c == self._lead_card:
                        self.result[p] += 3
                        self.result[self._current_player] += 1

            for p, c in guesses.items():
                if c == self._lead_card:
                    continue
                card_owner = self._current_table[c]
                if card_owner in self.players:
                    self.result[card_owner] += 1

    def end_turn(self):
        """Ends turn changing game.state, clearing internal variables
        and dealing cards.
        """
        self._state = (self._state + 1) % len(self.players)

        # clear table
        for c in self._current_table.keys():
            self._cards.append(c)

        # deal cards
        for p in self.players:
            while len(self._hands[p]) < 6:
                self._deal1(p)
        self._current_player = self.players[self._state]

    def end_game(self):
        self._state = -2

    def get_state(self):
        """returns 0 if game has ended,
        1 if game has not started
        2 if game is active

        game.get_state() is False only if it is incative.
        """
        if self._state == -2:
            return 0
        elif self._state == -1:
            return 1
        else:
            return 2

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

    def _deal1(self, target):
        """Deals 1 card to target, removes this card from available."""
        self._hands[target].append(self._cards.pop(0))

    def _deal6(self, target):
        """Deals 6 cards to target, removes these cards from available."""
        self._hands[target] = self._cards[:6]
        self._cards = self._cards[6:]

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


# сюда наверное надо геты прикрутить для фронта

class Card:
    """id: Card.id
    picture: link
    parent_id: Pack.id
    """
    __card_ids = {}

    def __init__(self, picture, parent_id):
        self._get_new_id()
        self.picture = picture
        self.parent_id = parent_id

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

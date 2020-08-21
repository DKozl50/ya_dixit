import logging
import redis
import json
from geventwebsocket import websocket
from geventwebsocket.handler import WebSocketHandler
from mechanics import Player, Game
from typing import Any, Dict, Optional, Union
from flask import Flask, redirect, url_for
from flask_sockets import Sockets
from gevent import pywsgi, spawn, sleep as gv_sleep
from gevent import monkey
monkey.patch_all()

app = Flask(__name__, static_folder='../../front/deploy')
sockets = Sockets(app)
redis = redis.from_url(url='redis://localhost:6379')


class Lobby(object):
    """Interface for registering and updating WebSocket clients."""

    def __init__(self):
        # game_id -> GameBackend
        self.backends: Dict[int, GameBackend] = dict()
        self.clients = list()
        self.pubsub = redis.pubsub()
        self.pubsub.subscribe(REDIS_CHAN)

    def __iter_data(self) -> Any:
        message: Dict[str, Any]
        for message in self.pubsub.listen():
            data = message.get('data')
            if message['type'] == 'message':
                logger.info(u'Sending message: {}'.format(data))
                yield data

    def register(self, ws: websocket.WebSocket) -> None:
        """Register a WebSocket connection for Redis updates."""
        self.clients.append(ws)

    def unregister(self, ws: websocket.WebSocket) -> None:
        """Unregister a WebSocket connection"""
        self.clients.remove(ws)

    @staticmethod
    def process_message(ws: websocket.WebSocket, message: Union) -> None:
        """Process a message from a client"""
        if message[0] == "CreateRoom":
            ws_to_player[ws].name = message[1]
            create_room(ws)
        elif message[0] == "JoinRoom":
            game_backend = main_lobby.backends.get(int(message[1]))
            if game_backend is None:
                fail_connect(ws)
                return
            game = game_backend.game
            ws_to_player[ws].name = message[2]
            join_room(ws, game)
            if len(game.players) == game.players_to_start:
                game_backend.start_game()

    def send(self, ws: websocket.WebSocket, data: str) -> None:
        """Send given data to the registered client.
        Automatically discards invalid connections."""
        try:
            ws.send(data)
        except Exception:
            logger.info(f'Player {ws} disconnected from lobby')
            self.unregister(ws)

    def run(self) -> None:
        """Listens for new messages in Redis, and sends them to clients."""
        data: str
        for data in self.__iter_data():
            ws: websocket.WebSocket
            for ws in self.clients:
                spawn(self.send, ws, data)

    def start(self) -> None:
        """Maintains Redis subscription in the background."""
        spawn(self.run)


class GameBackend(object):
    """Interface for game and updating WebSocket clients."""
    backend: Dict[websocket.WebSocket, Any] = {}

    def __init__(self):
        self.game = Game()
        self.clients = list()
        self.pubsub = redis.pubsub()
        self.pubsub.subscribe(self.game.id)
        self.start()

    def __bool__(self):
        return len(self.game.players) > 0

    def __iter_data(self):
        for message in self.pubsub.listen():
            data = message.get('data')
            print(message)
            if message['type'] == 'message':
                data = data.decode("utf-8")
                logger.info(u'Sending message: {}'.format(data))
                yield data

    def process_message(self, ws: websocket.WebSocket, message: Union) -> None:
        if message[0] == "LeaveRoom":
            leave_room(ws)
        elif message[0] == "SelectCard":
            self.select_card(ws, str(message[1]))
        elif message[0] == "TellStory":
            self.tell_story(ws, message[1])
        elif message[0] == "EndTurn":
            self.end_turn(ws)

    def register(self, ws: websocket.WebSocket) -> None:
        """Register a WebSocket connection for Redis updates."""
        logger.debug(f'Add {ws} in lobby')
        self.clients.append(ws)

    def unregister(self, ws: websocket.WebSocket) -> None:
        """Unregister a WebSocket connection"""
        self.clients.remove(ws)
        GameBackend.backend.pop(ws)
        self.game.remove_player(ws_to_player[ws])

    def send(self, ws: websocket.WebSocket, data: str) -> None:
        """Send given data to the registered client.
        Automatically discards invalid connections."""
        try:
            ws.send(data)
        except Exception as e:
            logger.info(f'Player {ws} disconnect from game with error {e}')
            self.unregister(ws)

    def update(self, ws: websocket.WebSocket) -> None:
        player = ws_to_player[ws]
        game = player.current_game
        if game != self.game:
            fail_connect(ws)
            return
        data = json.dumps([
            "RoomUpdate",
            game.make_current_game_state(player)
        ])
        logger.info(u'Sending message: {}'.format(data))
        spawn(self.send, ws, data)

    def update_all(self) -> None:
        for player in self.game.players:
            self.update(player_to_ws[player])

    def start_game(self) -> None:
        self.game.start_game()
        redis.publish(self.game.id, "UpdateAll")

    def select_card(self, ws: websocket.WebSocket, card_id: str) -> None:
        player = ws_to_player[ws]
        logger.debug(f'{player.id} select card {card_id}')
        game = self.game
        cur_player = game.get_cur_player()
        cur_phase = game.get_state()
        logger.debug(f'{cur_phase}, {cur_player.id}')
        if cur_phase == Game.GamePhase.INTERLUDE:
            return
        if cur_phase == Game.GamePhase.WAITING:
            return
        if cur_phase == Game.GamePhase.VICTORY:
            return
        if cur_phase == Game.GamePhase.GUESSING and player != cur_player:
            game.make_guess(player, card_id)
        if cur_phase == Game.GamePhase.MATCHING and player != cur_player:
            game.make_bet(player, card_id)
        if cur_phase == Game.GamePhase.STORYTELLING and player == cur_player:
            game.add_lead_card(card_id)

    def tell_story(self, ws: websocket.WebSocket, story: str) -> None:
        player = ws_to_player[ws]
        game = self.game
        cur_player = game.get_cur_player()
        cur_state = game.get_state()
        if cur_state != Game.GamePhase.STORYTELLING:
            return
        if cur_player != player:
            return
        logger.info(f"Player {player.name} is telling a story")
        game.start_turn(story)
        self.update_all()

    def end_turn(self, ws: websocket.WebSocket) -> None:
        player = ws_to_player[ws]
        game = self.game
        cur_player = game.get_cur_player()
        cur_state = game.get_state()
        logger.debug(f'end_turn from {ws}, status = {cur_state}')
        if cur_state != Game.GamePhase.GUESSING \
                and cur_state != Game.GamePhase.MATCHING:
            logger.debug(f'{player.id} try end turn for {cur_state}')
            return
        if cur_state == Game.GamePhase.GUESSING and player.id != cur_player:
            game.finish_turn(player)
            assert game.turn_ended[player]
            logger.debug(f'{player.id} end turn for {cur_state}, res = {game.all_turns_ended()}')
            if not game.all_turns_ended():
                for player in game.players:
                    logger.debug(f'{player.id} is {game.turn_ended[player]}')
            if game.all_turns_ended():
                logger.debug(f'{game.id} end round, showing results')
                game.valuate_guesses()
                redis.publish(game.id, "UpdateAll")
                gv_sleep(5)
                logger.debug(f'{game.id} start new round')
                game.end_turn()
                redis.publish(game.id, "UpdateAll")
                tmp = game.finished()
                if tmp is not None:
                    logger.debug(f'{game.id} game end')
                    game.end_game(tmp)
                    redis.publish(game.id, "UpdateAll")
                    gv_sleep(5)
                    logger.debug(f'{game.id} start new game')
                    game.start_game()
                    return
        if cur_state == Game.GamePhase.MATCHING and player != cur_player:
            game.finish_turn(player)
            logger.debug(f'{player.id} is {game.turn_ended[player]} for matching')
            if game.all_turns_ended():
                game.place_cards()
                redis.publish(game.id, "UpdateAll")
        self.update(ws)

    def run(self):
        """Listens for new messages in Redis, and sends them to clients."""
        for data in self.__iter_data():
            if data == "UpdateAll":
                self.update_all()
            else:
                for client in self.clients:
                    spawn(self.send(client, data))

    def start(self):
        """Maintains Redis subscription in the background."""
        spawn(self.run)


def create_room(ws):
    player = ws_to_player[ws]
    if player.current_game is not None:
        fail_connect(ws)
        return
    game_backend = GameBackend()
    game = game_backend.game
    main_lobby.backends[game.id] = game_backend
    try:
        join_room(ws, game)
    except Exception as error:
        logger.exception(f"Player can't join to game. {error}")


def leave_room(ws: websocket.WebSocket) -> None:
    player = ws_to_player[ws]
    assert player.current_game is not None
    game_backend = GameBackend.backend[ws]
    logger.debug(f'{player.id} try leave from {game_backend.game.id}')
    game_backend.unregister(ws)
    assert player.current_game is None
    if not game_backend:
        del game_backend
    assert player in main_lobby.clients

    main_lobby.register(ws)


def join_room(ws, game):
    logger.debug(f'{ws} join to {game.id}')
    main_lobby.unregister(ws)
    game.add_player(ws_to_player[ws])
    ws_to_player[ws].current_game = game
    game_backend = main_lobby.backends[game.id]
    GameBackend.backend[ws] = game_backend
    game_backend.register(ws)
    data = json.dumps(['RoomConnect', str(game.id), game.make_current_game_state(ws_to_player[ws])])
    redis.publish(game.id, data)


def game_by_ws(ws: websocket.WebSocket) -> Optional[GameBackend]:
    return GameBackend.backend.get(ws, None)


def fail_connect(user):
    user.send('"FailConnect"')


def route_message(ws: websocket.WebSocket, message: Any):
    print(message)
    if type(message) not in [str, list]:
        logger.info(f"Unexpected type of message: {message}")
        return
    if isinstance(message, str):
        message = [message]

    if message[0] == "CreateRoom":
        Lobby.process_message(ws, message)
    elif message[0] == "JoinRoom":
        Lobby.process_message(ws, message)
    else:
        game_backend = game_by_ws(ws)
        if game_backend is None:
            logger.warning(f"Unexpected message from client: {message}")
            return

        if message[0] in ["LeaveRoom", "SelectCard", "TellStory", "EndTurn"]:
            game_backend.process_message(ws, message)
        else:
            logger.warning(f"Unexpected message from client: {message}")


@sockets.route("/socket")
def socket(ws):
    logger.debug(f'New user {ws}')
    main_lobby.register(ws)
    player = Player("noname")
    ws_to_player[ws] = player
    player_to_ws[player] = ws

    while not ws.closed:
        gv_sleep(0.1)
        message = ws.receive()
        if message:
            route_message(ws, json.loads(message))
        else:
            logger.debug(f'{ws} leave from site')
            main_lobby.unregister(ws)


@app.route('/')
def index():
    return redirect(url_for('static', filename='index.html'))


# Constants
REDIS_CHAN = 'Secret?!'
# Create logger
logger = logging.getLogger('app')
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('app.log')
file_handler.setFormatter(logging.Formatter(
    '%(filename)s[LINE:%(lineno)-3s]# '
    '%(levelname)-8s [%(asctime)s]  %(message)s')
)
logger.addHandler(file_handler)
# Create Lobby and global dicts
main_lobby = Lobby()
ws_to_player: Dict[websocket.WebSocket, Player] = {}  # web_socket -> Player
player_to_ws: Dict[Player, websocket.WebSocket] = {}  # player_id -> web_socket
# main_lobby.start()
server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
server.serve_forever()

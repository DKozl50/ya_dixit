from mechanics import Player, Game, Card, Pack
from typing import Any, Dict, Optional, Union
from flask import Flask, redirect, url_for
from flask_sockets import Sockets
from gevent import pywsgi, spawn, sleep as gv_sleep
from geventwebsocket.handler import WebSocketHandler
from geventwebsocket import websocket
import os
import json
import time
import redis
from redis.client import Redis
import logging

app = Flask(__name__, static_folder='static')
sockets = Sockets(app)
redis = redis.from_url(url='redis://localhost:6379')


class Lobby(object):
    """Interface for registering and updating WebSocket clients."""
    def __init__(self):
        self.games = list()
        self.clients = list()
        self.pubsub = redis.pubsub()
        self.pubsub.subscribe(REDIS_CHAN)

    def __iter_data(self):
        message: object
        for message in self.pubsub.listen():
            print(type(message))
            print(message)
            data = message.get('data')
            if message['type'] == 'message':
                logger.info(u'Sending message: {}'.format(data))
                yield data

    def add_game(self, game_id):
        self.games.append(game_id)

    def register(self, client):
        """Register a WebSocket connection for Redis updates."""
        self.clients.append(client)

    def unregister(self, client):
        """Unregister a WebSocket connection"""
        self.clients.remove(client)

    def send(self, client, data):
        """Send given data to the registered client.
        Automatically discards invalid connections."""
        try:
            client.send(data)
        except Exception:
            logger.info(f'Player {client} disconnect from lobby')
            self.unregister(client)

    def run(self):
        """Listens for new messages in Redis, and sends them to clients."""
        for data in self.__iter_data():
            for client in self.clients:
                spawn(self.send, client, data)

    def start(self):
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

    def __iter_data(self):
        for message in self.pubsub.listen():
            data = message.get('data')
            if message['type'] == 'message':
                logger.info(u'Sending message: {}'.format(data))
                yield data

    def process_message(self, player: Player, message: Any):
        if message[0] == "LeaveRoom":
            pass
        elif message[0] == "SelectCard":
            pass
        elif message[0] == "TellStory":
            pass
        elif message[0] == "EndTurn":
            pass


    def register(self, client):
        """Register a WebSocket connection for Redis updates."""
        self.clients.append(client)

    def unregister(self, client):
        """Unregister a WebSocket connection"""
        self.clients.remove(client)

    def send(self, client, data):
        """Send given data to the registered client.
        Automatically discards invalid connections."""
        try:
            client.send(data)
        except Exception:
            logger.info(f'Player {client} disconnect from game')
            self.unregister(client)

    def run(self):
        """Listens for new messages in Redis, and sends them to clients."""
        for data in self.__iter_data():
            for client in self.clients:
                spawn(self.send, client, data)

    def start(self):
        """Maintains Redis subscription in the background."""
        spawn(self.run)


def CreateRoom(user):
    main_lobby.unregister(user)
    player = ws_to_player[user]
    game = Game()
    main_lobby.add_game(game.id)
    game.add_player(player.id)
    ws_to_player[user].add_game_to_archive(game.id)
    RoomConnect(user, game.id)


def JoinRoom(user, game_id):
    try:
        main_lobby.unregister(user)
        game = Game.get_game(game_id)
        game.add_player(ws_to_player[user].id)
        ws_to_player[user].add_game_to_archive(game_id)
        RoomConnect(user, game_id)
    except Exception as error:
        logger.exception(f"Player can't join to game. {error}")
        FailConnect(user)


def leave_room(ws: websocket.WebSocket) -> None:
    player = ws_to_player[ws]
    game = player.current_game
    game.remove_player(player)
    if len(game.players) == 0:
        GameBackend.delete_game(game)
    main_lobby.register(ws)


def SelectCard(user, card_id):
    player = ws_to_player[user]
    game = Game.get_game(player.get_cur_game())
    cur_player = game.get_cur_player()
    cur_state = game.get_state()
    if cur_state == Game.GamePhase.INTERLUDE:
        return
    if cur_state == Game.GamePhase.WAITING:
        return
    if cur_state == Game.GamePhase.VICTORY:
        return
    if cur_state == Game.GamePhase.GUESSING and player.id != cur_player:
        game.make_guess(player.id, card_id)
    if cur_state == Game.GamePhase.MATCHING and player.id != cur_player:
        game.make_bet(player.id, card_id)
    if cur_state == Game.GamePhase.STORYTELLING and player.id == cur_player:
        game.add_lead_card(card_id)
    RoomUpdate(user)


def TellStory(user, story):
    player = ws_to_player[user]
    game = Game.get_game(player.get_cur_game())
    cur_player = game.get_cur_player()
    cur_state = game.get_state()
    if cur_state != Game.GamePhase.STORYTELLING:
        return
    if cur_player != player.id:
        return
    game.start_turn(story)
    RoomUpdate(user)


def EndTurn(user):
    player = ws_to_player[user]
    game = Game.get_game(player.get_cur_game())
    cur_player = game.get_cur_player()
    cur_state = game.get_state()
    if cur_state != Game.GamePhase.GUESSING and cur_state != Game.GamePhase.MATCHING:
        return
    if cur_state == Game.GamePhase.GUESSING and player.id != cur_player:
        game.finish_turn(player)
        if game.all_turns_ended():
            game.valuate_guesses()
            RoomUpdateAll(user)
            game.end_turn()
            time.sleep(10)
            tmp = game.finished()
            if tmp is not None:
                game.end_game(tmp)
                RoomUpdateAll(user)
                time.sleep(10)
                game.start_game()
                return
    if cur_state == Game.GamePhase.MATCHING and player.id != cur_player:
        game.finish_turn(player)
        if game.all_turns_ended():
            game.place_cards()
            RoomUpdateAll(user)
    RoomUpdate(user)


def RoomUpdateAll(user):
    player = ws_to_player[user]
    game = Game.get_game(player.get_cur_game())
    for pl in game.players:
        RoomUpdate(id_to_ws[pl])


def RoomConnect(user, game_id):
    mas = []
    mas.append('RoomConnect')
    mas.append(str(game_id))
    game = Game.get_game(game_id)
    mas.append(game.make_current_game_state(ws_to_player[user].id))
    user.send(json.dumps(mas))


def game_by_ws(ws: websocket.WebSocket) -> Optional[GameBackend]:
    return GameBackend.backend.get(ws)

def RoomUpdate(user):
    mas = []
    player = ws_to_player[user]
    game = Game.get_game(player.get_cur_game())
    mas.append('RoomUpdate')
    mas.append(game.make_current_game_state(ws_to_player[user].id))
    user.send(json.dumps(mas))


def FailConnect(user):
    user.send('"FailConnect"')


def route_message(ws: websocket.WebSocket, message: Any):
    if type(message) not in [str, list]:
        logger.info(f"Unexpected type of message: {message}")
        return 

    if type(message) == str:
        message = [message]

    if message[0] == "CreateRoom":
        main_lobby.process_message(ws, message)
    elif message[0] == "JoinRoom":
        main_lobby.process_message(ws, message)
    else:
        game_backend = game_by_ws(ws)
        if game_backend is None:
            logger.info(f"Unexpected message from client: {message}")
            return 

        if  message[0] in ["LeaveRoom", "SelectCard", "TellStory", "EndTurn"]:
            game_backend.process_message(ws_to_player[ws], message)
        else:
            logger.info(f"Unexpected message from client: {message}")


@sockets.route("/socket")
def socket(ws):
    main_lobby.register(ws)
    e2
    player = Player("noname")
    ws_to_player[ws] = player
    id_to_ws[player.id] = ws

    while not ws.closed:
        gv_sleep(0.1)
        message = ws.receive()
        if message:
            # processing requests from the client
            redis.publish(REDIS_CHAN, message)
            ProcessMessage(ws, json.loads(message))
        else:
            main_lobby.unregister(ws)


@app.route('/')
def index():
    return redirect(url_for('static', filename='index.html'))


if __name__ == '__main__':
    """Constants"""
    REDIS_CHAN = 'Secret?!'
    """Create logger"""
    logger = logging.getLogger('app')
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler('app.log')
    file_handler.setFormatter(logging.Formatter('%(filename)s[LINE:%(lineno)-3s]# %(levelname)-8s [%(asctime)s]  %(message)s'))
    logger.addHandler(file_handler)
    """Create Lobby and global dicts"""
    main_lobby = Lobby()
    main_lobby.run()

    ws_to_player: Dict[websocket.WebSocket, Player] = {}  # web_socket -> Player
    id_to_ws: Dict[int, websocket.WebSocket] = {}  # player_id -> web_socket
    """Start server"""
    server = pywsgi.WSGIServer(('', int(os.environ.get('PORT', 5000))), app, handler_class=WebSocketHandler)
    server.serve_forever()

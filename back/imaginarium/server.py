from mechanics import Player, Game, Card, Pack
from flask import Flask, redirect, url_for
from flask_sockets import Sockets
from gevent import pywsgi, spawn, sleep as gv_sleep
from geventwebsocket.handler import WebSocketHandler
import os
import redis
import logging

app = Flask(__name__, static_folder='static')
sockets = Sockets(app)


class Lobby(object):
    """Interface for registering and updating WebSocket clients."""

    def __init__(self):
        self.games = list()
        self.clients = list()
        self.pubsub = redis.pubsub()
        self.pubsub.subscribe(REDIS_CHAN)

    def __iter_data(self):
        for message in self.pubsub.listen():
            data = message.get('data')
            if message['type'] == 'message':
                app.logger.info(u'Sending message: {}'.format(data))
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

    def __init__(self):
        self.game = Game()
        self.clients = list()
        self.pubsub = redis.pubsub()
        self.pubsub.subscribe(self.game.id)

    def __iter_data(self):
        for message in self.pubsub.listen():
            data = message.get('data')
            if message['type'] == 'message':
                app.logger.info(u'Sending message: {}'.format(data))
                yield data

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


def CreateGame(user):
    main_lobby.unregister(user)
    player = ws_to_player[user]
    game = Game()
    main_lobby.add_game(game.id)
    game.add_player(player.id)


def JoinGame(user, game_id):
    try:
        main_lobby.unregister(user)
        game = Game.get_game(game_id)
        game.add_player(ws_to_player[user].id)
    except Exception as error:
        logger.exception(f"Player can't join to game. {error}")
        FailConnect(user)


def FailConnect(user):
    user.send('Fail Connect')


def ProcessMessage(ws, message):
    if message == "CreateGame":
        CreateGame(ws)
    elif message[0] == "JoinGame":
        JoinGame(ws, message[1])
    elif message == "to be continued...":
        pass


@sockets.route('/socket')
def socket(ws):
    player = Player()
    ws_to_player[ws] = player
    id_to_ws[player.id] = ws
    main_lobby.register(ws)
    while not ws.closed:
        gv_sleep(0.1)
        message = ws.receive()
        if message:
            # processing requests from the client
            redis.publish(REDIS_CHAN, message)
            ProcessMessage(ws, message)
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
    ws_to_player = {}  # web_socket -> Player
    id_to_ws = {}  # player_id -> web_socket
    """Start server"""
    server = pywsgi.WSGIServer(('', int(os.environ.get('PORT', 5000))), app, handler_class=WebSocketHandler)
    server.serve_forever()

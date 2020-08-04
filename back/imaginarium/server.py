from mechanics import *
from flask import Flask, redirect, url_for
from flask_sockets import Sockets
from uuid import uuid1
import logging
import os
import redis
import gevent
import json

app = Flask(__name__, static_folder='static')
sockets = Sockets(app)


class Lobby(object):
    """Interface for registering and updating WebSocket clients."""
    def __init__(self):
        self.games = list()
        self.clients = list()
        self.pubsub = redis.pubsub()
        self.pubsub.subscribe(..)

    def __iter_data(self):
        for message in self.pubsub.listen():
            data = message.get('data')
            if message['type'] == 'message':
                app.logger.info(u'Sending message: {}'.format(data))
                yield data

    def add_game(game_id):
        games.append(game_id)

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
            self.unregister(client)

    def run(self):
        """Listens for new messages in Redis, and sends them to clients."""
        for data in self.__iter_data():
            for client in self.clients:
                gevent.spawn(self.send, client, data)

    def start(self):
        """Maintains Redis subscription in the background."""
        gevent.spawn(self.run)


class GameBackend(object):
    """Interface for registering and updating WebSocket clients."""

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
            self.unregister(client)

    def run(self):
        """Listens for new messages in Redis, and sends them to clients."""
        for data in self.__iter_data():
            for client in self.clients:
                gevent.spawn(self.send, client, data)

    def start(self):
        """Maintains Redis subscription in the background."""
        gevent.spawn(self.run)


logging.basicConfig()

lb = Lobby()
USERS = {}
WEB = {}

def CreateGame(user):
    lb.unregister(user)
    player = USERS[user]
    game = Game()
    lb.add_game(game.id)
    game.add_player(player.id)

def JoinGame(user, game_id):
    try:
        lb.unregister(user)
        game = Game.get_game(game_id)
    except Exception:
        PosholNahui(user)
    game.add_player(Users[user].id)

def PosholNahui(user):
    # PasskudaMat'TvouANuIdiSudaGovnoSobach'e
    user.send('Fail Connect')


def ProcessMessage(ws, message):
    if message == "CreateGame":
        CreateGame(ws)
    elif message[0] == "JoinGame":
        JoinGame(ws, message[1])
    elif message == "Durka":
        print("SASHA loh!1!")

@sockets.route('/socket')
def socket(ws):
    player = Player()
    USERS[ws] = player
    WEB[player.id] = ws
    lb.register(ws)
    while not ws.closed:
        gevent.sleep(0.1)
        message = ws.receive()
        if message:
            # processing requests from the client
            redis.publish(REDIS_CHAN, message)
            ProcossMessage(ws, message)
        else:
            lb.unregister(ws)


@app.route('/')
def index():
    return redirect(url_for('static', filename='index.html'))


if __name__ == '__main__':
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(
        ('', int(os.environ.get('PORT', 5000))), app, handler_class=WebSocketHandler
    )
    server.serve_forever()

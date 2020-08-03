from mechanics import *
from flask import Flask, redirect, url_for
from flask_sockets import Sockets
import logging
import os
import json

app = Flask(__name__, static_folder='static')
sockets = Sockets(app)


logging.basicConfig()

USERS = {}
WEB = {}


def register(websocket):
    player = Player()
    USERS[websocket] = player
    WEB[player.id] = websocket


def unregister(websocket):
    player = USERS[websocket]
    USERS.pop(websocket)
    WEB.pop(player.id)


mask = {'X': 'Cross', 'O': 'Nought'}


@sockets.route('/socket')
def tic_tac_toe_socket(ws):
    print(ws)
    register(ws)
    while not ws.closed:
        message = ws.receive()
        if message is None:
            break
        print(message)
        data = json.loads(message)
        print(data)
        if data == "CreateRoom":
            create_game(USERS[ws].id)
            game = TicTacToe.get_game(USERS[ws].state)
            answer = ["RoomConnect", f'{USERS[ws].state}', {"Progress": f'{mask[game.move_order]}Turn', "Field": game.field_to_front(),
                                                            "Side": mask[game.player_side(USERS[ws].id)]}]
            ws.send(json.dumps(answer))
        elif data[0] == "JoinRoom":
            try:
                join_game(USERS[ws].id, data[1])
                game = TicTacToe.get_game(USERS[ws].state)
                answer = ["RoomConnect", f'{USERS[ws].state}', {"Progress": f'{mask[game.move_order]}Turn', "Field": game.field_to_front(),
                                                                "Side": mask[game.player_side(USERS[ws].id)]}]
                ws.send(json.dumps(answer))
            except AttributeError:
                ws.send(json.dumps("FailConnect"))
        elif data == "LeaveRoom":
            leave_game(USERS[ws].id)
        elif data[0] == "MakeMove":
            move(USERS[ws].id, data[1])
            game = TicTacToe.get_game(USERS[ws].state)
            players = [game.player_x, game.player_o]
            for player_id in players:
                answer = ["RoomUpdate", {"Progress": f'{mask[game.move_order]}Turn', "Field": game.field_to_front(),
                                         "Side": mask[game.player_side(player_id)]}]
                WEB[player_id].send(json.dumps(answer))
        print('Got message')
    unregister(ws)


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

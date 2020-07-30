from tic_tac_toe.mechanics import *
import asyncio
import json
import logging
import websockets

logging.basicConfig()

STATE = {"value": 0}

USERS = {}
WEB = {}

def state_event():
    return json.dumps({"type": "state", **STATE})


def users_event():
    return json.dumps({"type": "users", "count": len(USERS)})


async def notify_state():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = state_event()
        await asyncio.wait([user.send(message) for user in USERS])


async def notify_users():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = users_event()
        await asyncio.wait([user.send(message) for user in USERS])


async def register(websocket):
    player = Player()
    USERS[websocket] = player
    WEB[player.id] = websocket
    await notify_users()


async def unregister(websocket):
    player = USERS[websocket]
    USERS.pop(websocket)
    WEB.pop(player.id)
    await notify_users()


mask = {'X': 'Cross', 'O': 'Nought'}


async def counter(websocket, path):
    # register(websocket) sends user_event() to websocket
    await register(websocket)
    try:
        async for message in websocket:
            data = json.loads(message)
            if data == "CreateRoom":
                create_game(USERS[websocket].id)
                game = TicTacToe.get_game(USERS[websocket].state)
                answer = ["RoomConnect", f'{USERS[websocket].state}', {"Progress": f'{mask[game.move_order]}Turn', "Field": game.field_to_front(),
                                                                       "Side": mask[game.player_side(USERS[websocket].id)]}]
                await websocket.send(json.dumps(answer))
            elif data[0] == "JoinRoom":
                try:
                    join_game(USERS[websocket].id, data[1])
                    game = TicTacToe.get_game(USERS[websocket].state)
                    answer = ["RoomConnect", f'{USERS[websocket].state}', {"Progress": f'{mask[game.move_order]}Turn', "Field": game.field_to_front(),
                                                                           "Side": mask[game.player_side(USERS[websocket].id)]}]
                    await websocket.send(json.dumps(answer))
                except AttributeError:
                    await websocket.send(json.dumps("FailConnect"))
            elif data == "LeaveRoom":
                leave_game(USERS[websocket].id)
            elif data[0] == "MakeMove":
                move(USERS[websocket].id, data[1])
                game = TicTacToe.get_game(USERS[websocket].state)
                players = [game.player_x, game.player_o]
                for player_id in players:
                    answer = ["RoomUpdate", {"Progress": f'{mask[game.move_order]}Turn', "Field": game.field_to_front(),
                                             "Side": mask[game.player_side(player_id)]}]
                    await WEB[player_id].send(json.dumps(answer))
            print('Got message')
    finally:
        print('Unregistered')
        await unregister(websocket)


start_server = websockets.serve(counter, "localhost", 50)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

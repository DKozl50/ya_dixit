from server import*

def main():
    while True:
        try:
            print('1) create_game\n2) join_game\n3) leave_game\n4) move\n5) new_player')
            request, *args = input().split()
            args = list(map(int, args))
            if request == '1':
                # args {web_socket}
                CreateGame(*args)
            elif request == '2':
                # args {web_socket, game_id}
                JoinGame(*args)
            elif request == '3':
                # args {web_socket}
                PosholNahui(*args)
            elif request == '4':
                pass
            elif request == '5':
                player = Player()
                USERS[ws] = player
                WEB[player.id] = ws
                lb.register(ws)
                print(f'Создали нового игрока {player.id}')
        except Exception as error:
            print(error)

if __name__ == '__main__':
    main()

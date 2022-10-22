import socket
import time
from functools import partial
from threading import Thread

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    PORT = input("Enter The PORT: ")
    s.bind(('localhost', int(PORT)))
    s.listen(0)

    users = []

    CONNECTED = 'connected'.encode('utf-8')
    UNLOCK = 'unlock'.encode('utf-8')


    class GameSession:
        def __init__(self, session):
            session = session
            def check_answers(cross, circle):
                win_combo = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]]
                winner = -1
                for i in win_combo:
                    if i[0] in cross and i[1] in cross and i[2] in cross:
                        winner = 0
                    elif i[0] in circle and i[1] in circle and i[2] in circle:
                        winner = 1
                if winner == -1:
                    if len(cross) + len(circle) == 9:
                        winner = 2
                return winner

            def sending(connection, cross, circle, positions, winner):
                msg = str([cross, circle, positions, winner]).encode('utf-8')
                connection[1][0].send(msg)
                connection[2][0].send(msg)

            global CONNECTED, UNLOCK, LOCK
            first_pl = session[1]
            second_pl = session[2]

            used_cross_figure = []
            used_circle_figure = []
            cross = 0
            circle = 0
            positions = [0 for _ in range(9)]
            winner = -1

            first_pl[0].send(CONNECTED)
            second_pl[0].send(CONNECTED)
            time.sleep(0.5)
            sending(session, cross, circle, positions, winner)
            time.sleep(0.5)
            while True:
                rw = True
                time.sleep(0.5)
                first_pl[0].send(UNLOCK)

                first_ans = int(first_pl[0].recv(1024).decode('utf-8'))
                used_cross_figure.append(first_ans)
                positions[first_ans] = 1

                winner = check_answers(used_cross_figure, used_circle_figure)
                if winner == 0 and rw:
                    cross += 1
                    rw = False
                    positions = [0 for _ in range(9)]
                    used_cross_figure = []
                    used_circle_figure = []

                elif winner == 1 and rw:
                    circle += 1
                    rw = False
                    positions = [0 for _ in range(9)]
                    used_cross_figure = []
                    used_circle_figure = []

                elif winner == 2:
                    rw = False
                    positions = [0 for _ in range(9)]
                    used_cross_figure = []
                    used_circle_figure = []

                sending(session, cross, circle, positions, winner)
                if not rw:
                    winner = -1
                    continue

                time.sleep(0.5)
                second_pl[0].send(UNLOCK)

                second_ans = int(second_pl[0].recv(1024).decode('utf-8'))
                used_circle_figure.append(second_ans)
                positions[second_ans] = 2

                winner = check_answers(used_cross_figure, used_circle_figure)
                if winner == 0 and rw:
                    cross += 1
                    positions = [0 for _ in range(9)]
                    used_cross_figure = []
                    used_circle_figure = []

                elif winner == 1 and rw:
                    circle += 1
                    positions = [0 for _ in range(9)]
                    used_cross_figure = []
                    used_circle_figure = []

                elif winner == 2:
                    positions = [0 for _ in range(9)]
                    used_cross_figure = []
                    used_circle_figure = []

                sending(session, cross, circle, positions, winner)
                if not rw:
                    winner = -1
                    continue

                time.sleep(0.5)

    while True:
           connection, address = s.accept()
           ans = connection.recv(1024).decode('utf-8')
           if ans == 'NS':
               users.append([len(users), (connection, address)])
               connection.send(str(len(users) - 1).encode('utf-8'))
           else:
               id = int(ans)
               if id < len(users):
                   users[id].append((connection, address))
                   connection.send(f"{len(users) - 1}".encode('utf-8'))
           for i in users:
               if len(i) == 3:
                   th = Thread(target=partial(GameSession, i), daemon=True)
                   th.start()
except:
    s.close()

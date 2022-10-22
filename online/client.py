import json
import socket
import sys
from functools import partial

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *


class Setting(QWidget):
    new_session = False

    def __init__(self):
        super().__init__()

        self.windows = []
        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.ip_address = QLineEdit()
        self.ip_address.setPlaceholderText("Enter IP:PORT")

        self.btn_new_ses = QPushButton("Create New Session")
        self.btn_new_ses.clicked.connect(self.new_session_func)
        self.btn_connect = QPushButton("Connect Session")
        self.btn_connect.clicked.connect(self.connect_func)

        self.grid.addWidget(self.ip_address, 0, 0, 1, 0)
        self.grid.addWidget(self.btn_new_ses, 1, 0)
        self.grid.addWidget(self.btn_connect, 1, 1)

    def new_session_func(self):
        self.new_session = True
        self.get_ip_func()
        game = GameSession()
        self.windows.append(game)
        game.show()
        self.destroy()

    def connect_func(self):
        self.get_ip_func()
        for i in range(self.grid.count()):
            self.grid.itemAt(i).widget().deleteLater()

        self.get_id = QLineEdit()
        self.get_id.setPlaceholderText('Enter game\'s ID')
        btn = QPushButton('Connect')
        btn.clicked.connect(self.get_id_func)

        self.grid.addWidget(self.get_id, 0, 0)
        self.grid.addWidget(btn, 1, 0)

    def get_ip_func(self):
        self.address = self.ip_address.text().split(':')

    def get_id_func(self):
        try:
            self.id = int(self.get_id.text())
            self.hide()
            game = GameSession()
            self.windows.append(game)
            game.show()
            self.destroy()
        except ValueError:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setText("Enter Number Only!!!")
            msg.exec()


class GameSession(QWidget):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __init__(self):
        super().__init__()
        try:
            self.sock.connect((settings.address[0], int(settings.address[1])))
            if settings.new_session:
                self.sock.send('NS'.encode('utf-8'))
                your_id = QLabel(f"Your ID:{self.sock.recv(1024).decode('utf-8')}")
                self.figure = True
            else:
                self.sock.send(str(settings.id).encode('utf-8'))
                your_id = QLabel(f"Your ID:{self.sock.recv(1024).decode('utf-8')}")
                self.figure = False

        except:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setText('Try Reconnect')
            msg.exec()
            self.close()

        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.cross = 0
        self.circle = 0
        self.status = QLabel('Wait The Player')

        self.grid.addWidget(your_id, 0, 0)
        self.grid.addWidget(self.status, 0, 1)

        self.array_of_buttons = [QPushButton() for _ in range(9)]
        array_of_positions = [(i, j) for i in range(2, 5) for j in range(0, 3)]

        self.lbl_cross = QPushButton()
        self.lbl_cross.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))
        self.lbl_cross.setIcon(QIcon("../cross.png"))
        self.lbl_cross.setText(f':{self.cross}')
        self.grid.addWidget(self.lbl_cross, 1, 0)

        self.lbl_circle = QPushButton()
        self.lbl_circle.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))
        self.lbl_circle.setIcon(QIcon("../circle.png"))
        self.lbl_circle.setText(f':{self.circle}')
        self.grid.addWidget(self.lbl_circle, 1, 2)

        self.grid.addWidget(QLabel(' ' * 25), 0, 2)

        for i in range(0, 9):
            self.array_of_buttons[i].setIcon(QIcon('./empty.png'))
            self.array_of_buttons[i].setDisabled(True)
            self.array_of_buttons[i].setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))
            self.array_of_buttons[i].clicked.connect(partial(self.evt, i))
            self.grid.addWidget(self.array_of_buttons[i], *array_of_positions[i])

        self.my_thread = Thread()
        self.my_thread.signal_of_do.connect(self.func_for_do)
        self.my_thread.signal_of_position.connect(self.func_for_position)
        self.my_thread.start()

    def func_for_do(self, task):
        if task == 'connected':
            self.status.setText('Connected!')
        elif task == 'unlock':
            for i in range(0, 9):
                self.array_of_buttons[i].setDisabled(False)
        elif 'cross' in task:
            self.lbl_cross.setText(task.split(' ')[1])
        elif 'circle' in task:
            self.lbl_circle.setText(task.split(' ')[1])
        elif 'winner' in task:
            winner = int(task.split(' ')[1])
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Information)
            if winner == 0:
                msg.setText('Win Cross!')
                msg.exec()
            elif winner == 1:
                msg.setText('Win Circle!')
                msg.exec()
            elif winner == 2:
                msg.setText('Draw!')
                msg.exec()

    def func_for_position(self, positions):
        self.positions = positions
        for i in range(9):
            if positions[i] == 1:
                self.array_of_buttons[i].setIcon(QIcon("../cross.png"))
            elif positions[i] == 2:
                self.array_of_buttons[i].setIcon(QIcon("../circle.png"))
            else:
                self.array_of_buttons[i].setIcon(QIcon("../empty.png"))

    def evt(self, i):
        if self.positions[i] == 0:
            try:
                self.sock.send(str(i).encode('utf-8'))
            except:
                self.sock.close()
                app.quit()
            for i in range(0, 9):
                self.array_of_buttons[i].setDisabled(True)


class Thread(QThread):
    signal_of_position = pyqtSignal(list)
    signal_of_do = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def run(self):
        while True:
            try:
                ans = GameSession.sock.recv(1024).decode('utf-8')
            except:
                GameSession.sock.close()
                app.quit()
            if ans:
                if ans in 'connected unlock lock':
                    self.signal_of_do.emit(ans)
                else:
                    self.msleep(200)
                    ans = json.loads(ans)
                    self.signal_of_do.emit(f'cross {ans[0]}')
                    self.signal_of_do.emit(f'circle {ans[1]}')
                    self.signal_of_position.emit(ans[2])
                    self.signal_of_do.emit(f'winner {ans[3]}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    settings = Setting()
    settings.show()
    sys.exit(app.exec_())

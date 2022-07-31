import sys
from functools import partial

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import *


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(0, 0)
        self.setWindowTitle('Tic Tac Toe')
        grid = QGridLayout()
        self.setLayout(grid)

        self.figure = False
        self.used_circle_figure = []
        self.used_cross_figure = []

        self.win_combo = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]]

        self.array_of_buttons = [QPushButton() for _ in range(9)]
        array_of_positions = [(i, j) for i in range(1, 4) for j in range(0, 3)]

        self.cross = 0
        self.circle = 0
        self.play = True

        self.lbl_cross = QPushButton()
        self.lbl_cross.setMinimumWidth(40)
        self.lbl_cross.setMinimumHeight(40)
        self.lbl_cross.setIcon(QIcon("./cross.png"))
        self.lbl_cross.setText(f':{self.cross}')
        grid.addWidget(self.lbl_cross, 0, 0)

        self.lbl_circle = QPushButton()
        self.lbl_circle.setMinimumWidth(40)
        self.lbl_circle.setMinimumHeight(40)
        self.lbl_circle.setIcon(QIcon("./circle.png"))
        self.lbl_circle.setText(f':{self.circle}')
        grid.addWidget(self.lbl_circle, 0, 1)

        self.reset = QPushButton()
        self.reset.setMinimumWidth(40)
        self.reset.setMinimumHeight(40)
        self.reset.setIcon(QIcon("./reset.png"))
        grid.addWidget(self.reset, 0, 2)
        self.reset.clicked.connect(self.evt_reset)

        for i in range(0, 9):
            self.array_of_buttons[i].setIcon(QIcon('./empty.png'))
            self.array_of_buttons[i].setMinimumHeight(40)
            self.array_of_buttons[i].setMinimumWidth(40)
            self.array_of_buttons[i].clicked.connect(partial(self.evt, i))
            grid.addWidget(self.array_of_buttons[i], *array_of_positions[i])

    def evt_reset(self):
        self.play = True
        for i in self.array_of_buttons:
            i.setIcon(QIcon("./empty.png"))
        self.figure = False
        self.used_circle_figure = []
        self.used_cross_figure = []

    def evt(self, i):
        if self.play:
            if i not in self.used_cross_figure and i not in self.used_circle_figure:
                if self.figure:
                    self.array_of_buttons[i].setIcon(QIcon('./circle.png'))
                    self.figure = False
                    self.used_circle_figure.append(i)
                else:
                    self.array_of_buttons[i].setIcon(QIcon('./cross.png'))
                    self.figure = True
                    self.used_cross_figure.append(i)

            if len(self.used_cross_figure) + len(self.used_circle_figure) == 9:
                self.play = False
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Information)
                msg.setText("Draw!")
                msg.exec()

            for i in self.win_combo:
                if i[0] in self.used_circle_figure and i[1] in self.used_circle_figure and i[2] in self.used_circle_figure:
                    self.circle += 1
                    self.lbl_circle.setText(f":{self.circle}")
                    self.play = False
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Icon.Information)
                    msg.setText("Win Circle")
                    msg.exec()

                elif i[0] in self.used_cross_figure and i[1] in self.used_cross_figure and i[
                    2] in self.used_cross_figure:
                    self.cross += 1
                    self.lbl_cross.setText(f':{self.cross}')
                    self.play = False
                    msg = QMessageBox(self)
                    msg.setIcon(QMessageBox.Icon.Information)
                    msg.setText("Win Cross")
                    msg.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())

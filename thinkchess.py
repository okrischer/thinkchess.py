import sys

from chess_lib import Game
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import (
  QApplication,
  QMainWindow,
  QVBoxLayout,
  QLabel,
  QWidget,
)

class MainWindow(QMainWindow):
  def __init__(self):
    super().__init__()
    self.setWindowTitle("ThinkChess")

    self.game = Game()
    self.svg = "img/board.svg"
    self.board = QSvgWidget(self.svg)
    self.label = QLabel("Make yor move")

    self.from_square = None

    layout = QVBoxLayout()
    layout.addWidget(self.board)
    layout.addWidget(self.label)

    view = QWidget()
    view.setLayout(layout)

    self.setCentralWidget(view)

  def mousePressEvent(self, e):
    x = int(e.position().x() - 30)
    y = int(e.position().y() - 30)
    # clicked on the board?
    if x > 0 and x < 360 and y > 0 and y < 360 and self.game.running:
      files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
      file = files[x//45]
      ranks = [8, 7, 6, 5, 4, 3, 2, 1]
      rank = ranks[y//45]
      square = file + str(rank)
      # set squares for move
      if self.from_square is None:
        self.from_square = square
        self.game.show_square(square)
        self.board.load(self.svg)
      elif self.from_square == square:
        self.from_square = None
        self.game.show_board()
        self.board.load(self.svg)
      else:
        self.make_move(self.from_square + square)

  def make_move(self, move):
    lan = self.game.make_move(move)
    if lan is not None:
      self.board.load(self.svg)
      self.label.setText(f"{lan} {self.game.message}")
    else:
      self.label.setText(f"{move} is not a valid move")
      self.game.show_board()
      self.board.load(self.svg)
    self.from_square = None

app = QApplication(sys.argv)
window = MainWindow()
window.show()

app.exec()

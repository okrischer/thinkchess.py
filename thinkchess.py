import sys

from PySide6.QtGui import QCloseEvent

from chess_lib import Game
from PySide6.QtCore import QSize
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import (
  QApplication,
  QMainWindow,
  QVBoxLayout,
  QPushButton,
  QLabel,
  QWidget,
)

class MainWindow(QMainWindow):
  def __init__(self):
    super().__init__()
    self.setWindowTitle("ThinkChess")

    self.game = Game()
    self.svg = "img/board.svg"
    self.from_square = None
    self.board = QSvgWidget()
    self.board.setFixedSize(QSize(390, 390))
    self.board.load(self.svg)
    self.lastmove = QLabel("make your move")
    self.message = QLabel()
    self.new = QPushButton("new game")
    self.new.hide()
    self.new.clicked.connect(self.new_game)

    undo = QPushButton("undo move")
    undo.clicked.connect(self.undo_move)
    cm = QPushButton("computer move")
    cm.clicked.connect(self.computer_move)

    layout = QVBoxLayout()
    layout.addWidget(self.board)
    layout.addWidget(self.lastmove)
    layout.addWidget(undo)
    layout.addWidget(cm)
    layout.addWidget(self.message)
    layout.addWidget(self.new)

    view = QWidget()
    view.setLayout(layout)

    self.setCentralWidget(view)

  def new_game(self):
    self.game.engine.quit()
    self.game = Game()
    self.board.load(self.svg)
    self.new.hide()
    self.message.setText(self.game.message)
    self.lastmove.setText("make your move")

  def undo_move(self):
    self.new.hide()
    lan = self.game.undo_move()
    if lan is not None:
      self.board.load(self.svg)
      self.lastmove.setText(lan)
      self.message.setText(self.game.message)

  def make_move(self, move: str) -> None:
    lan = self.game.make_move(move)
    self.check_move(lan, f"illagal move: {move}")

  def computer_move(self):
    move = self.game.computer_move()
    self.check_move(move, "computer couldn't find a legal move")

  def check_move(self, move: str | None, message: str) -> None:
    if not self.game.running:
      self.new.show()
    if move is not None:
      self.lastmove.setText(move)
      self.message.setText(self.game.message)
    else:
      self.message.setText(message)
      self.game.show_board()
    self.board.load(self.svg)
    self.from_square = None

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


  def closeEvent(self, e):
    self.game.engine.quit()
    return super().closeEvent(e)

app = QApplication(sys.argv)
window = MainWindow()
window.show()

app.exec()

import sys

from chess_lib import Game
from gui import Dialog
from PySide6.QtCore import Qt, QSize
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import (
  QApplication,
  QGridLayout,
  QLabel,
  QLineEdit,
  QMainWindow,
  QPushButton,
  QVBoxLayout,
  QWidget,
)


class MainWindow(QMainWindow):
  def __init__(self):
    super().__init__()
    self.setWindowTitle("ThinkChess")
    self.fen = None
    self.position = None
    self.game = Game()
    self.svg = "img/board.svg"
    self.from_square = None
    self.board = QSvgWidget()
    self.board.setFixedSize(QSize(390, 390))
    self.board.load(self.svg)
    self.lastmove = QLabel()
    self.lastmove.setAlignment(Qt.AlignmentFlag.AlignHCenter)
    font = self.lastmove.font()
    font.setPointSize(16)
    font.setBold(True)
    self.lastmove.setFont(font)
    self.fen_edit = QLineEdit()
    self.fen_edit.setPlaceholderText("enter a FEN for a new board position")
    self.fen_edit.textEdited.connect(self.create_fen)
    self.message = QLabel("new game")
    self.restore = QPushButton("restore position")
    self.restore.setDisabled(True)
    self.restore.clicked.connect(self.restore_position)

    new = QPushButton("new game")
    new.clicked.connect(self.open_dialog)
    undo = QPushButton("undo move")
    undo.clicked.connect(self.undo_move)
    cm = QPushButton("computer move")
    cm.clicked.connect(self.computer_move)
    save = QPushButton("save position")
    save.clicked.connect(self.save_position)

    main = QGridLayout()
    main.addWidget(self.fen_edit, 0, 0)
    main.addWidget(new, 0, 1)
    main.addWidget(self.board, 1, 0)
    control = QVBoxLayout()
    control.addWidget(self.lastmove)
    control.addWidget(undo)
    control.addWidget(cm)
    control.addWidget(save)
    control.addWidget(self.restore)
    ctrl = QWidget()
    ctrl.setLayout(control)
    main.addWidget(ctrl, 1, 1)
    message = QVBoxLayout()
    message.addWidget(self.message)
    msg = QWidget()
    msg.setLayout(message)
    main.addWidget(msg, 2, 0)

    view = QWidget()
    view.setLayout(main)
    self.setCentralWidget(view)


  def open_dialog(self):
    new = Dialog("New Game", "Discard current game and start new game?")
    if new.exec():
      self.new_game()
  
  def create_fen(self, text):
    self.fen = text

  def new_game(self):
    if self.fen == "":
      self.fen = None
    if self.fen is None or self.game.is_valid(self.fen):
      self.game.engine.quit()
      self.game = Game(self.fen)
      self.restore.setDisabled(True)
      self.position = None
      self.board.load(self.svg)
      if self.fen is None:
        self.message.setText("new game")
      else:
        self.message.setText("new game from FEN")
      self.lastmove.clear()
      self.fen = None
      self.fen_edit.clear()
    else:
      self.message.setText("illegal FEN")

  def save_position(self):
    self.position = self.game.get_fen()
    self.restore.setDisabled(False)
    self.message.setText("saved position")

  def restore_position(self):
    if self.game.set_fen(self.position):
      self.board.load(self.svg)
      self.lastmove.clear()
      self.message.setText("restored position")
    else:
      self.message.setText("could not restore position")

  def undo_move(self):
    lan = self.game.undo_move()
    if lan is not None:
      self.board.load(self.svg)
      self.lastmove.setText(lan)
      self.message.setText(self.game.message)

  def make_move(self, move: str) -> None:
    lan = self.game.make_move(move)
    self.check_move(lan, f"illegal move: {move}")

  def computer_move(self):
    if self.game.running:
      move = self.game.computer_move()
      self.check_move(move, "computer couldn't find a valid move")

  def check_move(self, move: str | None, message: str) -> None:
    if move is None:
      self.message.setText(message)
      self.game.show_board()
    else:
      self.lastmove.setText(move)
      self.message.setText(self.game.message)
    self.board.load(self.svg)
    self.from_square = None

  def mousePressEvent(self, e):
    x = int(e.position().x() - 28)
    y = int(e.position().y() - 65)
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
    quit = Dialog("Quit ThinkChess", "Are you sure to quit the app?")
    if quit.exec():
      self.game.engine.quit()
      super().closeEvent(e)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()

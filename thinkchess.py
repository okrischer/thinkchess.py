import sys

from chess_lib import Game
from gui import Dialog
from PySide6.QtCore import Qt, QSize
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import (
  QApplication,
  QComboBox,
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
    self.player = True
    self.level = 0
    self.levelbox = QComboBox()
    self.levelbox.addItems(["Beginner", "Advanced", "Master", "Grandmaster"])
    self.levelbox.currentIndexChanged.connect(self.set_level)
    self.game = Game()
    self.fen = None
    self.position = None
    self.from_square = None
    self.svg = "tmp/board.svg"
    self.board = QSvgWidget()
    self.board.setFixedSize(QSize(390, 390))
    self.board.load(self.svg)
    self.lastmove = QLabel()
    self.lastmove.setAlignment(Qt.AlignmentFlag.AlignHCenter)
    font = self.lastmove.font()
    font.setPointSize(16)
    font.setBold(True)
    self.lastmove.setFont(font)
    self.eval = QLabel("0")
    font = self.eval.font()
    font.setPointSize(20)
    font.setBold(True)
    self.eval.setFont(font)
    self.eval.setAlignment(Qt.AlignmentFlag.AlignHCenter)
    self.ptt = QSvgWidget("img/kw.svg")
    self.ptt.setFixedSize(QSize(45, 45))
    self.fen_edit = QLineEdit()
    self.fen_edit.setPlaceholderText("enter a FEN for a new game")
    self.fen_edit.textEdited.connect(self.create_fen)
    self.message = QLabel("")
    self.undo = QPushButton("undo move")
    self.undo.setDisabled(True)
    self.undo.clicked.connect(self.undo_move)

    new = QPushButton("new game")
    new.clicked.connect(self.open_dialog)
    tb = QPushButton("turn board")
    tb.clicked.connect(self.turn_board)
    cm = QPushButton("computer move")
    cm.clicked.connect(self.computer_move)

    main = QGridLayout()
    main.addWidget(self.fen_edit, 0, 0)
    main.addWidget(new, 0, 1)
    main.addWidget(self.board, 1, 0)
    control = QVBoxLayout()
    control.addWidget(self.levelbox)
    control.addWidget(tb)
    turn = QGridLayout()
    turn.addWidget(self.ptt, 0, 0)
    trn = QWidget()
    trn.setLayout(turn)
    control.addWidget(trn)
    control.addWidget(self.lastmove)
    control.addWidget(self.eval)
    control.addWidget(self.undo)
    control.addWidget(cm)
    ctrl = QWidget()
    ctrl.setLayout(control)
    main.addWidget(ctrl, 1, 1)
    information = QVBoxLayout()
    information.addWidget(self.message)
    info = QWidget()
    info.setLayout(information)
    main.addWidget(info, 2, 0)

    view = QWidget()
    view.setLayout(main)
    self.setCentralWidget(view)


  def open_dialog(self):
    new = Dialog("New Game", "Discard current game and start new game?")
    if new.exec():
      self.new_game()
  
  def create_fen(self, text):
    self.fen = text

  def turn_board(self):
    self.player = not self.player
    self.game.set_player(self.player)
    self.board.load(self.svg)

  def set_level(self, i):
    match i:
      case 0:
        self.level = 0
      case 1:
        self.level = 4
      case 2:
        self.level = 8
      case 3:
        self.level = 14
    self.game.set_level(self.level)

  def switch_turn(self):
    if self.game.board.turn:
      self.ptt.load("img/kw.svg")
    else:
      self.ptt.load("img/kb.svg")

  def new_game(self):
    if self.fen == "":
      self.fen = None
    if self.fen is None or self.game.is_valid(self.fen):
      self.game.engine.quit()
      self.game = Game(self.player, self.fen, self.level)
      self.undo.setDisabled(True)
      self.position = None
      self.switch_turn()
      self.eval.setText(str(self.game.score))
      self.board.load(self.svg)
      self.lastmove.clear()
      self.message.clear()
      self.fen = None
      self.fen_edit.clear()
    else:
      self.message.setText("illegal FEN")

  def undo_move(self):
    lan = self.game.undo_move()
    if lan is not None:
      self.board.load(self.svg)
      self.lastmove.setText(lan)
      self.eval.setText(str(self.game.score))
      self.switch_turn()
      self.message.setText(self.game.message)
    else:
      self.undo.setDisabled(True)

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
      self.switch_turn()
      self.eval.setText(str(self.game.score))
      self.undo.setDisabled(False)
      self.message.setText(self.game.message)
    self.board.load(self.svg)
    self.from_square = None

  def mousePressEvent(self, e):
    x = int(e.position().x() - 28)
    y = int(e.position().y() - 65)
    # clicked on the board?
    if x > 0 and x < 360 and y > 0 and y < 360 and self.game.running:
      files = ['h', 'g', 'f', 'e', 'd', 'c', 'b', 'a']
      ranks = [1, 2, 3, 4, 5, 6, 7, 8]
      if self.player:
        files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        ranks = [8, 7, 6, 5, 4, 3, 2, 1]
      file = files[x//45]
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
    super().closeEvent(e)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()

import asyncio
import chess
import chess.svg
import chess.engine
from chess.engine import SimpleEngine, Limit, PovScore

class Game():
  def __init__(self,
               player: bool = True,
               fen: str | None = None,
               level: int | None = None) -> None:
    if fen is None:
      self.board = chess.Board()
    else:
      self.board = chess.Board(fen=fen)
    level = level if level is not None else 0
    self.engine = SimpleEngine.popen_uci("/opt/homebrew/bin/stockfish")
    self.engine.configure({"Skill Level": level})
    self.score = 0
    self.set_score()
    self.player = player
    self.running = True
    self.message = ""
    self.show_board()

  def set_player(self, player):
    self.player = player
    lastmove = None
    try:
      lastmove = self.board.peek()
    except IndexError:
      self.show_board()
    self.show_board(lastmove=lastmove)

  def set_level(self, level):
    self.engine.configure({"Skill Level": level})

  def show_board(self, lastmove=None, check=None, fill={}) -> None:
    with open('tmp/board.svg', 'w') as svg:
      svg.write(chess.svg.board(self.board,
                                orientation=self.player,
                                lastmove=lastmove,
                                check=check,
                                fill=fill))

  def show_square(self, square: str) -> None:
    sq = chess.parse_square(square)
    white_squares = [1,  3, 5, 7,
                     8, 10,12,14,
                     17,19,21,23,
                     24,26,28,30,
                     33,35,37,39,
                     40,42,44,46,
                     49,51,53,55,
                     56,58,60,62]
    color = "#cdd16a" if sq in white_squares else "#aaa23b"
    self.show_board(fill={sq: color})

  def is_valid(self, fen: str) -> bool:
    board = chess.Board(fen=None)
    try:
      board.set_fen(fen)
    except ValueError:
      return False
    return True

  def get_fen(self) -> str:
    return self.board.fen()
  
  def set_fen(self, fen: str | None) -> bool:
    if fen is None: return False
    try:
      self.board.set_fen(fen)
    except ValueError:
      return False
    self.running = True
    self.message = ""
    self.set_score()
    self.show_board()
    return True

  def make_move(self, uci: str) -> str | None:
    move = chess.Move.from_uci(uci)
    try:
      move = self.board.find_move(move.from_square, move.to_square)
    except chess.IllegalMoveError:
      return None
    lan = self.board.lan(move)
    self.board.push(move)
    self.check_board()
    return lan
  
  def computer_move(self) -> str | None:
    result = self.engine.play(self.board, Limit(depth=20))
    if result.move is not None:
      lan = self.board.lan(result.move)
      self.board.push(result.move)
      self.check_board()
      return lan
    else:
      return None

  def undo_move(self) -> str | None:
    try:
      self.board.pop()
    except IndexError:
      return None
    self.running = True
    self.message = ""
    self.check_board()
    try:
      lastmove = self.board.peek()
    except IndexError:
      return ""
    from_square = chess.SQUARE_NAMES[lastmove.from_square]
    to_square = chess.SQUARE_NAMES[lastmove.to_square]
    return f"{from_square}-{to_square}"

  def check_board(self) -> None:
    if self.board.is_checkmate():
      self.running = False
      self.message = f"Checkmate! {"Black" if self.board.turn else "White"} wins."
    elif self.board.is_stalemate():
      self.running = False
      self.message = f"Stalemate! It's a draw."
    self.set_score()
    try:
      lastmove = self.board.peek()
    except IndexError:
      self.show_board()
      return
    check = chess.SQUARES[lastmove.to_square]
    checkers = self.board.checkers()
    if check in checkers:
      self.show_board(lastmove=lastmove, check=check)
    elif bool(checkers):
      self.show_board(lastmove=lastmove, check=checkers.pop())
    else:
      self.show_board(lastmove=lastmove)
  
  def set_score(self) -> None:
    info = self.engine.analyse(self.board, Limit(time=0.1))
    pscore = info.get('score')
    if pscore is not None:
      score = pscore.white()
      self.score = score.score(mate_score=1000)

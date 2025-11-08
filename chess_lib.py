import chess
import chess.svg
import chess.pgn
from chess.engine import SimpleEngine, Limit, PovScore, Info
from datetime import datetime

class Game():
  def __init__(self,
               orientation: bool = True,
               fen: str | None = None,
               level: int | None = None) -> None:
    if fen is None:
      self.board = chess.Board()
      self.initial_fen: str | None = None
      self.first_turn: bool = True
    else:
      self.board = chess.Board(fen=fen)
      self.initial_fen: str | None = fen
      self.first_turn: bool = self.board.turn
    level = level if level is not None else 0
    self.engine = SimpleEngine.popen_uci("/opt/homebrew/bin/stockfish")
    self.engine.configure({"Skill Level": level})
    self.score: int = 0
    self.orientation = orientation
    self.running: bool = True
    self.message: str = ""
    self.moves: list[str] = []
    self.result: str = "*"
    self.show_board()

  def load_game(self, file: str) -> str | None:
    try:
      pgn = open(file)
    except FileNotFoundError:
      return f"no such file: {file}"
    game = chess.pgn.read_game(pgn)
    if game is None: return "failed to parse pgn"
    self.board = game.board()
    for move in game.mainline_moves():
      self.moves.append(self.board.san(move))
      self.board.push(move)
    self.check_board()
    return None

  def set_orientation(self, orientation: bool) -> None:
    self.orientation = orientation
    lastmove = None
    try:
      lastmove = self.board.peek()
    except IndexError:
      self.show_board()
    self.show_board(lastmove=lastmove)

  def set_level(self, level: int) -> None:
    self.engine.configure({"Skill Level": level})

  def set_score(self, pscore: PovScore | None) -> None:
    if pscore is not None:
      score = pscore.white()
      if score.is_mate():
        self.message = "mate in " + str(score.mate())
      self.score = score.score(mate_score=2000)

  def get_score(self) -> None:
    info = self.engine.analyse(self.board, Limit(time=0.1))
    pscore = info.get('score')
    self.set_score(pscore)

  def show_board(self, lastmove=None, check=None, fill={}) -> None:
    with open('tmp/board.svg', 'w') as svg:
      svg.write(chess.svg.board(self.board,
                                orientation=self.orientation,
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
  
  def make_move(self, uci: str | None = None, san: str | None = None) -> str | None:
    if uci is not None:
      move = chess.Move.from_uci(uci)
      try:
        move = self.board.find_move(move.from_square, move.to_square)
      except chess.IllegalMoveError:
        return None
      checked_san = self.board.san(move)
    elif san is not None:
      checked_san = san
    else:
      return None
    self.moves.append(checked_san)
    self.board.push_san(checked_san)
    self.check_board()
    return checked_san
  
  def computer_move(self) -> str | None:
    result = self.engine.play(self.board, Limit(depth=20))
    if result.move is not None:
      san = self.board.san(result.move)
      self.moves.append(san)
      self.board.push(result.move)
      self.check_board()
      return san
    else:
      return None

  def undo_move(self) -> tuple[str, str] | None:
    try:
      self.board.pop()
    except IndexError:
      return None
    self.running = True
    self.result = "*"
    san = self.moves.pop()
    self.check_board()
    sz = len(self.moves)
    if sz == 0:
      return (san, "no previous move")
    else:
      return (san, self.moves[sz-1])

  def check_board(self) -> None:
    self.message = ""
    self.get_score()
    outcome = self.board.outcome()
    if outcome is not None:
      self.result = outcome.result()
      self.running = False
      match outcome.termination:
        case chess.Termination.CHECKMATE:
          self.message = f"Checkmate! {"White" if outcome.winner else "Black"} wins."
        case chess.Termination.STALEMATE:
          self.message = "Stalemate! It's a draw."
        case reason:
          self.message = f"Game over! {reason}"
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
  
  def get_movetext(self) -> str:
    text = ""
    m = 1
    i = 0
    sz = len(self.moves)
    if not self.first_turn:
      try:
        text = text + f"{m}...{self.moves[i]}\n"
      except IndexError:
        return text
      m = 2
      i = 1
    while i < sz:
      text = text + f"{m}.{self.moves[i]} "
      if i+1 < sz:
        text = text + f"{self.moves[i+1]}\n"
      elif not self.running:
        text = text + self.result
      i += 2
      m += 1
    return text

  def save_game(self) -> None:
    dt = datetime.now()
    file = f"data/{dt.year}-{dt.month}-{dt.day}-{dt.hour}:{dt.minute}.pgn"
    with open(file, 'w') as pgn:
      pgn.write(f"[Result \"{self.result}\"]\n")
      if self.initial_fen is not None:
        pgn.write(f"[SetUp \"1\"]\n")
        pgn.write(f"[FEN \"{self.initial_fen}\"]\n\n")
      else:
        pgn.write("\n")
      pgn.write(self.get_movetext())

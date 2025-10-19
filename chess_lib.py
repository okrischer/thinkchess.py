import chess
import chess.svg

class Game():
  def __init__(self):
    self.board = chess.Board()
    self.running = True
    self.message = ""
    self.show_board()

  def show_board(self, lastmove=None, check=None, fill={}):
    with open('img/board.svg', 'w') as svg:
      svg.write(chess.svg.board(self.board,
                                lastmove=lastmove,
                                check=check,
                                fill=fill))

  def show_square(self, square):
    square = chess.parse_square(square)
    white_squares = [1,  3, 5, 7,
                     8, 10,12,14,
                     17,19,21,23,
                     24,26,28,30,
                     33,35,37,39,
                     40,42,44,46,
                     49,51,53,55,
                     56,58,60,62]
    color = "#cdd16a" if square in white_squares else "#aaa23b"
    self.show_board(fill={square: color})

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
    
  def check_board(self):
    state = self.board.outcome()
    if state is not None:
      self.running = False
      match state.termination:
        case chess.Termination.CHECKMATE:
          self.message = f"Checkmate! {"White" if state.winner else "Black"} wins."
        case chess.Termination.STALEMATE:
          self.message = "Game over! It's a stalemate."
        case reason:
          self.message = f"Game over! {reason}"
    lastmove = self.board.peek()
    check = chess.SQUARES[lastmove.to_square]
    if check not in self.board.checkers():
      check = None
    self.show_board(lastmove=lastmove, check=check)
  
import subprocess
import chess

stockfish_path = r"C:\Users\sajee\stockfish\stockfish-windows-x86-64-avx2.exe"

engine = subprocess.Popen(
    [stockfish_path],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True
)

def send_command(cmd):
    engine.stdin.write(str(cmd)+ '\n')
    engine.stdin.flush()

def get_bestmove():
    while True:
        line = engine.stdout.readline().strip()
        if line:
            print(line)
        if "bestmove" in line:
            return line.split()[1]

color_choice = input("Play as White or Black? (w/b):").strip().lower()
play_white = (color_choice == "w")

fen_choice = input("Start from FEN? (y/n):").strip().lower()
if fen_choice == "y":
    fen = input("Enter FEN: ").strip()
    board = chess.Board(fen)
else:
    board = chess.Board()

send_command("uci")
send_command("isready")

while not board.is_game_over():
    print("\n Current Board")
    print(board)
    print()

    if(board.turn == chess.WHITE and play_white) or (board.turn == chess.BLACK and not play_white):
        move_uci = input("Your move :").strip()
        if move_uci.lower() == "quit":
            break
        try:
            move = chess.Move.from_uci(move_uci)
            if move in board.legal_moves:
                board.push(move)
            else:
                print("Illegal move. Try again")
                continue
        except:
            print("Invalid move format Try again")
            continue
    else:
        send_command(f"position fen {board.fen()}")
        send_command("go depth 12")
        best_move = get_bestmove()
        print(f"Stock fish plays {best_move}")

        board.push(chess.Move.from_uci(best_move))
        print("\n Game Over")
        print(board.result())                

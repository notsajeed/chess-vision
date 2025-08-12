import subprocess

stockfish_path = r"C:\Users\sajee\stockfish\stockfish-windows-x86-64-avx2.exe"

engine = subprocess.Popen(
    [stockfish_path],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True
)

def send_command(cmd):
    engine.stdin.write(cmd+ '\n')
    engine.stdin.flush()

def read_until_bestmove():
    while True:
        line = engine.stdout.readline().strip()
        if line:
            print(line)
        if "bestmove" in line:
            break

send_command("uci")
send_command("isready")

moves = []

while True:
    if moves:
        send_command(f"position startpos moves {' '.join(str(m) for m in moves)}")
    else:
        send_command("position startops")

    send_command("go depth 12")
    best_move = read_until_bestmove()
    print(f"\n StockFish plays: {best_move}\n")

    moves.append(best_move)

    opponents_move = input("Enter opponents move (or 'quit): ").strip()
    if opponents_move.lower() == "quit":
        break
    moves.append(opponents_move)

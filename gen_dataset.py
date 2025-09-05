import os, csv, argparse
from tqdm import tqdm
import chess
from chess_image_gen import render_position, random_legal_fen

def generate_dataset(n, out_dir, sq=256, sprites=None):
    os.makedirs(os.path.join(out_dir, "images"), exist_ok=True)
    meta_path = os.path.join(out_dir, "metadata.csv")

    with open(meta_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "id", "fen", "turn", "move_number",
            "castling_rights", "en_passant",
            "is_check", "is_game_over"
        ])

        for i in tqdm(range(1, n+1)):
            fen = random_legal_fen()
            img_file = f"{i:06d}.png"

            render_position(
                fen=fen,
                out_path=os.path.join(out_dir, "images", img_file),
                square_size=sq,
                margin=0,
                flipped=False,
                show_coordinates=False,
                sprite_dir=sprites
            )

            board = chess.Board(fen)

            writer.writerow([
                img_file,
                fen,
                board.turn,                 # True = White, False = Black
                board.fullmove_number,      # Fullmove counter
                board.castling_xfen(),      # Castling rights
                board.ep_square if board.ep_square else "-",  # En passant square
                board.is_check(),
                board.is_game_over()
            ])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, required=True, help="Number of samples")
    parser.add_argument("--out", type=str, required=True, help="Output directory")
    parser.add_argument("--sq", type=int, default=256, help="Image size (square)")
    parser.add_argument("--sprites", type=str, default="pieces", help="Sprite dir")
    args = parser.parse_args()

    generate_dataset(args.n, args.out, args.sq, args.sprites)

#!/usr/bin/env python3
"""
Chess Position Image Generator

Generates PNG images of chess positions (from FEN or randomly sampled legal
positions) with a visual style inspired by chess.com (green/tan squares).

Feature set
- Validates FENs and ensures positions are legal using python-chess
- Optionally samples random legal positions by playing a random playout
- Renders with Pillow, using either:
    1) Unicode chess glyphs (requires a font with chess glyphs, e.g. DejaVu Sans)
    2) A sprite pack directory containing PNGs named like "wp.png, bn.png, ..."
- Coordinates, board flip, margins, and square sizes are configurable

Dependencies
    pip install pillow python-chess

Usage
    python chess_image_gen.py --fen "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3" --out sample.png
    python chess_image_gen.py --random 60 --out random.png

Sprite packs (optional)
Provide a directory of 12 PNGs named according to piece symbols:
    White: wk.png, wq.png, wr.png, wb.png, wn.png, wp.png
    Black: bk.png, bq.png, br.png, bb.png, bn.png, bp.png
Each sprite will be scaled to fit the square size.
"""

from __future__ import annotations
import argparse
import os
import random
from typing import Optional, Tuple

from PIL import Image, ImageDraw, ImageFont
import chess

# --- Default board palette (chess.com-like) ---
LIGHT = (238, 238, 210)
DARK = (118, 150, 86)
BORDER = (34, 34, 34)
COORD = (40, 40, 40)

UNICODE_MAP = {
    'P': '\u2659', 'N': '\u2658', 'B': '\u2657', 'R': '\u2656', 'Q': '\u2655', 'K': '\u2654',
    'p': '\u265F', 'n': '\u265E', 'b': '\u265D', 'r': '\u265C', 'q': '\u265B', 'k': '\u265A',
}

SPRITE_FILENAMES = {
    'P': 'wp.png', 'N': 'wn.png', 'B': 'wb.png', 'R': 'wr.png', 'Q': 'wq.png', 'K': 'wk.png',
    'p': 'bp.png', 'n': 'bn.png', 'b': 'bb.png', 'r': 'br.png', 'q': 'bq.png', 'k': 'bk.png',
}

COMMON_FONT_PATHS = [
    # Linux / Ubuntu
    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',
    # macOS
    '/System/Library/Fonts/Supplemental/DejaVu Sans.ttf',
    '/Library/Fonts/DejaVu Sans.ttf',
    '/System/Library/Fonts/Supplemental/Arial Unicode.ttf',
    # Windows
    'C:/Windows/Fonts/DejaVuSans.ttf',
    'C:/Windows/Fonts/arial.ttf',
]


def load_font(square_size: int) -> Optional[ImageFont.FreeTypeFont]:
    size = int(square_size * 0.8)
    for p in COMMON_FONT_PATHS:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size=size)
            except Exception:
                continue
    try:
        return ImageFont.load_default()
    except Exception:
        return None


def is_legal_fen(fen: str) -> bool:
    try:
        board = chess.Board(fen)
        return board.is_valid()
    except Exception:
        return False


def random_legal_fen(max_plies: int = 80, seed: Optional[int] = None) -> str:
    if seed is not None:
        random.seed(seed)
    board = chess.Board()
    plies = random.randint(10, max_plies)
    for _ in range(plies):
        moves = list(board.legal_moves)
        if not moves:
            break
        move = random.choice(moves)
        board.push(move)
        if board.is_game_over():
            break
    return board.fen()


def algebraic_to_xy(file_idx: int, rank_idx: int, flipped: bool) -> Tuple[int, int]:
    if flipped:
        x = 7 - file_idx
        y = rank_idx
    else:
        x = file_idx
        y = 7 - rank_idx
    return x, y


def draw_coordinates(draw: ImageDraw.ImageDraw, img_w: int, img_h: int, sq: int, margin: int, flipped: bool):
    files = 'abcdefgh'
    ranks = '12345678'
    font = ImageFont.load_default()

    for f_idx, f in enumerate(files):
        x = margin + f_idx * sq + sq / 2
        y = img_h - margin + 4
        if flipped:
            f = files[7 - f_idx]
        bbox = font.getbbox(f)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text((x - w / 2, y), f, fill=COORD, font=font)

    for r_idx, r in enumerate(reversed(ranks)):
        y = margin + r_idx * sq + sq / 2
        x = 6
        if flipped:
            r = ranks[r_idx]
        bbox = font.getbbox(r)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text((x, y - h / 2), r, fill=COORD, font=font)


def load_sprites(sprite_dir: Optional[str]) -> dict:
    sprites = {}
    if not sprite_dir:
        return sprites
    for sym, fname in SPRITE_FILENAMES.items():
        path = os.path.join(sprite_dir, fname)
        if os.path.exists(path):
            try:
                sprites[sym] = Image.open(path).convert('RGBA')
            except Exception:
                pass
    return sprites


def render_position(
    fen: str,
    out_path: str = 'board.png',
    square_size: int = 96,
    margin: int = 32,
    flipped: bool = False,
    show_coordinates: bool = True,
    sprite_dir: Optional[str] = None,
) -> str:
    if not is_legal_fen(fen):
        raise ValueError("Provided FEN is not a legal position.")

    board = chess.Board(fen)
    board_px = square_size * 8
    img_w = board_px + margin * 2
    img_h = board_px + margin * 2

    img = Image.new('RGBA', (img_w, img_h), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0, 0), (img_w - 1, img_h - 1)], outline=BORDER, width=2)

    for file_idx in range(8):
        for rank_idx in range(8):
            x, y = algebraic_to_xy(file_idx, rank_idx, flipped)
            color = LIGHT if (file_idx + rank_idx) % 2 == 0 else DARK
            x0 = margin + x * square_size
            y0 = margin + y * square_size
            x1 = x0 + square_size
            y1 = y0 + square_size
            draw.rectangle([(x0, y0), (x1, y1)], fill=color)

    if show_coordinates:
        draw_coordinates(draw, img_w, img_h, square_size, margin, flipped)

    sprites = load_sprites(sprite_dir)
    font = load_font(square_size)

    for sq in chess.SQUARES:
        piece = board.piece_at(sq)
        if not piece:
            continue
        file_idx = chess.square_file(sq)
        rank_idx = chess.square_rank(sq)
        x, y = algebraic_to_xy(file_idx, rank_idx, flipped)
        x0 = margin + x * square_size
        y0 = margin + y * square_size
        cx = x0 + square_size // 2
        cy = y0 + square_size // 2

        sym = piece.symbol()

        if sym in sprites:
            sprite = sprites[sym]
            sprite_resized = sprite.resize((int(square_size*0.92), int(square_size*0.92)), Image.LANCZOS)
            px = cx - sprite_resized.width // 2
            py = cy - sprite_resized.height // 2
            img.alpha_composite(sprite_resized, (px, py))
        else:
            glyph = UNICODE_MAP[sym]
            if font is None:
                raise RuntimeError("No suitable font found for Unicode glyphs and no sprites provided.")
            bbox = font.getbbox(glyph)
            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text((cx - w/2 + 1, cy - h/2 + 1), glyph, font=font, fill=(0,0,0,140))
            draw.text((cx - w/2, cy - h/2), glyph, font=font, fill=(20,20,20) if sym.islower() else (250,250,250))

    img.save(out_path)
    return out_path


def main():
    parser = argparse.ArgumentParser(description='Generate an image of a chess position.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--fen', type=str, help='FEN string of the position to render')
    group.add_argument('--random', type=int, metavar='MAX_PLIES', help='Generate a random legal position with up to MAX_PLIES half-moves')

    parser.add_argument('--out', type=str, default='board.png', help='Output PNG path')
    parser.add_argument('--sq', type=int, default=96, help='Square size in pixels (default: 96)')
    parser.add_argument('--margin', type=int, default=32, help='Margin in pixels (default: 32)')
    parser.add_argument('--flip', action='store_true', help='Flip board to view from black side')
    parser.add_argument('--no-coords', action='store_true', help='Hide coordinates')
    parser.add_argument('--sprites', type=str, default=None, help='Directory with piece PNGs (e.g., wp.png, bn.png, ...)')

    args = parser.parse_args()

    if args.fen:
        fen = args.fen
    else:
        fen = random_legal_fen(max_plies=args.random)

    out = render_position(
        fen=fen,
        out_path=args.out,
        square_size=args.sq,
        margin=args.margin,
        flipped=args.flip,
        show_coordinates=not args.no_coords,
        sprite_dir=args.sprites,
    )
    print(f"Saved: {out}")
    print(f"FEN: {fen}")


if __name__ == '__main__':
    main()

# Chess Dataset Generator 

---

## Features
- 🎨 Render chessboards from **FEN strings**
- ⚡ Generate **N random legal positions**
- 📝 Export images + **metadata.csv**
- 🖼️ Configurable **sprite sets, board size, coordinates, margins**
- ♻️ Fully reproducible (same seed → same dataset)

---

## How It Works
1. **Generate FEN**  
   Using [`python-chess`](https://github.com/niklasf/python-chess), we sample **random legal chess positions**.  
2. **Render Image**  
   FEN is drawn using Pillow and custom chess piece sprites.  
3. **Save Metadata**  
   Alongside each `.png`, we store its full metadata in `metadata.csv`.  

---

## Example Usage
```bash
# Generate 1000 samples at 256px
python gen_dataset.py --n 1000 --out dataset --sq 256 --sprites ./pieces
````

### Resolution Examples

```bash
# 512x512 images
python gen_dataset.py --n 1000 --out dataset --sq 64 --sprites ./pieces

# 1024x1024 images
python gen_dataset.py --n 1000 --out dataset --sq 128 --sprites ./pieces
```

---

## Metadata

Each row in `metadata.csv` includes:

* `id` – image filename
* `fen` – full board state
* `turn` – `True` = white, `False` = black
* `move_number`
* `castling_rights`
* `en_passant`
* `is_check`
* `is_game_over`

---

## Requirements

```
pip install python-chess pillow tqdm
```

---

## Customization

* Change `--sprites` to swap different chess piece styles.
* Adjust `--sq` for higher-resolution datasets.
* Modify `random_legal_fen()` for specific position distributions.

---


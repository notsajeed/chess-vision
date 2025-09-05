import csv
import chess

def validate_metadata(meta_file, warnings_file="warnings.txt"):
    invalid_rows = []

    with open(meta_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            fen = row["fen"]
            try:
                board = chess.Board(fen)
                if not board.is_valid():
                    invalid_rows.append((row["id"], fen, "Invalid board state"))
            except Exception as e:
                invalid_rows.append((row["id"], fen, f"Error: {str(e)}"))

    # Write warnings to file
    if invalid_rows:
        with open(warnings_file, "w") as wf:
            for rid, fen, msg in invalid_rows:
                wf.write(f"{rid}: {fen}  -->  {msg}\n")

        print(f"⚠️ Found {len(invalid_rows)} invalid positions. Check {warnings_file}")
    else:
        print("✅ All positions are valid!")

if __name__ == "__main__":
    validate_metadata("metadata.csv")

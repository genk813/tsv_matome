import chardet
from pathlib import Path

FILE_PATH = Path("C:/Users/ygenk/Desktop/upd_t_sample.txt")

if not FILE_PATH.exists():
    print(f"File not found at {FILE_PATH}")
else:
    try:
        with open(FILE_PATH, 'r', encoding='utf-8', errors='replace') as f:
            print(f"--- First 5 lines of {FILE_PATH.name} ---")
            for i, line in enumerate(f):
                if i >= 5:
                    break
                print(line.strip())
            print("------------------------------------------")

    except Exception as e:
        print(f"Error reading file: {e}")

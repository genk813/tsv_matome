
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import chardet
from pathlib import Path
import shutil

# --- 設定 ---
SCRIPT_DIR = Path(__file__).parent.resolve()
TSV_DIR = SCRIPT_DIR / "tsv"
DECODED_TSV_DIR = SCRIPT_DIR / "decoded_tsvs"

def decode_tsv_files():
    if not TSV_DIR.exists():
        print(f"Error: Source TSV directory not found at {TSV_DIR}")
        return

    # decoded_tsvs フォルダが存在しない場合は作成、存在する場合は中身を削除
    if DECODED_TSV_DIR.exists():
        shutil.rmtree(DECODED_TSV_DIR)
    DECODED_TSV_DIR.mkdir()

    print(f"Decoding TSV files from {TSV_DIR} to {DECODED_TSV_DIR}...")

    for tsv_file in sorted(TSV_DIR.glob("*.tsv")):
        try:
            # ファイル内容をバイナリで読み込み、エンコーディングを検出
            with open(tsv_file, 'rb') as f:
                raw_data = f.read()
            detected_encoding = chardet.detect(raw_data)['encoding']

            # 検出されたエンコーディングでデコードし、UTF-8で保存
            decoded_content = raw_data.decode(detected_encoding, errors='replace')
            
            output_file = DECODED_TSV_DIR / f"{tsv_file.stem}.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(decoded_content)
            print(f"  Decoded '{tsv_file.name}' ({detected_encoding}) to '{output_file.name}'")

        except Exception as e:
            print(f"  Error decoding '{tsv_file.name}': {e}")

    print("Decoding complete.")

if __name__ == '__main__':
    decode_tsv_files()

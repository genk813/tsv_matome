# mcp_tsv_matome.py
import sys
import json
from pathlib import Path

def main():
    # Claudeからの標準入力を受け取る（実際は使わなくてもOK）
    _ = sys.stdin.read()

    folder = Path("C:/Users/ygenk/Desktop/tsv_matome")

    if not folder.exists():
        print(json.dumps({"error": "指定フォルダが存在しません"}))
        return

    # 読み取るファイルの拡張子を限定（任意）
    allowed_ext = {".py", ".html", ".tsv", ".txt"}
    files = [f for f in folder.glob("*") if f.suffix in allowed_ext]

    contents = {
        f.name: f.read_text(encoding="utf-8", errors="ignore")
        for f in files
    }

    response = {
        "message": f"{len(files)}件のファイルを読み込みました。",
        "files": list(contents.keys()),
        "contents": contents  # ファイル名 → 内容
    }

    print(json.dumps(response, ensure_ascii=False))

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
データベーススキーマ確認スクリプト
"""

import sqlite3
from pathlib import Path

def check_schema():
    """trademark_case_infoテーブルのスキーマを確認"""
    
    # データベースファイルを探す
    db_candidates = [
        Path(r"C:\Users\ygenk\Desktop\TMCloud\tmcloud_v2_20250818_081655.db"),
        Path(r"C:\Users\ygenk\Desktop\TMCloud\tmcloud_v2_20250805_232509.db")
    ]
    
    db_path = None
    for db in db_candidates:
        if db.exists():
            db_path = db
            print(f"データベース使用: {db.name}")
            break
    
    if not db_path:
        print("エラー: データベースが見つかりません")
        return
    
    # データベース接続
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    print("\n=== trademark_case_infoテーブルのカラム一覧 ===\n")
    
    # テーブル情報を取得
    cursor.execute("PRAGMA table_info(trademark_case_info)")
    columns = cursor.fetchall()
    
    # 立体商標関連のカラムを探す
    special_cols = []
    for col in columns:
        col_name = col[1]
        col_type = col[2]
        print(f"  {col_name:30s} {col_type}")
        
        # 立体商標関連のカラムを探す
        if any(keyword in col_name.lower() for keyword in ['special', 'dimensional', 'three', 'mark_type']):
            special_cols.append(col_name)
    
    print(f"\n=== 立体商標関連カラム ===")
    if special_cols:
        for col in special_cols:
            print(f"  - {col}")
    else:
        print("  該当なし")
    
    # 実際のデータを確認
    print(f"\n=== 出願番号2024061720のデータ ===")
    
    # 動的にSELECT文を構築
    special_cols_str = ", ".join(special_cols) if special_cols else "app_num"
    query = f"SELECT app_num, {special_cols_str} FROM trademark_case_info WHERE app_num = '2024061720'"
    
    try:
        cursor.execute(query)
        row = cursor.fetchone()
        if row:
            for i, col_name in enumerate(['app_num'] + special_cols):
                print(f"  {col_name}: {row[i]}")
        else:
            print("  データが見つかりません")
    except Exception as e:
        print(f"  エラー: {e}")
    
    conn.close()
    
    # 結果ファイルに出力
    with open("schema_check_result.txt", "w", encoding="utf-8") as f:
        f.write("立体商標関連カラム:\n")
        for col in special_cols:
            f.write(f"  - {col}\n")

if __name__ == "__main__":
    check_schema()
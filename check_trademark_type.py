#!/usr/bin/env python3
"""出願番号2024061720の商標タイプを調査"""

import sqlite3
from pathlib import Path

# データベースファイル
db_path = Path("C:/Users/ygenk/Desktop/TMCloud/tmcloud_v2_20250818_081655.db")

# データベース接続
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# 出願番号2024061720のデータを取得
app_num = "2024061720"

print(f"=== 出願番号 {app_num} の商標タイプ関連情報 ===\n")

# trademark_case_infoから情報取得
cursor.execute("""
    SELECT 
        app_num,
        trademark_type,
        dimensional_trademark_flag,
        special_mark_type,
        standard_char_exist
    FROM trademark_case_info
    WHERE app_num = ?
""", (app_num,))

result = cursor.fetchone()
if result:
    print("trademark_case_info テーブル:")
    for key in result.keys():
        print(f"  {key}: {result[key]}")
else:
    print(f"出願番号 {app_num} が見つかりません")

# trademark_basic_itemsからも確認
cursor.execute("""
    SELECT 
        app_num,
        trademark_type,
        special_trademark_type
    FROM trademark_basic_items
    WHERE app_num = ?
""", (app_num,))

result = cursor.fetchone()
if result:
    print("\ntrademark_basic_items テーブル:")
    for key in result.keys():
        print(f"  {key}: {result[key]}")

conn.close()
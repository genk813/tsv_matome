#!/usr/bin/env python3
"""
直接実行するテストスクリプト
"""

import sqlite3
from pathlib import Path

# データベースファイルパス
db_path = Path(r"C:\Users\ygenk\Desktop\TMCloud\tmcloud_v2_20250818_081655.db")

if not db_path.exists():
    print(f"エラー: データベースが見つかりません: {db_path}")
    exit(1)

print(f"データベース: {db_path}")

# データベース接続
conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("\n=== 出願番号2024061720のデータ確認 ===")

# データ取得
cursor.execute("""
    SELECT 
        app_num,
        standard_char_exist,
        special_mark_type,
        dimensional_trademark_flag
    FROM trademark_case_info
    WHERE app_num = '2024061720'
""")

row = cursor.fetchone()
if row:
    print(f"出願番号: {row['app_num']}")
    print(f"標準文字存在: {row['standard_char_exist']}")
    print(f"特殊マーク種別: {row['special_mark_type']}")
    print(f"立体商標フラグ: {row['dimensional_trademark_flag']}")
    
    # 判定
    if row['special_mark_type'] == '1' or row['dimensional_trademark_flag'] == '1':
        print("\n結果: ✅ 立体商標として判定される")
        print("理由: special_mark_type='1' または dimensional_trademark_flag='1'")
        success = True
    else:
        print("\n結果: ❌ 立体商標として判定されない")
        print(f"理由: special_mark_type='{row['special_mark_type']}', dimensional_trademark_flag='{row['dimensional_trademark_flag']}'")
        success = False
else:
    print("エラー: データが見つかりません")
    success = False

conn.close()

if success:
    print("\nテスト成功: 立体商標として正しく判定されています")
else:
    print("\nテスト失敗: 立体商標として判定されませんでした")
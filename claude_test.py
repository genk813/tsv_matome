#!/usr/bin/env python3
"""
Claudeが実行するテストスクリプト
"""

import sys
import sqlite3
from pathlib import Path

def test_3d_trademark():
    """立体商標のテストを実行"""
    
    # データベースファイルを探す
    db_candidates = [
        Path(r"C:\Users\ygenk\Desktop\TMCloud\tmcloud_v2_20250818_081655.db"),
        Path(r"C:\Users\ygenk\Desktop\TMCloud\tmcloud_v2_20250805_232509.db")
    ]
    
    db_path = None
    for db in db_candidates:
        if db.exists():
            db_path = db
            print(f"データベース発見: {db}")
            break
    
    if not db_path:
        print("エラー: データベースが見つかりません")
        return False
    
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
            special_mark_exist
        FROM trademark_case_info
        WHERE app_num = '2024061720'
    """)
    
    row = cursor.fetchone()
    if row:
        print(f"app_num: {row['app_num']}")
        print(f"standard_char_exist: {row['standard_char_exist']}")
        print(f"special_mark_exist: {row['special_mark_exist']}")
        
        # 判定（special_mark_exist=1なら立体商標等の特殊商標）
        if row['special_mark_exist'] == '1':
            print("結果: ✅ 立体商標として判定される")
            print("理由: special_mark_exist = '1' (特殊商標識別)")
            return True
        else:
            print("結果: ❌ 立体商標として判定されない")
            print(f"理由: special_mark_exist = '{row['special_mark_exist']}'")
            return False
    else:
        print("エラー: データが見つかりません")
        return False
    
    conn.close()

if __name__ == "__main__":
    success = test_3d_trademark()
    sys.exit(0 if success else 1)
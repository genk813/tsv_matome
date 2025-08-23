#!/bin/bash
# WSL環境で立体商標テストを実行

cd /home/ygenk/TMCloud

# テストスクリプトを作成
cat > test_3d_trademark.py << 'EOF'
#!/usr/bin/env python3
"""立体商標表示のテストスクリプト"""

import sys
import sqlite3
from pathlib import Path

# データベースパス
DB_PATH = Path("/home/ygenk/TMCloud/tmcloud_v2_20250805_232509.db")

def test_trademark_type():
    """出願番号2024061720の商標タイプをテスト"""
    
    if not DB_PATH.exists():
        print(f"データベースが見つかりません: {DB_PATH}")
        return
    
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("=" * 60)
    print("立体商標フラグの確認")
    print("=" * 60)
    
    # データベースの状態を確認
    cursor.execute("""
        SELECT 
            app_num,
            standard_char_exist,
            special_mark_type,
            dimensional_trademark_flag,
            special_mark_exist
        FROM trademark_case_info
        WHERE app_num = '2024061720'
    """)
    
    row = cursor.fetchone()
    if row:
        print(f"出願番号: {row['app_num']}")
        print(f"standard_char_exist: {row['standard_char_exist']}")
        print(f"special_mark_type: {row['special_mark_type']}")
        print(f"dimensional_trademark_flag: {row['dimensional_trademark_flag']}")
        print(f"special_mark_exist: {row['special_mark_exist']}")
        
        # 判定ロジック
        print("\n商標タイプ判定:")
        if row['standard_char_exist'] == '1':
            print("→ 標準文字")
        elif row['special_mark_type'] == '1' or row['dimensional_trademark_flag'] == '1':
            print("→ 立体商標")
        else:
            print("→ 通常")
    else:
        print("出願番号2024061720が見つかりません")
    
    # 他の立体商標も確認
    print("\n" + "=" * 60)
    print("立体商標フラグが設定されているデータ（最初の5件）")
    print("=" * 60)
    
    cursor.execute("""
        SELECT app_num, special_mark_type, dimensional_trademark_flag
        FROM trademark_case_info
        WHERE special_mark_type = '1' OR dimensional_trademark_flag = '1'
        LIMIT 5
    """)
    
    for row in cursor.fetchall():
        print(f"出願番号: {row['app_num']}")
        print(f"  special_mark_type: {row['special_mark_type']}")
        print(f"  dimensional_trademark_flag: {row['dimensional_trademark_flag']}")
    
    conn.close()

if __name__ == "__main__":
    test_trademark_type()
EOF

# テストを実行
echo "テストスクリプトを実行中..."
python3 test_3d_trademark.py

# 検索スクリプトで実際に検索
echo -e "\n\n実際の検索スクリプトで確認:"
./tmcloud "2024061720" --limit 1
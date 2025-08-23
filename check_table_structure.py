#!/usr/bin/env python3
"""テーブル構造の確認"""

import sqlite3
from pathlib import Path

def check_table_structure():
    db_path = Path(__file__).parent / "tmcloud_v2_20250818_081655.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # trademark_displayテーブルの構造を確認
    cursor.execute("PRAGMA table_info(trademark_display)")
    columns = cursor.fetchall()
    
    print("【trademark_displayテーブルの構造】")
    print("-" * 60)
    for col in columns:
        print(f"  {col[1]:30} {col[2]:15} {col[3]:5} {col[4]}")
    
    # サンプルデータの確認
    print("\n【サンプルデータ（最初の2件）】")
    print("-" * 60)
    cursor.execute("SELECT * FROM trademark_display LIMIT 2")
    rows = cursor.fetchall()
    
    col_names = [col[1] for col in columns]
    
    for row in rows:
        for i, (name, value) in enumerate(zip(col_names, row)):
            if value and len(str(value)) > 100:
                print(f"  {name}: {str(value)[:100]}...")
            else:
                print(f"  {name}: {value}")
        print()
    
    conn.close()

if __name__ == "__main__":
    check_table_structure()
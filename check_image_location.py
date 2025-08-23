#!/usr/bin/env python3
"""画像データの場所を確認"""

import sqlite3
from pathlib import Path

def check_image_location():
    db_path = Path(__file__).parent / "tmcloud_v2_20250818_081655.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # すべてのテーブルを取得
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print("=" * 80)
    print("画像データを含む可能性のあるカラムを探す")
    print("=" * 80)
    
    # 各テーブルで'image'や'binary'を含むカラムを探す
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        image_cols = []
        for col in columns:
            col_name = col[1].lower()
            if 'image' in col_name or 'binary' in col_name or 'blob' in col_name.lower() or col[2].upper() == 'BLOB':
                image_cols.append((col[1], col[2]))
        
        if image_cols:
            print(f"\n【{table_name}】")
            for col_name, col_type in image_cols:
                print(f"  - {col_name} ({col_type})")
    
    # trademark_basic_itemsテーブルを詳しく確認
    print("\n" + "=" * 80)
    print("trademark_basic_itemsテーブルの構造")
    print("=" * 80)
    
    cursor.execute("PRAGMA table_info(trademark_basic_items)")
    columns = cursor.fetchall()
    
    for col in columns:
        print(f"  {col[1]:30} {col[2]:15}")
    
    # 特定の出願番号のデータを確認
    app_nums = ['2025064433', '2025064506', '2025064160', '2025062137', '2025061841']
    
    print("\n" + "=" * 80)
    print("特定の出願番号のデータ確認（trademark_basic_items）")
    print("=" * 80)
    
    for app_num in app_nums:
        cursor.execute("""
            SELECT 
                app_num,
                LENGTH(image_binary_data) as img_size
            FROM trademark_basic_items 
            WHERE app_num = ?
        """, (app_num,))
        
        result = cursor.fetchone()
        if result:
            status = "表示OK" if app_num == '2025061841' else "表示NG"
            print(f"出願番号: {result[0]} ({status})")
            print(f"  画像サイズ: {result[1] if result[1] else 'NULL'} bytes")
        else:
            print(f"出願番号: {app_num} - データなし")
    
    conn.close()

if __name__ == "__main__":
    check_image_location()
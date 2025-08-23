#!/usr/bin/env python3
"""商標画像データの確認"""

import sqlite3
from pathlib import Path

def check_image_data():
    db_path = Path(__file__).parent / "tmcloud_v2_20250818_081655.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    app_nums = ['2025064433', '2025064506', '2025064160', '2025062137', '2025061841']
    
    print("=" * 80)
    print("商標画像データの確認")
    print("=" * 80)
    
    # trademark_displayテーブルの確認
    print("\n【trademark_displayテーブル】")
    print("-" * 60)
    
    for app_num in app_nums:
        cursor.execute("""
            SELECT 
                app_num,
                LENGTH(image_binary_data) as img_size,
                standard_char_exist,
                special_mark_exist
            FROM trademark_display 
            WHERE app_num = ?
        """, (app_num,))
        
        result = cursor.fetchone()
        if result:
            status = "表示されている" if app_num == '2025061841' else "表示されていない"
            print(f"出願番号: {result[0]} ({status})")
            print(f"  画像サイズ: {result[1] if result[1] else 'NULL'} bytes")
            print(f"  標準文字: {result[2]}")
            print(f"  特殊商標: {result[3]}")
        else:
            print(f"出願番号: {app_num} - データなし")
        print()
    
    # trademark_case_infoテーブルの確認
    print("\n【trademark_case_infoテーブル】")
    print("-" * 60)
    
    for app_num in app_nums:
        cursor.execute("""
            SELECT 
                app_num,
                standard_char_exist,
                special_mark_exist,
                app_date
            FROM trademark_case_info 
            WHERE app_num = ?
        """, (app_num,))
        
        result = cursor.fetchone()
        if result:
            print(f"出願番号: {result[0]}")
            print(f"  標準文字: {result[1]}")
            print(f"  特殊商標: {result[2]}")
            print(f"  出願日: {result[3]}")
        else:
            print(f"出願番号: {app_num} - データなし")
        print()
    
    # trademark_searchテーブルの確認
    print("\n【trademark_searchテーブル】")
    print("-" * 60)
    
    for app_num in app_nums:
        cursor.execute("""
            SELECT 
                app_num,
                search_use_t
            FROM trademark_search 
            WHERE app_num = ?
        """, (app_num,))
        
        result = cursor.fetchone()
        if result:
            print(f"出願番号: {result[0]}")
            print(f"  商標名: {result[1] if result[1] else 'NULL'}")
        else:
            print(f"出願番号: {app_num} - データなし")
        print()
    
    conn.close()

if __name__ == "__main__":
    check_image_data()
#!/usr/bin/env python3
"""商標画像データの確認（trademark_imagesテーブル）"""

import sqlite3
from pathlib import Path

def check_image_data():
    db_path = Path(__file__).parent / "tmcloud_v2_20250818_081655.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    app_nums = ['2025064433', '2025064506', '2025064160', '2025062137', '2025061841']
    
    print("=" * 80)
    print("商標画像データの確認（trademark_imagesテーブル）")
    print("=" * 80)
    
    # trademark_imagesテーブルの確認
    for app_num in app_nums:
        cursor.execute("""
            SELECT 
                app_num,
                LENGTH(image_data) as img_size,
                image_data_length,
                SUBSTR(image_data, 1, 20) as img_preview
            FROM trademark_images 
            WHERE app_num = ?
        """, (app_num,))
        
        result = cursor.fetchone()
        status = "表示OK" if app_num == '2025061841' else "表示NG"
        
        print(f"\n出願番号: {app_num} ({status})")
        if result:
            print(f"  画像サイズ（実際）: {result[1] if result[1] else 'NULL'} bytes")
            print(f"  画像サイズ（記録）: {result[2]}")
            print(f"  データ先頭20文字: {result[3] if result[3] else 'NULL'}")
        else:
            print(f"  ⚠️ データなし")
    
    # trademark_case_infoテーブルで特殊商標フラグを確認
    print("\n" + "=" * 80)
    print("特殊商標フラグの確認（trademark_case_info）")
    print("=" * 80)
    
    for app_num in app_nums:
        cursor.execute("""
            SELECT 
                app_num,
                special_mark_exist,
                standard_char_exist
            FROM trademark_case_info 
            WHERE app_num = ?
        """, (app_num,))
        
        result = cursor.fetchone()
        if result:
            print(f"出願番号: {app_num}")
            print(f"  特殊商標: {result[1]}")
            print(f"  標準文字: {result[2]}")
    
    # 実際の検索クエリをシミュレート
    print("\n" + "=" * 80)
    print("検索クエリのシミュレーション")
    print("=" * 80)
    
    for app_num in app_nums:
        # tmcloud_search_integrated.pyの_get_detailed_info_v2メソッドのクエリを模倣
        cursor.execute("""
            SELECT 
                tbi.app_num,
                ti.image_data
            FROM trademark_basic_items tbi
            LEFT JOIN trademark_images ti ON tbi.app_num = ti.app_num
            WHERE tbi.app_num = ?
        """, (app_num,))
        
        result = cursor.fetchone()
        if result:
            has_image = "あり" if result[1] else "なし"
            print(f"出願番号: {app_num} - 画像データ: {has_image}")
            if result[1]:
                print(f"  データサイズ: {len(result[1])} bytes")
    
    conn.close()

if __name__ == "__main__":
    check_image_data()
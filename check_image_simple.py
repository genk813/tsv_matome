#!/usr/bin/env python3
"""商標画像データの簡単な確認"""

import sqlite3
from pathlib import Path

def check_image_data():
    db_path = Path(__file__).parent / "tmcloud_v2_20250818_081655.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    app_nums = ['2025064433', '2025064506', '2025064160', '2025062137', '2025061841']
    
    print("=" * 80)
    print("商標画像データの有無確認")
    print("=" * 80)
    
    # trademark_imagesテーブルのデータ有無だけ確認
    for app_num in app_nums:
        cursor.execute("""
            SELECT 
                app_num,
                CASE WHEN image_data IS NULL THEN 'NULL' 
                     WHEN image_data = '' THEN 'EMPTY'
                     ELSE 'EXISTS' END as data_status,
                image_data_length
            FROM trademark_images 
            WHERE app_num = ?
        """, (app_num,))
        
        result = cursor.fetchone()
        status = "表示OK" if app_num == '2025061841' else "表示NG"
        
        print(f"\n出願番号: {app_num} ({status})")
        if result:
            print(f"  データ状態: {result['data_status']}")
            print(f"  記録サイズ: {result['image_data_length']}")
        else:
            print(f"  ⚠️ レコードなし")
    
    conn.close()

if __name__ == "__main__":
    check_image_data()
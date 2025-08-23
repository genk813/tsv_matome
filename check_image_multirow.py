#!/usr/bin/env python3
"""画像データの複数行確認"""

import sqlite3
from pathlib import Path

def check_image_multirow():
    db_path = Path(__file__).parent / "tmcloud_v2_20250818_081655.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    app_num = '2025050454'
    
    print(f"出願番号 {app_num} の画像データ構造確認")
    print("=" * 80)
    
    # trademark_imagesテーブルの構造確認
    cursor.execute("PRAGMA table_info(trademark_images)")
    columns = cursor.fetchall()
    print("【カラム一覧】")
    for col in columns:
        print(f"  {col[1]:20} {col[2]}")
    
    # 該当出願番号のレコード数確認
    print("\n【レコード確認】")
    cursor.execute("""
        SELECT 
            app_num,
            rec_seq_num,
            LENGTH(image_data) as data_length,
            compression_format,
            image_data_length
        FROM trademark_images 
        WHERE app_num = ?
        ORDER BY rec_seq_num
    """, (app_num,))
    
    rows = cursor.fetchall()
    print(f"レコード数: {len(rows)}")
    
    total_length = 0
    for row in rows:
        print(f"  順序番号: {row[1]}, データ長: {row[2]}, 形式: {row[3]}, 記録長: {row[4]}")
        if row[2]:
            total_length += row[2]
    
    print(f"\n合計データ長: {total_length:,} bytes")
    
    # データの先頭と末尾を確認
    print("\n【データの先頭と末尾】")
    cursor.execute("""
        SELECT 
            rec_seq_num,
            SUBSTR(image_data, 1, 50) as data_head,
            SUBSTR(image_data, -20) as data_tail
        FROM trademark_images 
        WHERE app_num = ?
        ORDER BY rec_seq_num
    """, (app_num,))
    
    for row in cursor.fetchall():
        print(f"順序番号 {row[0]}:")
        print(f"  先頭: {row[1]}")
        print(f"  末尾: {row[2]}")
    
    conn.close()

if __name__ == "__main__":
    check_image_multirow()
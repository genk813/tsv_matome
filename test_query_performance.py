#!/usr/bin/env python3
"""クエリ性能テスト"""

import sqlite3
import time
from pathlib import Path

def test_query_performance():
    db_path = Path(__file__).parent / "tmcloud_v2_20250818_081655.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    app_num = '2025064433'
    
    print("=" * 80)
    print("クエリ性能テスト")
    print("=" * 80)
    
    # 1. シンプルなクエリ
    print("\n1. シンプルなクエリ")
    start = time.time()
    cursor.execute("""
        SELECT app_num, image_data 
        FROM trademark_images 
        WHERE app_num = ?
    """, (app_num,))
    result = cursor.fetchone()
    elapsed = time.time() - start
    print(f"  時間: {elapsed:.4f}秒")
    
    # 2. GROUP_CONCATを使ったクエリ
    print("\n2. GROUP_CONCATクエリ")
    start = time.time()
    cursor.execute("""
        SELECT 
            app_num,
            GROUP_CONCAT(image_data, '') as image_data
        FROM (
            SELECT app_num, image_data, compression_format
            FROM trademark_images
            WHERE app_num = ?
            AND image_data IS NOT NULL
            AND LENGTH(image_data) > 0
            AND compression_format = 'JP'
            ORDER BY app_num, rec_seq_num
        )
        GROUP BY app_num
    """, (app_num,))
    result = cursor.fetchone()
    elapsed = time.time() - start
    print(f"  時間: {elapsed:.4f}秒")
    
    # 3. WITH句を使った複雑なクエリ（一部）
    print("\n3. WITH句を使った複雑なクエリ")
    start = time.time()
    cursor.execute("""
        WITH image_data AS (
            SELECT 
                app_num,
                GROUP_CONCAT(image_data, '') as image_data
            FROM (
                SELECT app_num, image_data, compression_format
                FROM trademark_images
                WHERE app_num = ?
                AND image_data IS NOT NULL
                AND LENGTH(image_data) > 0
                AND compression_format = 'JP'
                ORDER BY app_num, rec_seq_num
            )
            GROUP BY app_num
        )
        SELECT * FROM image_data
    """, (app_num,))
    result = cursor.fetchone()
    elapsed = time.time() - start
    print(f"  時間: {elapsed:.4f}秒")
    
    conn.close()

if __name__ == "__main__":
    test_query_performance()
#!/usr/bin/env python3
"""最小限のテスト"""

import sqlite3
import time
from pathlib import Path

def test_minimal():
    db_path = Path(__file__).parent / "tmcloud_v2_20250818_081655.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    app_num = '2025064433'
    
    print(f"出願番号 {app_num} の最小限の検索...")
    
    # 最もシンプルなクエリ
    start = time.time()
    cursor.execute("SELECT app_num FROM trademark_basic_items WHERE app_num = ?", (app_num,))
    result = cursor.fetchone()
    elapsed = time.time() - start
    
    print(f"基本検索: {elapsed:.4f}秒")
    print(f"  結果: {result}")
    
    # 画像データの検索
    start = time.time()
    cursor.execute("SELECT app_num, LENGTH(image_data) FROM trademark_images WHERE app_num = ?", (app_num,))
    result = cursor.fetchone()
    elapsed = time.time() - start
    
    print(f"画像検索: {elapsed:.4f}秒")
    print(f"  結果: {result}")
    
    # 画像データを実際に取得
    start = time.time()
    cursor.execute("SELECT image_data FROM trademark_images WHERE app_num = ?", (app_num,))
    result = cursor.fetchone()
    elapsed = time.time() - start
    
    print(f"画像取得: {elapsed:.4f}秒")
    if result and result[0]:
        print(f"  画像サイズ: {len(result[0])} bytes")
    
    conn.close()

if __name__ == "__main__":
    test_minimal()
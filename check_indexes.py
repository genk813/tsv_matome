#!/usr/bin/env python3
"""インデックスの確認"""

import sqlite3
from pathlib import Path

def check_indexes():
    db_path = Path(__file__).parent / "tmcloud_v2_20250818_081655.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    print("=" * 80)
    print("テーブルのインデックス確認")
    print("=" * 80)
    
    # trademark_imagesテーブルのインデックスを確認
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='trademark_images'")
    indexes = cursor.fetchall()
    
    print("\n【trademark_images】")
    if indexes:
        for idx in indexes:
            print(f"  - {idx[0]}")
    else:
        print("  インデックスなし！")
    
    # インデックスがない場合、作成を提案
    if not indexes:
        print("\n推奨: CREATE INDEX idx_trademark_images_app_num ON trademark_images(app_num);")
    
    # テーブルの行数を確認
    cursor.execute("SELECT COUNT(*) FROM trademark_images")
    count = cursor.fetchone()[0]
    print(f"\n行数: {count:,} 件")
    
    # EXPLAIN QUERYでクエリプランを確認
    print("\n【クエリプラン】")
    cursor.execute("EXPLAIN QUERY PLAN SELECT * FROM trademark_images WHERE app_num = '2025064433'")
    plan = cursor.fetchall()
    for row in plan:
        print(f"  {row}")
    
    conn.close()

if __name__ == "__main__":
    check_indexes()
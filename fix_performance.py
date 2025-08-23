#!/usr/bin/env python3
"""パフォーマンス問題の修正"""

import sqlite3
import time
from pathlib import Path

def fix_performance():
    db_path = Path(__file__).parent / "tmcloud_v2_20250818_081655.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    print("=" * 80)
    print("データベースのパフォーマンス最適化")
    print("=" * 80)
    
    # インデックス作成前のテスト
    app_num = '2025064433'
    
    print("\n【現在の性能】")
    start = time.time()
    cursor.execute("SELECT image_data FROM trademark_images WHERE app_num = ?", (app_num,))
    result = cursor.fetchone()
    elapsed = time.time() - start
    print(f"  画像検索時間: {elapsed:.4f}秒")
    
    # インデックスを作成
    print("\n【インデックス作成】")
    print("  CREATE INDEX idx_trademark_images_app_num ON trademark_images(app_num)...")
    
    start = time.time()
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_trademark_images_app_num ON trademark_images(app_num)")
    conn.commit()
    elapsed = time.time() - start
    print(f"  完了（{elapsed:.2f}秒）")
    
    # インデックス作成後のテスト
    print("\n【最適化後の性能】")
    start = time.time()
    cursor.execute("SELECT image_data FROM trademark_images WHERE app_num = ?", (app_num,))
    result = cursor.fetchone()
    elapsed = time.time() - start
    print(f"  画像検索時間: {elapsed:.4f}秒")
    
    # 他の重要なテーブルのインデックスも確認・作成
    tables_to_index = [
        ('trademark_case_info', 'app_num'),
        ('trademark_basic_items', 'app_num'),
        ('trademark_search', 'app_num'),
        ('trademark_goods_services', 'app_num'),
        ('trademark_applicants_agents', 'app_num')
    ]
    
    print("\n【その他のインデックス】")
    for table, column in tables_to_index:
        index_name = f"idx_{table}_{column}"
        try:
            cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table}({column})")
            print(f"  ✓ {index_name}")
        except Exception as e:
            print(f"  ✗ {index_name}: {e}")
    
    conn.commit()
    conn.close()
    
    print("\n✓ 最適化完了！")

if __name__ == "__main__":
    fix_performance()
#!/usr/bin/env python3
"""大容量画像データの問題調査"""

import sqlite3
from pathlib import Path
import time

def test_large_image():
    db_path = Path(__file__).parent / "tmcloud_v2_20250818_081655.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    app_num = '2025054756'
    
    print(f"出願番号 {app_num} の詳細調査")
    print("=" * 80)
    
    # 1. レコード数と各行のサイズを確認
    cursor.execute("""
        SELECT 
            rec_seq_num,
            LENGTH(image_data) as data_length
        FROM trademark_images 
        WHERE app_num = ?
        ORDER BY rec_seq_num
    """, (app_num,))
    
    rows = cursor.fetchall()
    print(f"レコード数: {len(rows)}")
    
    total_length = 0
    unique_seqs = set()
    for seq, length in rows:
        if seq not in unique_seqs:
            print(f"  順序番号 {seq}: {length:,} 文字")
            total_length += length
            unique_seqs.add(seq)
    
    print(f"\n合計（重複除外後）: {total_length:,} 文字")
    
    # 2. GROUP_CONCATの制限を確認
    cursor.execute("PRAGMA compile_options")
    options = cursor.fetchall()
    for opt in options:
        if 'MAX' in str(opt[0]):
            print(f"SQLite設定: {opt[0]}")
    
    # 3. 標準的な結合方法でテスト
    print("\n標準的な結合方法でテスト:")
    start = time.time()
    cursor.execute("""
        SELECT GROUP_CONCAT(image_data, '') as combined_data
        FROM (
            SELECT DISTINCT rec_seq_num, image_data
            FROM trademark_images
            WHERE app_num = ?
            AND image_data IS NOT NULL
            ORDER BY rec_seq_num
        )
    """, (app_num,))
    
    result = cursor.fetchone()
    elapsed = time.time() - start
    
    if result and result[0]:
        print(f"  結合成功: {len(result[0]):,} 文字 ({elapsed:.3f}秒)")
    else:
        print(f"  結合失敗 ({elapsed:.3f}秒)")
    
    # 4. Python側で結合
    print("\nPython側で結合:")
    start = time.time()
    cursor.execute("""
        SELECT DISTINCT rec_seq_num, image_data
        FROM trademark_images
        WHERE app_num = ?
        AND image_data IS NOT NULL
        ORDER BY rec_seq_num
    """, (app_num,))
    
    all_rows = cursor.fetchall()
    combined = ''.join([row[1] for row in all_rows if row[1]])
    elapsed = time.time() - start
    
    print(f"  結合成功: {len(combined):,} 文字 ({elapsed:.3f}秒)")
    
    # 5. 結合後のBase64検証
    if combined:
        import base64
        try:
            decoded = base64.b64decode(combined)
            print(f"  Base64デコード成功: {len(decoded):,} バイト")
            if decoded[:3] == b'\xff\xd8\xff':
                print(f"  JPEGヘッダー: OK")
        except Exception as e:
            print(f"  Base64デコードエラー: {e}")
    
    conn.close()

if __name__ == "__main__":
    test_large_image()
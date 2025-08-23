#!/usr/bin/env python3
"""重複レコード問題の調査"""

import sqlite3
from pathlib import Path

def check_duplicate_issue():
    db_path = Path(__file__).parent / "tmcloud_v2_20250818_081655.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    app_num = '2025054756'
    
    print(f"出願番号 {app_num} の重複問題調査")
    print("=" * 80)
    
    # 重複レコードの詳細確認
    cursor.execute("""
        SELECT 
            rec_seq_num,
            COUNT(*) as dup_count,
            GROUP_CONCAT(SUBSTR(image_data, 1, 20), ' | ') as data_samples
        FROM trademark_images
        WHERE app_num = ?
        AND image_data IS NOT NULL
        GROUP BY rec_seq_num
        HAVING COUNT(*) > 1
        ORDER BY rec_seq_num
    """, (app_num,))
    
    duplicates = cursor.fetchall()
    print(f"重複のある順序番号: {len(duplicates)}個")
    
    for seq, count, samples in duplicates[:5]:  # 最初の5つだけ表示
        print(f"  順序番号 {seq}: {count}回重複")
        print(f"    データ先頭: {samples}")
    
    # 正しいデータ取得方法（重複を考慮）
    print("\n正しい方法での画像データ取得:")
    
    # ROWIDで最小のレコードのみ取得
    cursor.execute("""
        SELECT rec_seq_num, image_data
        FROM trademark_images
        WHERE app_num = ?
        AND image_data IS NOT NULL
        AND ROWID IN (
            SELECT MIN(ROWID)
            FROM trademark_images
            WHERE app_num = ?
            AND image_data IS NOT NULL
            GROUP BY rec_seq_num
        )
        ORDER BY rec_seq_num
    """, (app_num, app_num))
    
    rows = cursor.fetchall()
    combined = ''.join([row[1] for row in rows])
    
    print(f"  レコード数: {len(rows)}")
    print(f"  結合後サイズ: {len(combined):,} 文字")
    
    # Base64検証
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
    check_duplicate_issue()
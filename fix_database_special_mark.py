#!/usr/bin/env python3
"""
立体商標のspecial_mark_typeを修正するスクリプト
dimensional_trademark_flag='1'の場合、special_mark_type='1'に設定
"""

import sqlite3
from pathlib import Path

def fix_special_mark_type():
    # データベース接続
    db_path = Path(r'C:\Users\ygenk\Desktop\TMCloud\tmcloud_v2_20250818_081655.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # まず現状を確認
    print("=== 修正前の状態 ===")
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM trademark_case_info
        WHERE dimensional_trademark_flag = '1' 
        AND (special_mark_type IS NULL OR special_mark_type = '')
    """)
    count = cursor.fetchone()[0]
    print(f"dimensional_trademark_flag='1'だがspecial_mark_typeが未設定: {count}件")
    
    # 2024061720の確認
    cursor.execute("""
        SELECT app_num, dimensional_trademark_flag, special_mark_type
        FROM trademark_case_info
        WHERE app_num = '2024061720'
    """)
    result = cursor.fetchone()
    if result:
        print(f"\n出願番号2024061720:")
        print(f"  dimensional_trademark_flag: {result[1]}")
        print(f"  special_mark_type: {result[2]}")
    
    # 修正実行
    print("\n=== 修正実行 ===")
    cursor.execute("""
        UPDATE trademark_case_info
        SET special_mark_type = '1'
        WHERE dimensional_trademark_flag = '1'
        AND (special_mark_type IS NULL OR special_mark_type = '')
    """)
    
    updated_count = cursor.rowcount
    print(f"{updated_count}件のレコードを更新しました")
    
    # コミット
    conn.commit()
    
    # 修正後の確認
    print("\n=== 修正後の確認 ===")
    cursor.execute("""
        SELECT app_num, dimensional_trademark_flag, special_mark_type
        FROM trademark_case_info
        WHERE app_num = '2024061720'
    """)
    result = cursor.fetchone()
    if result:
        print(f"出願番号2024061720:")
        print(f"  dimensional_trademark_flag: {result[1]}")
        print(f"  special_mark_type: {result[2]}")
        
    conn.close()
    print("\n修正完了！")

if __name__ == "__main__":
    fix_special_mark_type()
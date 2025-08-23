#!/usr/bin/env python3
"""商標タイプ判定のテストと修正"""

import sqlite3
from pathlib import Path

def test_and_fix():
    db_path = Path(r'C:\Users\ygenk\Desktop\TMCloud\tmcloud_v2_20250818_081655.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== 出願番号2024061720の現状 ===")
    cursor.execute("""
        SELECT app_num, trademark_type, dimensional_trademark_flag, 
               special_mark_type, standard_char_exist
        FROM trademark_case_info
        WHERE app_num = '2024061720'
    """)
    
    result = cursor.fetchone()
    if result:
        print(f"出願番号: {result[0]}")
        print(f"trademark_type: {result[1]}")
        print(f"dimensional_trademark_flag: {result[2]}")
        print(f"special_mark_type: {result[3]}")
        print(f"standard_char_exist: {result[4]}")
        
        # 立体商標として修正するかを判断
        if result[2] != '1' and result[3] != '1':
            print("\n[問題] dimensional_trademark_flagもspecial_mark_typeも設定されていません")
            print("\n立体商標として修正しますか？")
            print("修正する場合は、以下のSQLを実行してください：")
            print(f"""
UPDATE trademark_case_info
SET special_mark_type = '1',
    dimensional_trademark_flag = '1'
WHERE app_num = '2024061720';
            """)
            
            # 修正SQL実行用ファイルを作成
            with open('fix_2024061720.sql', 'w', encoding='utf-8') as f:
                f.write("-- 出願番号2024061720を立体商標に修正\n")
                f.write("UPDATE trademark_case_info\n")
                f.write("SET special_mark_type = '1',\n")
                f.write("    dimensional_trademark_flag = '1'\n")
                f.write("WHERE app_num = '2024061720';\n")
                f.write("\n-- 確認\n")
                f.write("SELECT app_num, special_mark_type, dimensional_trademark_flag\n")
                f.write("FROM trademark_case_info\n")
                f.write("WHERE app_num = '2024061720';\n")
            
            print("\nfix_2024061720.sql を作成しました。")
            print("実行コマンド: sqlite3 tmcloud_v2_20250818_081655.db < fix_2024061720.sql")
    else:
        print("出願番号2024061720が見つかりません")
    
    # 他の立体商標の例を確認
    print("\n=== 他の立体商標の例 ===")
    cursor.execute("""
        SELECT app_num, special_mark_type, dimensional_trademark_flag
        FROM trademark_case_info
        WHERE special_mark_type = '1' OR dimensional_trademark_flag = '1'
        LIMIT 5
    """)
    
    for row in cursor.fetchall():
        print(f"出願番号: {row[0]}, special_mark_type: {row[1]}, dimensional_trademark_flag: {row[2]}")
    
    conn.close()

if __name__ == "__main__":
    test_and_fix()
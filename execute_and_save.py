#!/usr/bin/env python3
"""実行して結果をファイルに保存"""

import sqlite3
import sys
from pathlib import Path

# 標準出力をファイルにリダイレクト
output_file = open(r'C:\Users\ygenk\Desktop\TMCloud\execution_output.txt', 'w', encoding='utf-8')
sys.stdout = output_file

try:
    db_path = Path(r'C:\Users\ygenk\Desktop\TMCloud\tmcloud_v2_20250818_081655.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== 出願番号2024061720の確認結果 ===\n")
    
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
        print(f"dimensional_trademark_flag: '{result[2]}'")
        print(f"special_mark_type: '{result[3]}'")
        print(f"standard_char_exist: '{result[4]}'")
        
        print("\n=== 分析 ===")
        if result[3] == '1':
            print("special_mark_type='1' → 立体商標として判定されるはず")
        elif result[3] in (None, '', 'NULL'):
            print("special_mark_type=NULL/空 → 通常商標として判定される（問題の原因）")
        
        if result[2] == '1':
            print("dimensional_trademark_flag='1' → 立体商標フラグあり")
        elif result[2] in (None, '', 'NULL'):
            print("dimensional_trademark_flag=NULL/空 → 立体商標フラグなし")
    else:
        print("出願番号2024061720が見つかりません")
    
    # 他の立体商標の例
    print("\n=== 立体商標の例 ===")
    cursor.execute("""
        SELECT app_num, special_mark_type, dimensional_trademark_flag
        FROM trademark_case_info
        WHERE special_mark_type = '1'
        LIMIT 3
    """)
    
    for row in cursor.fetchall():
        print(f"出願番号: {row[0]}, special_mark_type: {row[1]}, dimensional_trademark_flag: {row[2]}")
    
    conn.close()
    print("\n実行完了")
    
except Exception as e:
    print(f"エラー: {e}")

finally:
    output_file.close()
    sys.stdout = sys.__stdout__

# 実行したことを示すマーカー
import datetime
with open(r'C:\Users\ygenk\Desktop\TMCloud\execution_marker.txt', 'w') as f:
    f.write(f"Executed at {datetime.datetime.now()}")

print("execution_output.txt に結果を保存しました")
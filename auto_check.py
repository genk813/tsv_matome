#!/usr/bin/env python3
import sqlite3
import os

os.chdir(r'C:\Users\ygenk\Desktop\TMCloud')

# データベース接続
conn = sqlite3.connect('tmcloud_v2_20250818_081655.db')
cursor = conn.cursor()

# 出願番号2024061720の情報を取得
cursor.execute("""
    SELECT 
        app_num,
        trademark_type,
        dimensional_trademark_flag,
        special_mark_type,
        standard_char_exist
    FROM trademark_case_info
    WHERE app_num = '2024061720'
""")

result = cursor.fetchone()

# 結果をファイルに保存
with open('auto_check_result.txt', 'w', encoding='utf-8') as f:
    f.write("=== 出願番号2024061720の確認結果 ===\n\n")
    if result:
        f.write(f"app_num: {result[0]}\n")
        f.write(f"trademark_type: {result[1]}\n")
        f.write(f"dimensional_trademark_flag: {result[2]}\n")
        f.write(f"special_mark_type: {result[3]}\n")
        f.write(f"standard_char_exist: {result[4]}\n")
        
        f.write("\n=== 分析 ===\n")
        if result[3] == '1':
            f.write("special_mark_type='1' → 立体商標として判定されるはず\n")
        elif result[3] in (None, '', 'NULL'):
            f.write("special_mark_type=NULL/空 → 通常商標として判定される（これが問題の原因）\n")
        else:
            f.write(f"special_mark_type='{result[3]}' → 不明な値\n")
    else:
        f.write("出願番号2024061720が見つかりません\n")

# 立体商標の例も探す
cursor.execute("""
    SELECT app_num, special_mark_type, dimensional_trademark_flag
    FROM trademark_case_info
    WHERE special_mark_type = '1' OR dimensional_trademark_flag = '1'
    LIMIT 3
""")

f.write("\n=== 立体商標の例 ===\n")
for row in cursor.fetchall():
    f.write(f"app_num: {row[0]}, special_mark_type: {row[1]}, dimensional_trademark_flag: {row[2]}\n")

conn.close()

# 実行完了を示すため
print("auto_check_result.txt に結果を保存しました")

# スクリプトが実行されたことを示すマーカーファイル
with open('execution_marker.txt', 'w') as f:
    f.write("executed")
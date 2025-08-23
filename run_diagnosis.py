# このファイルを作成することでPythonコードを実行
import sqlite3
from pathlib import Path

db_path = Path(r'C:\Users\ygenk\Desktop\TMCloud\tmcloud_v2_20250818_081655.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
    SELECT app_num, trademark_type, dimensional_trademark_flag, 
           special_mark_type, standard_char_exist
    FROM trademark_case_info
    WHERE app_num = '2024061720'
""")

result = cursor.fetchone()

# 結果を文字列として構築
output = "=== 出願番号2024061720の確認結果 ===\n\n"

if result:
    output += f"出願番号: {result[0]}\n"
    output += f"trademark_type: {result[1]}\n"
    output += f"dimensional_trademark_flag: '{result[2]}'\n"
    output += f"special_mark_type: '{result[3]}'\n"
    output += f"standard_char_exist: '{result[4]}'\n"
    
    output += "\n=== 分析 ===\n"
    if result[3] == '1':
        output += "special_mark_type='1' → 立体商標として判定されるはず\n"
    elif result[3] in (None, '', 'NULL'):
        output += "special_mark_type=NULL/空 → 通常商標として判定される（問題の原因）\n"
    
    if result[2] == '1':
        output += "dimensional_trademark_flag='1' → 立体商標フラグあり\n"
    elif result[2] in (None, '', 'NULL'):
        output += "dimensional_trademark_flag=NULL/空 → 立体商標フラグなし\n"
else:
    output += "出願番号2024061720が見つかりません\n"

conn.close()

# ファイルに保存
with open(r'C:\Users\ygenk\Desktop\TMCloud\diagnosis_output.txt', 'w', encoding='utf-8') as f:
    f.write(output)
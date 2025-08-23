#!/usr/bin/env python3
"""データベースを確認して結果をファイルに保存"""

import sqlite3
import json
from pathlib import Path

# データベース接続
db_path = Path(r"C:\Users\ygenk\Desktop\TMCloud\tmcloud_v2_20250818_081655.db")
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# 出願番号2024061720の情報を取得
app_num = "2024061720"
cursor.execute("""
    SELECT 
        app_num,
        trademark_type,
        dimensional_trademark_flag,
        special_mark_type,
        standard_char_exist
    FROM trademark_case_info
    WHERE app_num = ?
""", (app_num,))

result = cursor.fetchone()
output = {}

if result:
    output = dict(result)
else:
    output = {"error": f"出願番号 {app_num} が見つかりません"}

# 立体商標の例も探す
cursor.execute("""
    SELECT 
        app_num,
        trademark_type,
        dimensional_trademark_flag,
        special_mark_type,
        standard_char_exist
    FROM trademark_case_info
    WHERE special_mark_type = '1' OR dimensional_trademark_flag = '1'
    LIMIT 5
""")

examples = []
for row in cursor.fetchall():
    examples.append(dict(row))

output["立体商標の例"] = examples

# 結果をJSONファイルに保存
output_path = Path(r"C:\Users\ygenk\Desktop\TMCloud\db_check_result.json")
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"結果を {output_path} に保存しました")
conn.close()
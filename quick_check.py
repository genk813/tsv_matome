import sqlite3
import sys

db_path = r"C:\Users\ygenk\Desktop\TMCloud\tmcloud_v2_20250818_081655.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

app_num = "2024061720"
cursor.execute("""
    SELECT app_num, trademark_type, dimensional_trademark_flag, 
           special_mark_type, standard_char_exist
    FROM trademark_case_info
    WHERE app_num = ?
""", (app_num,))

result = cursor.fetchone()
if result:
    for key in result.keys():
        print(f"{key}: {result[key]}")
else:
    print(f"出願番号 {app_num} が見つかりません")

conn.close()
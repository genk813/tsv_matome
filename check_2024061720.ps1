# PowerShellスクリプト - 出願番号2024061720の確認
cd C:\Users\ygenk\Desktop\TMCloud

$pythonScript = @"
import sqlite3
conn = sqlite3.connect('tmcloud_v2_20250818_081655.db')
cursor = conn.cursor()
cursor.execute('''
    SELECT 
        app_num,
        trademark_type,
        dimensional_trademark_flag,
        special_mark_type,
        standard_char_exist
    FROM trademark_case_info 
    WHERE app_num = "2024061720"
''')
result = cursor.fetchone()
if result:
    print(f"app_num: {result[0]}")
    print(f"trademark_type: {result[1]}")
    print(f"dimensional_trademark_flag: {result[2]}")
    print(f"special_mark_type: {result[3]}")
    print(f"standard_char_exist: {result[4]}")
else:
    print("Data not found")
conn.close()
"@

python -c $pythonScript
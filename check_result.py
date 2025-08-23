exec("""
import sqlite3
conn = sqlite3.connect(r'C:\\Users\\ygenk\\Desktop\\TMCloud\\tmcloud_v2_20250818_081655.db')
cursor = conn.cursor()
cursor.execute('SELECT app_num, trademark_type, dimensional_trademark_flag, special_mark_type, standard_char_exist FROM trademark_case_info WHERE app_num = \"2024061720\"')
result = cursor.fetchone()
output = ''
if result:
    output = f'app_num: {result[0]}\\n'
    output += f'trademark_type: {result[1]}\\n'
    output += f'dimensional_trademark_flag: {result[2]}\\n'
    output += f'special_mark_type: {result[3]}\\n'
    output += f'standard_char_exist: {result[4]}\\n'
else:
    output = 'Not found'
with open(r'C:\\Users\\ygenk\\Desktop\\TMCloud\\check_output.txt', 'w') as f:
    f.write(output)
conn.close()
""")
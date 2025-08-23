import sqlite3
import sys
from pathlib import Path

def check_2024061720():
    # データベース接続
    db_path = Path(r'C:\Users\ygenk\Desktop\TMCloud\tmcloud_v2_20250818_081655.db')
    conn = sqlite3.connect(db_path)
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
    
    output = []
    output.append("=== 出願番号2024061720の確認結果 ===\n")
    
    if result:
        output.append(f"app_num: {result[0]}")
        output.append(f"trademark_type: {result[1]}")
        output.append(f"dimensional_trademark_flag: {result[2]}")
        output.append(f"special_mark_type: {result[3]}")
        output.append(f"standard_char_exist: {result[4]}")
        
        output.append("\n=== 分析 ===")
        if result[3] == '1':
            output.append("special_mark_type='1' → 立体商標として判定されるはず")
        elif result[3] in (None, '', 'NULL'):
            output.append("special_mark_type=NULL/空 → 通常商標として判定される（これが問題の原因）")
        else:
            output.append(f"special_mark_type='{result[3]}' → 不明な値")
    else:
        output.append("出願番号2024061720が見つかりません")
    
    conn.close()
    
    # 結果を文字列として返す
    return '\n'.join(output)

# 実行
if __name__ == "__main__":
    result = check_2024061720()
    print(result)
    
    # ファイルにも保存
    with open(r'C:\Users\ygenk\Desktop\TMCloud\check_result_output.txt', 'w', encoding='utf-8') as f:
        f.write(result)
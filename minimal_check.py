#!/usr/bin/env python3
import sqlite3
import os

def check_application():
    db_path = r'C:\Users\ygenk\Desktop\TMCloud\tmcloud_v2_20250818_081655.db'
    
    print(f"データベースファイル存在確認: {os.path.exists(db_path)}")
    
    if not os.path.exists(db_path):
        print("データベースファイルが見つかりません")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 出願番号2024061720を検索
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
        
        print("=== 出願番号2024061720の確認結果 ===")
        if result:
            print(f"app_num: {result[0]}")
            print(f"trademark_type: {result[1]}")
            print(f"dimensional_trademark_flag: {result[2]}")
            print(f"special_mark_type: {result[3]}")
            print(f"standard_char_exist: {result[4]}")
            
            print("\n=== 分析 ===")
            if result[3] == '1':
                print("special_mark_type='1' → 立体商標として判定されるはず")
            elif result[3] in (None, '', 'NULL'):
                print("special_mark_type=NULL/空 → 通常商標として判定される（これが問題の原因）")
            else:
                print(f"special_mark_type='{result[3]}' → 不明な値")
                
            if result[2] == '1':
                print("dimensional_trademark_flag='1' → 立体商標フラグあり")
            elif result[2] in (None, '', 'NULL'):
                print("dimensional_trademark_flag=NULL/空")
            else:
                print(f"dimensional_trademark_flag='{result[2]}'")
        else:
            print("出願番号2024061720が見つかりません")
        
        conn.close()
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    check_application()
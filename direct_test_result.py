#!/usr/bin/env python3
import sqlite3
import sys
import os

# 現在のディレクトリを設定
os.chdir(r"C:\Users\ygenk\Desktop\TMCloud")

# データベースファイル確認
db_file = "tmcloud_v2_20250818_081655.db"
if not os.path.exists(db_file):
    db_file = "tmcloud_v2_20250805_232509.db"
    if not os.path.exists(db_file):
        print("データベースファイルが見つかりません")
        sys.exit(1)

print(f"使用データベース: {db_file}")

try:
    # データベース接続
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    print("\n=== 出願番号2024061720の立体商標判定テスト ===")
    
    # SQL実行
    cursor.execute("""
        SELECT 
            app_num,
            standard_char_exist,
            special_mark_type,
            dimensional_trademark_flag
        FROM trademark_case_info
        WHERE app_num = '2024061720'
    """)
    
    result = cursor.fetchone()
    
    if result:
        app_num, standard_char, special_mark, dimensional_flag = result
        
        print(f"出願番号: {app_num}")
        print(f"標準文字存在: {standard_char}")
        print(f"特殊マーク種別: {special_mark}")
        print(f"立体商標フラグ: {dimensional_flag}")
        
        # 立体商標判定
        is_3d = (special_mark == '1' or dimensional_flag == '1')
        
        if is_3d:
            print("\n✅ 結果: 立体商標として正しく判定されました")
            if special_mark == '1':
                print("理由: special_mark_type = '1' (立体商標)")
            if dimensional_flag == '1':
                print("理由: dimensional_trademark_flag = '1'")
        else:
            print("\n❌ 結果: 立体商標として判定されませんでした")
            print(f"special_mark_type='{special_mark}', dimensional_trademark_flag='{dimensional_flag}'")
    else:
        print("出願番号2024061720のデータが見つかりませんでした")
    
    conn.close()
    
except Exception as e:
    print(f"エラーが発生しました: {e}")
    
print("\nテスト完了")
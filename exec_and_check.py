#!/usr/bin/env python3

# simple_db_test.pyの内容を直接実行
exec_code = """
import sqlite3
import os

# データベースパス
db_path = r"C:\\Users\\ygenk\\Desktop\\TMCloud\\tmcloud_v2_20250818_081655.db"

result_message = []
result_message.append(f"データベースファイル存在確認: {os.path.exists(db_path)}")

if os.path.exists(db_path):
    try:
        # データベース接続
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 出願番号2024061720を検索
        query = '''
            SELECT 
                app_num,
                special_mark_type,
                dimensional_trademark_flag
            FROM trademark_case_info
            WHERE app_num = '2024061720'
        '''
        
        cursor.execute(query)
        result = cursor.fetchone()
        
        if result:
            app_num, special_mark, dimensional_flag = result
            result_message.append(f"出願番号: {app_num}")
            result_message.append(f"特殊マーク種別: {special_mark}")
            result_message.append(f"立体商標フラグ: {dimensional_flag}")
            
            # 立体商標判定
            is_3d = (special_mark == '1' or dimensional_flag == '1')
            result_message.append(f"立体商標判定: {'✅ YES' if is_3d else '❌ NO'}")
            
            final_result = 'SUCCESS' if is_3d else 'FAILED'
            result_message.append(f"最終判定: {final_result}")
            
        else:
            result_message.append("データが見つかりません")
            final_result = 'NOT_FOUND'
        
        conn.close()
        
    except Exception as e:
        result_message.append(f"エラー: {e}")
        final_result = 'ERROR'
        
else:
    result_message.append("データベースファイルが見つかりません")
    # 代替データベースをチェック
    alt_db = r"C:\\Users\\ygenk\\Desktop\\TMCloud\\tmcloud_v2_20250805_232509.db"
    result_message.append(f"代替データベースファイル存在確認: {os.path.exists(alt_db)}")
    final_result = 'NO_DATABASE'

# 結果をファイルに保存
result_file = r"C:\\Users\\ygenk\\Desktop\\TMCloud\\execution_result.txt"
with open(result_file, "w", encoding="utf-8") as f:
    f.write("TMCloud 出願番号2024061720 立体商標判定テスト結果\\n")
    f.write("="*60 + "\\n")
    for msg in result_message:
        f.write(msg + "\\n")
    f.write("="*60 + "\\n")
    f.write(f"実行結果: {final_result}\\n")

# 結果を表示用に格納
test_results = result_message.copy()
test_final = final_result
"""

# 実行
try:
    exec(exec_code)
    print("テスト実行完了")
    
    # 結果表示
    for msg in test_results:
        print(msg)
    print(f"最終結果: {test_final}")
    
    # 結果ファイルの内容を確認
    result_file = r"C:\Users\ygenk\Desktop\TMCloud\execution_result.txt"
    if os.path.exists(result_file):
        print(f"\n結果ファイル作成完了: {result_file}")
    else:
        print("\n結果ファイルの作成に失敗しました")
        
except Exception as e:
    print(f"実行エラー: {e}")
    import traceback
    traceback.print_exc()
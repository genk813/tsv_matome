#!/usr/bin/env python3
"""
最終確認用スクリプト - 結果をprint文で出力
"""

# 実行用コードを文字列として定義
verification_code = '''
import sqlite3
import os

# データベースファイル候補
db_candidates = [
    "C:/Users/ygenk/Desktop/TMCloud/tmcloud_v2_20250818_081655.db",
    "C:/Users/ygenk/Desktop/TMCloud/tmcloud_v2_20250805_232509.db"
]

print("=== TMCloud 立体商標判定テスト ===")

# データベースファイル確認
db_path = None
for db_file in db_candidates:
    print(f"確認中: {os.path.basename(db_file)}")
    if os.path.exists(db_file):
        db_path = db_file
        print(f"✓ データベース発見: {os.path.basename(db_file)}")
        break

if not db_path:
    print("❌ データベースファイルが見つかりません")
    exit()

try:
    # SQLite接続
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\\n出願番号2024061720を検索中...")
    
    # SQL実行
    query = """
        SELECT 
            app_num,
            special_mark_type,
            dimensional_trademark_flag
        FROM trademark_case_info
        WHERE app_num = ?
    """
    
    cursor.execute(query, ("2024061720",))
    result = cursor.fetchone()
    
    print("\\n=== 検索結果 ===")
    
    if result:
        app_num, special_mark_type, dimensional_flag = result
        
        print(f"出願番号: {app_num}")
        print(f"特殊マーク種別: {special_mark_type}")
        print(f"立体商標フラグ: {dimensional_flag}")
        
        # 立体商標判定
        is_3d_trademark = (special_mark_type == "1" or dimensional_flag == "1")
        
        print("\\n=== 立体商標判定 ===")
        if is_3d_trademark:
            print("✅ 結果: 立体商標として正しく判定されました")
            reasons = []
            if special_mark_type == "1":
                reasons.append("special_mark_type = \'1\' (立体商標)")
            if dimensional_flag == "1":
                reasons.append("dimensional_trademark_flag = \'1\'")
            print(f"判定理由: {", ".join(reasons)}")
            final_result = "SUCCESS"
        else:
            print("❌ 結果: 立体商標として判定されませんでした")
            print(f"special_mark_type=\'{special_mark_type}\', dimensional_trademark_flag=\'{dimensional_flag}\'")
            final_result = "FAILED"
    else:
        print("❌ 出願番号2024061720のデータが見つかりませんでした")
        final_result = "NOT_FOUND"
    
    conn.close()
    
    print(f"\\n=== 最終結果: {final_result} ===")
    
except Exception as e:
    print(f"❌ エラーが発生しました: {e}")
    final_result = "ERROR"

print("\\nテスト完了")
'''

# コードを実行
try:
    exec(verification_code)
except Exception as e:
    print(f"実行エラー: {e}")
    import traceback
    traceback.print_exc()
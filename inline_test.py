#!/usr/bin/env python3
"""
インライン実行テスト - 結果を直接print
"""

import sqlite3
import sys
import traceback

print("TMCloud立体商標判定テスト開始")
print("=" * 50)

try:
    # データベースファイルチェック
    import os
    
    db_candidates = [
        r"C:\Users\ygenk\Desktop\TMCloud\tmcloud_v2_20250818_081655.db",
        r"C:\Users\ygenk\Desktop\TMCloud\tmcloud_v2_20250805_232509.db"
    ]
    
    db_path = None
    for db in db_candidates:
        print(f"チェック中: {db}")
        if os.path.exists(db):
            db_path = db
            print(f"✅ データベース発見: {os.path.basename(db)}")
            break
        else:
            print(f"❌ 見つかりません")
    
    if not db_path:
        print("❌ エラー: 利用可能なデータベースが見つかりません")
        sys.exit(1)
    
    # データベース接続
    print(f"\nデータベース接続中: {os.path.basename(db_path)}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # テーブル存在確認
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='trademark_case_info'")
    if not cursor.fetchone():
        print("❌ エラー: trademark_case_infoテーブルが存在しません")
        sys.exit(1)
    
    print("✅ テーブル確認完了")
    
    # メイン検索
    print(f"\n出願番号2024061720を検索中...")
    cursor.execute("""
        SELECT 
            app_num,
            standard_char_exist,
            special_mark_type,
            dimensional_trademark_flag
        FROM trademark_case_info
        WHERE app_num = ?
    """, ('2024061720',))
    
    row = cursor.fetchone()
    
    print("\n" + "=" * 50)
    print("検索結果")
    print("=" * 50)
    
    if row:
        app_num, standard_char, special_mark, dimensional_flag = row
        
        print(f"出願番号: {app_num}")
        print(f"標準文字存在: {standard_char}")
        print(f"特殊マーク種別: {special_mark}")
        print(f"立体商標フラグ: {dimensional_flag}")
        
        # 立体商標判定ロジック
        is_3d_trademark = (special_mark == '1' or dimensional_flag == '1')
        
        print("\n" + "=" * 50)
        print("立体商標判定")
        print("=" * 50)
        
        if is_3d_trademark:
            print("✅ 結果: 立体商標として正しく判定されました")
            
            reasons = []
            if special_mark == '1':
                reasons.append("特殊マーク種別 = '1' (立体商標)")
            if dimensional_flag == '1':
                reasons.append("立体商標フラグ = '1'")
            
            print("判定理由:")
            for reason in reasons:
                print(f"  - {reason}")
            
            final_result = "SUCCESS: 立体商標として正しく判定"
        else:
            print("❌ 結果: 立体商標として判定されませんでした")
            print(f"詳細: special_mark_type='{special_mark}', dimensional_trademark_flag='{dimensional_flag}'")
            final_result = "FAILED: 立体商標として判定されない"
    else:
        print("❌ 出願番号2024061720のデータがデータベースに存在しません")
        final_result = "NOT_FOUND: データが存在しない"
    
    conn.close()
    
    print("\n" + "=" * 50)
    print("最終結果")
    print("=" * 50)
    print(final_result)
    
    # 結果ファイル保存
    result_file = r"C:\Users\ygenk\Desktop\TMCloud\test_result_final.txt"
    with open(result_file, "w", encoding="utf-8") as f:
        f.write(f"TMCloud立体商標判定テスト結果\n")
        f.write(f"実行日時: {__import__('datetime').datetime.now()}\n")
        f.write(f"データベース: {os.path.basename(db_path) if db_path else 'なし'}\n")
        f.write(f"最終結果: {final_result}\n")
        if 'row' in locals() and row:
            f.write(f"\nデータ詳細:\n")
            f.write(f"  出願番号: {app_num}\n")
            f.write(f"  特殊マーク種別: {special_mark}\n") 
            f.write(f"  立体商標フラグ: {dimensional_flag}\n")
    
    print(f"結果を保存しました: {result_file}")

except Exception as e:
    print(f"❌ エラーが発生しました:")
    print(f"エラー内容: {str(e)}")
    print("\nスタックトレース:")
    traceback.print_exc()
    
    # エラーログ保存
    error_file = r"C:\Users\ygenk\Desktop\TMCloud\test_error_log.txt"
    with open(error_file, "w", encoding="utf-8") as f:
        f.write(f"エラーログ\n")
        f.write(f"実行日時: {__import__('datetime').datetime.now()}\n")
        f.write(f"エラー: {str(e)}\n")
        f.write(f"スタックトレース:\n")
        f.write(traceback.format_exc())
    
    print(f"エラーログを保存しました: {error_file}")

print("\nテスト実行完了")

# 直接実行のため、結果を再表示
try:
    result_file = r"C:\Users\ygenk\Desktop\TMCloud\test_result_final.txt"
    if os.path.exists(result_file):
        print("\n" + "=" * 50)
        print("保存された結果ファイル内容")
        print("=" * 50)
        with open(result_file, "r", encoding="utf-8") as f:
            print(f.read())
except:
    pass
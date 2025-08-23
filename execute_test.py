import sqlite3
import os

# ディレクトリ変更
os.chdir(r"C:\Users\ygenk\Desktop\TMCloud")

# データベース確認
db_candidates = [
    "tmcloud_v2_20250818_081655.db",
    "tmcloud_v2_20250805_232509.db"
]

db_path = None
for db in db_candidates:
    if os.path.exists(db):
        db_path = db
        print(f"データベース発見: {db}")
        break

if not db_path:
    print("エラー: データベースが見つかりません")
    exit()

# テスト実行
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n=== 出願番号2024061720の立体商標判定テスト ===")
    
    cursor.execute("""
        SELECT 
            app_num,
            standard_char_exist,
            special_mark_type,
            dimensional_trademark_flag
        FROM trademark_case_info
        WHERE app_num = '2024061720'
    """)
    
    row = cursor.fetchone()
    
    if row:
        app_num, standard_char, special_mark, dimensional_flag = row
        
        print(f"出願番号: {app_num}")
        print(f"標準文字存在: {standard_char}")
        print(f"特殊マーク種別: {special_mark}")
        print(f"立体商標フラグ: {dimensional_flag}")
        
        # 判定ロジック
        is_3d_trademark = (special_mark == '1' or dimensional_flag == '1')
        
        print("\n=== 判定結果 ===")
        if is_3d_trademark:
            print("✅ 立体商標として正しく判定されました")
            reasons = []
            if special_mark == '1':
                reasons.append("special_mark_type = '1' (特殊マーク種別が立体商標)")
            if dimensional_flag == '1':
                reasons.append("dimensional_trademark_flag = '1' (立体商標フラグが設定)")
            print("判定理由:", ", ".join(reasons))
            result = "SUCCESS"
        else:
            print("❌ 立体商標として判定されませんでした")
            print(f"special_mark_type='{special_mark}', dimensional_trademark_flag='{dimensional_flag}'")
            result = "FAILED"
    else:
        print("❌ 出願番号2024061720のデータが見つかりません")
        result = "NOT_FOUND"
    
    conn.close()
    
    # 結果をファイルに保存
    with open("test_execution_result.txt", "w", encoding="utf-8") as f:
        f.write(f"テスト結果: {result}\n")
        f.write(f"データベース: {db_path}\n")
        if row:
            f.write(f"出願番号: {app_num}\n")
            f.write(f"特殊マーク種別: {special_mark}\n") 
            f.write(f"立体商標フラグ: {dimensional_flag}\n")
            f.write(f"立体商標判定: {'YES' if is_3d_trademark else 'NO'}\n")
    
    print(f"\n結果をtest_execution_result.txtに保存しました")
    print(f"最終判定: {result}")
    
except Exception as e:
    print(f"エラーが発生しました: {e}")
    with open("test_execution_error.txt", "w", encoding="utf-8") as f:
        f.write(f"エラー: {str(e)}")

print("テスト実行完了")
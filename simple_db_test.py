import sqlite3
import os

# データベースパス
db_path = r"C:\Users\ygenk\Desktop\TMCloud\tmcloud_v2_20250818_081655.db"

print(f"データベースファイル存在確認: {os.path.exists(db_path)}")

if os.path.exists(db_path):
    try:
        # データベース接続
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 出願番号2024061720を検索
        query = """
            SELECT 
                app_num,
                special_mark_type,
                dimensional_trademark_flag
            FROM trademark_case_info
            WHERE app_num = '2024061720'
        """
        
        cursor.execute(query)
        result = cursor.fetchone()
        
        if result:
            app_num, special_mark, dimensional_flag = result
            print(f"出願番号: {app_num}")
            print(f"特殊マーク種別: {special_mark}")
            print(f"立体商標フラグ: {dimensional_flag}")
            
            # 立体商標判定
            is_3d = (special_mark == '1' or dimensional_flag == '1')
            print(f"立体商標判定: {'✅ YES' if is_3d else '❌ NO'}")
            
            # 結果をファイルに出力
            with open(r"C:\Users\ygenk\Desktop\TMCloud\final_test_result.txt", "w") as f:
                f.write(f"出願番号2024061720の立体商標判定結果\n")
                f.write(f"出願番号: {app_num}\n")
                f.write(f"特殊マーク種別: {special_mark}\n")
                f.write(f"立体商標フラグ: {dimensional_flag}\n")
                f.write(f"立体商標判定: {'YES' if is_3d else 'NO'}\n")
                f.write(f"判定理由: special_mark_type='{special_mark}' or dimensional_trademark_flag='{dimensional_flag}'\n")
        else:
            print("データが見つかりません")
            with open(r"C:\Users\ygenk\Desktop\TMCloud\final_test_result.txt", "w") as f:
                f.write("出願番号2024061720のデータは見つかりませんでした\n")
        
        conn.close()
        print("結果をfinal_test_result.txtに保存しました")
        
    except Exception as e:
        print(f"エラー: {e}")
        with open(r"C:\Users\ygenk\Desktop\TMCloud\final_test_result.txt", "w") as f:
            f.write(f"エラーが発生しました: {e}\n")
else:
    print("データベースファイルが見つかりません")
    # 代替データベースをチェック
    alt_db = r"C:\Users\ygenk\Desktop\TMCloud\tmcloud_v2_20250805_232509.db"
    print(f"代替データベースファイル存在確認: {os.path.exists(alt_db)}")
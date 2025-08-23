#!/usr/bin/env python3

# ここで直接実行してレスポンスを生成
def test_3d_trademark():
    import sqlite3
    import os
    
    # データベースパス
    db_file = r"C:\Users\ygenk\Desktop\TMCloud\tmcloud_v2_20250818_081655.db"
    
    if not os.path.exists(db_file):
        db_file = r"C:\Users\ygenk\Desktop\TMCloud\tmcloud_v2_20250805_232509.db"
        if not os.path.exists(db_file):
            return "エラー: データベースファイルが見つかりません"
    
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # SQL実行
        cursor.execute("""
            SELECT 
                app_num,
                special_mark_type,
                dimensional_trademark_flag
            FROM trademark_case_info
            WHERE app_num = '2024061720'
        """)
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            app_num, special_mark, dimensional_flag = result
            
            # 判定ロジック
            is_3d = (special_mark == '1' or dimensional_flag == '1')
            
            report = f"""=== 出願番号2024061720 立体商標判定結果 ===

データベース: {os.path.basename(db_file)}
出願番号: {app_num}
特殊マーク種別: {special_mark}
立体商標フラグ: {dimensional_flag}

立体商標判定: {'✅ YES (立体商標として判定される)' if is_3d else '❌ NO (立体商標として判定されない)'}

判定理由: special_mark_type='{special_mark}' または dimensional_trademark_flag='{dimensional_flag}'

結論: {'SUCCESS - 正しく立体商標として判定されています' if is_3d else 'FAILED - 立体商標として判定されませんでした'}"""
            
            return report
        else:
            return "エラー: 出願番号2024061720のデータがデータベースに存在しません"
            
    except Exception as e:
        return f"エラー: {str(e)}"

# テスト実行
if __name__ == "__main__":
    result = test_3d_trademark()
    print(result)
    
    # 結果をファイルに保存も試行
    try:
        with open(r"C:\Users\ygenk\Desktop\TMCloud\immediate_result.txt", "w", encoding="utf-8") as f:
            f.write(result)
        print("\n結果をimmediate_result.txtに保存しました")
    except Exception as e:
        print(f"ファイル保存エラー: {e}")
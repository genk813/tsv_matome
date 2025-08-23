import sqlite3
import sys
import os

# データベースファイルのパス
db_path = r"C:\Users\ygenk\Desktop\TMCloud\tmcloud_v2_20250818_081655.db"

# データベースファイルの存在確認
if not os.path.exists(db_path):
    print(f"データベースファイルが見つかりません: {db_path}")
    sys.exit(1)

try:
    # データベースに接続
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 出願番号2024061720の情報を検索
    app_num = "2024061720"
    print(f"出願番号 {app_num} の商標タイプ関連情報を検索中...")
    
    cursor.execute("""
        SELECT app_num, trademark_type, dimensional_trademark_flag, 
               special_mark_type, standard_char_exist
        FROM trademark_case_info
        WHERE app_num = ?
    """, (app_num,))
    
    result = cursor.fetchone()
    if result:
        print("\n検索結果:")
        print("-" * 40)
        for key in result.keys():
            print(f"{key}: {result[key]}")
    else:
        print(f"出願番号 {app_num} が見つかりません")
        
        # テーブル内のレコード数を確認
        cursor.execute("SELECT COUNT(*) as count FROM trademark_case_info")
        count_result = cursor.fetchone()
        print(f"trademark_case_info テーブルの総レコード数: {count_result['count']}")
        
        # 類似の出願番号があるか確認
        cursor.execute("""
            SELECT app_num FROM trademark_case_info 
            WHERE app_num LIKE '2024%' 
            ORDER BY app_num 
            LIMIT 5
        """)
        similar_results = cursor.fetchall()
        if similar_results:
            print("\n2024年の出願番号例:")
            for row in similar_results:
                print(f"  {row['app_num']}")

except sqlite3.Error as e:
    print(f"SQLiteエラー: {e}")
except Exception as e:
    print(f"エラー: {e}")
finally:
    if 'conn' in locals():
        conn.close()
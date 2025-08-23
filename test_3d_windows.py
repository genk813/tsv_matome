#!/usr/bin/env python3
"""
立体商標表示のテストスクリプト（Windows版）
"""

import sqlite3
from pathlib import Path
import sys

# Windowsのパス
DB_PATH = Path(r"C:\Users\ygenk\Desktop\TMCloud\tmcloud_v2_20250818_081655.db")

def test_trademark_type():
    """出願番号2024061720の商標タイプをテスト"""
    
    if not DB_PATH.exists():
        print(f"データベースが見つかりません: {DB_PATH}")
        # 他のデータベースを探す
        alt_db = Path(r"C:\Users\ygenk\Desktop\TMCloud\tmcloud_v2_20250805_232509.db")
        if alt_db.exists():
            print(f"代替データベースを使用: {alt_db}")
            db_path = alt_db
        else:
            return
    else:
        db_path = DB_PATH
    
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("=" * 60)
    print("立体商標フラグの確認（Windows環境）")
    print("=" * 60)
    
    # データベースの状態を確認
    cursor.execute("""
        SELECT 
            app_num,
            standard_char_exist,
            special_mark_type,
            dimensional_trademark_flag,
            special_mark_exist
        FROM trademark_case_info
        WHERE app_num = '2024061720'
    """)
    
    row = cursor.fetchone()
    if row:
        print(f"\n出願番号: {row['app_num']}")
        print(f"standard_char_exist: {row['standard_char_exist']}")
        print(f"special_mark_type: {row['special_mark_type']}")
        print(f"dimensional_trademark_flag: {row['dimensional_trademark_flag']}")
        print(f"special_mark_exist: {row['special_mark_exist']}")
        
        # 判定ロジック
        print("\n商標タイプ判定:")
        if row['standard_char_exist'] == '1':
            print("→ 標準文字")
        elif row['special_mark_type'] == '1' or row['dimensional_trademark_flag'] == '1':
            print("→ ✅ 立体商標（正しく判定されています）")
        else:
            print("→ ❌ 通常（修正が必要）")
    else:
        print("出願番号2024061720が見つかりません")
    
    # 統合検索システムを使ったテスト
    print("\n" + "=" * 60)
    print("統合検索システムでの確認")
    print("=" * 60)
    
    # tmcloud_search_integrated をインポート
    sys.path.insert(0, str(Path(__file__).parent))
    from tmcloud_search_integrated import TMCloudIntegratedSearch
    
    try:
        searcher = TMCloudIntegratedSearch(str(db_path))
        result = searcher.search_by_app_num('2024061720', unified_format=True)
        
        if result:
            print(f"\n出願番号: {result.get('app_num')}")
            print(f"商標名: {result.get('trademark_name')}")
            print(f"商標タイプ: {result.get('trademark_type')}")
            
            if result.get('trademark_type') == '立体商標':
                print("\n✅ 成功: 立体商標が正しく表示されています！")
            else:
                print(f"\n❌ 失敗: 期待値「立体商標」、実際「{result.get('trademark_type')}」")
                print("\n修正が必要な可能性があります。")
    except Exception as e:
        print(f"エラー: {e}")
    
    conn.close()

if __name__ == "__main__":
    test_trademark_type()
    input("\nEnterキーを押して終了...")
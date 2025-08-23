#!/usr/bin/env python3
"""
立体商標表示のテストスクリプト
"""

from tmcloud_search_integrated import TMCloudIntegratedSearch
from pathlib import Path
import json

# データベースパス
DB_PATH = Path(__file__).parent / "tmcloud_v2_20250818_081655.db"

def test_trademark_type():
    """出願番号2024061720の商標タイプをテスト"""
    
    # 検索エンジンを初期化
    searcher = TMCloudIntegratedSearch(str(DB_PATH))
    
    print("=" * 60)
    print("立体商標表示テスト")
    print("=" * 60)
    
    # 出願番号で検索
    result = searcher.search_by_app_num('2024061720', unified_format=True)
    
    if result:
        print(f"\n出願番号: {result.get('app_num')}")
        print(f"商標名: {result.get('trademark_name')}")
        print(f"商標タイプ: {result.get('trademark_type')}")
        
        # デバッグ情報
        print("\n[デバッグ情報]")
        if hasattr(searcher, 'conn'):
            cursor = searcher.conn.cursor()
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
                print(f"standard_char_exist: {row[1]}")
                print(f"special_mark_type: {row[2]}")
                print(f"dimensional_trademark_flag: {row[3]}")
                print(f"special_mark_exist: {row[4]}")
        
        print("\n[期待値]")
        print("商標タイプは「立体商標」と表示されるべき")
        
        # 判定
        if result.get('trademark_type') == '立体商標':
            print("\n✅ テスト成功: 立体商標が正しく表示されています")
        else:
            print(f"\n❌ テスト失敗: 期待値「立体商標」、実際「{result.get('trademark_type')}」")
    else:
        print("❌ エラー: 出願番号2024061720が見つかりません")
    
    # 他の立体商標も確認
    print("\n" + "=" * 60)
    print("他の立体商標の例")
    print("=" * 60)
    
    cursor = searcher.conn.cursor()
    cursor.execute("""
        SELECT app_num, special_mark_type, dimensional_trademark_flag
        FROM trademark_case_info
        WHERE special_mark_type = '1' OR dimensional_trademark_flag = '1'
        LIMIT 5
    """)
    
    for row in cursor.fetchall():
        result = searcher.search_by_app_num(row[0], unified_format=True)
        if result:
            print(f"\n出願番号: {row[0]}")
            print(f"  special_mark_type: {row[1]}")
            print(f"  dimensional_trademark_flag: {row[2]}")
            print(f"  表示される商標タイプ: {result.get('trademark_type')}")

if __name__ == "__main__":
    test_trademark_type()
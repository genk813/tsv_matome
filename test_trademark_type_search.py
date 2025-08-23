#!/usr/bin/env python3
"""商標タイプ検索機能のテスト"""

from tmcloud_search_integrated import TMCloudIntegratedSearch
from pathlib import Path

def test_trademark_type_search():
    db_path = Path(__file__).parent / "tmcloud_v2_20250818_081655.db"
    if not db_path.exists():
        print(f"データベースが見つかりません: {db_path}")
        return
    
    searcher = TMCloudIntegratedSearch(str(db_path))
    
    print("=" * 50)
    print("商標タイプ検索機能テスト")
    print("=" * 50)
    
    # テストケース
    test_cases = [
        ('標準文字', 5),
        ('立体商標', 3),
        ('通常', 10),
        ('?', 5)  # 全タイプ
    ]
    
    for type_name, limit in test_cases:
        print(f"\n【{type_name}の検索】（上限{limit}件）")
        print("-" * 30)
        
        results = searcher.search_by_trademark_type(type_name, limit=limit)
        
        if results:
            print(f"検索結果: {len(results)}件")
            for i, result in enumerate(results[:3], 1):
                print(f"\n{i}. 出願番号: {result.get('app_num')}")
                print(f"   商標名: {result.get('trademark_name', 'N/A')}")
                print(f"   商標タイプ: {result.get('trademark_type', 'N/A')}")
                print(f"   出願日: {result.get('app_date', 'N/A')}")
                print(f"   登録番号: {result.get('reg_num', 'N/A')}")
        else:
            print("該当なし")
    
    # 複合検索のテスト
    print("\n" + "=" * 50)
    print("複合検索テスト（商標タイプ + 区分）")
    print("=" * 50)
    
    conditions = [
        {'type': 'trademark_type', 'keyword': '標準文字'},
        {'type': 'class', 'keyword': '09'}
    ]
    
    results = searcher.search_complex(conditions, operator='AND', limit=5)
    print(f"\n標準文字商標 AND 第9類の検索結果: {len(results)}件")
    
    if results:
        for i, result in enumerate(results[:3], 1):
            print(f"\n{i}. 出願番号: {result.get('app_num')}")
            print(f"   商標名: {result.get('trademark_name', 'N/A')}")
            print(f"   商標タイプ: {result.get('trademark_type', 'N/A')}")
            print(f"   区分: {result.get('classes', 'N/A')}")

if __name__ == "__main__":
    test_trademark_type_search()
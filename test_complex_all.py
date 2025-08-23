#!/usr/bin/env python3
"""複合検索の結果確認（全件表示）"""

from tmcloud_search_integrated import TMCloudIntegratedSearch
from pathlib import Path

def test_complex_search():
    db_path = Path(__file__).parent / "tmcloud_v2_20250818_081655.db"
    searcher = TMCloudIntegratedSearch(str(db_path))
    
    # 立体商標を検索
    conditions = [{'type': 'trademark_type', 'keyword': '立体商標'}]
    
    print("=" * 80)
    print("立体商標の複合検索結果（上位10件）")
    print("=" * 80)
    
    results = searcher.search_complex(conditions, operator='AND', limit=10, unified_format=True)
    
    print(f"\n検索結果: {len(results)}件\n")
    
    for i, result in enumerate(results, 1):
        basic_info = result.get('basic_info', {})
        app_num = basic_info.get('app_num')
        
        print(f"{i}. 出願番号: {app_num}")
        print(f"   商標名: {basic_info.get('trademark_name')}")
        print(f"   画像データ: {'あり' if basic_info.get('trademark_image_data') else 'なし'}")
        print(f"   出願日: {basic_info.get('app_date')}")
        print()

if __name__ == "__main__":
    test_complex_search()
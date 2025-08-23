#!/usr/bin/env python3
"""複合検索の結果確認"""

from tmcloud_search_integrated import TMCloudIntegratedSearch
from pathlib import Path
import json

def test_complex_search():
    db_path = Path(__file__).parent / "tmcloud_v2_20250818_081655.db"
    searcher = TMCloudIntegratedSearch(str(db_path))
    
    # 立体商標を検索
    conditions = [{'type': 'trademark_type', 'keyword': '立体商標'}]
    
    print("=" * 80)
    print("立体商標の複合検索結果")
    print("=" * 80)
    
    results = searcher.search_complex(conditions, operator='AND', limit=10, unified_format=True)
    
    print(f"\n検索結果: {len(results)}件")
    
    # 問題のある出願番号を確認
    target_app_nums = ['2025064433', '2025064506', '2025064160', '2025062137', '2025061841']
    
    for result in results:
        basic_info = result.get('basic_info', {})
        app_num = basic_info.get('app_num')
        
        if app_num in target_app_nums:
            print(f"\n出願番号: {app_num}")
            print(f"  商標名: {basic_info.get('trademark_name')}")
            print(f"  画像データ: {'あり' if basic_info.get('trademark_image_data') else 'なし'}")
            
            # 画像データが存在する場合、最初の50文字を表示
            if basic_info.get('trademark_image_data'):
                img_data = basic_info.get('trademark_image_data')
                print(f"  画像データ先頭: {img_data[:50]}...")
                print(f"  画像データ長: {len(img_data)}")

if __name__ == "__main__":
    test_complex_search()
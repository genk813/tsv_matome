#!/usr/bin/env python3
"""直接検索のテスト"""

from tmcloud_search_integrated import TMCloudIntegratedSearch
from pathlib import Path
import time

def test_direct_search():
    db_path = Path(__file__).parent / "tmcloud_v2_20250818_081655.db"
    searcher = TMCloudIntegratedSearch(str(db_path))
    
    app_num = '2025064433'
    
    print(f"出願番号 {app_num} を直接検索...")
    
    # search_by_app_numを直接使う
    start = time.time()
    result = searcher.search_by_app_num(app_num, unified_format=True)
    elapsed = time.time() - start
    
    print(f"✓ 完了（{elapsed:.2f}秒）")
    
    if result:
        basic_info = result.get('basic_info', {})
        print(f"  商標名: {basic_info.get('trademark_name')}")
        print(f"  画像データ: {'あり' if basic_info.get('trademark_image_data') else 'なし'}")
    
    # search_complexを使った場合
    print(f"\nsearch_complexを使った検索...")
    start = time.time()
    try:
        conditions = [{'type': 'app_num', 'keyword': app_num}]
        results = searcher.search_complex(conditions, operator='AND', limit=1, unified_format=True)
        elapsed = time.time() - start
        print(f"✓ 完了（{elapsed:.2f}秒）")
        
        if results:
            basic_info = results[0].get('basic_info', {})
            print(f"  商標名: {basic_info.get('trademark_name')}")
            print(f"  画像データ: {'あり' if basic_info.get('trademark_image_data') else 'なし'}")
    except Exception as e:
        elapsed = time.time() - start
        print(f"✗ エラー（{elapsed:.2f}秒）: {e}")

if __name__ == "__main__":
    test_direct_search()
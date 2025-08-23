#!/usr/bin/env python3
"""全修正完了後のテスト"""

from tmcloud_search_integrated import TMCloudIntegratedSearch
from tmcloud_search_optimized import TMCloudOptimizedSearch
from tmcloud_search_simple import TMCloudSimpleSearch
from pathlib import Path
import time

def test_all_fixed():
    db_path = Path(__file__).parent / "tmcloud_v2_20250818_081655.db"
    
    # 問題のあった出願番号
    app_nums = ['2025050454', '2025054756', '2025064433']
    
    print("=" * 80)
    print("全修正完了後のテスト")
    print("=" * 80)
    
    # 1. tmcloud_search_integrated.py のテスト
    print("\n【tmcloud_search_integrated.py】")
    searcher1 = TMCloudIntegratedSearch(str(db_path))
    for app_num in app_nums:
        start = time.time()
        result = searcher1.search_by_app_num(app_num, unified_format=True)
        elapsed = time.time() - start
        
        if result:
            basic_info = result.get('basic_info', {})
            image_data = basic_info.get('trademark_image_data')
            print(f"{app_num}: 画像{'あり' if image_data else 'なし'} ({len(image_data) if image_data else 0:,}文字) - {elapsed:.3f}秒")
    
    # 2. tmcloud_search_optimized.py のテスト
    print("\n【tmcloud_search_optimized.py】")
    searcher2 = TMCloudOptimizedSearch(str(db_path))
    for app_num in app_nums:
        start = time.time()
        result = searcher2.get_full_info(app_num)
        elapsed = time.time() - start
        
        if result:
            basic_info = result.get('basic_info', {})
            image_data = basic_info.get('trademark_image_data')
            print(f"{app_num}: 画像{'あり' if image_data else 'なし'} ({len(image_data) if image_data else 0:,}文字) - {elapsed:.3f}秒")
    
    # 3. tmcloud_search_simple.py のテスト
    print("\n【tmcloud_search_simple.py】")
    searcher3 = TMCloudSimpleSearch(str(db_path))
    for app_num in app_nums:
        start = time.time()
        image_data = searcher3.get_image(app_num)
        elapsed = time.time() - start
        print(f"{app_num}: 画像{'あり' if image_data else 'なし'} ({len(image_data) if image_data else 0:,}文字) - {elapsed:.3f}秒")
    
    searcher1.close()
    searcher2.close()
    searcher3.close()

if __name__ == "__main__":
    test_all_fixed()
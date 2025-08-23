#!/usr/bin/env python3
"""検索メソッドのデバッグ"""

from tmcloud_search_integrated import TMCloudIntegratedSearch
from pathlib import Path
import time

def test_search_debug():
    db_path = Path(__file__).parent / "tmcloud_v2_20250818_081655.db"
    searcher = TMCloudIntegratedSearch(str(db_path))
    
    app_num = '2025064433'
    
    print("=" * 80)
    print("検索メソッドのデバッグ")
    print("=" * 80)
    
    # 1. search_by_app_numのテスト
    print("\n1. search_by_app_num (unified_format=False)")
    start = time.time()
    result = searcher.search_by_app_num(app_num, unified_format=False)
    elapsed = time.time() - start
    print(f"  時間: {elapsed:.3f}秒")
    print(f"  結果: {'あり' if result else 'なし'}")
    
    # 2. search_by_app_numのテスト（統一フォーマット）
    print("\n2. search_by_app_num (unified_format=True)")
    start = time.time()
    result = searcher.search_by_app_num(app_num, unified_format=True)
    elapsed = time.time() - start
    print(f"  時間: {elapsed:.3f}秒")
    print(f"  結果: {'あり' if result else 'なし'}")
    if result:
        basic_info = result.get('basic_info', {})
        print(f"  画像データ: {'あり' if basic_info.get('trademark_image_data') else 'なし'}")

if __name__ == "__main__":
    test_search_debug()
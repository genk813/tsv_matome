#!/usr/bin/env python3
"""検索結果の確認"""

from tmcloud_search_integrated import TMCloudIntegratedSearch
from pathlib import Path
import json

def test_search_result():
    db_path = Path(__file__).parent / "tmcloud_v2_20250818_081655.db"
    searcher = TMCloudIntegratedSearch(str(db_path))
    
    app_nums = ['2025064433', '2025064506', '2025064160', '2025062137', '2025061841']
    
    print("=" * 80)
    print("検索結果の確認")
    print("=" * 80)
    
    for app_num in app_nums:
        print(f"\n出願番号: {app_num}")
        print("-" * 60)
        
        # 出願番号で検索
        result = searcher.search_by_app_num(app_num, unified_format=True)
        
        if result:
            basic_info = result.get('basic_info', {})
            
            # 商標名と画像データの確認
            trademark_name = basic_info.get('trademark_name')
            trademark_image = basic_info.get('trademark_image_data')
            
            print(f"  商標名: {trademark_name}")
            print(f"  画像データ: {'あり' if trademark_image else 'なし'}")
            
            if trademark_image:
                # 画像データの最初の50文字を表示
                print(f"  画像データ先頭: {trademark_image[:50]}...")
            
            # 商標タイプの確認
            trademark_type = basic_info.get('trademark_type')
            print(f"  商標タイプ: {trademark_type}")
            
            # special_mark_existの確認
            print(f"  special_mark_exist: {basic_info.get('special_mark_exist', 'N/A')}")
            print(f"  standard_char_exist: {basic_info.get('standard_char_exist', 'N/A')}")
        else:
            print("  データなし")

if __name__ == "__main__":
    test_search_result()
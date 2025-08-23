#!/usr/bin/env python3
"""修正後の画像表示テスト"""

from tmcloud_search_integrated import TMCloudIntegratedSearch
from pathlib import Path

def test_fixed_image():
    db_path = Path(__file__).parent / "tmcloud_v2_20250818_081655.db"
    searcher = TMCloudIntegratedSearch(str(db_path))
    
    # 問題のある出願番号をテスト
    app_nums = ['2025050454', '2025054756']
    
    print("=" * 80)
    print("画像データ結合修正後のテスト")
    print("=" * 80)
    
    for app_num in app_nums:
        print(f"\n出願番号: {app_num}")
        print("-" * 60)
        
        result = searcher.search_by_app_num(app_num, unified_format=True)
        
        if result:
            basic_info = result.get('basic_info', {})
            image_data = basic_info.get('trademark_image_data')
            
            print(f"  商標名: {basic_info.get('trademark_name')}")
            print(f"  画像データ: {'あり' if image_data else 'なし'}")
            
            if image_data:
                print(f"  画像データ長: {len(image_data):,} 文字")
                # Base64の終端を確認
                if image_data.endswith('='):
                    print(f"  Base64終端: OK (=)")
                elif image_data.endswith('/Z'):
                    print(f"  Base64終端: OK (/Z)")
                else:
                    print(f"  Base64終端: {image_data[-10:]}")
                
                # Base64として正しいか確認
                import base64
                try:
                    decoded = base64.b64decode(image_data)
                    print(f"  デコード成功: {len(decoded):,} バイト")
                    # JPEGヘッダー確認
                    if decoded[:3] == b'\xff\xd8\xff':
                        print(f"  JPEGヘッダー: OK")
                    else:
                        print(f"  JPEGヘッダー: NG")
                except Exception as e:
                    print(f"  デコードエラー: {e}")
        else:
            print("  データなし")

if __name__ == "__main__":
    test_fixed_image()
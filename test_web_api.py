#!/usr/bin/env python3
"""Web APIのテスト"""

import requests
import json

def test_web_api():
    base_url = "http://localhost:5000"
    
    # 問題のある出願番号を検索
    app_nums = ['2025064433', '2025064506', '2025064160', '2025062137', '2025061841']
    
    print("=" * 80)
    print("Web API経由での検索テスト")
    print("=" * 80)
    
    for app_num in app_nums:
        print(f"\n出願番号: {app_num}")
        print("-" * 60)
        
        # 出願番号で検索
        conditions = [{'type': 'app_num', 'keyword': app_num}]
        
        try:
            response = requests.post(
                f"{base_url}/search_complex",
                json={
                    'conditions': conditions,
                    'operator': 'AND',
                    'sort_by': 'app_date_desc'
                },
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data['results'] and len(data['results']) > 0:
                    result = data['results'][0]
                    basic_info = result.get('basic_info', {})
                    
                    print(f"  商標名: {basic_info.get('trademark_name')}")
                    
                    # 画像データの有無を確認
                    img_data = basic_info.get('trademark_image_data')
                    if img_data:
                        print(f"  画像データ: あり（{len(img_data)}文字）")
                        print(f"  画像データ先頭: {img_data[:50]}...")
                    else:
                        print(f"  画像データ: なし")
                    
                    print(f"  商標タイプ: {basic_info.get('trademark_type')}")
                else:
                    print("  結果なし")
            else:
                print(f"  エラー: HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            print("  タイムアウト")
        except Exception as e:
            print(f"  エラー: {e}")

if __name__ == "__main__":
    test_web_api()
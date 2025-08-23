#!/usr/bin/env python3
"""シンプルなAPIテスト（タイムアウト短縮）"""

import requests
import time

def test_api():
    base_url = "http://localhost:5000"
    app_num = '2025064433'
    
    print(f"出願番号 {app_num} を検索...")
    
    start = time.time()
    
    try:
        response = requests.post(
            f"{base_url}/search_complex",
            json={
                'conditions': [{'type': 'app_num', 'keyword': app_num}],
                'operator': 'AND'
            },
            timeout=5  # 5秒でタイムアウト
        )
        
        elapsed = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            if data['results']:
                result = data['results'][0]
                basic_info = result.get('basic_info', {})
                print(f"✓ 成功（{elapsed:.2f}秒）")
                print(f"  商標名: {basic_info.get('trademark_name')}")
                print(f"  画像データ: {'あり' if basic_info.get('trademark_image_data') else 'なし'}")
            else:
                print(f"✗ 結果なし（{elapsed:.2f}秒）")
        else:
            print(f"✗ HTTPエラー {response.status_code}（{elapsed:.2f}秒）")
            
    except requests.exceptions.Timeout:
        print(f"✗ タイムアウト（5秒以上）")
    except Exception as e:
        print(f"✗ エラー: {e}")

if __name__ == "__main__":
    test_api()
#!/usr/bin/env python3
"""新しいAPIのテスト"""

import requests
import time

def test_v2_api():
    base_url = "http://localhost:5001"
    
    # 問題のあった出願番号をテスト
    app_nums = ['2025064433', '2025064506', '2025064160', '2025062137', '2025061841']
    
    print("=" * 80)
    print("TMCloud v2 API テスト")
    print("=" * 80)
    
    for app_num in app_nums:
        print(f"\n出願番号: {app_num}")
        
        start = time.time()
        try:
            response = requests.get(f"{base_url}/api/app_num/{app_num}", timeout=5)
            elapsed = time.time() - start
            
            if response.status_code == 200:
                data = response.json()
                info = data.get('basic_info', {})
                
                print(f"  ✅ 成功（{elapsed:.3f}秒）")
                print(f"  商標名: {info.get('trademark_name')}")
                print(f"  画像データ: {'あり' if info.get('trademark_image_data') else 'なし'}")
                print(f"  商標タイプ: {info.get('trademark_type')}")
            else:
                print(f"  ❌ エラー: HTTP {response.status_code}（{elapsed:.3f}秒）")
                
        except requests.exceptions.Timeout:
            print(f"  ❌ タイムアウト（5秒以上）")
        except requests.exceptions.ConnectionError:
            print(f"  ❌ 接続エラー（サーバーが起動していません）")
        except Exception as e:
            print(f"  ❌ エラー: {e}")
    
    # 商標タイプ検索のテスト
    print("\n" + "=" * 80)
    print("商標タイプ検索テスト")
    print("=" * 80)
    
    start = time.time()
    try:
        response = requests.get(f"{base_url}/api/type/立体商標", timeout=5)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 立体商標検索成功（{elapsed:.3f}秒）")
            print(f"  結果: {data['count']}件")
        else:
            print(f"❌ エラー: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == "__main__":
    # サーバー起動を待つ
    time.sleep(2)
    test_v2_api()
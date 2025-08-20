#!/usr/bin/env python3
import requests
import json
import re

# 1. トップページ取得
print("=== WEB画面シミュレーション ===\n")
print("1. トップページアクセス")
response = requests.get('http://localhost:5000/')
if response.status_code == 200:
    print("  ✓ トップページ表示成功")
    # JavaScriptの検索機能を確認
    if 'performSearch' in response.text:
        print("  ✓ JavaScript検索機能あり")
else:
    print(f"  ✗ エラー: {response.status_code}")

# 2. 検索実行（JavaScriptがやることを再現）
print("\n2. 検索実行（出願番号: 2024022742）")
search_data = {
    "keyword": "2024022742",
    "search_type": "app_num"
}

# APIエンドポイントに直接POST
api_response = requests.post(
    'http://localhost:5000/search',
    json=search_data,
    headers={'Content-Type': 'application/json'}
)

if api_response.status_code == 200:
    data = api_response.json()
    if 'results' in data and data['results']:
        result = data['results'][0]['basic_info']
        print(f"  ✓ 検索成功: {result.get('app_num')}")
        print(f"  ✓ 商標名: {result.get('trademark_name')}")
        
        # 中間記録の確認
        if 'progress_records' in result:
            records = result['progress_records']
            print("\n3. 中間記録の表示状態")
            print(f"  審査中間記録: {len(records.get('exam', []))}件")
            for i, rec in enumerate(records.get('exam', [])[:3], 1):
                print(f"    {i}. {rec}")
            
            print(f"  審判中間記録: {len(records.get('trial', []))}件")
            for i, rec in enumerate(records.get('trial', [])[:3], 1):
                print(f"    {i}. {rec}")
            
            print(f"  登録中間記録: {len(records.get('registration', []))}件")
            for i, rec in enumerate(records.get('registration', [])[:3], 1):
                print(f"    {i}. {rec}")
        else:
            print("  ✗ 中間記録が含まれていない")
    else:
        print("  ✗ 検索結果なし")
else:
    print(f"  ✗ API エラー: {api_response.status_code}")
    print(f"  レスポンス: {api_response.text}")

# 3. HTMLでの表示確認（JavaScriptの動作を確認）
print("\n4. HTMLページでのJavaScript関数確認")
if 'formatSearchResults' in response.text:
    print("  ✓ formatSearchResults関数あり")
    
    # 中間記録表示部分のコードを確認
    if 'progress_records' in response.text and 'formatIntermediateRecords' in response.text:
        print("  ✓ 中間記録表示用コードあり")
        
        # 実際の表示セクションを確認
        sections = ['審査中間記録', '審判中間記録', '登録中間記録']
        for section in sections:
            if section in response.text:
                print(f"  ✓ {section}セクションのコードあり")
            else:
                print(f"  ✗ {section}セクションのコードなし")
    else:
        print("  ✗ 中間記録表示用コードなし")
else:
    print("  ✗ formatSearchResults関数なし")

print("\n=== 確認完了 ===")
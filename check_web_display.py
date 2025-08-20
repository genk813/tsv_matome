#!/usr/bin/env python3
import requests
import json

# まず検索を実行
search_data = {"keyword": "2024022742", "search_type": "app_num"}
api_response = requests.post(
    'http://localhost:5000/search',
    json=search_data,
    headers={'Content-Type': 'application/json'}
)

# レスポンスを整形
if api_response.status_code == 200:
    data = api_response.json()
    
    # JavaScriptが生成するHTMLをシミュレート
    if 'results' in data and data['results']:
        result = data['results'][0]['basic_info']
        
        print("=== WEBブラウザでの表示イメージ ===\n")
        print(f"【検索結果】")
        print(f"出願番号: {result.get('app_num')}")
        print(f"商標名: {result.get('trademark_name')}")
        print(f"出願日: {result.get('app_date')}")
        print(f"区分: {', '.join(result.get('classes', []))}")
        
        # 中間記録の表示
        if 'progress_records' in result:
            records = result['progress_records']
            
            # 審査中間記録
            if records.get('exam'):
                print(f"\n【審査中間記録】 ({len(records['exam'])}件)")
                for rec in records['exam']:
                    code, date = rec.split(':', 1) if ':' in rec else (rec, '')
                    print(f"  • {code} ({date})")
            else:
                print("\n【審査中間記録】 なし")
            
            # 審判中間記録
            if records.get('trial'):
                print(f"\n【審判中間記録】 ({len(records['trial'])}件)")
                for rec in records['trial']:
                    code, date = rec.split(':', 1) if ':' in rec else (rec, '')
                    print(f"  • {code} ({date})")
            else:
                print("\n【審判中間記録】 なし")
            
            # 登録中間記録
            if records.get('registration'):
                print(f"\n【登録中間記録】 ({len(records['registration'])}件)")
                for rec in records['registration']:
                    code, date = rec.split(':', 1) if ':' in rec else (rec, '')
                    print(f"  • {code} ({date})")
            else:
                print("\n【登録中間記録】 なし")
        else:
            print("\n✗ 中間記録データが取得できていません")
        
        print("\n" + "="*50)
        print("結論: ", end="")
        if 'progress_records' in result and any(records.values()):
            print("✓ 中間記録は正しく表示される状態です")
        else:
            print("✗ 中間記録の表示に問題があります")
else:
    print(f"✗ API エラー: {api_response.status_code}")
    print(api_response.text)
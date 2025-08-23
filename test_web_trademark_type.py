#!/usr/bin/env python3
"""Webインターフェースの商標タイプ検索機能のテスト"""

import requests
import json

def test_web_trademark_type_search():
    base_url = "http://localhost:5000"
    
    # テストケース
    test_cases = [
        {
            'name': '標準文字商標の検索',
            'conditions': [{'type': 'trademark_type', 'keyword': '標準文字'}],
            'operator': 'AND'
        },
        {
            'name': '立体商標の検索',
            'conditions': [{'type': 'trademark_type', 'keyword': '立体商標'}],
            'operator': 'AND'
        },
        {
            'name': '標準文字商標 AND 第9類',
            'conditions': [
                {'type': 'trademark_type', 'keyword': '標準文字'},
                {'type': 'class', 'keyword': '09'}
            ],
            'operator': 'AND'
        }
    ]
    
    for test in test_cases:
        print(f"\n{'='*50}")
        print(f"テスト: {test['name']}")
        print(f"条件: {test['conditions']}")
        print(f"演算子: {test['operator']}")
        print('-'*50)
        
        try:
            response = requests.post(
                f"{base_url}/search_complex",
                json={
                    'conditions': test['conditions'],
                    'operator': test['operator'],
                    'sort_by': 'app_date_desc'
                },
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"検索結果: {data['count']}件")
                
                # 最初の3件を表示
                for i, result in enumerate(data['results'][:3], 1):
                    print(f"\n{i}. 出願番号: {result.get('app_num')}")
                    print(f"   商標名: {result.get('trademark_name', 'N/A')}")
                    print(f"   商標タイプ: {result.get('trademark_type', 'N/A')}")
                    print(f"   出願日: {result.get('app_date', 'N/A')}")
            else:
                print(f"エラー: HTTP {response.status_code}")
                print(response.text)
                
        except requests.exceptions.ConnectionError:
            print("エラー: Webサーバーに接続できません")
            print("tmcloud_simple_web.pyが起動していることを確認してください")
            break
        except Exception as e:
            print(f"エラー: {e}")

if __name__ == "__main__":
    test_web_trademark_type_search()
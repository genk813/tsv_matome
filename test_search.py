#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup

# HTMLフォームからの検索をシミュレート
response = requests.get('http://localhost:5000/')
soup = BeautifulSoup(response.text, 'html.parser')
print("=== TOP PAGE ===")
print(f"Title: {soup.title.string if soup.title else 'No title'}")

# 検索フォームの送信先を探す
form = soup.find('form')
if form:
    action = form.get('action', '/search')
    method = form.get('method', 'POST').upper()
    print(f"Form action: {action}, method: {method}")
    
    # 検索実行
    if method == 'POST':
        data = {
            'keyword': '2024022742',
            'search_type': 'app_num'
        }
        search_response = requests.post(f'http://localhost:5000{action}', data=data)
    else:
        search_response = requests.get(f'http://localhost:5000{action}', 
                                       params={'keyword': '2024022742', 'search_type': 'app_num'})
    
    # 結果をパース
    result_soup = BeautifulSoup(search_response.text, 'html.parser')
    
    # 中間記録セクションを探す
    sections = ['審査中間記録', '審判中間記録', '登録中間記録']
    for section in sections:
        # h3やh4タグ、またはテキストで探す
        found = False
        for tag in ['h3', 'h4', 'div', 'span']:
            elements = result_soup.find_all(tag, string=lambda text: text and section in text)
            if elements:
                print(f"\n{section}: 見つかりました ({len(elements)}箇所)")
                found = True
                break
        if not found:
            print(f"\n{section}: 見つかりません")
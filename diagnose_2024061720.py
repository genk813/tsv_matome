#!/usr/bin/env python3
"""出願番号2024061720の診断スクリプト"""

import sqlite3
import sys
from pathlib import Path

# パスを追加
sys.path.insert(0, r'C:\Users\ygenk\Desktop\TMCloud')

# データベース直接確認
print("=== データベース直接確認 ===")
db_path = Path(r'C:\Users\ygenk\Desktop\TMCloud\tmcloud_v2_20250818_081655.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# trademark_case_infoテーブルから取得
cursor.execute("""
    SELECT 
        app_num,
        trademark_type,
        dimensional_trademark_flag,
        special_mark_type,
        standard_char_exist
    FROM trademark_case_info
    WHERE app_num = '2024061720'
""")

result = cursor.fetchone()
if result:
    print("trademark_case_info テーブル:")
    print(f"  app_num: {result[0]}")
    print(f"  trademark_type: {result[1]}")
    print(f"  dimensional_trademark_flag: '{result[2]}' (type: {type(result[2])})")
    print(f"  special_mark_type: '{result[3]}' (type: {type(result[3])})")
    print(f"  standard_char_exist: '{result[4]}' (type: {type(result[4])})")
else:
    print("出願番号2024061720がtrademark_case_infoに見つかりません")

# trademark_basic_itemsテーブルも確認
cursor.execute("""
    SELECT 
        app_num,
        trademark_type,
        special_trademark_type
    FROM trademark_basic_items
    WHERE app_num = '2024061720'
""")

result = cursor.fetchone()
if result:
    print("\ntrademark_basic_items テーブル:")
    print(f"  app_num: {result[0]}")
    print(f"  trademark_type: '{result[1]}' (type: {type(result[1])})")
    print(f"  special_trademark_type: '{result[2]}' (type: {type(result[2])})")
else:
    print("出願番号2024061720がtrademark_basic_itemsに見つかりません")

# 検索システムを使った確認
print("\n=== 検索システム経由の確認 ===")
from tmcloud_search_integrated import TMCloudIntegratedSearch

searcher = TMCloudIntegratedSearch(str(db_path))
results = searcher.search_by_number("2024061720")

if results:
    result = results[0]
    print(f"商標タイプ: {result.get('trademark_type', 'N/A')}")
    print(f"special_mark_type (raw): {result.get('special_mark_type', 'N/A')}")
    print(f"dimensional_trademark_flag (raw): {result.get('dimensional_trademark_flag', 'N/A')}")
    
    # 判定ロジックを直接実行
    print("\n=== 判定ロジック確認 ===")
    row_dict = {
        'app_num': '2024061720',
        'special_mark_type': result.get('special_mark_type'),
        'dimensional_trademark_flag': result.get('dimensional_trademark_flag'),
        'standard_char_exist': result.get('standard_char_exist')
    }
    
    trademark_type = searcher._determine_trademark_type(row_dict)
    print(f"判定結果: {trademark_type}")
else:
    print("検索システムで見つかりません")

searcher.close()
conn.close()

# 結果をファイルに保存
with open('diagnose_result.txt', 'w', encoding='utf-8') as f:
    f.write("診断完了。コンソール出力を確認してください。\n")
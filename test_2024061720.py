#!/usr/bin/env python3
"""出願番号2024061720の商標タイプを調査（検索システム経由）"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from tmcloud_search_integrated import TMCloudIntegratedSearch

# 検索システム初期化
db_path = Path("C:/Users/ygenk/Desktop/TMCloud/tmcloud_v2_20250818_081655.db")
searcher = TMCloudIntegratedSearch(str(db_path))

# 出願番号で検索
results = searcher.search_by_number("2024061720")

if results:
    result = results[0]
    print(f"=== 出願番号 2024061720 の詳細情報 ===\n")
    print(f"商標名: {result.get('trademark_name', 'N/A')}")
    print(f"商標タイプ: {result.get('trademark_type', 'N/A')}")
    print(f"出願人: {result.get('applicant_name', 'N/A')}")
    print(f"出願日: {result.get('app_date', 'N/A')}")
    print(f"ステータス: {result.get('status', 'N/A')}")
    
    # デバッグ情報
    print("\n=== デバッグ情報 ===")
    print(f"special_mark_type: {result.get('special_mark_type', 'N/A')}")
    print(f"dimensional_trademark_flag: {result.get('dimensional_trademark_flag', 'N/A')}")
    print(f"standard_char_exist: {result.get('standard_char_exist', 'N/A')}")
else:
    print("出願番号 2024061720 が見つかりません")

searcher.close()
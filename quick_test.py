#!/usr/bin/env python3
"""
クイックテスト - Windows環境で直接実行可能
"""

import sys
import os
from pathlib import Path

print("=" * 60)
print("TMCloud 環境チェック")
print("=" * 60)

# Python環境の確認
print(f"Python バージョン: {sys.version}")
print(f"実行環境: {os.name}")  # 'nt' = Windows, 'posix' = Linux/Mac
print(f"カレントディレクトリ: {os.getcwd()}")

# データベースファイルの確認
print("\nデータベースファイル検索:")
db_patterns = ['tmcloud_v2_*.db', 'tmcloud.db']
found_dbs = []
for pattern in db_patterns:
    for db in Path('.').glob(pattern):
        print(f"  ✓ {db}")
        found_dbs.append(db)

if not found_dbs:
    print("  ✗ データベースファイルが見つかりません")
    sys.exit(1)

# tmcloud_search_integratedのインポートテスト
print("\nモジュールインポートテスト:")
try:
    from tmcloud_search_integrated import TMCloudIntegratedSearch
    print("  ✓ tmcloud_search_integrated モジュール")
except ImportError as e:
    print(f"  ✗ tmcloud_search_integrated: {e}")
    sys.exit(1)

# 簡単な検索テスト
print("\n検索エンジン初期化テスト:")
try:
    db_path = str(found_dbs[0])
    searcher = TMCloudIntegratedSearch(db_path)
    print(f"  ✓ データベース接続成功: {db_path}")
    
    # 出願番号2024061720の検索
    print("\n出願番号2024061720の検索テスト:")
    result = searcher.search_by_app_num('2024061720', unified_format=True)
    if result:
        print(f"  ✓ 検索成功")
        print(f"    商標タイプ: {result.get('trademark_type')}")
        if result.get('trademark_type') == '立体商標':
            print("    ✅ 立体商標が正しく表示されています！")
        else:
            print(f"    ⚠️ 期待値は「立体商標」ですが「{result.get('trademark_type')}」と表示されています")
    else:
        print("  ✗ 出願番号2024061720が見つかりません")
        
except Exception as e:
    print(f"  ✗ エラー: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("テスト完了")
print("=" * 60)
#!/usr/bin/env python3
"""
立体商標表示の最終テスト
"""

import sqlite3
from pathlib import Path

print("=" * 60)
print("立体商標表示 最終テスト")
print("=" * 60)

# データベースファイルを探す
db_files = list(Path(".").glob("tmcloud_v2_*.db"))
if not db_files:
    print("エラー: データベースファイルが見つかりません")
    exit(1)

db_path = db_files[0]
print(f"使用データベース: {db_path}")

# 1. スキーマ確認
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

print("\n1. テーブルスキーマ確認")
print("-" * 40)
cursor.execute("PRAGMA table_info(trademark_case_info)")
columns = cursor.fetchall()

# special_mark関連カラムを探す
special_cols = []
for col in columns:
    if 'special' in col[1].lower() or 'dimensional' in col[1].lower():
        special_cols.append(col[1])
        print(f"  ✓ {col[1]} ({col[2]})")

if not special_cols:
    print("  ✗ special_mark関連カラムが見つかりません")

# 2. 出願番号2024061720のデータ確認
print("\n2. 出願番号2024061720のデータ")
print("-" * 40)

# 存在するカラムのみでクエリを構築
base_cols = ['app_num', 'standard_char_exist']
query_cols = base_cols + special_cols
query = f"SELECT {', '.join(query_cols)} FROM trademark_case_info WHERE app_num = '2024061720'"

cursor.execute(query)
row = cursor.fetchone()

if row:
    for i, col in enumerate(query_cols):
        print(f"  {col}: {row[i]}")
    
    # 判定ロジック
    print("\n3. 商標タイプ判定")
    print("-" * 40)
    if 'special_mark_exist' in special_cols and row[query_cols.index('special_mark_exist')] == '1':
        print("  → 立体商標（special_mark_exist = '1'）")
        print("  ✅ テスト成功")
    else:
        print("  → 通常")
        print("  ❌ テスト失敗: 立体商標として判定されません")
else:
    print("  ✗ データが見つかりません")

# 3. 統合検索システムのテスト
print("\n4. 統合検索システムテスト")
print("-" * 40)

try:
    from tmcloud_search_integrated import TMCloudIntegratedSearch
    searcher = TMCloudIntegratedSearch(str(db_path))
    result = searcher.search_by_app_num('2024061720', unified_format=True)
    
    if result:
        print(f"  商標タイプ: {result.get('trademark_type')}")
        if result.get('trademark_type') == '立体商標':
            print("  ✅ 統合検索システム: 成功")
        else:
            print("  ❌ 統合検索システム: 失敗")
    else:
        print("  ✗ 検索結果なし")
except Exception as e:
    print(f"  ✗ エラー: {e}")

conn.close()

print("\n" + "=" * 60)
print("テスト完了")
print("=" * 60)
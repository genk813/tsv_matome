#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

conn = sqlite3.connect('tmcloud_v2_20250807_213449.db')
cursor = conn.cursor()

# 拒絶理由条文コードの分布確認
cursor.execute("""
    SELECT rejection_reason_code, COUNT(*) as cnt
    FROM trademark_draft_records
    WHERE rejection_reason_code IS NOT NULL
    GROUP BY rejection_reason_code
    ORDER BY cnt DESC
    LIMIT 20
""")

print("拒絶理由条文コードの分布:")
for row in cursor.fetchall():
    if row[0]:  # 空文字列でない場合のみ表示
        print(f"  {row[0]}: {row[1]}件")

# 中間書類コードの分布も確認
cursor.execute("""
    SELECT intermediate_doc_code, COUNT(*) as cnt
    FROM trademark_draft_records
    WHERE intermediate_doc_code IS NOT NULL
    GROUP BY intermediate_doc_code
    ORDER BY cnt DESC
    LIMIT 20
""")

print("\n中間書類コードの分布:")
for row in cursor.fetchall():
    if row[0]:  # 空文字列でない場合のみ表示
        print(f"  {row[0]}: {row[1]}件")

# サンプルデータ確認
cursor.execute("""
    SELECT app_num, intermediate_doc_code, rejection_reason_code, draft_date
    FROM trademark_draft_records
    WHERE rejection_reason_code IS NOT NULL AND rejection_reason_code != ''
    LIMIT 5
""")

print("\nサンプルデータ（拒絶理由あり）:")
for row in cursor.fetchall():
    print(f"  出願番号: {row[0]}, 中間書類: {row[1]}, 拒絶理由: {row[2]}, 起案日: {row[3]}")

conn.close()
import sqlite3
from pathlib import Path

# データベース接続
db_files = sorted(Path(".").glob("tmcloud_v2_*.db"))
conn = sqlite3.connect(str(db_files[-1]))
cursor = conn.cursor()

print("=== 類似群コードデータの確認 ===")

# 出願番号2025061338の類似群コード
cursor.execute("SELECT class_num, similar_group_codes, LENGTH(similar_group_codes) as len FROM trademark_similar_group_codes WHERE app_num = '2025061338'")
for row in cursor.fetchall():
    print(f"出願番号2025061338 - 区分: {row[0]}, 類似群: '{row[1]}', 長さ: {row[2]}")

# 最新データをいくつか確認
print("\n【最新データの類似群コード（出願番号降順）】")
cursor.execute("SELECT app_num, class_num, similar_group_codes FROM trademark_similar_group_codes WHERE app_num LIKE '2025%' ORDER BY app_num DESC LIMIT 10")
for row in cursor.fetchall():
    print(f"{row[0]} - 区分{row[1]}: '{row[2]}'")

conn.close()

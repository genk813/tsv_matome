#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

conn = sqlite3.connect('output.db')
cursor = conn.cursor()

# データが存在する出願番号を確認
print('=== goods_class_artのサンプル ===')
cursor.execute('SELECT * FROM goods_class_art WHERE goods_classes IS NOT NULL AND goods_classes != "" LIMIT 5')
for row in cursor.fetchall():
    print(row)

print('\n=== right_person_art_tのサンプル ===')
cursor.execute('SELECT * FROM right_person_art_t WHERE normalized_app_num IS NOT NULL AND normalized_app_num != "" LIMIT 5')
for row in cursor.fetchall():
    print(row)

print('\n=== jiken_c_tのサンプル ===')
cursor.execute('SELECT * FROM jiken_c_t LIMIT 5')
for row in cursor.fetchall():
    print(row)

# 完全結合のテスト
print('\n=== 完全結合のテスト ===')
cursor.execute('''
    SELECT 
        j.normalized_app_num,
        COALESCE(s.standard_char_t, iu.indct_use_t, su.search_use_t) as mark_text,
        GROUP_CONCAT(DISTINCT gca.goods_classes) AS goods_classes,
        h.right_person_name AS owner_name,
        h.right_person_addr AS owner_addr
    FROM jiken_c_t j
    LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num
    LEFT JOIN indct_use_t_art iu ON j.normalized_app_num = iu.normalized_app_num
    LEFT JOIN search_use_t_art_table su ON j.normalized_app_num = su.normalized_app_num
    LEFT JOIN right_person_art_t h ON j.normalized_app_num = h.normalized_app_num
    LEFT JOIN goods_class_art gca ON j.normalized_app_num = gca.normalized_app_num
    WHERE h.right_person_name IS NOT NULL AND gca.goods_classes IS NOT NULL
    GROUP BY j.normalized_app_num
    LIMIT 5
''')

results = cursor.fetchall()
print(f'結合成功例: {len(results)}件')
for row in results:
    app_num, mark_text, goods_classes, owner_name, owner_addr = row
    print(f'出願番号: {app_num}')
    print(f'  商標文字: {mark_text}')
    print(f'  商品区分: {goods_classes}')
    print(f'  権利者名: {owner_name}')
    print(f'  権利者住所: {owner_addr}')
    print()

conn.close()
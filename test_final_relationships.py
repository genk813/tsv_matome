#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def test_final_relationships():
    conn = sqlite3.connect('output.db')
    cursor = conn.cursor()
    
    print('=== 修正後のデータ関連付けテスト ===')
    
    # 商品区分情報があるもの
    print('\n1. 商品区分情報があるケース:')
    cursor.execute('''
        SELECT j.normalized_app_num, j.reg_reg_ymd, gca.goods_classes
        FROM jiken_c_t j
        JOIN goods_class_art gca ON j.normalized_app_num = gca.normalized_app_num
        WHERE gca.goods_classes IS NOT NULL AND gca.goods_classes != ''
        LIMIT 5
    ''')
    
    goods_cases = cursor.fetchall()
    print(f'出願番号ベースでの商品区分マッチ: {len(goods_cases)}件')
    for app_num, reg_date, goods_class in goods_cases:
        print(f'  {app_num}: 区分{goods_class} (登録日: {reg_date or "なし"})')
    
    # 権利者情報があるもの  
    print('\n2. 権利者情報があるケース:')
    cursor.execute('''
        SELECT j.normalized_app_num, j.reg_reg_ymd, r.right_person_name, r.right_person_addr
        FROM jiken_c_t j
        JOIN right_person_art_t r ON j.normalized_app_num = r.normalized_app_num
        WHERE r.right_person_name IS NOT NULL AND r.right_person_name != ''
        LIMIT 5
    ''')
    
    rights_cases = cursor.fetchall()
    print(f'出願番号ベースでの権利者マッチ: {len(rights_cases)}件')
    for app_num, reg_date, name, addr in rights_cases:
        print(f'  {app_num}: {name} ({addr}) (登録日: {reg_date or "なし"})')
    
    # 完全な結合テスト
    print('\n3. 完全結合テスト（商標文字、権利者、商品区分すべてあり）:')
    cursor.execute('''
        SELECT 
            j.normalized_app_num,
            COALESCE(s.standard_char_t, iu.indct_use_t, su.search_use_t) as mark_text,
            r.right_person_name,
            r.right_person_addr,
            GROUP_CONCAT(DISTINCT gca.goods_classes) AS goods_classes
        FROM jiken_c_t j
        LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num
        LEFT JOIN indct_use_t_art iu ON j.normalized_app_num = iu.normalized_app_num
        LEFT JOIN search_use_t_art_table su ON j.normalized_app_num = su.normalized_app_num
        LEFT JOIN right_person_art_t r ON j.normalized_app_num = r.normalized_app_num
        LEFT JOIN goods_class_art gca ON j.normalized_app_num = gca.normalized_app_num
        WHERE (s.standard_char_t IS NOT NULL OR iu.indct_use_t IS NOT NULL OR su.search_use_t IS NOT NULL)
          AND r.right_person_name IS NOT NULL 
          AND gca.goods_classes IS NOT NULL
        GROUP BY j.normalized_app_num
        LIMIT 5
    ''')
    
    complete_cases = cursor.fetchall()
    print(f'完全な情報があるケース: {len(complete_cases)}件')
    for app_num, mark_text, owner_name, owner_addr, goods_classes in complete_cases:
        print(f'  {app_num}:')
        print(f'    商標: {mark_text}')
        print(f'    権利者: {owner_name} ({owner_addr})')
        print(f'    商品区分: {goods_classes}')
        print()
    
    # 統計情報
    print('4. 統計情報:')
    cursor.execute('SELECT COUNT(*) FROM jiken_c_t')
    total = cursor.fetchone()[0]
    
    cursor.execute('''
        SELECT COUNT(DISTINCT j.normalized_app_num)
        FROM jiken_c_t j
        JOIN goods_class_art gca ON j.normalized_app_num = gca.normalized_app_num
        WHERE gca.goods_classes IS NOT NULL
    ''')
    with_goods = cursor.fetchone()[0]
    
    cursor.execute('''
        SELECT COUNT(DISTINCT j.normalized_app_num)
        FROM jiken_c_t j
        JOIN right_person_art_t r ON j.normalized_app_num = r.normalized_app_num
        WHERE r.right_person_name IS NOT NULL
    ''')
    with_rights = cursor.fetchone()[0]
    
    print(f'  総事件数: {total}')
    print(f'  商品区分あり: {with_goods}件 ({with_goods/total*100:.1f}%)')
    print(f'  権利者情報あり: {with_rights}件 ({with_rights/total*100:.1f}%)')
    
    conn.close()

if __name__ == "__main__":
    test_final_relationships()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def analyze_data_relationships():
    conn = sqlite3.connect('output.db')
    cursor = conn.cursor()
    
    print('=== jiken_c_tの登録日があるもの ===')
    cursor.execute('SELECT normalized_app_num, reg_reg_ymd FROM jiken_c_t WHERE reg_reg_ymd IS NOT NULL AND reg_reg_ymd != "" LIMIT 5')
    for row in cursor.fetchall():
        print(row)
    
    print('\n=== right_person_art_tのreg_numサンプル ===')
    cursor.execute('SELECT reg_num, normalized_app_num, right_person_name FROM right_person_art_t LIMIT 5')
    for row in cursor.fetchall():
        print(row)
    
    # jiken_c_tのnormalized_app_numとright_person_art_tのnormalized_app_numを比較
    print('\n=== 出願番号が一致するものがあるか確認 ===')
    cursor.execute('''
        SELECT j.normalized_app_num, r.normalized_app_num, r.right_person_name
        FROM jiken_c_t j
        JOIN right_person_art_t r ON j.normalized_app_num = r.normalized_app_num
        WHERE r.normalized_app_num != '0000000000'
        LIMIT 5
    ''')
    matches = cursor.fetchall()
    print(f'一致件数: {len(matches)}')
    for row in matches:
        print(row)
    
    # TSVファイルから実際のデータ構造を確認
    print('\n=== TSVファイルの実際のデータ構造確認 ===')
    
    # goods_class_artで実際の出願番号があるもの
    cursor.execute('''
        SELECT normalized_app_num, goods_classes
        FROM goods_class_art 
        WHERE normalized_app_num != '0000000000' 
        AND normalized_app_num IS NOT NULL
        AND goods_classes IS NOT NULL
        LIMIT 5
    ''')
    goods_with_app = cursor.fetchall()
    print(f'商品区分で出願番号があるもの: {len(goods_with_app)}件')
    for row in goods_with_app:
        print(f'  {row}')
    
    # right_person_art_tで実際の出願番号があるもの
    cursor.execute('''
        SELECT normalized_app_num, right_person_name, right_person_addr
        FROM right_person_art_t 
        WHERE normalized_app_num != '0000000000' 
        AND normalized_app_num IS NOT NULL
        LIMIT 5
    ''')
    rights_with_app = cursor.fetchall()
    print(f'\n権利者で出願番号があるもの: {len(rights_with_app)}件')
    for row in rights_with_app:
        print(f'  {row}')
    
    # reg_numベースでの関連付けテスト
    print('\n=== reg_numベースでの関連付けテスト ===')
    # 実際にあるreg_numを使ってテスト
    cursor.execute('SELECT DISTINCT reg_num FROM right_person_art_t WHERE reg_num IS NOT NULL LIMIT 3')
    sample_reg_nums = [row[0] for row in cursor.fetchall()]
    
    for reg_num in sample_reg_nums:
        print(f'\nreg_num: {reg_num}')
        
        # このreg_numの権利者情報
        cursor.execute('SELECT right_person_name, right_person_addr FROM right_person_art_t WHERE reg_num = ?', (reg_num,))
        rights_info = cursor.fetchone()
        if rights_info:
            print(f'  権利者: {rights_info[0]}')
            print(f'  住所: {rights_info[1]}')
        
        # このreg_numの商品区分情報
        cursor.execute('SELECT goods_classes FROM goods_class_art WHERE reg_num = ?', (reg_num,))
        goods_info = cursor.fetchall()
        if goods_info:
            goods_list = [row[0] for row in goods_info if row[0]]
            print(f'  商品区分: {", ".join(goods_list)}')
    
    conn.close()

if __name__ == "__main__":
    analyze_data_relationships()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
検索用商標に§が含まれているレコードの画像データ状況を確認
"""

import sqlite3
from pathlib import Path

def check_section_symbol_trademarks():
    """検索用商標に§が含まれているレコードを調査"""
    
    db_path = Path(__file__).parent / "output.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== 図形文字を含む検索用商標の調査 ===")
    
    # 図形文字を含む検索用商標のレコードを検索（×、●、▲など）
    cursor.execute("""
        SELECT 
            j.normalized_app_num,
            su.search_use_t,
            ts.image_data,
            CASE WHEN ts.image_data IS NOT NULL AND ts.image_data != '' THEN 'あり' ELSE 'なし' END as image_status
        FROM jiken_c_t j
        JOIN search_use_t_art_table su ON j.normalized_app_num = su.normalized_app_num
        LEFT JOIN t_sample ts ON j.normalized_app_num = ts.normalized_app_num
        WHERE su.search_use_t LIKE '%×%' OR su.search_use_t LIKE '%●%' OR su.search_use_t LIKE '%▲%'
        ORDER BY j.normalized_app_num
        LIMIT 30
    """)
    
    results = cursor.fetchall()
    print(f"図形文字を含む検索用商標（最初の30件）:")
    print()
    print("出願番号 | 検索用商標 | 画像データ状況")
    print("-" * 100)
    
    image_exists_count = 0
    image_missing_count = 0
    
    for row in results:
        app_num, search_text, image_data, image_status = row
        search_preview = (search_text[:50] + "...") if len(search_text) > 50 else search_text
        print(f"{app_num} | {search_preview} | {image_status}")
        
        if image_status == 'あり':
            image_exists_count += 1
        else:
            image_missing_count += 1
    
    # 総数も確認
    cursor.execute("""
        SELECT COUNT(*) 
        FROM search_use_t_art_table 
        WHERE search_use_t LIKE '%×%' OR search_use_t LIKE '%●%' OR search_use_t LIKE '%▲%'
    """)
    total_section_count = cursor.fetchone()[0]
    
    # 図形文字を含む検索用商標のうち、画像データがあるものの数
    cursor.execute("""
        SELECT COUNT(DISTINCT j.normalized_app_num)
        FROM jiken_c_t j
        JOIN search_use_t_art_table su ON j.normalized_app_num = su.normalized_app_num
        JOIN t_sample ts ON j.normalized_app_num = ts.normalized_app_num
        WHERE (su.search_use_t LIKE '%×%' OR su.search_use_t LIKE '%●%' OR su.search_use_t LIKE '%▲%')
          AND ts.image_data IS NOT NULL 
          AND ts.image_data != ''
    """)
    total_with_image = cursor.fetchone()[0]
    
    # 図形文字を含む検索用商標のうち、画像データがないものの数
    cursor.execute("""
        SELECT COUNT(DISTINCT j.normalized_app_num)
        FROM jiken_c_t j
        JOIN search_use_t_art_table su ON j.normalized_app_num = su.normalized_app_num
        LEFT JOIN t_sample ts ON j.normalized_app_num = ts.normalized_app_num
        WHERE (su.search_use_t LIKE '%×%' OR su.search_use_t LIKE '%●%' OR su.search_use_t LIKE '%▲%')
          AND (ts.image_data IS NULL OR ts.image_data = '')
    """)
    total_without_image = cursor.fetchone()[0]
    
    print(f"\n=== 統計情報 ===")
    print(f"図形文字を含む検索用商標の総数: {total_section_count}件")
    if total_section_count > 0:
        print(f"そのうち画像データがあるもの: {total_with_image}件 ({total_with_image/total_section_count*100:.1f}%)")
        print(f"そのうち画像データがないもの: {total_without_image}件 ({total_without_image/total_section_count*100:.1f}%)")
    
    # 図形文字を含む検索用商標で画像データがないサンプルを表示
    print(f"\n=== 図形文字を含むが画像データがないサンプル ===")
    cursor.execute("""
        SELECT 
            j.normalized_app_num,
            su.search_use_t
        FROM jiken_c_t j
        JOIN search_use_t_art_table su ON j.normalized_app_num = su.normalized_app_num
        LEFT JOIN t_sample ts ON j.normalized_app_num = ts.normalized_app_num
        WHERE (su.search_use_t LIKE '%×%' OR su.search_use_t LIKE '%●%' OR su.search_use_t LIKE '%▲%')
          AND (ts.image_data IS NULL OR ts.image_data = '')
        ORDER BY j.normalized_app_num
        LIMIT 10
    """)
    
    no_image_samples = cursor.fetchall()
    for app_num, search_text in no_image_samples:
        search_preview = (search_text[:60] + "...") if len(search_text) > 60 else search_text
        print(f"{app_num}: {search_preview}")
    
    conn.close()

if __name__ == "__main__":
    check_section_symbol_trademarks()
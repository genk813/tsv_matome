#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
拡張商標表示問題の分析スクリプト
新しく追加された表示用商標と検索用商標を含めて分析
"""

import sqlite3
from pathlib import Path

def analyze_enhanced_trademark_display():
    """拡張商標表示の問題を分析"""
    
    db_path = Path(__file__).parent / "output.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== 拡張データベース全体の状況 ===")
    cursor.execute("SELECT COUNT(*) FROM jiken_c_t")
    total_cases = cursor.fetchone()[0]
    print(f"総事件数: {total_cases}")
    
    # 各商標テーブルの状況
    tables_info = [
        ('standard_char_t_art', '標準文字商標'),
        ('indct_use_t_art', '表示用商標'),
        ('search_use_t_art_table', '検索用商標'),
        ('t_sample', 'サンプル画像')
    ]
    
    for table, desc in tables_info:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{desc}: {count} レコード")
    
    print("\n=== 商標データのカバー率分析 ===")
    
    # 各商標タイプのカバー率
    for table, desc in tables_info:
        if table == 't_sample':
            cursor.execute(f"""
                SELECT COUNT(DISTINCT j.normalized_app_num) FROM jiken_c_t j
                LEFT JOIN {table} t ON j.normalized_app_num = t.normalized_app_num
                WHERE t.image_data IS NOT NULL AND t.image_data != ''
            """)
        elif table == 'search_use_t_art_table':
            cursor.execute(f"""
                SELECT COUNT(DISTINCT j.normalized_app_num) FROM jiken_c_t j
                LEFT JOIN {table} t ON j.normalized_app_num = t.normalized_app_num
                WHERE t.search_use_t IS NOT NULL AND t.search_use_t != ''
            """)
        elif table == 'indct_use_t_art':
            cursor.execute(f"""
                SELECT COUNT(DISTINCT j.normalized_app_num) FROM jiken_c_t j
                LEFT JOIN {table} t ON j.normalized_app_num = t.normalized_app_num
                WHERE t.indct_use_t IS NOT NULL AND t.indct_use_t != ''
            """)
        else:  # standard_char_t_art
            cursor.execute(f"""
                SELECT COUNT(DISTINCT j.normalized_app_num) FROM jiken_c_t j
                LEFT JOIN {table} t ON j.normalized_app_num = t.normalized_app_num
                WHERE t.standard_char_t IS NOT NULL AND t.standard_char_t != ''
            """)
        
        coverage = cursor.fetchone()[0]
        percentage = coverage / total_cases * 100
        print(f"{desc}カバー率: {coverage}件 ({percentage:.1f}%)")
    
    print("\n=== 商標表示の優先度分析 ===")
    
    # 商標表示の優先度：標準文字 > 表示用商標 > 検索用商標 > 画像
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN s.standard_char_t IS NOT NULL AND s.standard_char_t != '' THEN 1 END) as has_standard,
            COUNT(CASE WHEN i.indct_use_t IS NOT NULL AND i.indct_use_t != '' THEN 1 END) as has_display,
            COUNT(CASE WHEN se.search_use_t IS NOT NULL AND se.search_use_t != '' THEN 1 END) as has_search,
            COUNT(CASE WHEN ts.image_data IS NOT NULL AND ts.image_data != '' THEN 1 END) as has_image
        FROM jiken_c_t j
        LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num
        LEFT JOIN indct_use_t_art i ON j.normalized_app_num = i.normalized_app_num
        LEFT JOIN search_use_t_art_table se ON j.normalized_app_num = se.normalized_app_num
        LEFT JOIN t_sample ts ON j.normalized_app_num = ts.normalized_app_num
    """)
    
    result = cursor.fetchone()
    total, has_standard, has_display, has_search, has_image = result
    
    print(f"標準文字商標: {has_standard}件 ({has_standard/total*100:.1f}%)")
    print(f"表示用商標: {has_display}件 ({has_display/total*100:.1f}%)")
    print(f"検索用商標: {has_search}件 ({has_search/total*100:.1f}%)")
    print(f"画像データ: {has_image}件 ({has_image/total*100:.1f}%)")
    
    # 何らかの商標表示があるもの
    cursor.execute("""
        SELECT COUNT(DISTINCT j.normalized_app_num) FROM jiken_c_t j
        LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num
        LEFT JOIN indct_use_t_art i ON j.normalized_app_num = i.normalized_app_num
        LEFT JOIN search_use_t_art_table se ON j.normalized_app_num = se.normalized_app_num
        LEFT JOIN t_sample ts ON j.normalized_app_num = ts.normalized_app_num
        WHERE (s.standard_char_t IS NOT NULL AND s.standard_char_t != '')
           OR (i.indct_use_t IS NOT NULL AND i.indct_use_t != '')
           OR (se.search_use_t IS NOT NULL AND se.search_use_t != '')
           OR (ts.image_data IS NOT NULL AND ts.image_data != '')
    """)
    
    has_any_trademark = cursor.fetchone()[0]
    print(f"\n何らかの商標表示あり: {has_any_trademark}件 ({has_any_trademark/total*100:.1f}%)")
    print(f"商標表示なし: {total - has_any_trademark}件 ({(total - has_any_trademark)/total*100:.1f}%)")
    
    print("\n=== 商標表示なしの事件分析 ===")
    cursor.execute("""
        SELECT j.normalized_app_num, j.shutugan_bi, j.reg_reg_ymd
        FROM jiken_c_t j
        LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num
        LEFT JOIN indct_use_t_art i ON j.normalized_app_num = i.normalized_app_num
        LEFT JOIN search_use_t_art_table se ON j.normalized_app_num = se.normalized_app_num
        LEFT JOIN t_sample ts ON j.normalized_app_num = ts.normalized_app_num
        WHERE (s.standard_char_t IS NULL OR s.standard_char_t = '')
          AND (i.indct_use_t IS NULL OR i.indct_use_t = '')
          AND (se.search_use_t IS NULL OR se.search_use_t = '')
          AND (ts.image_data IS NULL OR ts.image_data = '')
        ORDER BY j.normalized_app_num
        LIMIT 10
    """)
    
    no_trademark_samples = cursor.fetchall()
    if no_trademark_samples:
        print("商標表示なしの事件サンプル:")
        for sample in no_trademark_samples:
            print(f"  {sample[0]} -> 出願日: {sample[1]} / 登録日: {sample[2] or 'なし'}")
    else:
        print("✅ すべての事件に何らかの商標表示があります！")
    
    print("\n=== 商標表示の優先順位別サンプル ===")
    
    # 各タイプの商標表示のサンプルを取得
    sample_queries = [
        ("標準文字商標", """
            SELECT j.normalized_app_num, s.standard_char_t as trademark_text
            FROM jiken_c_t j
            JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num
            WHERE s.standard_char_t IS NOT NULL AND s.standard_char_t != ''
            ORDER BY j.normalized_app_num LIMIT 5
        """),
        ("表示用商標", """
            SELECT j.normalized_app_num, i.indct_use_t as trademark_text
            FROM jiken_c_t j
            JOIN indct_use_t_art i ON j.normalized_app_num = i.normalized_app_num
            LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num
            WHERE i.indct_use_t IS NOT NULL AND i.indct_use_t != ''
              AND (s.standard_char_t IS NULL OR s.standard_char_t = '')
            ORDER BY j.normalized_app_num LIMIT 5
        """),
        ("検索用商標", """
            SELECT j.normalized_app_num, se.search_use_t as trademark_text
            FROM jiken_c_t j
            JOIN search_use_t_art_table se ON j.normalized_app_num = se.normalized_app_num
            LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num
            LEFT JOIN indct_use_t_art i ON j.normalized_app_num = i.normalized_app_num
            WHERE se.search_use_t IS NOT NULL AND se.search_use_t != ''
              AND (s.standard_char_t IS NULL OR s.standard_char_t = '')
              AND (i.indct_use_t IS NULL OR i.indct_use_t = '')
            ORDER BY j.normalized_app_num LIMIT 5
        """)
    ]
    
    for desc, query in sample_queries:
        cursor.execute(query)
        samples = cursor.fetchall()
        print(f"\n{desc}のサンプル:")
        for sample in samples:
            print(f"  {sample[0]} -> {sample[1]}")
    
    conn.close()

if __name__ == "__main__":
    analyze_enhanced_trademark_display()
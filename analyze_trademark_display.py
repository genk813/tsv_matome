#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
商標表示問題の分析スクリプト
"""

import sqlite3
from pathlib import Path

def analyze_trademark_display():
    """商標表示の問題を分析"""
    
    db_path = Path(__file__).parent / "output.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== データベース全体の状況 ===")
    cursor.execute("SELECT COUNT(*) FROM jiken_c_t")
    total_cases = cursor.fetchone()[0]
    print(f"総事件数: {total_cases}")
    
    cursor.execute("SELECT COUNT(*) FROM standard_char_t_art")
    total_standard_chars = cursor.fetchone()[0]
    print(f"標準文字商標数: {total_standard_chars}")
    
    cursor.execute("SELECT COUNT(*) FROM t_sample")
    total_samples = cursor.fetchone()[0]
    print(f"サンプル画像数: {total_samples}")
    
    print("\n=== 商標表示に関する分析 ===")
    
    # 標準文字商標があるケース
    cursor.execute("""
        SELECT COUNT(*) FROM jiken_c_t j
        LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num
        WHERE s.standard_char_t IS NOT NULL AND s.standard_char_t != ''
    """)
    with_standard_char = cursor.fetchone()[0]
    print(f"標準文字商標がある事件: {with_standard_char}")
    
    # 画像サンプルがあるケース
    cursor.execute("""
        SELECT COUNT(*) FROM jiken_c_t j
        LEFT JOIN t_sample ts ON j.normalized_app_num = ts.normalized_app_num
        WHERE ts.image_data IS NOT NULL AND ts.image_data != ''
    """)
    with_image = cursor.fetchone()[0]
    print(f"画像データがある事件: {with_image}")
    
    # 標準文字も画像もないケース
    cursor.execute("""
        SELECT COUNT(*) FROM jiken_c_t j
        LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num
        LEFT JOIN t_sample ts ON j.normalized_app_num = ts.normalized_app_num
        WHERE (s.standard_char_t IS NULL OR s.standard_char_t = '') 
        AND (ts.image_data IS NULL OR ts.image_data = '')
    """)
    no_trademark = cursor.fetchone()[0]
    print(f"商標表示がない事件: {no_trademark}")
    
    # 統計情報
    print(f"\n=== 統計情報 ===")
    print(f"標準文字商標カバー率: {with_standard_char/total_cases*100:.1f}%")
    print(f"画像データカバー率: {with_image/total_cases*100:.1f}%")
    print(f"商標表示なし率: {no_trademark/total_cases*100:.1f}%")
    
    print("\n=== サンプル事件の詳細 ===")
    cursor.execute("""
        SELECT j.normalized_app_num, s.standard_char_t, 
               CASE WHEN ts.image_data IS NOT NULL THEN 'あり' ELSE 'なし' END as image_status
        FROM jiken_c_t j
        LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num
        LEFT JOIN t_sample ts ON j.normalized_app_num = ts.normalized_app_num
        ORDER BY j.normalized_app_num
        LIMIT 10
    """)
    samples = cursor.fetchall()
    for sample in samples:
        print(f"  {sample[0]} -> 標準文字: {sample[1] or 'なし'} / 画像: {sample[2]}")
    
    print("\n=== 商標表示なしの事件サンプル ===")
    cursor.execute("""
        SELECT j.normalized_app_num, j.shutugan_bi, j.reg_reg_ymd
        FROM jiken_c_t j
        LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num
        LEFT JOIN t_sample ts ON j.normalized_app_num = ts.normalized_app_num
        WHERE (s.standard_char_t IS NULL OR s.standard_char_t = '') 
        AND (ts.image_data IS NULL OR ts.image_data = '')
        ORDER BY j.normalized_app_num
        LIMIT 10
    """)
    no_trademark_samples = cursor.fetchall()
    for sample in no_trademark_samples:
        print(f"  {sample[0]} -> 出願日: {sample[1]} / 登録日: {sample[2] or 'なし'}")
    
    print("\n=== アプリケーション表示チェック ===")
    # アプリケーションでの表示状況を確認
    cursor.execute("""
        SELECT j.normalized_app_num, s.standard_char_t, ts.image_data
        FROM jiken_c_t j
        LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num
        LEFT JOIN t_sample ts ON j.normalized_app_num = ts.normalized_app_num
        WHERE j.normalized_app_num LIKE '%200%'
        ORDER BY j.normalized_app_num
        LIMIT 5
    """)
    app_samples = cursor.fetchall()
    for sample in app_samples:
        has_text = bool(sample[1] and sample[1].strip())
        has_image = bool(sample[2] and sample[2].strip())
        print(f"  {sample[0]} -> テキスト: {has_text} / 画像: {has_image}")
    
    conn.close()

if __name__ == "__main__":
    analyze_trademark_display()
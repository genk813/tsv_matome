#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
from pathlib import Path

def test_search():
    """検索機能の基本動作をテスト"""
    db_path = Path("output.db")
    
    if not db_path.exists():
        print(f"エラー: {db_path} が存在しません")
        return
    
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    
    # テスト検索: "東京"を含む商標を検索
    search_term = "東京"
    
    print(f"\n検索語: '{search_term}'")
    print("="*50)
    
    # 基本検索クエリ
    query = """
        SELECT DISTINCT
            j.normalized_app_num as app_num,
            j.shutugan_bi as app_date,
            j.reg_reg_ymd as reg_date,
            -- 商標テキスト（優先順位: 標準文字 → 表示用 → 検索用）
            COALESCE(s.standard_char_t, iu.indct_use_t, su.search_use_t) as mark_text,
            -- 商品区分
            gca.goods_classes,
            -- 権利者情報（直接結合を試みる）
            rp.right_person_name,
            rp.right_person_addr
        FROM jiken_c_t j
        LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num
        LEFT JOIN indct_use_t_art iu ON j.normalized_app_num = iu.normalized_app_num
        LEFT JOIN search_use_t_art_table su ON j.normalized_app_num = su.normalized_app_num
        LEFT JOIN goods_class_art gca ON j.normalized_app_num = gca.normalized_app_num
        LEFT JOIN reg_mapping rm ON j.normalized_app_num = rm.app_num
        LEFT JOIN right_person_art_t rp ON rm.reg_num = rp.reg_num
        WHERE 
            s.standard_char_t LIKE ? OR
            iu.indct_use_t LIKE ? OR
            su.search_use_t LIKE ?
        LIMIT 10
    """
    
    search_pattern = f"%{search_term}%"
    cur.execute(query, (search_pattern, search_pattern, search_pattern))
    
    results = cur.fetchall()
    
    print(f"\n検索結果: {len(results)}件")
    
    for i, row in enumerate(results, 1):
        print(f"\n--- 結果 {i} ---")
        print(f"出願番号: {row['app_num']}")
        print(f"商標テキスト: {row['mark_text']}")
        print(f"出願日: {row['app_date']}")
        print(f"登録日: {row['reg_date']}")
        print(f"商品区分: {row['goods_classes']}")
        print(f"権利者名: {row['right_person_name']}")
        print(f"権利者住所: {row['right_person_addr']}")
    
    # 権利者情報の取得可能性をテスト
    print("\n\n権利者情報マッピングのテスト")
    print("="*50)
    
    # 特定の登録番号で権利者情報を検索
    test_query = """
        SELECT 
            rp.reg_num,
            rp.right_person_name,
            rp.right_person_addr,
            gca.normalized_app_num
        FROM right_person_art_t rp
        LEFT JOIN goods_class_art gca ON rp.reg_num = gca.reg_num
        WHERE rp.reg_num IS NOT NULL
        AND gca.normalized_app_num IS NOT NULL
        LIMIT 5
    """
    
    cur.execute(test_query)
    mapping_results = cur.fetchall()
    
    print(f"\n登録番号経由のマッピング例:")
    for row in mapping_results:
        print(f"登録番号: {row['reg_num']} → 出願番号: {row['normalized_app_num']}")
        print(f"  権利者: {row['right_person_name']} ({row['right_person_addr']})")
    
    con.close()

if __name__ == "__main__":
    test_search()
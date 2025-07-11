#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
from pathlib import Path

def build_reg_mapping():
    """reg_mappingテーブルを構築"""
    db_path = Path("output.db")
    
    if not db_path.exists():
        print(f"エラー: {db_path} が存在しません")
        return
    
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    
    print("reg_mappingテーブルを構築中...")
    
    # 既存のレコードを削除
    cur.execute("DELETE FROM reg_mapping")
    
    # goods_class_artテーブルから登録番号と出願番号のマッピングを抽出
    insert_query = """
        INSERT INTO reg_mapping (app_num, reg_num)
        SELECT DISTINCT 
            normalized_app_num as app_num,
            reg_num
        FROM goods_class_art
        WHERE normalized_app_num IS NOT NULL
        AND normalized_app_num != '0000000000'
        AND reg_num IS NOT NULL
        AND reg_num != '0000000'
    """
    
    cur.execute(insert_query)
    inserted_count = cur.rowcount
    
    # right_person_art_tから追加のマッピングを試みる
    # （goods_class_artにない登録番号があるかもしれない）
    additional_query = """
        INSERT OR IGNORE INTO reg_mapping (app_num, reg_num)
        SELECT DISTINCT
            gca.normalized_app_num as app_num,
            rp.reg_num
        FROM right_person_art_t rp
        INNER JOIN goods_class_art gca ON rp.reg_num = gca.reg_num
        WHERE gca.normalized_app_num IS NOT NULL
        AND gca.normalized_app_num != '0000000000'
        AND rp.reg_num IS NOT NULL
        AND rp.reg_num != '0000000'
    """
    
    cur.execute(additional_query)
    additional_count = cur.rowcount
    
    con.commit()
    
    # 結果を確認
    cur.execute("SELECT COUNT(*) FROM reg_mapping")
    total_count = cur.fetchone()[0]
    
    print(f"\nreg_mappingテーブル構築完了:")
    print(f"  - goods_class_artから: {inserted_count}件")
    print(f"  - 追加マッピング: {additional_count}件")
    print(f"  - 合計: {total_count}件")
    
    # サンプルデータを表示
    print("\nサンプルマッピング:")
    cur.execute("SELECT app_num, reg_num FROM reg_mapping LIMIT 10")
    for row in cur.fetchall():
        print(f"  出願番号: {row[0]} → 登録番号: {row[1]}")
    
    # 権利者情報が取得できるか確認
    print("\n権利者情報の取得テスト:")
    test_query = """
        SELECT 
            rm.app_num,
            rm.reg_num,
            rp.right_person_name,
            rp.right_person_addr
        FROM reg_mapping rm
        INNER JOIN right_person_art_t rp ON rm.reg_num = rp.reg_num
        LIMIT 5
    """
    
    cur.execute(test_query)
    for row in cur.fetchall():
        print(f"  出願番号: {row[0]} → 権利者: {row[2]} ({row[3]})")
    
    con.close()
    print("\n完了！")

if __name__ == "__main__":
    build_reg_mapping()
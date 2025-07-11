#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import csv
from pathlib import Path

def create_applicant_master_tables():
    """申請人マスターテーブルを作成"""
    db_path = Path("output.db")
    
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    
    # 申請人マスターテーブルの作成
    print("申請人マスターテーブルを作成中...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS applicant_master (
            data_id_cd TEXT,
            appl_cd TEXT PRIMARY KEY,           -- 申請人コード
            appl_name TEXT,                     -- 申請人名
            appl_cana_name TEXT,                -- 申請人カナ名
            appl_postcode TEXT,                 -- 郵便番号
            appl_addr TEXT,                     -- 申請人住所
            wes_join_name TEXT,                 -- 西欧結合名
            wes_join_addr TEXT,                 -- 西欧結合住所
            integ_appl_cd TEXT,                 -- 統合申請人コード
            dbl_reg_integ_mgt_srl_num TEXT      -- 重複登録統合管理連番
        )
    """)
    
    # 統合申請人情報テーブルの作成
    cur.execute("""
        CREATE TABLE IF NOT EXISTS under_integ_applicant (
            appl_cd TEXT,                       -- 申請人コード
            repeat_num TEXT,                    -- 繰り返し番号
            under_integ_appl_cd TEXT,           -- 被統合申請人コード
            PRIMARY KEY (appl_cd, repeat_num)
        )
    """)
    
    # インデックスの作成
    cur.execute("CREATE INDEX IF NOT EXISTS idx_applicant_master_appl_cd ON applicant_master(appl_cd)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_applicant_master_name ON applicant_master(appl_name)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_under_integ_appl_cd ON under_integ_applicant(appl_cd)")
    
    con.commit()
    con.close()
    print("申請人マスターテーブル作成完了")

def import_applicant_master_data():
    """申請人マスターデータをインポート"""
    tsv_path = Path("tsv_data/tsv/upd_appl_reg_info.tsv")
    db_path = Path("output.db")
    
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    
    # 既存データを削除
    cur.execute("DELETE FROM applicant_master")
    
    print("申請人マスターデータをインポート中...")
    
    with open(tsv_path, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f, delimiter='\t')
        headers = next(reader)  # ヘッダー行をスキップ
        
        insert_sql = """
            INSERT INTO applicant_master (
                data_id_cd, appl_cd, appl_name, appl_cana_name, appl_postcode,
                appl_addr, wes_join_name, wes_join_addr, integ_appl_cd, dbl_reg_integ_mgt_srl_num
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        imported_count = 0
        for row in reader:
            try:
                if len(row) >= 10:
                    cur.execute(insert_sql, row[:10])
                    imported_count += 1
            except Exception as e:
                print(f"エラー: {e}, 行: {row}")
                continue
    
    con.commit()
    print(f"申請人マスターデータインポート完了: {imported_count}件")
    
    # サンプルデータを表示
    cur.execute("""
        SELECT appl_cd, appl_name, appl_addr
        FROM applicant_master 
        WHERE appl_name IS NOT NULL 
        AND appl_name != '' 
        AND appl_name NOT LIKE '%省略%'
        LIMIT 10
    """)
    
    print("\n申請人マスターサンプル:")
    for row in cur.fetchall():
        print(f"  コード: {row[0]} → {row[1]} ({row[2]})")
    
    con.close()

def import_integrated_applicant_data():
    """統合申請人データをインポート"""
    tsv_path = Path("tsv_data/tsv/upd_under_integ_appl_info_mgt.tsv")
    db_path = Path("output.db")
    
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    
    # 既存データを削除
    cur.execute("DELETE FROM under_integ_applicant")
    
    print("統合申請人データをインポート中...")
    
    with open(tsv_path, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f, delimiter='\t')
        headers = next(reader)  # ヘッダー行をスキップ
        
        insert_sql = """
            INSERT INTO under_integ_applicant (appl_cd, repeat_num, under_integ_appl_cd)
            VALUES (?, ?, ?)
        """
        
        imported_count = 0
        for row in reader:
            try:
                if len(row) >= 3:
                    cur.execute(insert_sql, row[:3])
                    imported_count += 1
            except Exception as e:
                continue
    
    con.commit()
    print(f"統合申請人データインポート完了: {imported_count}件")
    con.close()

def test_applicant_resolution():
    """申請人名前解決のテスト"""
    db_path = Path("output.db")
    
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    
    print("\n=== 申請人名前解決テスト ===")
    
    # 既存の申請人コードから実際の名前を解決
    test_query = """
        SELECT 
            ap.shutugannindairinin_code,
            am.appl_name,
            am.appl_addr,
            COUNT(*) as usage_count
        FROM jiken_c_t_shutugannindairinin ap
        LEFT JOIN applicant_master am ON ap.shutugannindairinin_code = am.appl_cd
        WHERE ap.shutugannindairinin_sikbt = '1'  -- 申請人のみ
        AND am.appl_name IS NOT NULL
        AND am.appl_name != ''
        AND am.appl_name NOT LIKE '%省略%'
        GROUP BY ap.shutugannindairinin_code, am.appl_name, am.appl_addr
        ORDER BY usage_count DESC
        LIMIT 10
    """
    
    cur.execute(test_query)
    results = cur.fetchall()
    
    print(f"名前解決成功例: {len(results)}件")
    for row in results:
        print(f"  コード: {row['shutugannindairinin_code']} → {row['appl_name']} ({row['appl_addr']}) - {row['usage_count']}件")
    
    # 解決率の統計
    cur.execute("""
        SELECT 
            COUNT(*) as total_applicants,
            COUNT(am.appl_name) as resolved_applicants,
            ROUND(100.0 * COUNT(am.appl_name) / COUNT(*), 1) as resolution_rate
        FROM (
            SELECT DISTINCT shutugannindairinin_code
            FROM jiken_c_t_shutugannindairinin 
            WHERE shutugannindairinin_sikbt = '1'
        ) ap
        LEFT JOIN applicant_master am ON ap.shutugannindairinin_code = am.appl_cd
        WHERE am.appl_name IS NULL OR am.appl_name = '' OR am.appl_name LIKE '%省略%'
    """)
    
    stats = cur.fetchone()
    print(f"\n申請人名前解決統計:")
    print(f"  総申請人コード数: {stats['total_applicants']}")
    print(f"  名前解決成功数: {stats['resolved_applicants']}")
    print(f"  解決率: {stats['resolution_rate']}%")
    
    con.close()

def create_enhanced_search_with_names():
    """実名表示対応の拡張検索テスト"""
    db_path = Path("output.db")
    
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    
    # 実名表示対応検索クエリ
    enhanced_query = """
        SELECT 
            j.normalized_app_num as app_num,
            j.shutugan_bi as app_date,
            j.reg_reg_ymd as reg_date,
            COALESCE(s.standard_char_t, iu.indct_use_t, su.search_use_t) as mark_text,
            gca.goods_classes,
            -- 申請人情報（実名表示）
            CASE 
                WHEN am.appl_name IS NOT NULL AND am.appl_name != '' AND am.appl_name NOT LIKE '%省略%'
                THEN am.appl_name
                ELSE 'コード:' || ap.shutugannindairinin_code
            END as applicant_display,
            am.appl_addr as applicant_address,
            -- 権利者情報（登録済み）
            rp.right_person_name,
            rp.right_person_addr
        FROM jiken_c_t j
        LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num
        LEFT JOIN indct_use_t_art iu ON j.normalized_app_num = iu.normalized_app_num
        LEFT JOIN search_use_t_art_table su ON j.normalized_app_num = su.normalized_app_num
        LEFT JOIN goods_class_art gca ON j.normalized_app_num = gca.normalized_app_num
        LEFT JOIN jiken_c_t_shutugannindairinin ap ON j.normalized_app_num = ap.shutugan_no 
                                                   AND ap.shutugannindairinin_sikbt = '1'
        LEFT JOIN applicant_master am ON ap.shutugannindairinin_code = am.appl_cd
        LEFT JOIN reg_mapping rm ON j.normalized_app_num = rm.app_num
        LEFT JOIN right_person_art_t rp ON rm.reg_num = rp.reg_num
        WHERE 
            s.standard_char_t LIKE ? OR
            iu.indct_use_t LIKE ? OR
            su.search_use_t LIKE ?
        LIMIT 10
    """
    
    # テスト検索
    search_term = "東京"
    search_pattern = f"%{search_term}%"
    
    print(f"\n=== 実名表示対応検索テスト: '{search_term}' ===")
    
    cur.execute(enhanced_query, (search_pattern, search_pattern, search_pattern))
    results = cur.fetchall()
    
    print(f"検索結果: {len(results)}件")
    
    for i, row in enumerate(results, 1):
        print(f"\n--- 結果 {i} ---")
        print(f"出願番号: {row['app_num']}")
        print(f"商標: {row['mark_text']}")
        print(f"出願日: {row['app_date']}")
        print(f"申請人: {row['applicant_display']}")
        if row['applicant_address']:
            print(f"申請人住所: {row['applicant_address']}")
        if row['right_person_name']:
            print(f"権利者: {row['right_person_name']} ({row['right_person_addr']})")
    
    con.close()

if __name__ == "__main__":
    print("=== 申請人マスターシステム構築 ===")
    create_applicant_master_tables()
    import_applicant_master_data()
    import_integrated_applicant_data()
    test_applicant_resolution()
    create_enhanced_search_with_names()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
from pathlib import Path

def create_partial_applicant_mapping():
    """登録済み商標から申請人コードと権利者名の部分的マッピングを作成"""
    db_path = Path("output.db")
    
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    
    # 部分的申請人マッピングテーブルの作成
    cur.execute("""
        CREATE TABLE IF NOT EXISTS applicant_mapping (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            applicant_code TEXT,
            applicant_name TEXT,
            applicant_addr TEXT,
            trademark_count INTEGER,
            confidence_level TEXT,
            created_date TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(applicant_code, applicant_name, applicant_addr)
        )
    """)
    
    # 既存データを削除
    cur.execute("DELETE FROM applicant_mapping")
    
    # 申請人コードと権利者名の関係を抽出
    mapping_query = """
        INSERT OR IGNORE INTO applicant_mapping (applicant_code, applicant_name, applicant_addr, trademark_count, confidence_level)
        SELECT 
            ap.shutugannindairinin_code,
            rp.right_person_name,
            rp.right_person_addr,
            COUNT(*) as trademark_count,
            CASE 
                WHEN COUNT(*) >= 20 THEN '高'
                WHEN COUNT(*) >= 5 THEN '中'
                ELSE '低'
            END as confidence_level
        FROM jiken_c_t_shutugannindairinin ap
        INNER JOIN reg_mapping rm ON ap.shutugan_no = rm.app_num
        INNER JOIN right_person_art_t rp ON rm.reg_num = rp.reg_num
        WHERE ap.shutugannindairinin_sikbt = '1'  -- 申請人のみ
        AND rp.right_person_name IS NOT NULL
        AND rp.right_person_name != ''
        AND ap.shutugannindairinin_code IS NOT NULL
        AND ap.shutugannindairinin_code != ''
        GROUP BY ap.shutugannindairinin_code, rp.right_person_name, rp.right_person_addr
        HAVING COUNT(*) >= 3  -- 3件以上の商標を持つ申請人のみ
    """
    
    cur.execute(mapping_query)
    con.commit()
    
    # 結果を確認
    cur.execute("SELECT COUNT(*) FROM applicant_mapping")
    total_count = cur.fetchone()[0]
    
    print(f"部分的申請人マッピング作成完了: {total_count}件")
    
    # 信頼度別の統計
    cur.execute("""
        SELECT confidence_level, COUNT(*) as count
        FROM applicant_mapping
        GROUP BY confidence_level
        ORDER BY 
            CASE confidence_level 
                WHEN '高' THEN 1 
                WHEN '中' THEN 2 
                WHEN '低' THEN 3 
            END
    """)
    
    print("\n信頼度別統計:")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}件")
    
    # 上位マッピングを表示
    cur.execute("""
        SELECT applicant_code, applicant_name, trademark_count, confidence_level
        FROM applicant_mapping
        ORDER BY trademark_count DESC
        LIMIT 20
    """)
    
    print("\n上位申請人マッピング:")
    for i, row in enumerate(cur.fetchall(), 1):
        print(f"  {i:2d}. {row[0]} → {row[1]} ({row[2]}件, 信頼度:{row[3]})")
    
    con.close()

def create_enhanced_search_with_mapping():
    """マッピングを使った拡張検索機能を作成"""
    db_path = Path("output.db")
    
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    
    # 申請人マッピングを使った検索クエリ
    enhanced_query = """
        SELECT 
            j.normalized_app_num as app_num,
            j.shutugan_bi as app_date,
            j.reg_reg_ymd as reg_date,
            COALESCE(s.standard_char_t, iu.indct_use_t, su.search_use_t) as mark_text,
            gca.goods_classes,
            -- 申請人情報（マッピング使用）
            CASE 
                WHEN am.applicant_name IS NOT NULL THEN am.applicant_name
                ELSE 'コード:' || ap.shutugannindairinin_code
            END as applicant_display,
            am.confidence_level as applicant_confidence,
            -- 代理人情報（コードのみ）
            'コード:' || ag.shutugannindairinin_code as agent_display,
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
        LEFT JOIN (
            SELECT applicant_code, applicant_name, confidence_level,
                   ROW_NUMBER() OVER (PARTITION BY applicant_code ORDER BY trademark_count DESC) as rn
            FROM applicant_mapping
        ) am ON ap.shutugannindairinin_code = am.applicant_code AND am.rn = 1
        LEFT JOIN jiken_c_t_shutugannindairinin ag ON j.normalized_app_num = ag.shutugan_no 
                                                   AND ag.shutugannindairinin_sikbt = '2'
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
    
    print(f"\n=== 拡張検索テスト: '{search_term}' ===")
    
    cur.execute(enhanced_query, (search_pattern, search_pattern, search_pattern))
    results = cur.fetchall()
    
    print(f"検索結果: {len(results)}件")
    
    for i, row in enumerate(results, 1):
        print(f"\n--- 結果 {i} ---")
        print(f"出願番号: {row['app_num']}")
        print(f"商標: {row['mark_text']}")
        print(f"出願日: {row['app_date']}")
        print(f"登録日: {row['reg_date'] if row['reg_date'] else '(未登録)'}")
        print(f"商品区分: {row['goods_classes'] if row['goods_classes'] else '(なし)'}")
        
        # 申請人情報（マッピング使用）
        applicant_info = row['applicant_display']
        if row['applicant_confidence']:
            applicant_info += f" (信頼度:{row['applicant_confidence']})"
        print(f"申請人: {applicant_info}")
        
        print(f"代理人: {row['agent_display'] if row['agent_display'] != 'コード:' else '(なし)'}")
        
        # 権利者情報
        if row['right_person_name']:
            print(f"権利者: {row['right_person_name']} ({row['right_person_addr']})")
        else:
            print("権利者: (未登録)")
    
    con.close()

if __name__ == "__main__":
    print("=== 部分的申請人マッピング作成 ===")
    create_partial_applicant_mapping()
    
    print("\n=== 拡張検索テスト ===")
    create_enhanced_search_with_mapping()
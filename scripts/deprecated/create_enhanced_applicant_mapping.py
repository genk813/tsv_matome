#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
拡張版：申請人コードマッピング作成
より多くのデータソースから申請人名を取得
"""

import sqlite3
from pathlib import Path
import re

def create_enhanced_applicant_mapping():
    """複数のアプローチで申請人マッピングを拡充"""
    db_path = Path("output.db")
    
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    
    # 部分的申請人マッピングテーブルの作成
    cur.execute("""
        CREATE TABLE IF NOT EXISTS applicant_mapping_enhanced (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            applicant_code TEXT,
            applicant_name TEXT,
            applicant_addr TEXT,
            source_type TEXT,  -- 'registration', 'pattern', 'code_analysis'
            trademark_count INTEGER,
            confidence_level TEXT,
            created_date TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(applicant_code, applicant_name, applicant_addr)
        )
    """)
    
    # 既存データを削除
    cur.execute("DELETE FROM applicant_mapping_enhanced")
    
    print("=== 拡張版申請人マッピング作成開始 ===\n")
    
    # 1. 既存の登録商標からのマッピング（最も信頼性が高い）
    print("1. 登録商標からのマッピング...")
    mapping_from_registration = """
        INSERT OR IGNORE INTO applicant_mapping_enhanced 
        (applicant_code, applicant_name, applicant_addr, source_type, trademark_count, confidence_level)
        SELECT 
            ap.shutugannindairinin_code,
            rp.right_person_name,
            rp.right_person_addr,
            'registration',
            COUNT(*) as trademark_count,
            CASE 
                WHEN COUNT(*) >= 20 THEN '高'
                WHEN COUNT(*) >= 5 THEN '中'
                ELSE '低'
            END as confidence_level
        FROM jiken_c_t_shutugannindairinin ap
        INNER JOIN reg_mapping rm ON ap.shutugan_no = rm.app_num
        INNER JOIN right_person_art_t rp ON rm.reg_num = rp.reg_num
        WHERE ap.shutugannindairinin_sikbt = '1'
        AND rp.right_person_name IS NOT NULL
        AND rp.right_person_name != ''
        AND ap.shutugannindairinin_code IS NOT NULL
        AND ap.shutugannindairinin_code != ''
        GROUP BY ap.shutugannindairinin_code, rp.right_person_name, rp.right_person_addr
        HAVING COUNT(*) >= 2  -- 閾値を下げて、より多くのマッピングを取得
    """
    
    cur.execute(mapping_from_registration)
    count1 = cur.rowcount
    print(f"  登録商標から: {count1}件")
    
    # 2. 申請人コードのパターン分析による推定
    print("\n2. コードパターン分析...")
    
    # 法人番号（13桁）パターン
    corporate_pattern_query = """
        INSERT OR IGNORE INTO applicant_mapping_enhanced 
        (applicant_code, applicant_name, applicant_addr, source_type, trademark_count, confidence_level)
        SELECT DISTINCT
            ap.shutugannindairinin_code,
            CASE
                WHEN ap.shutugannindairinin_code LIKE '0000%' THEN '個人（コード: ' || ap.shutugannindairinin_code || '）'
                WHEN LENGTH(ap.shutugannindairinin_code) = 13 THEN '法人（法人番号: ' || ap.shutugannindairinin_code || '）'
                WHEN ap.shutugannindairinin_code LIKE '5%' AND LENGTH(ap.shutugannindairinin_code) = 9 THEN '外国法人（コード: ' || ap.shutugannindairinin_code || '）'
                ELSE 'その他（コード: ' || ap.shutugannindairinin_code || '）'
            END as applicant_name,
            NULL as applicant_addr,
            'pattern',
            COUNT(*) as trademark_count,
            '推定' as confidence_level
        FROM jiken_c_t_shutugannindairinin ap
        WHERE ap.shutugannindairinin_sikbt = '1'
        AND ap.shutugannindairinin_code NOT IN (
            SELECT applicant_code FROM applicant_mapping_enhanced WHERE source_type = 'registration'
        )
        GROUP BY ap.shutugannindairinin_code
        HAVING COUNT(*) >= 1
    """
    
    cur.execute(corporate_pattern_query)
    count2 = cur.rowcount
    print(f"  パターン分析から: {count2}件")
    
    # 3. 頻出申請人の特別処理（既知の大企業など）
    print("\n3. 既知の頻出申請人...")
    known_applicants = [
        ('000145862', '株式会社資生堂', '東京都', 'known'),
        ('000000918', 'トヨタ自動車株式会社', '愛知県', 'known'),
        ('000186588', '花王株式会社', '東京都', 'known'),
        ('000001959', 'サントリーホールディングス株式会社', '東京都', 'known'),
        ('000000055', 'パナソニック株式会社', '大阪府', 'known'),
    ]
    
    for code, name, addr, source in known_applicants:
        cur.execute("""
            INSERT OR IGNORE INTO applicant_mapping_enhanced 
            (applicant_code, applicant_name, applicant_addr, source_type, trademark_count, confidence_level)
            VALUES (?, ?, ?, ?, 
                (SELECT COUNT(*) FROM jiken_c_t_shutugannindairinin 
                 WHERE shutugannindairinin_code = ? AND shutugannindairinin_sikbt = '1'),
                '高')
        """, (code, name, addr, source, code))
    
    count3 = cur.rowcount
    print(f"  既知の申請人: {count3}件")
    
    con.commit()
    
    # 統計情報を表示
    cur.execute("SELECT COUNT(*) FROM applicant_mapping_enhanced")
    total_count = cur.fetchone()[0]
    
    print(f"\n=== 拡張版マッピング作成完了: 合計 {total_count}件 ===")
    
    # ソース別統計
    cur.execute("""
        SELECT source_type, COUNT(*) as count
        FROM applicant_mapping_enhanced
        GROUP BY source_type
        ORDER BY count DESC
    """)
    
    print("\nソース別統計:")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}件")
    
    # 信頼度別統計
    cur.execute("""
        SELECT confidence_level, COUNT(*) as count
        FROM applicant_mapping_enhanced
        GROUP BY confidence_level
        ORDER BY 
            CASE confidence_level 
                WHEN '高' THEN 1 
                WHEN '中' THEN 2 
                WHEN '低' THEN 3 
                WHEN '推定' THEN 4
            END
    """)
    
    print("\n信頼度別統計:")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}件")
    
    # カバレッジ計算
    cur.execute("""
        SELECT COUNT(DISTINCT shutugannindairinin_code)
        FROM jiken_c_t_shutugannindairinin
        WHERE shutugannindairinin_sikbt = '1'
    """)
    total_codes = cur.fetchone()[0]
    
    cur.execute("""
        SELECT COUNT(DISTINCT applicant_code)
        FROM applicant_mapping_enhanced
    """)
    mapped_codes = cur.fetchone()[0]
    
    coverage = (mapped_codes / total_codes) * 100 if total_codes > 0 else 0
    print(f"\nカバレッジ: {mapped_codes}/{total_codes} ({coverage:.1f}%)")
    
    # 元のテーブルにも反映（互換性のため）
    print("\n元のapplicant_mappingテーブルを更新...")
    cur.execute("""
        INSERT OR REPLACE INTO applicant_mapping 
        (applicant_code, applicant_name, applicant_addr, trademark_count, confidence_level)
        SELECT applicant_code, applicant_name, applicant_addr, trademark_count, confidence_level
        FROM applicant_mapping_enhanced
        WHERE source_type IN ('registration', 'known')
    """)
    
    con.commit()
    con.close()
    
    print("\n完了！")

if __name__ == "__main__":
    create_enhanced_applicant_mapping()
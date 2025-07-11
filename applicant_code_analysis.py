#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
from pathlib import Path
from collections import Counter

def analyze_applicant_codes():
    """申請人コードの分析と仕様の理解"""
    db_path = Path("output.db")
    
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    
    print("=== 申請人コード分析 ===")
    
    # 1. 申請人コードの統計
    cur.execute("""
        SELECT 
            shutugannindairinin_sikbt,
            COUNT(*) as count,
            COUNT(DISTINCT shutugannindairinin_code) as unique_codes
        FROM jiken_c_t_shutugannindairinin
        WHERE shutugannindairinin_code IS NOT NULL
        AND shutugannindairinin_code != ''
        GROUP BY shutugannindairinin_sikbt
    """)
    
    print("\n1. 申請人・代理人コードの統計:")
    for row in cur.fetchall():
        sikbt = '申請人' if row[0] == '1' else '代理人' if row[0] == '2' else '不明'
        print(f"   {sikbt}: {row[1]}件 (ユニークコード: {row[2]}個)")
    
    # 2. 申請人コードのパターン分析
    cur.execute("""
        SELECT shutugannindairinin_code, COUNT(*) as count
        FROM jiken_c_t_shutugannindairinin
        WHERE shutugannindairinin_sikbt = '1'
        AND shutugannindairinin_code IS NOT NULL
        GROUP BY shutugannindairinin_code
        ORDER BY count DESC
        LIMIT 10
    """)
    
    print("\n2. 頻出申請人コード（TOP10）:")
    for i, row in enumerate(cur.fetchall(), 1):
        print(f"   {i:2d}. コード: {row[0]} ({row[1]}件)")
    
    # 3. 代理人コードのパターン分析
    cur.execute("""
        SELECT shutugannindairinin_code, COUNT(*) as count
        FROM jiken_c_t_shutugannindairinin
        WHERE shutugannindairinin_sikbt = '2'
        AND shutugannindairinin_code IS NOT NULL
        GROUP BY shutugannindairinin_code
        ORDER BY count DESC
        LIMIT 10
    """)
    
    print("\n3. 頻出代理人コード（TOP10）:")
    for i, row in enumerate(cur.fetchall(), 1):
        print(f"   {i:2d}. コード: {row[0]} ({row[1]}件)")
    
    # 4. 申請人コードのフォーマット分析
    cur.execute("""
        SELECT shutugannindairinin_code
        FROM jiken_c_t_shutugannindairinin
        WHERE shutugannindairinin_sikbt = '1'
        AND shutugannindairinin_code IS NOT NULL
        LIMIT 100
    """)
    
    codes = [row[0] for row in cur.fetchall()]
    code_lengths = [len(code) for code in codes]
    
    print("\n4. 申請人コードの形式分析:")
    print(f"   コード長の分布: {Counter(code_lengths)}")
    print(f"   サンプルコード: {codes[:10]}")
    
    # 5. 申請人コードと権利者の関係性
    cur.execute("""
        SELECT 
            ap.shutugannindairinin_code,
            rp.right_person_name,
            COUNT(*) as count
        FROM jiken_c_t_shutugannindairinin ap
        INNER JOIN reg_mapping rm ON ap.shutugan_no = rm.app_num
        INNER JOIN right_person_art_t rp ON rm.reg_num = rp.reg_num
        WHERE ap.shutugannindairinin_sikbt = '1'
        AND rp.right_person_name IS NOT NULL
        AND rp.right_person_name != ''
        GROUP BY ap.shutugannindairinin_code, rp.right_person_name
        ORDER BY count DESC
        LIMIT 10
    """)
    
    print("\n5. 申請人コード → 権利者名の関係（登録済み商標）:")
    for row in cur.fetchall():
        print(f"   コード: {row[0]} → {row[1]} ({row[2]}件)")
    
    con.close()

def create_applicant_master_proposal():
    """申請人マスターテーブルの提案"""
    print("\n=== 申請人マスターテーブルの提案 ===")
    
    proposal = """
-- 申請人マスターテーブル（仮想）
-- 実際のTSVファイルが必要: upd_申請人マスター.tsv または similar
CREATE TABLE IF NOT EXISTS applicant_master (
    applicant_code TEXT PRIMARY KEY,     -- 申請人コード
    applicant_name TEXT,                 -- 申請人名
    applicant_addr TEXT,                 -- 申請人住所
    applicant_type TEXT,                 -- 申請人種別（個人/法人）
    update_date TEXT,                    -- 更新日
    status TEXT                          -- 状態（有効/無効）
);

-- 代理人マスターテーブル（仮想）
-- 実際のTSVファイルが必要: upd_代理人マスター.tsv または similar
CREATE TABLE IF NOT EXISTS agent_master (
    agent_code TEXT PRIMARY KEY,         -- 代理人コード
    agent_name TEXT,                     -- 代理人名
    agent_addr TEXT,                     -- 代理人住所
    agent_qualification TEXT,            -- 代理人資格
    update_date TEXT,                    -- 更新日
    status TEXT                          -- 状態（有効/無効）
);

-- 申請人情報を含む拡張検索クエリ
SELECT 
    j.normalized_app_num,
    j.shutugan_bi,
    COALESCE(s.standard_char_t, iu.indct_use_t, su.search_use_t) as mark_text,
    -- 申請人情報（マスターテーブル結合）
    am.applicant_name,
    am.applicant_addr,
    -- 代理人情報（マスターテーブル結合）
    ag.agent_name,
    ag.agent_addr,
    -- 権利者情報（登録済み）
    rp.right_person_name,
    rp.right_person_addr
FROM jiken_c_t j
LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num
LEFT JOIN indct_use_t_art iu ON j.normalized_app_num = iu.normalized_app_num
LEFT JOIN search_use_t_art_table su ON j.normalized_app_num = su.normalized_app_num
LEFT JOIN jiken_c_t_shutugannindairinin ap ON j.normalized_app_num = ap.shutugan_no 
                                           AND ap.shutugannindairinin_sikbt = '1'
LEFT JOIN applicant_master am ON ap.shutugannindairinin_code = am.applicant_code
LEFT JOIN jiken_c_t_shutugannindairinin ag ON j.normalized_app_num = ag.shutugan_no 
                                           AND ag.shutugannindairinin_sikbt = '2'
LEFT JOIN agent_master agt ON ag.shutugannindairinin_code = agt.agent_code
LEFT JOIN reg_mapping rm ON j.normalized_app_num = rm.app_num
LEFT JOIN right_person_art_t rp ON rm.reg_num = rp.reg_num;
"""
    
    print(proposal)
    
    print("\n必要なTSVファイル:")
    print("1. 申請人マスターファイル (upd_申請人マスター.tsv)")
    print("   - 申請人コード, 申請人名, 申請人住所, 申請人種別")
    print("2. 代理人マスターファイル (upd_代理人マスター.tsv)")
    print("   - 代理人コード, 代理人名, 代理人住所, 代理人資格")
    print("3. または統合マスターファイル (upd_申請人代理人マスター.tsv)")
    print("   - コード, 名前, 住所, 種別（申請人/代理人）")

def suggest_data_sources():
    """データソースの提案"""
    print("\n=== データソース取得の提案 ===")
    
    suggestions = [
        "1. 特許庁のデータベース公開情報",
        "   - 申請人マスターファイル",
        "   - 代理人マスターファイル",
        "   - 権利者マスターファイル",
        "",
        "2. 可能な代替手段:",
        "   - 登録済み商標の権利者情報から逆引き",
        "   - 申請人コードと権利者名の対応表作成",
        "   - 頻出申請人コードの手動マッピング",
        "",
        "3. 暫定的な解決策:",
        "   - 申請人コードを「申請人コード:XXXXXX」として表示",
        "   - 権利者情報が判明している場合は権利者名を併記",
        "   - ツールチップで「申請人情報は個人情報保護のためコード表示」と説明"
    ]
    
    for suggestion in suggestions:
        print(suggestion)

if __name__ == "__main__":
    analyze_applicant_codes()
    create_applicant_master_proposal()
    suggest_data_sources()
#!/usr/bin/env python3
"""
出願人データの状況調査スクリプト
現在のデータベースにおける出願人情報の充足状況を詳細に調査
"""

import sqlite3
from pathlib import Path

def main():
    # 最新のデータベースファイルを特定
    db_files = sorted(Path('.').glob('tmcloud_v2_*.db'))
    if not db_files:
        print("データベースファイルが見つかりません")
        return
    
    db_path = db_files[-1]
    print(f"使用データベース: {db_path}")
    
    conn = sqlite3.connect(db_path)
    
    print("\n=== データベース構造調査 ===")
    
    # 1. 各テーブルのレコード数
    tables = ['trademark_applicants_agents', 'applicant_registration_info', 'trademark_case_info']
    for table in tables:
        try:
            cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{table}: {count:,}件")
        except sqlite3.OperationalError as e:
            print(f"{table}: エラー ({e})")
    
    print("\n=== 出願人・代理人データ調査 ===")
    
    # 2. 出願人・代理人の種別分布
    try:
        cursor = conn.execute("""
            SELECT applicant_agent_type, COUNT(*) as count
            FROM trademark_applicants_agents
            GROUP BY applicant_agent_type
        """)
        print("種別分布:")
        for row in cursor:
            agent_type = "出願人" if row[0] == '1' else "代理人" if row[0] == '2' else f"不明({row[0]})"
            print(f"  {agent_type}: {row[1]:,}件")
    except sqlite3.OperationalError as e:
        print(f"種別分布調査エラー: {e}")
    
    # 3. 申請人マスタとのマッチング状況
    try:
        cursor = conn.execute("""
            SELECT 
                COUNT(*) as total_applicants,
                COUNT(ar.applicant_code) as matched_applicants,
                ROUND(COUNT(ar.applicant_code) * 100.0 / COUNT(*), 2) as match_rate
            FROM trademark_applicants_agents ta
            LEFT JOIN applicant_registration_info ar ON ta.applicant_agent_code = ar.applicant_code
            WHERE ta.applicant_agent_type = '1'
        """)
        row = cursor.fetchone()
        print(f"\n出願人データのマッチング状況:")
        print(f"  総出願人レコード数: {row[0]:,}件")
        print(f"  申請人マスタとマッチ: {row[1]:,}件")
        print(f"  マッチ率: {row[2]}%")
    except sqlite3.OperationalError as e:
        print(f"マッチング状況調査エラー: {e}")
    
    # 4. 具体的なマッチング例とミスマッチ例
    print("\n=== 具体例調査 ===")
    
    # マッチング成功例
    try:
        cursor = conn.execute("""
            SELECT 
                ta.app_num,
                ta.applicant_agent_code,
                ar.applicant_name
            FROM trademark_applicants_agents ta
            INNER JOIN applicant_registration_info ar ON ta.applicant_agent_code = ar.applicant_code
            WHERE ta.applicant_agent_type = '1'
            LIMIT 5
        """)
        print("マッチング成功例:")
        for row in cursor:
            print(f"  出願番号: {row[0]}, コード: {row[1]}, 名称: {row[2]}")
    except sqlite3.OperationalError as e:
        print(f"成功例調査エラー: {e}")
    
    # マッチング失敗例
    try:
        cursor = conn.execute("""
            SELECT 
                ta.app_num,
                ta.applicant_agent_code,
                '申請人マスタに存在しない' as note
            FROM trademark_applicants_agents ta
            LEFT JOIN applicant_registration_info ar ON ta.applicant_agent_code = ar.applicant_code
            WHERE ta.applicant_agent_type = '1' AND ar.applicant_code IS NULL
            LIMIT 5
        """)
        print("\nマッチング失敗例:")
        for row in cursor:
            print(f"  出願番号: {row[0]}, コード: {row[1]}, 注記: {row[2]}")
    except sqlite3.OperationalError as e:
        print(f"失敗例調査エラー: {e}")
    
    # 5. 申請人マスタに存在するコードのサンプル
    try:
        cursor = conn.execute("""
            SELECT applicant_code, applicant_name
            FROM applicant_registration_info
            WHERE applicant_name IS NOT NULL AND applicant_name != ''
            LIMIT 10
        """)
        print("\n申請人マスタの実例:")
        for row in cursor:
            print(f"  コード: {row[0]}, 名称: {row[1]}")
    except sqlite3.OperationalError as e:
        print(f"申請人マスタ実例調査エラー: {e}")
    
    # 6. 出願人・代理人テーブルで使われているコードのサンプル
    try:
        cursor = conn.execute("""
            SELECT DISTINCT applicant_agent_code
            FROM trademark_applicants_agents
            WHERE applicant_agent_type = '1'
            LIMIT 10
        """)
        print("\n出願人・代理人テーブルで使用中のコード:")
        codes = [row[0] for row in cursor]
        for code in codes:
            print(f"  {code}")
    except sqlite3.OperationalError as e:
        print(f"使用中コード調査エラー: {e}")
    
    conn.close()

if __name__ == '__main__':
    main()
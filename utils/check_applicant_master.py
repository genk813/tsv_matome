#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

conn = sqlite3.connect('tmcloud_v2_20250807_213449.db')
cursor = conn.cursor()

# 申請人マスタレコード数
cursor.execute('SELECT COUNT(*) FROM applicant_registration_info')
print(f'申請人マスタレコード数: {cursor.fetchone()[0]}')

# サンプルデータ
cursor.execute("""
    SELECT applicant_code, applicant_name, applicant_address 
    FROM applicant_registration_info 
    WHERE applicant_name IS NOT NULL AND applicant_name != ''
    LIMIT 5
""")
print('\n申請人マスタのサンプル:')
for row in cursor.fetchall():
    print(f'  コード: {row[0]}, 名前: {row[1]}, 住所: {row[2]}')

# 出願人テーブルとJOINして実際に名前が取得できるか確認
cursor.execute("""
    SELECT COUNT(*)
    FROM trademark_applicants_agents taa
    JOIN applicant_registration_info ari ON taa.applicant_agent_code = ari.applicant_code
    WHERE taa.applicant_agent_type = '1' AND ari.applicant_name IS NOT NULL
""")
print(f'\nJOINで名前が取得できる出願人数: {cursor.fetchone()[0]}')

# JOINしたサンプルデータ
cursor.execute("""
    SELECT taa.app_num, ari.applicant_name, ari.applicant_address
    FROM trademark_applicants_agents taa
    JOIN applicant_registration_info ari ON taa.applicant_agent_code = ari.applicant_code
    WHERE taa.applicant_agent_type = '1' AND ari.applicant_name IS NOT NULL
    LIMIT 5
""")
print('\nJOINしたサンプル:')
for row in cursor.fetchall():
    print(f'  出願番号: {row[0]}, 名前: {row[1]}, 住所: {row[2]}')

conn.close()
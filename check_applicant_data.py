#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
from pathlib import Path

def check_applicant_data():
    """出願人データの実際の内容を確認"""
    db_path = Path("output.db")
    
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    
    # 出願人データの実際の内容を確認
    cur.execute('''
        SELECT shutugan_no, shutugannindairinin_simei, shutugannindairinin_jusho, 
               shutugannindairinin_sikbt, shutugannindairinin_code
        FROM jiken_c_t_shutugannindairinin 
        WHERE shutugannindairinin_code IS NOT NULL 
        AND shutugannindairinin_code != ''
        LIMIT 10
    ''')
    
    print('出願人データ（コード基準）:')
    for row in cur.fetchall():
        sikbt = '出願人' if row[3] == '1' else '代理人' if row[3] == '2' else '不明'
        print(f'出願番号: {row[0]}, 識別: {sikbt}, コード: {row[4]}')
        print(f'  氏名: "{row[1]}"')
        print(f'  住所: "{row[2]}"')
        print()
    
    # 識別別の統計
    cur.execute('''
        SELECT shutugannindairinin_sikbt, COUNT(*) as count
        FROM jiken_c_t_shutugannindairinin
        GROUP BY shutugannindairinin_sikbt
    ''')
    
    print('識別別統計:')
    for row in cur.fetchall():
        sikbt = '出願人' if row[0] == '1' else '代理人' if row[0] == '2' else '不明'
        print(f'  {sikbt}({row[0]}): {row[1]}件')
    
    con.close()

if __name__ == "__main__":
    check_applicant_data()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import sqlite3
from pathlib import Path

def analyze_applicant_tsv():
    """出願人代理人TSVファイルの構造を分析"""
    tsv_path = Path("tsv_data/tsv/upd_jiken_c_t_shutugannindairinin.tsv")
    
    if not tsv_path.exists():
        print(f"ファイルが見つかりません: {tsv_path}")
        return
    
    print("出願人代理人TSVファイルの分析中...")
    
    # ファイルを読み込んで構造を確認
    with open(tsv_path, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f, delimiter='\t')
        
        # ヘッダー行を取得
        headers = next(reader)
        print(f"\nヘッダー ({len(headers)}列):")
        for i, header in enumerate(headers):
            print(f"  {i+1:2d}. {header}")
        
        # 最初の数行のデータを確認
        print("\nサンプルデータ (最初の5行):")
        for i, row in enumerate(reader):
            if i >= 5:
                break
            print(f"\n--- 行 {i+1} ---")
            for j, (header, value) in enumerate(zip(headers, row)):
                if j < len(row):
                    print(f"  {header}: {value}")
    
    # 重要なカラムの特定
    important_columns = [
        'shutugan_no',                    # 出願番号
        'shutugannindairinin_simei',      # 出願人代理人氏名
        'shutugannindairinin_jusho',      # 出願人代理人住所
        'shutugannindairinin_sikbt',      # 出願人代理人識別
        'daihyoshutugannin_sikibetu',     # 代表出願人識別
        'dairinin_shubetu',               # 代理人種別
        'dairininsikaku_shubetu'          # 代理人資格種別
    ]
    
    print("\n重要なカラムの位置:")
    for col in important_columns:
        if col in headers:
            idx = headers.index(col)
            print(f"  {col}: {idx+1}列目")
        else:
            print(f"  {col}: 見つからない")

def create_applicant_table():
    """出願人情報テーブルを作成"""
    db_path = Path("output.db")
    
    if not db_path.exists():
        print(f"データベースが見つかりません: {db_path}")
        return
    
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    
    # 出願人代理人テーブルの作成
    create_sql = """
    CREATE TABLE IF NOT EXISTS jiken_c_t_shutugannindairinin (
        yonpo_code TEXT,                        -- 四法コード
        shutugan_no TEXT,                       -- 出願番号
        shutugannindairinin_sikbt TEXT,         -- 出願人代理人識別
        shutugannindairinin_code TEXT,          -- 出願人代理人コード
        gez_henko_no TEXT,                      -- 源泉変更番号
        gez_kohokan_kubun TEXT,                 -- 源泉公報関区分
        gez_kokken_code TEXT,                   -- 源泉国権コード
        daihyoshutugannin_sikibetu TEXT,        -- 代表出願人識別
        jokishutugannin_nanmei TEXT,            -- 上記出願人何名
        dairininhoka_nanmei TEXT,               -- 代理人他何名
        dairinin_shubetu TEXT,                  -- 代理人種別
        dairininsikaku_shubetu TEXT,            -- 代理人資格種別
        shutugannindairinin_jusho TEXT,         -- 出願人代理人住所
        shutugannindairinin_simei TEXT,         -- 出願人代理人氏名
        gez_junjo_no TEXT,                      -- 源泉順序番号
        FOREIGN KEY (shutugan_no) REFERENCES jiken_c_t(normalized_app_num)
    )
    """
    
    cur.execute(create_sql)
    
    # インデックスの作成
    index_sql = """
    CREATE INDEX IF NOT EXISTS idx_applicant_shutugan_no 
    ON jiken_c_t_shutugannindairinin(shutugan_no)
    """
    
    cur.execute(index_sql)
    con.commit()
    
    print("出願人代理人テーブルを作成しました")
    
    # テーブル構造を確認
    cur.execute("PRAGMA table_info(jiken_c_t_shutugannindairinin)")
    columns = cur.fetchall()
    print(f"\nテーブル構造 ({len(columns)}列):")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    con.close()

def import_applicant_data():
    """出願人データをインポート"""
    tsv_path = Path("tsv_data/tsv/upd_jiken_c_t_shutugannindairinin.tsv")
    db_path = Path("output.db")
    
    if not tsv_path.exists() or not db_path.exists():
        print("必要なファイルが見つかりません")
        return
    
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    
    # 既存データを削除
    cur.execute("DELETE FROM jiken_c_t_shutugannindairinin")
    
    # TSVファイルからデータをインポート
    with open(tsv_path, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f, delimiter='\t')
        headers = next(reader)  # ヘッダー行をスキップ
        
        insert_sql = """
        INSERT INTO jiken_c_t_shutugannindairinin (
            yonpo_code, shutugan_no, shutugannindairinin_sikbt, 
            shutugannindairinin_code, gez_henko_no, gez_kohokan_kubun,
            gez_kokken_code, daihyoshutugannin_sikibetu, jokishutugannin_nanmei,
            dairininhoka_nanmei, dairinin_shubetu, dairininsikaku_shubetu,
            shutugannindairinin_jusho, shutugannindairinin_simei, gez_junjo_no
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        imported_count = 0
        for row in reader:
            try:
                # 15列のデータを期待
                if len(row) >= 15:
                    cur.execute(insert_sql, row[:15])
                    imported_count += 1
            except Exception as e:
                print(f"エラー: {e}")
                continue
    
    con.commit()
    
    # 結果を確認
    cur.execute("SELECT COUNT(*) FROM jiken_c_t_shutugannindairinin")
    total_count = cur.fetchone()[0]
    
    print(f"\n出願人データのインポート完了:")
    print(f"  処理行数: {imported_count}")
    print(f"  総レコード数: {total_count}")
    
    # サンプルデータを表示
    cur.execute("""
        SELECT shutugan_no, shutugannindairinin_simei, shutugannindairinin_jusho,
               shutugannindairinin_sikbt, daihyoshutugannin_sikibetu
        FROM jiken_c_t_shutugannindairinin 
        WHERE shutugannindairinin_simei != '' 
        LIMIT 10
    """)
    
    print("\nサンプルデータ:")
    for row in cur.fetchall():
        print(f"  出願番号: {row[0]}")
        print(f"  氏名: {row[1]}")
        print(f"  住所: {row[2]}")
        print(f"  識別: {row[3]}")
        print(f"  代表: {row[4]}")
        print()
    
    con.close()

if __name__ == "__main__":
    print("=== 出願人データ分析 ===")
    analyze_applicant_tsv()
    
    print("\n=== テーブル作成 ===")
    create_applicant_table()
    
    print("\n=== データインポート ===")
    import_applicant_data()
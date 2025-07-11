#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import sqlite3
from pathlib import Path
import codecs

def detect_and_fix_encoding():
    """出願人TSVファイルの文字化けを修正"""
    tsv_path = Path("tsv_data/tsv/upd_jiken_c_t_shutugannindairinin.tsv")
    
    if not tsv_path.exists():
        print(f"ファイルが見つかりません: {tsv_path}")
        return
    
    # 複数のエンコーディングを試す
    encodings = ['utf-8', 'cp932', 'shift_jis', 'euc-jp', 'iso-2022-jp']
    
    for encoding in encodings:
        try:
            print(f"\n{encoding}でファイルを読み込み中...")
            
            with open(tsv_path, 'r', encoding=encoding, errors='ignore') as f:
                reader = csv.reader(f, delimiter='\t')
                headers = next(reader)
                
                # サンプルデータを確認
                sample_rows = []
                for i, row in enumerate(reader):
                    if i >= 10:  # 最初の10行のみ
                        break
                    sample_rows.append(row)
                
                # 氏名と住所カラムをチェック
                name_idx = headers.index('shutugannindairinin_simei')
                addr_idx = headers.index('shutugannindairinin_jusho')
                
                print(f"サンプルデータ ({encoding}):")
                valid_count = 0
                for i, row in enumerate(sample_rows):
                    if len(row) > max(name_idx, addr_idx):
                        name = row[name_idx]
                        addr = row[addr_idx]
                        print(f"  行{i+1}: 氏名='{name}' 住所='{addr}'")
                        if name and not name.isspace() and '?' not in name:
                            valid_count += 1
                
                if valid_count > 0:
                    print(f"✓ {encoding}で{valid_count}行の有効データを確認")
                    return encoding
                else:
                    print(f"✗ {encoding}では有効データが見つかりません")
                    
        except Exception as e:
            print(f"✗ {encoding}でエラー: {e}")
            continue
    
    print("適切なエンコーディングが見つかりませんでした")
    return None

def reimport_with_correct_encoding():
    """正しいエンコーディングで再インポート"""
    # まずエンコーディングを検出
    correct_encoding = detect_and_fix_encoding()
    if not correct_encoding:
        print("正しいエンコーディングが見つかりません。手動で修正が必要です。")
        return
    
    print(f"\n{correct_encoding}でデータを再インポートします...")
    
    tsv_path = Path("tsv_data/tsv/upd_jiken_c_t_shutugannindairinin.tsv")
    db_path = Path("output.db")
    
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    
    # 既存データを削除
    cur.execute("DELETE FROM jiken_c_t_shutugannindairinin")
    
    # 正しいエンコーディングでインポート
    with open(tsv_path, 'r', encoding=correct_encoding, errors='ignore') as f:
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
                if len(row) >= 15:
                    cur.execute(insert_sql, row[:15])
                    imported_count += 1
            except Exception as e:
                continue
    
    con.commit()
    
    # 結果を確認
    cur.execute("SELECT COUNT(*) FROM jiken_c_t_shutugannindairinin")
    total_count = cur.fetchone()[0]
    
    print(f"\n再インポート完了:")
    print(f"  処理行数: {imported_count}")
    print(f"  総レコード数: {total_count}")
    
    # 有効なデータを確認
    cur.execute("""
        SELECT shutugan_no, shutugannindairinin_simei, shutugannindairinin_jusho,
               shutugannindairinin_sikbt
        FROM jiken_c_t_shutugannindairinin 
        WHERE shutugannindairinin_simei IS NOT NULL 
        AND shutugannindairinin_simei != '' 
        AND LENGTH(shutugannindairinin_simei) > 0
        LIMIT 10
    """)
    
    valid_data = cur.fetchall()
    print(f"\n有効なデータ例 ({len(valid_data)}件):")
    for row in valid_data:
        print(f"  出願番号: {row[0]}")
        print(f"  氏名: {row[1]}")
        print(f"  住所: {row[2]}")
        print(f"  識別: {row[3]} ({'出願人' if row[3] == '1' else '代理人' if row[3] == '2' else '不明'})")
        print()
    
    con.close()

def test_applicant_search():
    """出願人情報を含む検索をテスト"""
    db_path = Path("output.db")
    
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    
    # 出願人情報を含む検索クエリ
    test_query = """
        SELECT 
            j.normalized_app_num,
            j.shutugan_bi,
            COALESCE(s.standard_char_t, iu.indct_use_t, su.search_use_t) as mark_text,
            -- 出願人情報（識別=1）
            ap.shutugannindairinin_simei as applicant_name,
            ap.shutugannindairinin_jusho as applicant_addr,
            -- 代理人情報（識別=2）
            ag.shutugannindairinin_simei as agent_name,
            ag.shutugannindairinin_jusho as agent_addr,
            -- 権利者情報（登録済み）
            rp.right_person_name,
            rp.right_person_addr
        FROM jiken_c_t j
        LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num
        LEFT JOIN indct_use_t_art iu ON j.normalized_app_num = iu.normalized_app_num
        LEFT JOIN search_use_t_art_table su ON j.normalized_app_num = su.normalized_app_num
        -- 出願人情報（識別=1）
        LEFT JOIN jiken_c_t_shutugannindairinin ap ON j.normalized_app_num = ap.shutugan_no 
                                                    AND ap.shutugannindairinin_sikbt = '1'
        -- 代理人情報（識別=2）
        LEFT JOIN jiken_c_t_shutugannindairinin ag ON j.normalized_app_num = ag.shutugan_no 
                                                    AND ag.shutugannindairinin_sikbt = '2'
        -- 権利者情報（登録済み）
        LEFT JOIN reg_mapping rm ON j.normalized_app_num = rm.app_num
        LEFT JOIN right_person_art_t rp ON rm.reg_num = rp.reg_num
        WHERE j.normalized_app_num IN (
            SELECT DISTINCT shutugan_no FROM jiken_c_t_shutugannindairinin 
            WHERE shutugannindairinin_simei IS NOT NULL 
            AND shutugannindairinin_simei != ''
        )
        LIMIT 10
    """
    
    cur.execute(test_query)
    results = cur.fetchall()
    
    print(f"\n出願人情報を含む検索結果: {len(results)}件")
    
    for i, row in enumerate(results, 1):
        print(f"\n--- 結果 {i} ---")
        print(f"出願番号: {row['normalized_app_num']}")
        print(f"商標: {row['mark_text']}")
        print(f"出願日: {row['shutugan_bi']}")
        print(f"出願人: {row['applicant_name']} ({row['applicant_addr']})")
        print(f"代理人: {row['agent_name']} ({row['agent_addr']})")
        print(f"権利者: {row['right_person_name']} ({row['right_person_addr']})")
    
    con.close()

if __name__ == "__main__":
    print("=== 出願人データの文字化け修正 ===")
    reimport_with_correct_encoding()
    
    print("\n=== 出願人情報を含む検索テスト ===")
    test_applicant_search()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TSVデータインポートスクリプト
商標データのTSVファイルをoutput.dbにインポートします。
"""

import sqlite3
import csv
import os
import sys
from pathlib import Path
import argparse

def get_db_connection(db_path):
    """データベース接続を取得"""
    if not Path(db_path).exists():
        print(f"エラー: データベースファイルが見つかりません: {db_path}")
        print("まず init_database.py を実行してデータベースを初期化してください。")
        sys.exit(1)
    
    conn = sqlite3.connect(db_path)
    return conn

def import_jiken_c_t(conn, tsv_path):
    """jiken_c_t テーブルにデータをインポート"""
    print(f"インポート中: {tsv_path} -> jiken_c_t")
    
    cursor = conn.cursor()
    imported = 0
    
    with open(tsv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO jiken_c_t (normalized_app_num, shutugan_bi, reg_reg_ymd)
                VALUES (?, ?, ?)
            """, (
                row.get('normalized_app_num'),
                row.get('shutugan_bi'),
                row.get('reg_reg_ymd')
            ))
            imported += 1
            
            if imported % 1000 == 0:
                print(f"  {imported} レコード処理済み...")
    
    conn.commit()
    print(f"  完了: {imported} レコードをインポート")

def import_standard_char_t_art(conn, tsv_path):
    """standard_char_t_art テーブルにデータをインポート"""
    print(f"インポート中: {tsv_path} -> standard_char_t_art")
    
    cursor = conn.cursor()
    imported = 0
    
    with open(tsv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO standard_char_t_art (normalized_app_num, standard_char_t)
                VALUES (?, ?)
            """, (
                row.get('normalized_app_num'),
                row.get('standard_char_t')
            ))
            imported += 1
            
            if imported % 1000 == 0:
                print(f"  {imported} レコード処理済み...")
    
    conn.commit()
    print(f"  完了: {imported} レコードをインポート")

def import_goods_class_art(conn, tsv_path):
    """goods_class_art テーブルにデータをインポート"""
    print(f"インポート中: {tsv_path} -> goods_class_art")
    
    cursor = conn.cursor()
    imported = 0
    
    with open(tsv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO goods_class_art (normalized_app_num, goods_classes)
                VALUES (?, ?)
            """, (
                row.get('normalized_app_num'),
                row.get('goods_classes')
            ))
            imported += 1
            
            if imported % 1000 == 0:
                print(f"  {imported} レコード処理済み...")
    
    conn.commit()
    print(f"  完了: {imported} レコードをインポート")

def import_jiken_c_t_shohin_joho(conn, tsv_path):
    """jiken_c_t_shohin_joho テーブルにデータをインポート"""
    print(f"インポート中: {tsv_path} -> jiken_c_t_shohin_joho")
    
    cursor = conn.cursor()
    imported = 0
    
    with open(tsv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO jiken_c_t_shohin_joho (normalized_app_num, designated_goods)
                VALUES (?, ?)
            """, (
                row.get('normalized_app_num'),
                row.get('designated_goods')
            ))
            imported += 1
            
            if imported % 1000 == 0:
                print(f"  {imported} レコード処理済み...")
    
    conn.commit()
    print(f"  完了: {imported} レコードをインポート")

def import_t_knd_info_art_table(conn, tsv_path):
    """t_knd_info_art_table テーブルにデータをインポート"""
    print(f"インポート中: {tsv_path} -> t_knd_info_art_table")
    
    cursor = conn.cursor()
    imported = 0
    
    with open(tsv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO t_knd_info_art_table (normalized_app_num, smlr_dsgn_group_cd)
                VALUES (?, ?)
            """, (
                row.get('normalized_app_num'),
                row.get('smlr_dsgn_group_cd')
            ))
            imported += 1
            
            if imported % 1000 == 0:
                print(f"  {imported} レコード処理済み...")
    
    conn.commit()
    print(f"  完了: {imported} レコードをインポート")

def import_reg_mapping(conn, tsv_path):
    """reg_mapping テーブルにデータをインポート"""
    print(f"インポート中: {tsv_path} -> reg_mapping")
    
    cursor = conn.cursor()
    imported = 0
    
    with open(tsv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO reg_mapping (app_num, reg_num)
                VALUES (?, ?)
            """, (
                row.get('app_num'),
                row.get('reg_num')
            ))
            imported += 1
            
            if imported % 1000 == 0:
                print(f"  {imported} レコード処理済み...")
    
    conn.commit()
    print(f"  完了: {imported} レコードをインポート")

def import_right_person_art_t(conn, tsv_path):
    """right_person_art_t テーブルにデータをインポート"""
    print(f"インポート中: {tsv_path} -> right_person_art_t")
    
    cursor = conn.cursor()
    imported = 0
    
    with open(tsv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO right_person_art_t (reg_num, right_person_name, right_person_addr)
                VALUES (?, ?, ?)
            """, (
                row.get('reg_num'),
                row.get('right_person_name'),
                row.get('right_person_addr')
            ))
            imported += 1
            
            if imported % 1000 == 0:
                print(f"  {imported} レコード処理済み...")
    
    conn.commit()
    print(f"  完了: {imported} レコードをインポート")

def import_t_dsgnt_art(conn, tsv_path):
    """t_dsgnt_art テーブルにデータをインポート"""
    print(f"インポート中: {tsv_path} -> t_dsgnt_art")
    
    cursor = conn.cursor()
    imported = 0
    
    with open(tsv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO t_dsgnt_art (normalized_app_num, dsgnt)
                VALUES (?, ?)
            """, (
                row.get('normalized_app_num'),
                row.get('dsgnt')
            ))
            imported += 1
            
            if imported % 1000 == 0:
                print(f"  {imported} レコード処理済み...")
    
    conn.commit()
    print(f"  完了: {imported} レコードをインポート")

def import_t_sample(conn, tsv_path):
    """t_sample テーブルにデータをインポート"""
    print(f"インポート中: {tsv_path} -> t_sample")
    
    cursor = conn.cursor()
    imported = 0
    
    with open(tsv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO t_sample (normalized_app_num, image_data, rec_seq_num)
                VALUES (?, ?, ?)
            """, (
                row.get('normalized_app_num'),
                row.get('image_data'),
                row.get('rec_seq_num', 1)
            ))
            imported += 1
            
            if imported % 1000 == 0:
                print(f"  {imported} レコード処理済み...")
    
    conn.commit()
    print(f"  完了: {imported} レコードをインポート")

def search_tsv_files(base_dir):
    """TSVファイルを検索"""
    print(f"TSVファイルを検索中: {base_dir}")
    
    base_path = Path(base_dir)
    if not base_path.exists():
        print(f"ディレクトリが見つかりません: {base_dir}")
        return {}
    
    # 検索パターン
    file_patterns = {
        'jiken_c_t': ['upd_jiken_c_t.tsv', 'jiken_c_t.tsv'],
        'standard_char_t_art': ['upd_standard_char_t_art.tsv', 'standard_char_t_art.tsv'],
        'goods_class_art': ['upd_goods_class_art.tsv', 'goods_class_art.tsv'],
        'jiken_c_t_shohin_joho': ['upd_jiken_c_t_shohin_joho.tsv', 'jiken_c_t_shohin_joho.tsv'],
        't_knd_info_art_table': ['upd_t_knd_info_art_table.tsv', 't_knd_info_art_table.tsv'],
        'reg_mapping': ['upd_reg_mapping.tsv', 'reg_mapping.tsv'],
        'right_person_art_t': ['upd_right_person_art_t.tsv', 'right_person_art_t.tsv'],
        't_dsgnt_art': ['upd_t_dsgnt_art.tsv', 't_dsgnt_art.tsv'],
        't_sample': ['upd_t_sample.tsv', 't_sample.tsv']
    }
    
    found_files = {}
    
    # 現在のディレクトリとサブディレクトリを検索
    for root, dirs, files in os.walk(base_path):
        for table_name, patterns in file_patterns.items():
            for pattern in patterns:
                if pattern in files:
                    found_files[table_name] = Path(root) / pattern
                    print(f"  見つかりました: {table_name} -> {found_files[table_name]}")
    
    return found_files

def main():
    parser = argparse.ArgumentParser(description='TSVデータをデータベースにインポート')
    parser.add_argument('--db', default='output.db', help='データベースファイルパス')
    parser.add_argument('--tsv-dir', default='.', help='TSVファイルのディレクトリ')
    parser.add_argument('--table', help='特定のテーブルのみインポート')
    parser.add_argument('--list', action='store_true', help='利用可能なTSVファイルを一覧表示')
    
    args = parser.parse_args()
    
    print("=== TSVデータインポートスクリプト ===")
    print()
    
    # TSVファイルを検索
    found_files = search_tsv_files(args.tsv_dir)
    
    if args.list:
        print("\n見つかったTSVファイル:")
        for table_name, file_path in found_files.items():
            print(f"  {table_name}: {file_path}")
        return
    
    if not found_files:
        print("TSVファイルが見つかりませんでした。")
        print("\n想定されるTSVファイル:")
        expected_files = [
            'upd_jiken_c_t.tsv',
            'upd_standard_char_t_art.tsv',
            'upd_goods_class_art.tsv',
            'upd_jiken_c_t_shohin_joho.tsv',
            'upd_t_knd_info_art_table.tsv',
            'upd_reg_mapping.tsv',
            'upd_right_person_art_t.tsv',
            'upd_t_dsgnt_art.tsv',
            'upd_t_sample.tsv'
        ]
        for file_name in expected_files:
            print(f"  - {file_name}")
        return
    
    # データベース接続
    conn = get_db_connection(args.db)
    
    # インポート関数のマッピング
    import_functions = {
        'jiken_c_t': import_jiken_c_t,
        'standard_char_t_art': import_standard_char_t_art,
        'goods_class_art': import_goods_class_art,
        'jiken_c_t_shohin_joho': import_jiken_c_t_shohin_joho,
        't_knd_info_art_table': import_t_knd_info_art_table,
        'reg_mapping': import_reg_mapping,
        'right_person_art_t': import_right_person_art_t,
        't_dsgnt_art': import_t_dsgnt_art,
        't_sample': import_t_sample
    }
    
    try:
        if args.table:
            # 特定のテーブルのみインポート
            if args.table in found_files and args.table in import_functions:
                import_functions[args.table](conn, found_files[args.table])
            else:
                print(f"テーブル '{args.table}' のTSVファイルが見つかりません。")
        else:
            # 全てのテーブルをインポート
            print(f"\n{len(found_files)} 個のTSVファイルをインポートします...")
            
            for table_name, file_path in found_files.items():
                if table_name in import_functions:
                    try:
                        import_functions[table_name](conn, file_path)
                    except Exception as e:
                        print(f"エラー: {table_name} のインポートに失敗: {e}")
                        continue
        
        print("\n=== インポート完了 ===")
        
        # 各テーブルのレコード数を確認
        cursor = conn.cursor()
        for table_name in import_functions.keys():
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"{table_name}: {count} レコード")
        
    except Exception as e:
        print(f"エラー: {e}")
        sys.exit(1)
    
    finally:
        conn.close()

if __name__ == "__main__":
    main()
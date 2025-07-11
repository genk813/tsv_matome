#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import sqlite3
from pathlib import Path

def import_applicant_master():
    """申請人マスターファイルをインポート"""
    tsv_path = Path("tsv_data/tsv/upd_appl_reg_info.tsv")
    
    if not tsv_path.exists():
        print(f"ファイルが見つかりません: {tsv_path}")
        return
    
    # ファイルの最初の2行を読んで構造を確認
    with open(tsv_path, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f, delimiter='\t')
        headers = next(reader)
        sample_data = next(reader)
        
        print("申請人マスターファイル構造:")
        print(f"ヘッダー: {headers}")
        print(f"サンプル: {sample_data}")

def import_integrated_applicant():
    """統合申請人情報をインポート"""
    tsv_path = Path("tsv_data/tsv/upd_under_integ_appl_info_mgt.tsv")
    
    if not tsv_path.exists():
        print(f"ファイルが見つかりません: {tsv_path}")
        return
    
    # ファイルの最初の2行を読んで構造を確認
    with open(tsv_path, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f, delimiter='\t')
        headers = next(reader)
        sample_data = next(reader)
        
        print("統合申請人情報ファイル構造:")
        print(f"ヘッダー: {headers}")
        print(f"サンプル: {sample_data}")

if __name__ == "__main__":
    print("=== 申請人マスターファイルのインポート ===")
    import_applicant_master()
    
    print("\n=== 統合申請人情報のインポート ===")
    import_integrated_applicant()

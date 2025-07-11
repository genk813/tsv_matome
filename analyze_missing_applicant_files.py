#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from pathlib import Path

def check_missing_files():
    """欠落している申請人ファイルの確認"""
    tsv_dir = Path("/home/ygenk/tsv_matome/tsv_data/tsv")
    
    # 期待される申請人関連ファイル
    expected_files = [
        "upd_appl_reg_info.tsv",           # 申請人登録情報
        "upd_under_integ_appl_info_mgt.tsv" # 統合申請人情報管理
    ]
    
    print("=== 申請人関連ファイルの確認 ===")
    
    print(f"\nTSVディレクトリ: {tsv_dir}")
    print(f"ディレクトリ存在: {tsv_dir.exists()}")
    
    if tsv_dir.exists():
        existing_files = list(tsv_dir.glob("*.tsv"))
        print(f"\n既存TSVファイル数: {len(existing_files)}")
        
        print("\n期待される申請人ファイル:")
        for file in expected_files:
            file_path = tsv_dir / file
            exists = file_path.exists()
            print(f"  - {file}: {'存在' if exists else '不存在'}")
            if exists:
                size = file_path.stat().st_size
                print(f"    サイズ: {size:,} bytes")
    
    # 既存の申請人関連ファイルを確認
    print("\n既存の申請人関連ファイル:")
    applicant_related = [
        "upd_jiken_c_t_shutugannindairinin.tsv",  # 出願人代理人
        "upd_right_person_art_t.tsv",             # 権利者情報
        "upd_atty_art_t.tsv"                      # 代理人情報
    ]
    
    for file in applicant_related:
        file_path = tsv_dir / file
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"  ✓ {file} ({size:,} bytes)")
        else:
            print(f"  ✗ {file} (不存在)")

def suggest_file_locations():
    """ファイルの配置提案"""
    print("\n=== ファイル配置の提案 ===")
    print("以下のファイルを tsv_data/tsv/ フォルダに配置してください:")
    print("1. upd_appl_reg_info.tsv")
    print("   - 申請人登録情報マスターファイル")
    print("   - 申請人コードと氏名・住所の対応表")
    print()
    print("2. upd_under_integ_appl_info_mgt.tsv") 
    print("   - 統合申請人情報管理ファイル")
    print("   - 申請人の詳細情報")
    print()
    print("配置コマンド例:")
    print("cp /path/to/upd_appl_reg_info.tsv /home/ygenk/tsv_matome/tsv_data/tsv/")
    print("cp /path/to/upd_under_integ_appl_info_mgt.tsv /home/ygenk/tsv_matome/tsv_data/tsv/")

def prepare_import_script():
    """インポートスクリプトの準備"""
    print("\n=== インポートスクリプトの準備 ===")
    
    import_script = '''#!/usr/bin/env python3
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
        reader = csv.reader(f, delimiter='\\t')
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
        reader = csv.reader(f, delimiter='\\t')
        headers = next(reader)
        sample_data = next(reader)
        
        print("統合申請人情報ファイル構造:")
        print(f"ヘッダー: {headers}")
        print(f"サンプル: {sample_data}")

if __name__ == "__main__":
    print("=== 申請人マスターファイルのインポート ===")
    import_applicant_master()
    
    print("\\n=== 統合申請人情報のインポート ===")
    import_integrated_applicant()
'''
    
    script_path = Path("/home/ygenk/tsv_matome/import_applicant_master.py")
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(import_script)
    
    print(f"インポートスクリプトを作成しました: {script_path}")
    print("ファイル配置後に実行してください: python3 import_applicant_master.py")

if __name__ == "__main__":
    check_missing_files()
    suggest_file_locations()
    prepare_import_script()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
週次データ更新スクリプト
特許庁からの新しいTSVデータを既存のデータベースに追加・更新する
"""

import sqlite3
import csv
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime
import argparse

class WeeklyDataUpdater:
    def __init__(self, db_path="output.db"):
        self.db_path = Path(db_path)
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        
    def create_backup(self):
        """データベースのバックアップを作成"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"output_backup_{timestamp}.db"
        
        print(f"データベースをバックアップ中: {backup_path}")
        shutil.copy2(self.db_path, backup_path)
        
        # 古いバックアップを削除（最新5つを保持）
        backups = sorted(self.backup_dir.glob("output_backup_*.db"), reverse=True)
        for old_backup in backups[5:]:
            old_backup.unlink()
            print(f"古いバックアップを削除: {old_backup}")
        
        return backup_path
    
    def get_database_stats(self):
        """データベースの統計情報を取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        tables = [
            'jiken_c_t', 'standard_char_t_art', 'goods_class_art',
            'jiken_c_t_shohin_joho', 't_knd_info_art_table',
            'right_person_art_t', 't_dsgnt_art', 't_sample'
        ]
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            stats[table] = cursor.fetchone()[0]
        
        conn.close()
        return stats
    
    def update_jiken_c_t(self, tsv_path):
        """jiken_c_tテーブルを更新"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        updated = 0
        inserted = 0
        
        with open(tsv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                app_num = row.get('shutugan_no', '')
                normalized_app_num = app_num.replace('-', '') if app_num else None
                
                if not normalized_app_num:
                    continue
                
                # 既存データをチェック
                cursor.execute("SELECT COUNT(*) FROM jiken_c_t WHERE normalized_app_num = ?", (normalized_app_num,))
                exists = cursor.fetchone()[0] > 0
                
                if exists:
                    # 更新
                    cursor.execute("""
                        UPDATE jiken_c_t 
                        SET shutugan_bi = ?, reg_reg_ymd = ?
                        WHERE normalized_app_num = ?
                    """, (
                        row.get('shutugan_bi'),
                        row.get('toroku_bi'),
                        normalized_app_num
                    ))
                    updated += 1
                else:
                    # 新規挿入
                    cursor.execute("""
                        INSERT INTO jiken_c_t (normalized_app_num, shutugan_bi, reg_reg_ymd)
                        VALUES (?, ?, ?)
                    """, (
                        normalized_app_num,
                        row.get('shutugan_bi'),
                        row.get('toroku_bi')
                    ))
                    inserted += 1
                
                if (updated + inserted) % 1000 == 0:
                    print(f"  処理済み: {updated + inserted} レコード")
        
        conn.commit()
        conn.close()
        
        print(f"  jiken_c_t: 新規{inserted}件、更新{updated}件")
        return inserted, updated
    
    def update_standard_char_t_art(self, tsv_path):
        """standard_char_t_artテーブルを更新"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        updated = 0
        inserted = 0
        
        with open(tsv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                app_num = row.get('app_num', '')
                normalized_app_num = app_num.replace('-', '') if app_num else None
                
                if not normalized_app_num:
                    continue
                
                cursor.execute("SELECT COUNT(*) FROM standard_char_t_art WHERE normalized_app_num = ?", (normalized_app_num,))
                exists = cursor.fetchone()[0] > 0
                
                if exists:
                    cursor.execute("""
                        UPDATE standard_char_t_art 
                        SET standard_char_t = ?
                        WHERE normalized_app_num = ?
                    """, (
                        row.get('standard_char_t'),
                        normalized_app_num
                    ))
                    updated += 1
                else:
                    cursor.execute("""
                        INSERT INTO standard_char_t_art (normalized_app_num, standard_char_t)
                        VALUES (?, ?)
                    """, (
                        normalized_app_num,
                        row.get('standard_char_t')
                    ))
                    inserted += 1
                
                if (updated + inserted) % 1000 == 0:
                    print(f"  処理済み: {updated + inserted} レコード")
        
        conn.commit()
        conn.close()
        
        print(f"  standard_char_t_art: 新規{inserted}件、更新{updated}件")
        return inserted, updated
    
    def update_table_generic(self, table_name, tsv_path, column_mapping):
        """汎用的なテーブル更新"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        updated = 0
        inserted = 0
        
        with open(tsv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                app_num = row.get('app_num', '')
                normalized_app_num = app_num.replace('-', '') if app_num else None
                
                if not normalized_app_num:
                    continue
                
                # 既存データをチェック
                cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE normalized_app_num = ?", (normalized_app_num,))
                exists = cursor.fetchone()[0] > 0
                
                values = [normalized_app_num]
                for col in column_mapping:
                    values.append(row.get(col))
                
                if exists:
                    # 更新（重複レコードは削除してから挿入）
                    cursor.execute(f"DELETE FROM {table_name} WHERE normalized_app_num = ?", (normalized_app_num,))
                    placeholders = ",".join(["?" for _ in values])
                    cursor.execute(f"INSERT INTO {table_name} VALUES ({placeholders})", values)
                    updated += 1
                else:
                    # 新規挿入
                    placeholders = ",".join(["?" for _ in values])
                    cursor.execute(f"INSERT INTO {table_name} VALUES ({placeholders})", values)
                    inserted += 1
                
                if (updated + inserted) % 1000 == 0:
                    print(f"  処理済み: {updated + inserted} レコード")
        
        conn.commit()
        conn.close()
        
        print(f"  {table_name}: 新規{inserted}件、更新{updated}件")
        return inserted, updated
    
    def update_from_directory(self, tsv_dir):
        """TSVディレクトリから一括更新"""
        tsv_path = Path(tsv_dir)
        if not tsv_path.exists():
            print(f"エラー: TSVディレクトリが見つかりません: {tsv_dir}")
            return False
        
        print(f"=== 週次データ更新開始 ===")
        print(f"TSVディレクトリ: {tsv_path}")
        
        # バックアップ作成
        backup_path = self.create_backup()
        
        # 更新前の統計
        stats_before = self.get_database_stats()
        print(f"\\n更新前の統計:")
        for table, count in stats_before.items():
            print(f"  {table}: {count} レコード")
        
        # 各テーブルの更新
        update_files = {
            'jiken_c_t': 'upd_jiken_c_t.tsv',
            'standard_char_t_art': 'upd_standard_char_t_art.tsv',
            'goods_class_art': 'upd_goods_class_art.tsv',
            'jiken_c_t_shohin_joho': 'upd_jiken_c_t_shohin_joho.tsv',
            't_knd_info_art_table': 'upd_t_knd_info_art_table.tsv',
            'right_person_art_t': 'upd_right_person_art_t.tsv',
            't_dsgnt_art': 'upd_t_dsgnt_art.tsv',
            't_sample': 'upd_t_sample.tsv'
        }
        
        total_inserted = 0
        total_updated = 0
        
        print(f"\\n=== テーブル更新開始 ===")
        
        for table_name, file_name in update_files.items():
            file_path = tsv_path / file_name
            if file_path.exists():
                print(f"\\n{table_name}を更新中...")
                
                if table_name == 'jiken_c_t':
                    inserted, updated = self.update_jiken_c_t(file_path)
                elif table_name == 'standard_char_t_art':
                    inserted, updated = self.update_standard_char_t_art(file_path)
                elif table_name == 'goods_class_art':
                    inserted, updated = self.update_table_generic(table_name, file_path, ['goods_classes'])
                elif table_name == 'jiken_c_t_shohin_joho':
                    inserted, updated = self.update_table_generic(table_name, file_path, ['designated_goods'])
                elif table_name == 't_knd_info_art_table':
                    inserted, updated = self.update_table_generic(table_name, file_path, ['smlr_dsgn_group_cd'])
                elif table_name == 't_dsgnt_art':
                    inserted, updated = self.update_table_generic(table_name, file_path, ['dsgnt'])
                elif table_name == 't_sample':
                    inserted, updated = self.update_table_generic(table_name, file_path, ['image_data', 'rec_seq_num'])
                elif table_name == 'right_person_art_t':
                    # 権利者情報は特別処理（reg_numベース）
                    inserted, updated = 0, 0
                    print(f"  {table_name}: スキップ（特別処理が必要）")
                
                total_inserted += inserted
                total_updated += updated
            else:
                print(f"  {file_name}: ファイルが見つかりません")
        
        # 更新後の統計
        stats_after = self.get_database_stats()
        print(f"\\n更新後の統計:")
        for table, count in stats_after.items():
            before = stats_before.get(table, 0)
            diff = count - before
            print(f"  {table}: {count} レコード ({diff:+d})")
        
        print(f"\\n=== 更新完了 ===")
        print(f"総新規レコード: {total_inserted}")
        print(f"総更新レコード: {total_updated}")
        print(f"バックアップ: {backup_path}")
        
        return True
    
    def validate_update(self):
        """更新後のデータ検証"""
        print("\\n=== データ検証 ===")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 基本統計
        cursor.execute("SELECT COUNT(*) FROM jiken_c_t")
        total_cases = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM standard_char_t_art WHERE standard_char_t IS NOT NULL AND standard_char_t != ''")
        with_text = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM t_sample WHERE image_data IS NOT NULL AND image_data != ''")
        with_image = cursor.fetchone()[0]
        
        print(f"総事件数: {total_cases}")
        print(f"商標テキストあり: {with_text} ({with_text/total_cases*100:.1f}%)")
        print(f"画像データあり: {with_image} ({with_image/total_cases*100:.1f}%)")
        
        # データ整合性チェック
        cursor.execute("""
            SELECT COUNT(*) FROM jiken_c_t j
            LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num
            WHERE s.normalized_app_num IS NULL
        """)
        missing_standard = cursor.fetchone()[0]
        
        if missing_standard > 0:
            print(f"⚠️  標準文字データが欠落している事件: {missing_standard}")
        
        conn.close()
        print("検証完了")

def main():
    parser = argparse.ArgumentParser(description='週次データ更新スクリプト')
    parser.add_argument('tsv_dir', help='新しいTSVファイルのディレクトリ')
    parser.add_argument('--db', default='output.db', help='データベースファイル')
    parser.add_argument('--validate', action='store_true', help='更新後にデータ検証を実行')
    
    args = parser.parse_args()
    
    updater = WeeklyDataUpdater(args.db)
    
    if updater.update_from_directory(args.tsv_dir):
        if args.validate:
            updater.validate_update()
        
        print(f"\\n週次データ更新が完了しました！")
        print(f"次回の更新時は以下のコマンドを実行してください：")
        print(f"python3 weekly_data_updater.py <新しいTSVディレクトリ>")
    else:
        print("更新に失敗しました。")
        sys.exit(1)

if __name__ == "__main__":
    main()
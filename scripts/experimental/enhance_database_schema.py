#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
データベース拡張ツール
既存のデータベースを保持しながら、TSVファイルから不足している項目を追加する
"""

import sqlite3
import csv
import sys
from pathlib import Path
from typing import Dict, List, Any

class DatabaseEnhancer:
    """データベース拡張クラス"""
    
    def __init__(self, db_path: str = "output.db"):
        self.db_path = Path(db_path)
        self.backup_path = Path("output_backup.db")
        
    def backup_database(self):
        """現在のデータベースをバックアップ"""
        if self.db_path.exists():
            print(f"📦 データベースをバックアップ: {self.backup_path}")
            import shutil
            shutil.copy2(self.db_path, self.backup_path)
        
    def analyze_jiken_c_t_tsv(self) -> Dict[str, int]:
        """upd_jiken_c_t.tsvの構造を分析"""
        tsv_path = Path("tsv_data/tsv/upd_jiken_c_t.tsv")
        
        print(f"📊 {tsv_path} の構造分析中...")
        
        with open(tsv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='\t')
            headers = next(reader)
            
            print(f"✅ カラム数: {len(headers)}")
            print("📋 カラム一覧:")
            
            column_mapping = {}
            for i, header in enumerate(headers):
                print(f"  {i:2d}: {header}")
                column_mapping[header] = i
                
            # サンプルデータを3行読む
            print("\n📝 サンプルデータ:")
            for row_num in range(3):
                try:
                    row = next(reader)
                    print(f"  行{row_num + 1}: {len(row)}カラム")
                    # 重要なカラムのみ表示
                    important_cols = [
                        'shutugan_no', 'shutugan_bi', 'toroku_bi', 
                        'raz_toroku_no', 'raz_kohohakko_bi', 'pcz_kokaikohohakko_bi'
                    ]
                    for col in important_cols:
                        if col in column_mapping:
                            idx = column_mapping[col]
                            value = row[idx] if idx < len(row) else 'N/A'
                            print(f"    {col}: {value}")
                except StopIteration:
                    break
                    
        return column_mapping
    
    def create_enhanced_jiken_table(self):
        """拡張されたjiken_c_tテーブルを作成"""
        print("🔧 拡張jiken_c_tテーブルを作成中...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 新しいテーブル構造（既存データを保持しながら拡張）
        create_sql = """
        CREATE TABLE IF NOT EXISTS jiken_c_t_enhanced (
            -- 既存フィールド
            normalized_app_num TEXT PRIMARY KEY,
            shutugan_bi TEXT,           -- 出願日
            reg_reg_ymd TEXT,           -- 登録日（既存）
            
            -- 新規追加フィールド
            masterkosin_nitiji TEXT,    -- マスター更新日時
            yonpo_code TEXT,           -- 四法コード
            shutugan_no TEXT,          -- 出願番号（原本）
            shutugan_shubetu1 TEXT,    -- 出願種別1
            shutugan_shubetu2 TEXT,    -- 出願種別2
            shutugan_shubetu3 TEXT,    -- 出願種別3
            shutugan_shubetu4 TEXT,    -- 出願種別4
            shutugan_shubetu5 TEXT,    -- 出願種別5
            seiri_no TEXT,             -- 整理番号
            saishushobun_shubetu TEXT, -- 最終処分種別
            saishushobun_bi TEXT,      -- 最終処分日
            raz_toroku_no TEXT,        -- 登録番号
            raz_bunkatu_no TEXT,       -- 分割番号
            bogo_no TEXT,              -- 母号番号
            toroku_bi TEXT,            -- 登録日（詳細）
            raz_sotugo_su TEXT,        -- 登録総号数
            raz_nenkantugo_su TEXT,    -- 登録年間通号数
            raz_kohohakko_bi TEXT,     -- 登録公報発行日
            tantokan_code TEXT,        -- 担当官コード
            pcz_kokaikohohakko_bi TEXT,-- 公開公報発行日
            kubun_su TEXT,             -- 区分数
            torokusateijikubun_su TEXT,-- 登録査定時区分数
            hyojunmoji_umu TEXT,       -- 標準文字有無
            rittaishohyo_umu TEXT,     -- 立体商標有無
            hyoshosikisai_umu TEXT,    -- 標章色彩有無
            shohyoho3jo2ko_flag TEXT,  -- 商標法3条2項フラグ
            shohyoho5jo4ko_flag TEXT,  -- 商標法5条4項フラグ
            genshutugan_shubetu TEXT,  -- 原出願種別
            genshutuganyonpo_code TEXT,-- 原出願四法コード
            genshutugan_no TEXT,       -- 原出願番号
            sokyu_bi TEXT,             -- 遡及日
            obz_shutugan_no TEXT,      -- OBZ出願番号
            obz_toroku_no TEXT,        -- OBZ登録番号
            obz_bunkatu_no TEXT,       -- OBZ分割番号
            kosintoroku_no TEXT,       -- 更新登録番号
            pez_bunkatu_no TEXT,       -- PEZ分割番号
            pez_bogo_no TEXT,          -- PEZ母号番号
            kakikaetoroku_no TEXT,     -- 書換登録番号
            ktz_bunkatu_no TEXT,       -- KTZ分割番号
            ktz_bogo_no TEXT,          -- KTZ母号番号
            krz_kojoryozokuihan_flag TEXT, -- KRZ個人領続犯フラグ
            sokisinsa_mark TEXT,       -- 早期審査マーク
            tekiyohoki_kubun TEXT,     -- 適用法規区分
            sinsa_shubetu TEXT,        -- 審査種別
            sosho_code TEXT,           -- 争訟コード
            satei_shubetu TEXT,        -- 査定種別
            igiken_su TEXT,            -- 異議件数
            igiyuko_su TEXT            -- 異議有効数
        );
        """
        
        cursor.execute(create_sql)
        conn.commit()
        conn.close()
        
        print("✅ 拡張テーブル作成完了")
    
    def import_enhanced_jiken_data(self):
        """拡張jiken_c_tデータをインポート"""
        tsv_path = Path("tsv_data/tsv/upd_jiken_c_t.tsv")
        
        print(f"📥 {tsv_path} からデータをインポート中...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 既存データを新テーブルに移行
        cursor.execute("""
            INSERT OR IGNORE INTO jiken_c_t_enhanced (normalized_app_num, shutugan_bi, reg_reg_ymd)
            SELECT normalized_app_num, shutugan_bi, reg_reg_ymd FROM jiken_c_t
        """)
        
        imported_count = 0
        updated_count = 0
        
        try:
            with open(tsv_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter='\t')
                headers = next(reader)  # ヘッダーをスキップ
                
                for row_num, row in enumerate(reader, 1):
                    if row_num % 5000 == 0:
                        print(f"  処理中: {row_num:,}行")
                    
                    try:
                        # 出願番号を正規化
                        shutugan_no = row[2] if len(row) > 2 else None
                        if not shutugan_no:
                            continue
                            
                        normalized_app_num = shutugan_no.replace('-', '')
                        
                        # データを挿入/更新（基本項目のみ）
                        cursor.execute("""
                            INSERT OR REPLACE INTO jiken_c_t_enhanced (
                                normalized_app_num, shutugan_no, shutugan_bi, toroku_bi,
                                raz_toroku_no, raz_kohohakko_bi, pcz_kokaikohohakko_bi,
                                kubun_su, hyojunmoji_umu
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            normalized_app_num,
                            row[2] if len(row) > 2 else None,   # shutugan_no
                            row[3] if len(row) > 3 else None,   # shutugan_bi
                            row[15] if len(row) > 15 else None, # toroku_bi
                            row[12] if len(row) > 12 else None, # raz_toroku_no (登録番号)
                            row[18] if len(row) > 18 else None, # raz_kohohakko_bi (登録公報発行日)
                            row[20] if len(row) > 20 else None, # pcz_kokaikohohakko_bi (公開公報発行日)
                            row[21] if len(row) > 21 else None, # kubun_su (区分数)
                            row[23] if len(row) > 23 else None  # hyojunmoji_umu (標準文字有無)
                        ))
                        
                        imported_count += 1
                        
                    except Exception as e:
                        print(f"  ⚠️  行{row_num}でエラー: {e}")
                        continue
                
                conn.commit()
                
        except Exception as e:
            print(f"❌ インポートエラー: {e}")
            conn.rollback()
            
        finally:
            conn.close()
        
        print(f"✅ インポート完了: {imported_count:,}件")
    
    def update_cli_search_for_enhanced_data(self):
        """CLI検索ツールを拡張データに対応"""
        print("🔧 CLI検索ツールを拡張データ対応に更新中...")
        
        # 既存のCLIファイルをバックアップ
        cli_path = Path("cli_trademark_search.py")
        if cli_path.exists():
            backup_cli_path = Path("cli_trademark_search_backup.py")
            import shutil
            shutil.copy2(cli_path, backup_cli_path)
            print(f"📦 CLI検索ツールをバックアップ: {backup_cli_path}")
    
    def run_enhancement(self):
        """データベース拡張の実行"""
        print("🚀 データベース拡張開始")
        print("=" * 80)
        
        # 1. バックアップ
        self.backup_database()
        
        # 2. TSV構造分析
        column_mapping = self.analyze_jiken_c_t_tsv()
        
        # 3. 拡張テーブル作成
        self.create_enhanced_jiken_table()
        
        # 4. データインポート
        self.import_enhanced_jiken_data()
        
        # 5. CLI更新準備
        self.update_cli_search_for_enhanced_data()
        
        print("\n✅ データベース拡張完了!")
        print(f"📦 バックアップ: {self.backup_path}")
        print(f"🗃️  拡張テーブル: jiken_c_t_enhanced")

def main():
    """メイン実行"""
    enhancer = DatabaseEnhancer()
    enhancer.run_enhancement()

if __name__ == "__main__":
    main()
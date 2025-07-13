#!/usr/bin/env python3
"""
Phase 2: 国際商標データインポートスクリプト
TSVファイルから国際商標データを適切なテーブルにインポートする
"""

import sqlite3
import csv
import os
import sys
from pathlib import Path
from datetime import datetime

class InternationalTrademarkImporter:
    def __init__(self, db_path="output.db", tsv_dir="tsv_data/tsv"):
        self.db_path = db_path
        self.tsv_dir = Path(tsv_dir)
        self.conn = None
        
        # TSVファイルマッピング
        self.tsv_files = {
            "registration": "upd_intl_t_org_org_reg_mgt_info.tsv",
            "progress": "upd_intl_t_org_prog_info.tsv", 
            "holder": "upd_intl_t_org_set_crr_nm_addr.tsv",
            "goods_services": "upd_intl_t_org_set_dsgn_gds_srvc.tsv",
            "trademark_text": "upd_intl_t_org_set_frst_indct.tsv"
        }
        
        # 各ファイルのカラムマッピング（仕様書から抽出）
        self.column_mappings = {
            "registration": [
                "add_del_id", "intl_reg_num", "intl_reg_num_updt_cnt_sign_cd", 
                "intl_reg_num_split_sign_cd", "app_num", "app_num_split_sign_cd",
                "app_date", "intl_reg_date", "effective_date", "basic_app_ctry_cd",
                "basic_app_num", "basic_app_date", "basic_reg_ctry_cd", 
                "basic_reg_num", "basic_reg_date", "rep_figure_num", "vienna_class",
                "color_claim_flg", "app_lang_cd", "second_lang_cd", "define_flg",
                "updt_year_month_day", "batch_updt_year_month_day"
            ],
            "progress": [
                "add_del_id", "intl_reg_num", "intl_reg_num_updt_cnt_sign_cd",
                "intl_reg_num_split_sign_cd", "prog_seq", "prog_cd", "prog_date",
                "prog_content", "define_flg", "updt_year_month_day", "batch_updt_year_month_day"
            ],
            "holder": [
                "add_del_id", "intl_reg_num", "intl_reg_num_updt_cnt_sign_cd",
                "intl_reg_num_split_sign_cd", "holder_seq", "holder_name",
                "holder_name_japanese", "holder_addr", "holder_addr_japanese",
                "holder_ctry_cd", "define_flg", "updt_year_month_day", "batch_updt_year_month_day"
            ],
            "goods_services": [
                "add_del_id", "intl_reg_num", "intl_reg_num_updt_cnt_sign_cd",
                "intl_reg_num_split_sign_cd", "aft_desig_year_month_day", 
                "temp_principal_reg_id_flg", "indct_seq", "goods_seq",
                "goods_class", "goods_content", "intl_reg_rec_dt", "define_flg",
                "updt_year_month_day", "batch_updt_year_month_day"
            ],
            "trademark_text": [
                "add_del_id", "intl_reg_num", "intl_reg_num_updt_cnt_sign_cd",
                "intl_reg_num_split_sign_cd", "aft_desig_year_month_day",
                "temp_principal_reg_id_flg", "indct_seq", "finl_dcsn_year_month_day",
                "trial_dcsn_year_month_day", "pri_app_gvrn_cntrcntry_cd",
                "pri_app_year_month_day", "pri_clim_cnt", "special_t_typ_flg",
                "group_cert_warranty_flg", "define_flg", "updt_year_month_day",
                "batch_updt_year_month_day", "t_dtl_explntn"
            ]
        }

    def connect_db(self):
        """データベース接続"""
        if not Path(self.db_path).exists():
            raise FileNotFoundError(f"データベースファイルが見つかりません: {self.db_path}")
        
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        print(f"✅ データベースに接続: {self.db_path}")

    def create_tables(self):
        """スキーマファイルを読み込んでテーブル作成"""
        schema_file = Path("scripts/phase2_schema.sql")
        if not schema_file.exists():
            raise FileNotFoundError(f"スキーマファイルが見つかりません: {schema_file}")
        
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        cursor = self.conn.cursor()
        cursor.executescript(schema_sql)
        self.conn.commit()
        print("✅ Phase 2テーブル作成完了")

    def analyze_tsv_file(self, file_path):
        """TSVファイルの構造分析"""
        print(f"\n📄 {file_path.name} を分析中...")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter='\t')
                headers = next(reader)
                sample_rows = []
                
                # 最初の5行を取得
                for i, row in enumerate(reader):
                    if i >= 5:
                        break
                    sample_rows.append(row)
                
                print(f"   カラム数: {len(headers)}")
                print(f"   サンプル行数: {len(sample_rows)}")
                
                # 主要カラムを表示
                key_columns = []
                for i, col in enumerate(headers):
                    if i < 10:  # 最初の10カラム
                        key_columns.append(f"{i}: {col}")
                
                print("   主要カラム:")
                for col in key_columns:
                    print(f"     {col}")
                
                return headers, sample_rows
                
        except Exception as e:
            print(f"   ❌ エラー: {e}")
            return None, None

    def import_registration_data(self):
        """国際商標登録管理情報のインポート"""
        file_path = self.tsv_dir / self.tsv_files["registration"]
        if not file_path.exists():
            print(f"⚠️  ファイル未検出: {file_path}")
            return 0
        
        print(f"\n📥 国際商標登録管理情報をインポート: {file_path.name}")
        
        cursor = self.conn.cursor()
        imported_count = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter='\t')
                headers = next(reader)
                
                # カラム数チェック
                expected_cols = len(self.column_mappings["registration"])
                actual_cols = len(headers)
                print(f"   期待カラム数: {expected_cols}, 実際: {actual_cols}")
                
                for row_num, row in enumerate(reader, 1):
                    if len(row) != actual_cols:
                        continue  # 不正な行をスキップ
                    
                    # データの準備（Noneで埋める不足分）
                    row_data = row + [None] * max(0, expected_cols - len(row))
                    row_data = row_data[:expected_cols]  # 余分を切り捨て
                    
                    # INSERT文実行
                    placeholders = ', '.join(['?'] * expected_cols)
                    sql = f"""
                    INSERT OR REPLACE INTO intl_trademark_registration 
                    ({', '.join(self.column_mappings["registration"])})
                    VALUES ({placeholders})
                    """
                    
                    cursor.execute(sql, row_data)
                    imported_count += 1
                    
                    if imported_count % 500 == 0:
                        print(f"   進行中: {imported_count:,} 件")
                        self.conn.commit()
                
                self.conn.commit()
                print(f"✅ 登録管理情報インポート完了: {imported_count:,} 件")
                
        except Exception as e:
            print(f"❌ インポートエラー: {e}")
            self.conn.rollback()
        
        return imported_count

    def import_progress_data(self):
        """国際商標進行情報のインポート"""
        file_path = self.tsv_dir / self.tsv_files["progress"]
        if not file_path.exists():
            print(f"⚠️  ファイル未検出: {file_path}")
            return 0
        
        print(f"\n📥 国際商標進行情報をインポート: {file_path.name}")
        
        cursor = self.conn.cursor()
        imported_count = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter='\t')
                headers = next(reader)
                
                expected_cols = len(self.column_mappings["progress"])
                
                for row in reader:
                    if len(row) < expected_cols:
                        row_data = row + [None] * (expected_cols - len(row))
                    else:
                        row_data = row[:expected_cols]
                    
                    placeholders = ', '.join(['?'] * expected_cols)
                    sql = f"""
                    INSERT OR REPLACE INTO intl_trademark_progress 
                    ({', '.join(self.column_mappings["progress"])})
                    VALUES ({placeholders})
                    """
                    
                    cursor.execute(sql, row_data)
                    imported_count += 1
                    
                    if imported_count % 500 == 0:
                        print(f"   進行中: {imported_count:,} 件")
                        self.conn.commit()
                
                self.conn.commit()
                print(f"✅ 進行情報インポート完了: {imported_count:,} 件")
                
        except Exception as e:
            print(f"❌ インポートエラー: {e}")
            self.conn.rollback()
        
        return imported_count

    def import_holder_data(self):
        """国際商標権者情報のインポート"""
        file_path = self.tsv_dir / self.tsv_files["holder"]
        if not file_path.exists():
            print(f"⚠️  ファイル未検出: {file_path}")
            return 0
        
        print(f"\n📥 国際商標権者情報をインポート: {file_path.name}")
        
        cursor = self.conn.cursor()
        imported_count = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter='\t')
                headers = next(reader)
                
                expected_cols = len(self.column_mappings["holder"])
                
                for row in reader:
                    if len(row) < expected_cols:
                        row_data = row + [None] * (expected_cols - len(row))
                    else:
                        row_data = row[:expected_cols]
                    
                    placeholders = ', '.join(['?'] * expected_cols)
                    sql = f"""
                    INSERT OR REPLACE INTO intl_trademark_holder 
                    ({', '.join(self.column_mappings["holder"])})
                    VALUES ({placeholders})
                    """
                    
                    cursor.execute(sql, row_data)
                    imported_count += 1
                    
                    if imported_count % 500 == 0:
                        print(f"   進行中: {imported_count:,} 件")
                        self.conn.commit()
                
                self.conn.commit()
                print(f"✅ 権者情報インポート完了: {imported_count:,} 件")
                
        except Exception as e:
            print(f"❌ インポートエラー: {e}")
            self.conn.rollback()
        
        return imported_count

    def import_goods_services_data(self):
        """国際商標指定商品・サービス情報のインポート"""
        file_path = self.tsv_dir / self.tsv_files["goods_services"]
        if not file_path.exists():
            print(f"⚠️  ファイル未検出: {file_path}")
            return 0
        
        print(f"\n📥 国際商標指定商品・サービス情報をインポート: {file_path.name}")
        
        cursor = self.conn.cursor()
        imported_count = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter='\t')
                headers = next(reader)
                
                expected_cols = len(self.column_mappings["goods_services"])
                
                for row in reader:
                    if len(row) < expected_cols:
                        row_data = row + [None] * (expected_cols - len(row))
                    else:
                        row_data = row[:expected_cols]
                    
                    placeholders = ', '.join(['?'] * expected_cols)
                    sql = f"""
                    INSERT OR REPLACE INTO intl_trademark_goods_services 
                    ({', '.join(self.column_mappings["goods_services"])})
                    VALUES ({placeholders})
                    """
                    
                    cursor.execute(sql, row_data)
                    imported_count += 1
                    
                    if imported_count % 500 == 0:
                        print(f"   進行中: {imported_count:,} 件")
                        self.conn.commit()
                
                self.conn.commit()
                print(f"✅ 指定商品・サービス情報インポート完了: {imported_count:,} 件")
                
        except Exception as e:
            print(f"❌ インポートエラー: {e}")
            self.conn.rollback()
        
        return imported_count

    def import_trademark_text_data(self):
        """国際商標テキスト情報のインポート"""
        file_path = self.tsv_dir / self.tsv_files["trademark_text"]
        if not file_path.exists():
            print(f"⚠️  ファイル未検出: {file_path}")
            return 0
        
        print(f"\n📥 国際商標テキスト情報をインポート: {file_path.name}")
        
        cursor = self.conn.cursor()
        imported_count = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter='\t')
                headers = next(reader)
                
                expected_cols = len(self.column_mappings["trademark_text"])
                
                for row in reader:
                    if len(row) < expected_cols:
                        row_data = row + [None] * (expected_cols - len(row))
                    else:
                        row_data = row[:expected_cols]
                    
                    placeholders = ', '.join(['?'] * expected_cols)
                    sql = f"""
                    INSERT OR REPLACE INTO intl_trademark_text 
                    ({', '.join(self.column_mappings["trademark_text"])})
                    VALUES ({placeholders})
                    """
                    
                    cursor.execute(sql, row_data)
                    imported_count += 1
                    
                    if imported_count % 500 == 0:
                        print(f"   進行中: {imported_count:,} 件")
                        self.conn.commit()
                
                self.conn.commit()
                print(f"✅ 商標テキスト情報インポート完了: {imported_count:,} 件")
                
        except Exception as e:
            print(f"❌ インポートエラー: {e}")
            self.conn.rollback()
        
        return imported_count

    def verify_import(self):
        """インポート結果の検証"""
        print(f"\n🔍 Phase 2インポート結果検証")
        print("=" * 50)
        
        cursor = self.conn.cursor()
        
        tables = [
            ("intl_trademark_registration", "国際商標登録管理"),
            ("intl_trademark_progress", "国際商標進行情報"),
            ("intl_trademark_holder", "国際商標権者情報"),
            ("intl_trademark_goods_services", "国際商標指定商品・サービス"),
            ("intl_trademark_text", "国際商標テキスト情報")
        ]
        
        total_records = 0
        
        for table_name, description in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                total_records += count
                print(f"📊 {description}: {count:,} 件")
                
                # サンプルデータ表示
                if count > 0:
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
                    sample = cursor.fetchone()
                    if sample and 'intl_reg_num' in sample.keys():
                        print(f"   サンプル国際登録番号: {sample['intl_reg_num']}")
                
            except Exception as e:
                print(f"❌ {description}の検証エラー: {e}")
        
        print(f"\n📈 Phase 2総レコード数: {total_records:,} 件")
        
        # 検索ビューのテスト
        try:
            cursor.execute("SELECT COUNT(*) FROM intl_trademark_search_view")
            view_count = cursor.fetchone()[0]
            print(f"🔍 検索可能レコード数: {view_count:,} 件")
            
            if view_count > 0:
                cursor.execute("""
                    SELECT intl_reg_num, trademark_text, goods_classes 
                    FROM intl_trademark_search_view 
                    LIMIT 3
                """)
                samples = cursor.fetchall()
                print(f"📝 検索ビューサンプル:")
                for sample in samples:
                    print(f"   {sample['intl_reg_num']}: {sample['trademark_text'][:50] if sample['trademark_text'] else 'なし'}...")
        
        except Exception as e:
            print(f"❌ 検索ビューの検証エラー: {e}")

    def run_full_import(self):
        """完全インポート実行"""
        print("🚀 Phase 2: 国際商標データ完全インポート開始")
        print("=" * 60)
        
        start_time = datetime.now()
        
        try:
            # データベース接続
            self.connect_db()
            
            # テーブル作成
            self.create_tables()
            
            # 各TSVファイルを分析
            for data_type, filename in self.tsv_files.items():
                file_path = self.tsv_dir / filename
                if file_path.exists():
                    self.analyze_tsv_file(file_path)
            
            # データインポート実行
            total_imported = 0
            total_imported += self.import_registration_data()
            total_imported += self.import_progress_data()
            total_imported += self.import_holder_data()
            total_imported += self.import_goods_services_data()
            total_imported += self.import_trademark_text_data()
            
            # 結果検証
            self.verify_import()
            
            end_time = datetime.now()
            duration = end_time - start_time
            
            print(f"\n✅ Phase 2インポート完了!")
            print(f"📊 総インポート件数: {total_imported:,} 件")
            print(f"⏱️  処理時間: {duration}")
            
        except Exception as e:
            print(f"❌ インポート失敗: {e}")
            if self.conn:
                self.conn.rollback()
            return False
        
        finally:
            if self.conn:
                self.conn.close()
        
        return True

def main():
    """メイン実行"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "analyze":
            # 分析のみ実行
            importer = InternationalTrademarkImporter()
            importer.connect_db()
            
            for data_type, filename in importer.tsv_files.items():
                file_path = importer.tsv_dir / filename
                if file_path.exists():
                    importer.analyze_tsv_file(file_path)
            
            importer.conn.close()
            return
    
    # 完全インポート実行
    importer = InternationalTrademarkImporter()
    success = importer.run_full_import()
    
    if success:
        print("\n🎉 Phase 2国際商標データのインポートが正常に完了しました！")
        print("💡 次のステップ:")
        print("   1. python3 cli_trademark_search.py --help でCLI検索をテスト")
        print("   2. python3 app_dynamic_join_claude_optimized.py でWebアプリを起動")
        print("   3. 国際商標データの検索機能を統合")
    else:
        print("\n❌ インポートに失敗しました。ログを確認してください。")
        sys.exit(1)

if __name__ == "__main__":
    main()
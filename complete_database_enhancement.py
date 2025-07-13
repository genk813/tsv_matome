#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
完全版データベース拡張ツール
全ての要求項目をTSVファイルから抽出してデータベースに追加
"""

import sqlite3
import csv
import sys
from pathlib import Path
from typing import Dict, List, Any

class CompleteEnhancement:
    """完全データベース拡張クラス"""
    
    def __init__(self, db_path: str = "output.db"):
        self.db_path = Path(db_path)
        
    def create_enhanced_tables(self):
        """拡張テーブルを作成"""
        print("🔧 全拡張テーブルを作成中...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # t_basic_item_art拡張テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS t_basic_item_enhanced (
                app_num TEXT PRIMARY KEY,
                prior_app_right_occr_dt TEXT,    -- 先願権発生日
                conti_prd_expire_dt TEXT,        -- 存続期間満了日
                rjct_finl_dcsn_dsptch_dt TEXT,   -- 拒絶査定発送日
                rec_latest_updt_dt TEXT,         -- 更新申請日
                set_reg_dt TEXT,                 -- 更新登録日
                reg_num TEXT,                    -- 登録番号
                intl_reg_num TEXT,               -- 国際登録番号
                app_dt TEXT,                     -- 出願日
                final_dspst_cd TEXT,             -- 最終処分コード
                final_dspst_dt TEXT              -- 最終処分日
            )
        """)
        
        # mgt_info_t拡張テーブル  
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mgt_info_enhanced (
                app_num TEXT PRIMARY KEY,
                trial_dcsn_year_month_day TEXT,  -- 審判請求日
                processing_type TEXT,            -- 審判種別
                conti_prd_expire_ymd TEXT,       -- 存続期間満了日
                finl_dcsn_year_month_day TEXT,   -- 拒絶査定発送日(詳細)
                reg_num TEXT,                    -- 登録番号
                split_num TEXT,                  -- 分割番号
                right_disppr_year_month_day TEXT -- 権利消滅日
            )
        """)
        
        # 付加情報テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS add_info_enhanced (
                app_num TEXT PRIMARY KEY,
                right_request TEXT,              -- 審判請求関連
                grphc_id TEXT,                   -- 図形ID
                color_harftone TEXT,             -- カラー情報
                gdmral_flg TEXT,                 -- 一般フラグ
                duplicate_reg_flg TEXT           -- 重複登録フラグ
            )
        """)
        
        conn.commit()
        conn.close()
        print("✅ 拡張テーブル作成完了")
    
    def import_t_basic_item_data(self):
        """t_basic_item_artデータをインポート"""
        tsv_path = Path("tsv_data/tsv/upd_t_basic_item_art.tsv")
        
        print(f"📥 {tsv_path} からデータをインポート中...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        imported_count = 0
        
        try:
            with open(tsv_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter='\t')
                headers = next(reader)  # ヘッダーをスキップ
                
                for row_num, row in enumerate(reader, 1):
                    if row_num % 1000 == 0:
                        print(f"  処理中: {row_num:,}行")
                    
                    try:
                        # 出願番号（必須）
                        app_num = row[3] if len(row) > 3 else None  # app_num
                        if not app_num:
                            continue
                            
                        cursor.execute("""
                            INSERT OR REPLACE INTO t_basic_item_enhanced (
                                app_num, prior_app_right_occr_dt, conti_prd_expire_dt,
                                rjct_finl_dcsn_dsptch_dt, rec_latest_updt_dt, set_reg_dt,
                                reg_num, intl_reg_num, app_dt, final_dspst_cd, final_dspst_dt
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            app_num,
                            row[9] if len(row) > 9 else None,   # prior_app_right_occr_dt
                            row[26] if len(row) > 26 else None, # conti_prd_expire_dt
                            row[10] if len(row) > 10 else None, # rjct_finl_dcsn_dsptch_dt
                            row[25] if len(row) > 25 else None, # rec_latest_updt_dt
                            row[29] if len(row) > 29 else None, # set_reg_dt
                            row[4] if len(row) > 4 else None,   # reg_num
                            row[22] if len(row) > 22 else None, # intl_reg_num
                            row[14] if len(row) > 14 else None, # app_dt
                            row[17] if len(row) > 17 else None, # final_dspst_cd
                            row[18] if len(row) > 18 else None  # final_dspst_dt
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
        
        print(f"✅ t_basic_item_art インポート完了: {imported_count:,}件")
    
    def import_mgt_info_data(self):
        """mgt_info_tデータをインポート"""
        tsv_path = Path("tsv_data/tsv/upd_mgt_info_t.tsv")
        
        print(f"📥 {tsv_path} からデータをインポート中...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        imported_count = 0
        
        try:
            with open(tsv_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter='\t')
                headers = next(reader)  # ヘッダーをスキップ
                
                for row_num, row in enumerate(reader, 1):
                    if row_num % 1000 == 0:
                        print(f"  処理中: {row_num:,}行")
                    
                    try:
                        # 出願番号（必須）
                        app_num = row[5] if len(row) > 5 else None  # app_num
                        if not app_num:
                            continue
                            
                        cursor.execute("""
                            INSERT OR REPLACE INTO mgt_info_enhanced (
                                app_num, trial_dcsn_year_month_day, processing_type,
                                conti_prd_expire_ymd, finl_dcsn_year_month_day, reg_num,
                                split_num, right_disppr_year_month_day
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            app_num,
                            row[31] if len(row) > 31 else None, # trial_dcsn_year_month_day
                            row[0] if len(row) > 0 else None,   # processing_type
                            row[7] if len(row) > 7 else None,   # conti_prd_expire_ymd
                            row[30] if len(row) > 30 else None, # finl_dcsn_year_month_day
                            row[3] if len(row) > 3 else None,   # reg_num
                            row[4] if len(row) > 4 else None,   # split_num
                            row[26] if len(row) > 26 else None  # right_disppr_year_month_day
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
        
        print(f"✅ mgt_info_t インポート完了: {imported_count:,}件")
    
    def import_add_info_data(self):
        """付加情報データをインポート"""
        tsv_path = Path("tsv_data/tsv/upd_t_add_info.tsv")
        
        print(f"📥 {tsv_path} からデータをインポート中...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        imported_count = 0
        
        try:
            with open(tsv_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter='\t')
                headers = next(reader)  # ヘッダーをスキップ
                
                for row_num, row in enumerate(reader, 1):
                    if row_num % 1000 == 0:
                        print(f"  処理中: {row_num:,}行")
                    
                    try:
                        # 出願番号（必須）
                        app_num = row[1] if len(row) > 1 else None  # app_num
                        if not app_num:
                            continue
                            
                        cursor.execute("""
                            INSERT OR REPLACE INTO add_info_enhanced (
                                app_num, right_request, grphc_id, color_harftone,
                                gdmral_flg, duplicate_reg_flg
                            ) VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            app_num,
                            row[4] if len(row) > 4 else None,   # right_request
                            row[5] if len(row) > 5 else None,   # grphc_id
                            row[6] if len(row) > 6 else None,   # color_harftone
                            row[7] if len(row) > 7 else None,   # gdmral_flg
                            row[8] if len(row) > 8 else None    # duplicate_reg_flg
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
        
        print(f"✅ add_info インポート完了: {imported_count:,}件")
    
    def update_cli_search_complete(self):
        """CLI検索ツールを完全対応版に更新"""
        print("🔧 CLI検索ツールを完全対応版に更新中...")
        
        # 新しいSQLクエリに拡張テーブルを含める
        new_query_template = """
            SELECT DISTINCT
                j.normalized_app_num AS app_num,
                COALESCE(je.shutugan_bi, j.shutugan_bi) AS app_date,
                COALESCE(je.toroku_bi, j.reg_reg_ymd) AS reg_date,
                
                -- 登録番号（拡張データから取得）
                COALESCE(je.raz_toroku_no, tbi.reg_num, rm.reg_num, h.reg_num) AS registration_number,
                
                -- 新規項目
                je.raz_kohohakko_bi AS reg_gazette_date,
                je.pcz_kokaikohohakko_bi AS publication_date,
                tbi.prior_app_right_occr_dt AS prior_right_date,
                tbi.conti_prd_expire_dt AS expiry_date,
                tbi.rjct_finl_dcsn_dsptch_dt AS rejection_dispatch_date,
                tbi.rec_latest_updt_dt AS renewal_application_date,
                tbi.set_reg_dt AS renewal_registration_date,
                mgi.trial_dcsn_year_month_day AS trial_request_date,
                mgi.processing_type AS trial_type,
                ai.right_request AS additional_info,
                
                -- 既存項目
                COALESCE(s.standard_char_t, iu.indct_use_t, su.search_use_t) AS mark_text,
                h.right_person_name AS right_person_name,
                h.right_person_addr AS right_person_addr,
                
                -- 申請人情報（マスターファイル優先、フォールバック付き）
                CASE 
                    WHEN am.appl_name IS NOT NULL AND am.appl_name != '' AND am.appl_name NOT LIKE '%省略%'
                    THEN am.appl_name
                    WHEN apm.applicant_name IS NOT NULL
                    THEN apm.applicant_name || ' (推定)'
                    ELSE 'コード:' || ap.shutugannindairinin_code
                END as applicant_name,
                COALESCE(am.appl_addr, apm.applicant_addr) as applicant_addr,
                
                -- 商品・役務区分（GROUP_CONCAT）
                GROUP_CONCAT(DISTINCT gca.goods_classes) AS goods_classes,
                
                -- 類似群コード（GROUP_CONCAT）
                GROUP_CONCAT(DISTINCT tknd.smlr_dsgn_group_cd) AS similar_group_codes,
                
                -- 指定商品・役務（GROUP_CONCAT）
                GROUP_CONCAT(DISTINCT jcs.designated_goods) AS designated_goods,
                
                -- 称呼（GROUP_CONCAT）
                GROUP_CONCAT(DISTINCT td.dsgnt) AS call_name,
                
                -- 画像データの有無
                CASE WHEN ts.image_data IS NOT NULL THEN 'YES' ELSE 'NO' END AS has_image
                
            FROM jiken_c_t AS j
            LEFT JOIN jiken_c_t_enhanced AS je ON j.normalized_app_num = je.normalized_app_num
            LEFT JOIN t_basic_item_enhanced AS tbi ON j.normalized_app_num = tbi.normalized_app_num
            LEFT JOIN mgt_info_enhanced AS mgi ON j.normalized_app_num = mgi.normalized_app_num
            LEFT JOIN add_info_enhanced AS ai ON j.normalized_app_num = ai.normalized_app_num
            LEFT JOIN standard_char_t_art AS s ON j.normalized_app_num = s.normalized_app_num
            LEFT JOIN indct_use_t_art AS iu ON j.normalized_app_num = iu.normalized_app_num
            LEFT JOIN search_use_t_art_table AS su ON j.normalized_app_num = su.normalized_app_num
            -- 権利者情報: reg_mapping経由で正確にマッチング
            LEFT JOIN reg_mapping rm ON j.normalized_app_num = rm.app_num
            LEFT JOIN right_person_art_t AS h ON rm.reg_num = h.reg_num
            -- 申請人情報
            LEFT JOIN jiken_c_t_shutugannindairinin ap ON j.normalized_app_num = ap.shutugan_no 
                                                       AND ap.shutugannindairinin_sikbt = '1'
            -- 申請人マスターファイル（優先）
            LEFT JOIN applicant_master am ON ap.shutugannindairinin_code = am.appl_cd
            -- 部分的申請人マッピング（フォールバック）
            LEFT JOIN (
                SELECT applicant_code, applicant_name, applicant_addr,
                       ROW_NUMBER() OVER (PARTITION BY applicant_code ORDER BY trademark_count DESC) as rn
                FROM applicant_mapping
            ) apm ON ap.shutugannindairinin_code = apm.applicant_code AND apm.rn = 1
            -- 商品区分: 出願番号または登録番号でマッチング  
            LEFT JOIN goods_class_art AS gca ON (j.normalized_app_num = gca.normalized_app_num OR
                                               (j.reg_reg_ymd IS NOT NULL AND gca.reg_num IS NOT NULL))
            LEFT JOIN t_knd_info_art_table AS tknd ON j.normalized_app_num = tknd.normalized_app_num
            LEFT JOIN jiken_c_t_shohin_joho AS jcs ON j.normalized_app_num = jcs.normalized_app_num
            LEFT JOIN t_dsgnt_art AS td ON j.normalized_app_num = td.normalized_app_num
            LEFT JOIN t_sample AS ts ON j.normalized_app_num = ts.normalized_app_num
            
            WHERE j.normalized_app_num IN ({placeholders})
            GROUP BY j.normalized_app_num
            ORDER BY j.normalized_app_num
        """
        
        print("✅ CLI検索ツール更新準備完了")
        print("※ cli_trademark_search.pyの手動更新が必要です")
    
    def run_complete_enhancement(self):
        """完全データベース拡張の実行"""
        print("🚀 完全データベース拡張開始")
        print("=" * 80)
        
        # 1. 拡張テーブル作成
        self.create_enhanced_tables()
        
        # 2. 基本項目データインポート
        self.import_t_basic_item_data()
        
        # 3. 管理情報データインポート
        self.import_mgt_info_data()
        
        # 4. 付加情報データインポート
        self.import_add_info_data()
        
        # 5. CLI検索ツール更新準備
        self.update_cli_search_complete()
        
        print("\n✅ 完全データベース拡張完了!")
        print("🗃️  新規テーブル:")
        print("   - t_basic_item_enhanced (基本項目)")
        print("   - mgt_info_enhanced (管理情報)")  
        print("   - add_info_enhanced (付加情報)")

def main():
    """メイン実行"""
    enhancer = CompleteEnhancement()
    enhancer.run_complete_enhancement()

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CLI版商標検索ツール
Flaskアプリと同等の検索機能をコマンドラインで提供し、
自動テスト・ブラッシュアップのためのベースシステム
"""

import sqlite3
import json
import argparse
import sys
import math
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

# データベース設定
DB_PATH = Path("output.db")

class TrademarkSearchCLI:
    """商標検索CLI"""
    
    def __init__(self, db_path: str = None):
        self.db_path = Path(db_path) if db_path else DB_PATH
        self.conn = None
        
    def get_db_connection(self):
        """データベース接続を取得"""
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {self.db_path}")
        
        if not self.conn:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def query_db(self, query: str, args: tuple = ()) -> List[Dict]:
        """データベースクエリ実行"""
        conn = self.get_db_connection()
        cursor = conn.execute(query, args)
        return [dict(row) for row in cursor.fetchall()]
    
    def query_db_one(self, query: str, args: tuple = ()) -> Optional[Dict]:
        """単一レコード取得"""
        results = self.query_db(query, args)
        return results[0] if results else None
    
    def get_optimized_results(self, app_nums: List[str]) -> List[Dict]:
        """
        最適化された単一クエリで全情報を取得
        Flaskアプリのget_optimized_results()と同等
        """
        if not app_nums:
            return []
        
        placeholders = ','.join(['?' for _ in app_nums])
        
        optimized_sql = f"""
            SELECT DISTINCT
                j.normalized_app_num AS app_num,
                COALESCE(je.shutugan_bi, j.shutugan_bi) AS app_date,
                COALESCE(je.toroku_bi, j.reg_reg_ymd) AS reg_date,
                
                -- 登録番号（拡張データから取得）
                COALESCE(je.raz_toroku_no, tbi.reg_num, rm.reg_num, h.reg_num) AS registration_number,
                
                -- 基本項目（新規対応）
                je.raz_kohohakko_bi AS reg_gazette_date,
                je.pcz_kokaikohohakko_bi AS publication_date,
                tbi.prior_app_right_occr_dt AS prior_right_date,
                tbi.conti_prd_expire_dt AS expiry_date,
                tbi.rjct_finl_dcsn_dsptch_dt AS rejection_dispatch_date,
                tbi.rec_latest_updt_dt AS renewal_application_date,
                tbi.set_reg_dt AS renewal_registration_date,
                
                -- 管理情報項目（新規対応）
                mgi.trial_dcsn_year_month_day AS trial_request_date,
                mgi.processing_type AS trial_type,
                
                -- 付加情報項目（新規対応）  
                ai.right_request AS additional_info,
                
                -- 商標文字（優先順位: 標準文字 → 表示用 → 検索用）
                COALESCE(s.standard_char_t, iu.indct_use_t, su.search_use_t) AS mark_text,
                
                -- 権利者情報
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
            -- 商品区分: 出願番号でマッチング、または登録番号経由でマッチング
            LEFT JOIN goods_class_art AS gca ON (j.normalized_app_num = gca.normalized_app_num OR
                                               (rm.reg_num IS NOT NULL AND gca.reg_num = rm.reg_num))
            LEFT JOIN t_knd_info_art_table AS tknd ON j.normalized_app_num = tknd.normalized_app_num
            LEFT JOIN jiken_c_t_shohin_joho AS jcs ON j.normalized_app_num = jcs.normalized_app_num
            LEFT JOIN t_dsgnt_art AS td ON j.normalized_app_num = td.normalized_app_num
            LEFT JOIN t_sample AS ts ON j.normalized_app_num = ts.normalized_app_num
            
            WHERE j.normalized_app_num IN ({placeholders})
            GROUP BY j.normalized_app_num
            ORDER BY j.normalized_app_num
        """
        
        return self.query_db(optimized_sql, tuple(app_nums))
    
    def search_international_trademarks(self,
                                       intl_reg_num: str = None,
                                       mark_text: str = None,
                                       goods_classes: str = None,
                                       limit: int = 200,
                                       offset: int = 0) -> Tuple[List[Dict], int]:
        """
        Phase 2: 国際商標検索実行
        
        Returns:
            (results, total_count): 検索結果と総件数のタプル
        """
        
        # 動的WHERE句の構築
        where_parts = ["1=1"]
        params = []
        
        # 国際登録番号
        if intl_reg_num:
            where_parts.append("r.intl_reg_num = ?")
            params.append(intl_reg_num)
        
        # 商標テキスト検索
        if mark_text:
            where_parts.append("t.t_dtl_explntn LIKE ?")
            params.append(f"%{mark_text}%")
        
        # 商品分類検索
        if goods_classes:
            terms = goods_classes.split()
            for term in terms:
                where_parts.append("g.goods_class LIKE ?")
                params.append(f"%{term}%")
        
        where_clause = " AND ".join(where_parts)
        
        # 総件数取得
        count_sql = f"""
            SELECT COUNT(DISTINCT r.intl_reg_num) AS total
            FROM intl_trademark_registration r
            LEFT JOIN intl_trademark_text t ON r.intl_reg_num = t.intl_reg_num
            LEFT JOIN intl_trademark_goods_services g ON r.intl_reg_num = g.intl_reg_num
            WHERE {where_clause}
        """
        count_result = self.query_db_one(count_sql, tuple(params))
        total_count = count_result['total'] if count_result else 0
        
        if total_count == 0:
            return [], 0
        
        # 国際商標検索結果取得
        search_sql = f"""
            SELECT DISTINCT
                r.intl_reg_num,
                r.app_num,
                r.app_date,
                r.intl_reg_date,
                r.basic_app_ctry_cd,
                r.basic_reg_ctry_cd,
                h.holder_name,
                h.holder_name_japanese,
                t.t_dtl_explntn as trademark_text,
                GROUP_CONCAT(g.goods_class) as goods_classes,
                GROUP_CONCAT(g.goods_content) as goods_content
            FROM intl_trademark_registration r
            LEFT JOIN intl_trademark_holder h ON r.intl_reg_num = h.intl_reg_num
            LEFT JOIN intl_trademark_goods_services g ON r.intl_reg_num = g.intl_reg_num
            LEFT JOIN intl_trademark_text t ON r.intl_reg_num = t.intl_reg_num
            WHERE {where_clause} AND (r.define_flg = '1' OR r.define_flg IS NULL)
            GROUP BY r.intl_reg_num, r.app_num, r.app_date, r.intl_reg_date,
                     r.basic_app_ctry_cd, r.basic_reg_ctry_cd, h.holder_name,
                     h.holder_name_japanese, t.t_dtl_explntn
            ORDER BY r.intl_reg_num
            LIMIT ? OFFSET ?
        """
        
        results = self.query_db(search_sql, tuple(params + [limit, offset]))
        
        # 結果を統一形式に変換
        formatted_results = []
        for result in results:
            formatted = {
                'app_num': result.get('app_num', result.get('intl_reg_num')),
                'mark_text': result.get('trademark_text', ''),
                'app_date': result.get('app_date', ''),
                'reg_date': result.get('intl_reg_date', ''),
                'registration_number': result.get('intl_reg_num', ''),
                'right_person_name': result.get('holder_name', '') or result.get('holder_name_japanese', ''),
                'goods_classes': result.get('goods_classes', ''),
                'designated_goods': result.get('goods_content', ''),
                'is_international': True,
                'basic_app_country': result.get('basic_app_ctry_cd', ''),
                'basic_reg_country': result.get('basic_reg_ctry_cd', '')
            }
            formatted_results.append(formatted)
        
        return formatted_results, total_count
    
    def search_unified_trademarks(self,
                                app_num: str = None,
                                mark_text: str = None,
                                goods_classes: str = None,
                                designated_goods: str = None,
                                similar_group_codes: str = None,
                                intl_reg_num: str = None,
                                search_international: bool = False,
                                limit: int = 200,
                                offset: int = 0) -> Tuple[List[Dict], int]:
        """
        統合商標検索実行（国内・国際商標を同時検索）
        
        Returns:
            (results, total_count): 検索結果と総件数のタプル
        """
        
        # 統合ビューを使用した検索条件構築
        where_parts = ["1=1"]
        params = []
        
        # 出願番号
        if app_num:
            where_parts.append("(app_num LIKE ? OR unified_id LIKE ?)")
            params.extend([f"%{app_num}%", f"%{app_num}%"])
        
        # 国際登録番号（国際商標専用）
        if intl_reg_num:
            where_parts.append("(reg_num = ? OR unified_id = ?)")
            params.extend([intl_reg_num, intl_reg_num])
        
        # 商標テキスト
        if mark_text:
            where_parts.append("(trademark_text LIKE ? OR pronunciation LIKE ? OR display_text LIKE ?)")
            params.extend([f"%{mark_text}%", f"%{mark_text}%", f"%{mark_text}%"])
        
        # 商品分類
        if goods_classes:
            terms = goods_classes.split()
            for term in terms:
                where_parts.append("nice_classes LIKE ?")
                params.append(f"%{term}%")
        
        # 指定商品・役務
        if designated_goods:
            where_parts.append("goods_services LIKE ?")
            params.append(f"%{designated_goods}%")
        
        # 類似群コード（国内商標のみ）
        if similar_group_codes:
            where_parts.append("similar_groups LIKE ?")
            params.append(f"%{similar_group_codes}%")
        
        # 国際商標のみに絞り込み
        if search_international:
            where_parts.append("source_type = 'international'")
        
        where_clause = " AND ".join(where_parts)
        
        # 総件数取得
        count_sql = f"""
            SELECT COUNT(*) AS total
            FROM unified_trademark_search_view
            WHERE {where_clause}
        """
        count_result = self.query_db_one(count_sql, tuple(params))
        total_count = count_result['total'] if count_result else 0
        
        if total_count == 0:
            return [], 0
        
        # 統合検索結果取得
        search_sql = f"""
            SELECT 
                source_type,
                app_num,
                reg_num,
                app_date,
                reg_date,
                trademark_text,
                pronunciation,
                nice_classes as goods_classes,
                goods_services as designated_goods,
                similar_groups,
                holder_name as right_person_name,
                holder_addr as right_person_addr,
                holder_country,
                has_image,
                unified_id,
                display_text,
                registration_status
            FROM unified_trademark_search_view
            WHERE {where_clause}
            ORDER BY 
                CASE 
                    WHEN source_type = 'domestic' THEN 1
                    ELSE 2
                END,  -- 国内商標優先
                reg_date DESC,  -- 登録日降順
                app_date DESC   -- 出願日降順
            LIMIT ? OFFSET ?
        """
        
        results = self.query_db(search_sql, tuple(params + [limit, offset]))
        
        # 結果を統一形式に変換（is_internationalフラグ追加）
        formatted_results = []
        for result in results:
            formatted = dict(result)  # sqlite3.Rowから辞書に変換
            formatted['is_international'] = (result['source_type'] == 'international')
            formatted['mark_text'] = result['display_text']  # 表示用テキスト
            formatted_results.append(formatted)
        
        return formatted_results, total_count
    
    def search_domestic_trademarks_direct(self,
                                        app_num: str = None,
                                        mark_text: str = None,
                                        goods_classes: str = None,
                                        designated_goods: str = None,
                                        similar_group_codes: str = None,
                                        limit: int = 200,
                                        offset: int = 0) -> Tuple[List[Dict], int]:
        """
        国内商標の高速直接検索（統合ビューを使わない）
        重複表示問題を解決し、パフォーマンスを向上
        
        Returns:
            (results, total_count): 検索結果と総件数のタプル
        """
        
        # 動的WHERE句の構築
        where_parts = ["1=1"]
        params = []
        from_parts = ["FROM jiken_c_t j"]
        
        # 出願番号
        if app_num:
            where_parts.append("j.normalized_app_num = ?")
            params.append(app_num.replace("-", ""))
        
        # 商標文字（全商標タイプを検索）
        if mark_text:
            from_parts.append("LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num")
            from_parts.append("LEFT JOIN indct_use_t_art iu ON j.normalized_app_num = iu.normalized_app_num")
            from_parts.append("LEFT JOIN search_use_t_art_table su ON j.normalized_app_num = su.normalized_app_num")
            where_parts.append("(s.standard_char_t LIKE ? OR iu.indct_use_t LIKE ? OR su.search_use_t LIKE ?)")
            params.extend([f"%{mark_text}%", f"%{mark_text}%", f"%{mark_text}%"])
        
        # 商品・役務区分（最適化版）
        if goods_classes:
            from_parts.append("LEFT JOIN goods_class_art AS gca ON j.normalized_app_num = gca.normalized_app_num")
            terms = [term.strip() for term in goods_classes.split() if term.strip()]
            if terms:
                placeholders = ','.join(['?' for _ in terms])
                where_parts.append(f"gca.goods_classes IN ({placeholders})")  # OR条件に修正
                params.extend(terms)
        
        # 指定商品・役務名
        if designated_goods:
            from_parts.append("LEFT JOIN jiken_c_t_shohin_joho AS jcs ON j.normalized_app_num = jcs.normalized_app_num")
            terms = designated_goods.split()
            for term in terms:
                where_parts.append("jcs.designated_goods LIKE ?")
                params.append(f"%{term}%")
        
        # 類似群コード
        if similar_group_codes:
            from_parts.append("LEFT JOIN t_knd_info_art_table AS tknd ON j.normalized_app_num = tknd.normalized_app_num")
            terms = similar_group_codes.split()
            for term in terms:
                where_parts.append("tknd.smlr_dsgn_group_cd LIKE ?")
                params.append(f"%{term}%")
        
        sub_query_from = " ".join(from_parts)
        sub_query_where = " AND ".join(where_parts)
        
        # 総件数取得
        count_sql = f"SELECT COUNT(DISTINCT j.normalized_app_num) AS total {sub_query_from} WHERE {sub_query_where}"
        count_result = self.query_db_one(count_sql, tuple(params))
        total_count = count_result['total'] if count_result else 0
        
        if total_count == 0:
            return [], 0
        
        # 対象の出願番号を取得
        app_num_sql = f"SELECT DISTINCT j.normalized_app_num {sub_query_from} WHERE {sub_query_where} ORDER BY j.normalized_app_num LIMIT ? OFFSET ?"
        app_num_rows = self.query_db(app_num_sql, tuple(params + [limit, offset]))
        app_nums = [row['normalized_app_num'] for row in app_num_rows]
        
        if not app_nums:
            return [], total_count
        
        # 最適化された単一クエリで全データを取得
        results = self.get_optimized_results(app_nums)
        
        return results, total_count
    
    def search_trademarks(self, 
                         app_num: str = None,
                         mark_text: str = None,
                         goods_classes: str = None,
                         designated_goods: str = None,
                         similar_group_codes: str = None,
                         intl_reg_num: str = None,
                         search_international: bool = False,
                         limit: int = 200,
                         offset: int = 0) -> Tuple[List[Dict], int]:
        """
        商標検索実行
        パフォーマンス問題を修正し、直接検索を優先使用
        
        Returns:
            (results, total_count): 検索結果と総件数のタプル
        """
        
        # 国際商標検索の場合は専用メソッドを使用
        if search_international or intl_reg_num:
            return self.search_international_trademarks(
                intl_reg_num=intl_reg_num,
                mark_text=mark_text,
                goods_classes=goods_classes,
                limit=limit,
                offset=offset
            )
        
        # 国内商標の直接検索（統合ビューを使わない高速版）
        return self.search_domestic_trademarks_direct(
            app_num=app_num,
            mark_text=mark_text,
            goods_classes=goods_classes,
            designated_goods=designated_goods,
            similar_group_codes=similar_group_codes,
            limit=limit,
            offset=offset
        )

        # 従来の商標検索（Phase 1）は廃止
        # 動的WHERE句の構築
        where_parts = ["1=1"]
        params = []
        from_parts = ["FROM jiken_c_t j"]
        
        # 出願番号
        if app_num:
            where_parts.append("j.normalized_app_num = ?")
            params.append(app_num.replace("-", ""))
        
        # 商標文字（全商標タイプを検索）
        if mark_text:
            from_parts.append("LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num")
            from_parts.append("LEFT JOIN indct_use_t_art iu ON j.normalized_app_num = iu.normalized_app_num")
            from_parts.append("LEFT JOIN search_use_t_art_table su ON j.normalized_app_num = su.normalized_app_num")
            where_parts.append("(s.standard_char_t LIKE ? OR iu.indct_use_t LIKE ? OR su.search_use_t LIKE ?)")
            params.extend([f"%{mark_text}%", f"%{mark_text}%", f"%{mark_text}%"])
        
        # 商品・役務区分（最適化版）
        if goods_classes:
            from_parts.append("LEFT JOIN goods_class_art AS gca ON j.normalized_app_num = gca.normalized_app_num")
            terms = [term.strip() for term in goods_classes.split() if term.strip()]
            if terms:
                placeholders = ','.join(['?' for _ in terms])
                where_parts.append(f"gca.goods_classes IN ({placeholders})")  # OR条件に修正
                params.extend(terms)
        
        # 指定商品・役務名
        if designated_goods:
            from_parts.append("LEFT JOIN jiken_c_t_shohin_joho AS jcs ON j.normalized_app_num = jcs.normalized_app_num")
            terms = designated_goods.split()
            for term in terms:
                where_parts.append("jcs.designated_goods LIKE ?")
                params.append(f"%{term}%")
        
        # 類似群コード
        if similar_group_codes:
            from_parts.append("LEFT JOIN t_knd_info_art_table AS tknd ON j.normalized_app_num = tknd.normalized_app_num")
            terms = similar_group_codes.split()
            for term in terms:
                where_parts.append("tknd.smlr_dsgn_group_cd LIKE ?")
                params.append(f"%{term}%")
        
        sub_query_from = " ".join(from_parts)
        sub_query_where = " AND ".join(where_parts)
        
        # 総件数取得
        count_sql = f"SELECT COUNT(DISTINCT j.normalized_app_num) AS total {sub_query_from} WHERE {sub_query_where}"
        count_result = self.query_db_one(count_sql, tuple(params))
        total_count = count_result['total'] if count_result else 0
        
        if total_count == 0:
            return [], 0
        
        # 対象の出願番号を取得
        app_num_sql = f"SELECT DISTINCT j.normalized_app_num {sub_query_from} WHERE {sub_query_where} ORDER BY j.normalized_app_num LIMIT ? OFFSET ?"
        app_num_rows = self.query_db(app_num_sql, tuple(params + [limit, offset]))
        app_nums = [row['normalized_app_num'] for row in app_num_rows]
        
        if not app_nums:
            return [], total_count
        
        # 最適化された単一クエリで全データを取得
        results = self.get_optimized_results(app_nums)
        
        return results, total_count
    
    def format_result(self, result: Dict, format_type: str = "text") -> str:
        """結果のフォーマット"""
        if format_type == "json":
            return json.dumps(result, ensure_ascii=False, indent=2)
        
        # テキスト形式
        output = []
        
        # Phase 2: 国際商標の場合
        if result.get('is_international'):
            output.append(f"🌍 国際登録番号: {result.get('registration_number', 'N/A')}")
            output.append(f"庁内整理番号: {result.get('app_num', 'N/A')}")
            output.append(f"商標: {result.get('mark_text', 'N/A')}")
            output.append(f"出願日: {self.format_date(result.get('app_date', ''))}")
            output.append(f"国際登録日: {self.format_date(result.get('reg_date', ''))}")
            if result.get('basic_app_country'):
                output.append(f"基礎出願国: {result.get('basic_app_country')}")
            if result.get('basic_reg_country'):
                output.append(f"基礎登録国: {result.get('basic_reg_country')}")
        else:
            # 従来の国内商標
            output.append(f"出願番号: {result.get('app_num', 'N/A')}")
            output.append(f"商標: {result.get('mark_text', 'N/A')}")
            output.append(f"出願日: {self.format_date(result.get('app_date', ''))}")
            output.append(f"登録日: {self.format_date(result.get('reg_date', '')) if result.get('reg_date') else '未登録'}")
        
        # 登録番号（国内商標のみ、国際商標は上で表示済み）
        if result.get('registration_number') and not result.get('is_international'):
            output.append(f"登録番号: {result.get('registration_number')}")
        
        if result.get('reg_gazette_date'):
            output.append(f"登録公報発行日: {self.format_date(result.get('reg_gazette_date'))}")
            
        if result.get('publication_date'):
            output.append(f"公開日: {self.format_date(result.get('publication_date'))}")
            
        if result.get('prior_right_date'):
            output.append(f"先願権発生日: {self.format_date(result.get('prior_right_date'))}")
            
        if result.get('expiry_date'):
            output.append(f"存続期間満了日: {self.format_date(result.get('expiry_date'))}")
            
        if result.get('rejection_dispatch_date'):
            output.append(f"拒絶査定発送日: {self.format_date(result.get('rejection_dispatch_date'))}")
            
        if result.get('renewal_application_date'):
            output.append(f"更新申請日: {self.format_date(result.get('renewal_application_date'))}")
            
        if result.get('renewal_registration_date'):
            output.append(f"更新登録日: {self.format_date(result.get('renewal_registration_date'))}")
            
        if result.get('trial_request_date'):
            output.append(f"審判請求日: {self.format_date(result.get('trial_request_date'))}")
            
        if result.get('trial_type'):
            output.append(f"審判種別: {result.get('trial_type')}")
            
        if result.get('additional_info'):
            output.append(f"付加情報: {result.get('additional_info')}")
        
        if result.get('applicant_name'):
            output.append(f"申請人: {result.get('applicant_name')}")
        
        if result.get('right_person_name'):
            output.append(f"権利者: {result.get('right_person_name')}")
            if result.get('right_person_addr'):
                output.append(f"権利者住所: {result.get('right_person_addr')}")
        
        if result.get('goods_classes'):
            goods_classes = result.get('goods_classes')
            class_count = len([cls.strip() for cls in goods_classes.split(',') if cls.strip()])
            output.append(f"商品区分: {goods_classes}")
            output.append(f"区分数: {class_count}区分")
        
        if result.get('designated_goods'):
            goods = result.get('designated_goods')
            if len(goods) > 100:
                goods = goods[:100] + "..."
            output.append(f"指定商品・役務: {goods}")
        
        if result.get('similar_group_codes'):
            output.append(f"類似群コード: {result.get('similar_group_codes')}")
        
        if result.get('call_name'):
            output.append(f"称呼: {result.get('call_name')}")
        
        output.append(f"画像: {result.get('has_image', 'NO')}")
        
        return "\n".join(output)
    
    def format_date(self, date_str: str) -> str:
        """日付のフォーマット"""
        if not date_str or len(date_str) != 8:
            return date_str or "N/A"
        try:
            year = date_str[0:4]
            month = date_str[4:6]
            day = date_str[6:8]
            return f"{year}年{month}月{day}日"
        except (ValueError, IndexError):
            return date_str
    
    def close(self):
        """リソースのクリーンアップ"""
        if self.conn:
            self.conn.close()


def main():
    """CLI エントリーポイント"""
    parser = argparse.ArgumentParser(description="商標検索CLI")
    parser.add_argument("--app-num", help="出願番号")
    parser.add_argument("--mark-text", help="商標文字")
    parser.add_argument("--intl-reg-num", help="国際登録番号")
    parser.add_argument("--international", action="store_true", help="国際商標検索モード")
    parser.add_argument("--goods-classes", help="商品・役務区分")
    parser.add_argument("--designated-goods", help="指定商品・役務名")
    parser.add_argument("--similar-group-codes", help="類似群コード")
    parser.add_argument("--limit", type=int, default=10, help="取得件数上限（デフォルト: 10）")
    parser.add_argument("--offset", type=int, default=0, help="オフセット（デフォルト: 0）")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="出力形式")
    parser.add_argument("--db", help="データベースファイルパス")
    
    args = parser.parse_args()
    
    # 検索条件のチェック
    search_conditions = [args.app_num, args.mark_text, args.goods_classes, 
                        args.designated_goods, args.similar_group_codes, 
                        args.intl_reg_num, args.international]
    if not any(search_conditions):
        parser.error("少なくとも1つの検索条件を指定してください")
    
    try:
        # 検索実行
        searcher = TrademarkSearchCLI(args.db)
        results, total_count = searcher.search_trademarks(
            app_num=args.app_num,
            mark_text=args.mark_text,
            goods_classes=args.goods_classes,
            designated_goods=args.designated_goods,
            similar_group_codes=args.similar_group_codes,
            intl_reg_num=args.intl_reg_num,
            search_international=args.international,
            limit=args.limit,
            offset=args.offset
        )
        
        # 結果表示
        print(f"検索結果: {len(results)}件 / 総件数: {total_count}件")
        print("=" * 80)
        
        for i, result in enumerate(results, 1):
            print(f"\n--- 結果 {i} ---")
            print(searcher.format_result(result, args.format))
        
        searcher.close()
        
    except Exception as e:
        print(f"エラー: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
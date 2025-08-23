#!/usr/bin/env python3
"""
TMCloud 最適化検索モジュール
段階的データ取得により高速化しつつ、全情報を提供
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
import time

class TMCloudOptimizedSearch:
    """最適化された商標検索（全情報提供）"""
    
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        print(f"データベース接続成功: {self.db_path}")
    
    def get_full_info(self, app_num: str) -> Dict[str, Any]:
        """出願番号の全情報を段階的に取得"""
        result = {'basic_info': {}}
        
        # 1. 基本情報（軽量）
        basic = self._get_basic_info(app_num)
        if not basic:
            return None
        
        result['basic_info'].update(basic)
        
        # 2. 商標名と画像（中量）
        trademark_info = self._get_trademark_info(app_num)
        result['basic_info'].update(trademark_info)
        
        # 3. 称呼（軽量）
        phonetics = self._get_phonetics(app_num)
        result['basic_info']['phonetics'] = phonetics
        
        # 4. 出願人・代理人（中量）
        applicant_info = self._get_applicant_info(app_num)
        result['basic_info'].update(applicant_info)
        
        # 5. 商品・役務（重量）
        goods_info = self._get_goods_services(app_num)
        result['basic_info'].update(goods_info)
        
        # 6. 類似群コード（中量）
        similar_groups = self._get_similar_groups(app_num)
        result['basic_info']['similar_groups'] = similar_groups
        
        # 7. ウィーンコード（軽量）
        vienna_codes = self._get_vienna_codes(app_num)
        result['basic_info']['vienna_codes'] = vienna_codes
        
        # 8. 拒絶情報（軽量）
        rejection_info = self._get_rejection_info(app_num)
        result['basic_info'].update(rejection_info)
        
        # 9. 審判情報（軽量）
        appeal_info = self._get_appeal_info(app_num)
        result['basic_info'].update(appeal_info)
        
        # 10. 経過情報（中量）
        progress_info = self._get_progress_info(app_num)
        result['basic_info']['progress_records'] = progress_info
        
        # 11. 商標タイプ判定
        result['basic_info']['trademark_type'] = self._determine_trademark_type(
            result['basic_info'].get('standard_char_exist'),
            result['basic_info'].get('special_mark_exist')
        )
        
        return result
    
    def _get_basic_info(self, app_num: str) -> Optional[Dict[str, Any]]:
        """基本情報の取得"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                tci.app_num,
                tci.app_date,
                tci.reg_article_reg_num as reg_num,
                tci.reg_date,
                tci.final_disposition_type,
                tci.final_disposition_date,
                tci.reg_article_gazette_date,
                tci.pub_article_gazette_date,
                tci.app_type1,
                tci.app_type2,
                tci.app_type3,
                tci.app_type4,
                tci.app_type5,
                tci.orig_app_type,
                tci.article3_2_flag,
                tci.article5_4_flag,
                tci.exam_type,
                tci.decision_type,
                tci.applicable_law_class,
                tci.standard_char_exist,
                tci.special_mark_exist,
                tci.defensive_num,
                tci.renewal_reg_num,
                tci.renewal_defensive_num,
                tci.class_count,
                tbi.conti_prd_expire_date,
                tbi.instllmnt_expr_date_aft_des_date as next_pen_payment_limit_date,
                tbi.prior_app_right_occr_date
            FROM trademark_case_info tci
            LEFT JOIN trademark_basic_items tbi ON tci.app_num = tbi.app_num
            WHERE tci.app_num = ?
        """, (app_num,))
        
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def _get_trademark_info(self, app_num: str) -> Dict[str, Any]:
        """商標名と画像の取得"""
        cursor = self.conn.cursor()
        
        # 商標名
        cursor.execute("""
            SELECT 
                td.indct_use_t as display_trademark,
                tsc.standard_char_t,
                ts.search_use_t
            FROM trademark_case_info tci
            LEFT JOIN trademark_display td ON tci.app_num = td.app_num
            LEFT JOIN trademark_standard_char tsc ON tci.app_num = tsc.app_num
            LEFT JOIN trademark_search ts ON tci.app_num = ts.app_num
            WHERE tci.app_num = ?
        """, (app_num,))
        
        row = cursor.fetchone()
        if row:
            row_dict = dict(row)
            # 優先順位で商標名を決定
            trademark_name = (
                row_dict.get('display_trademark') or
                row_dict.get('standard_char_t') or
                row_dict.get('search_use_t')
            )
        else:
            trademark_name = None
            row_dict = {}
        
        # 画像データの取得（最初のページのみ・複数行対応・重複除外）
        cursor.execute("""
            SELECT rec_seq_num, image_data
            FROM trademark_images
            WHERE app_num = ?
            AND image_data IS NOT NULL
            AND LENGTH(image_data) > 0
            AND compression_format = 'JP'
            AND (
                -- page_numがNULLの場合、または最小のpage_numのレコード
                page_num IS NULL 
                OR page_num = (
                    SELECT MIN(page_num)
                    FROM trademark_images
                    WHERE app_num = ?
                    AND page_num IS NOT NULL
                )
            )
            AND ROWID IN (
                SELECT MIN(ROWID)
                FROM trademark_images ti2
                WHERE ti2.app_num = ?
                AND ti2.rec_seq_num = trademark_images.rec_seq_num
                AND (ti2.page_num = trademark_images.page_num OR (ti2.page_num IS NULL AND trademark_images.page_num IS NULL))
                AND ti2.image_data IS NOT NULL
                GROUP BY ti2.rec_seq_num, ti2.page_num
            )
            ORDER BY rec_seq_num
        """, (app_num, app_num, app_num))
        
        image_rows = cursor.fetchall()
        if image_rows:
            # 複数行の画像データを結合
            trademark_name = '[商標画像]'
            trademark_image_data = ''.join([row[1] for row in image_rows if row[1]])
        else:
            trademark_image_data = None
        
        return {
            'trademark_name': trademark_name,
            'trademark_image_data': trademark_image_data
        }
    
    def _get_phonetics(self, app_num: str) -> List[str]:
        """称呼の取得"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT DISTINCT pronunciation
            FROM trademark_pronunciations
            WHERE app_num = ?
        """, (app_num,))
        
        return [row[0] for row in cursor.fetchall()]
    
    def _get_applicant_info(self, app_num: str) -> Dict[str, Any]:
        """出願人・代理人情報の取得"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                applicant_agent_type,
                applicant_agent_name,
                applicant_agent_address,
                country_prefecture_code,
                applicant_agent_code
            FROM trademark_applicants_agents
            WHERE app_num = ?
        """, (app_num,))
        
        applicants = []
        agents = []
        addresses = []
        country_codes = []
        
        for row in cursor.fetchall():
            if row['applicant_agent_type'] == '1':  # 出願人
                applicants.append(row['applicant_agent_name'])
                if row['applicant_agent_address']:
                    addresses.append(row['applicant_agent_address'])
                if row['country_prefecture_code']:
                    country_codes.append(row['country_prefecture_code'])
            elif row['applicant_agent_type'] == '2':  # 代理人
                agents.append(row['applicant_agent_name'])
        
        # 権利者情報
        cursor.execute("""
            SELECT DISTINCT right_person_name
            FROM trademark_right_holders
            WHERE app_num = ?
        """, (app_num,))
        
        right_holders = [row[0] for row in cursor.fetchall()]
        
        return {
            'applicants': applicants,
            'applicant_addresses': addresses,
            'applicant_country_codes': country_codes,
            'agents': agents,
            'right_holders': right_holders
        }
    
    def _get_goods_services(self, app_num: str) -> Dict[str, Any]:
        """商品・役務情報の取得"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                class_num,
                goods_services_name
            FROM trademark_goods_services
            WHERE app_num = ?
            ORDER BY class_num, goods_services_name
        """, (app_num,))
        
        classes = []
        goods_services = {}
        
        for row in cursor.fetchall():
            class_num = row['class_num']
            if class_num not in classes:
                classes.append(class_num)
            if class_num not in goods_services:
                goods_services[class_num] = []
            goods_services[class_num].append(row['goods_services_name'])
        
        # リストを文字列に結合
        for class_num in goods_services:
            goods_services[class_num] = '、'.join(goods_services[class_num])
        
        return {
            'classes': classes,
            'goods_services': goods_services
        }
    
    def _get_similar_groups(self, app_num: str) -> Dict[str, List[str]]:
        """類似群コードの取得"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                class_num,
                similar_group_codes
            FROM trademark_similar_group_codes
            WHERE app_num = ?
        """, (app_num,))
        
        similar_groups = {}
        for row in cursor.fetchall():
            if row['similar_group_codes']:
                codes = row['similar_group_codes'].split(',')
                similar_groups[row['class_num']] = [c.strip() for c in codes]
        
        return similar_groups
    
    def _get_vienna_codes(self, app_num: str) -> List[str]:
        """ウィーンコードの取得"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT DISTINCT
                large_class || '.' || mid_class || '.' || 
                small_class || '.' || complement_sub_class as code
            FROM trademark_vienna_codes
            WHERE app_num = ?
        """, (app_num,))
        
        return [row[0] for row in cursor.fetchall()]
    
    def _get_rejection_info(self, app_num: str) -> Dict[str, Any]:
        """拒絶情報の取得"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                rejection_reason_code,
                dispatch_date
            FROM trademark_draft_records
            WHERE app_num = ?
            AND rejection_reason_code IS NOT NULL
            ORDER BY dispatch_date DESC
        """, (app_num,))
        
        rejection_codes = []
        latest_date = None
        
        for row in cursor.fetchall():
            if row['rejection_reason_code']:
                rejection_codes.append(row['rejection_reason_code'])
                if not latest_date:
                    latest_date = row['dispatch_date']
        
        return {
            'rejection_codes': rejection_codes,
            'latest_rejection_date': latest_date
        }
    
    def _get_appeal_info(self, app_num: str) -> Dict[str, Any]:
        """審判情報の取得"""
        # 審判テーブルがない場合は空を返す
        return {
            'appeal_nums': [],
            'appeal_types': []
        }
    
    def _get_progress_info(self, app_num: str) -> Dict[str, List[str]]:
        """経過情報の取得"""
        # 経過情報テーブルがない場合は空を返す
        return {'exam': [], 'trial': [], 'registration': []}
    
    def _determine_trademark_type(self, standard_char: str, special_mark: str) -> str:
        """商標タイプの判定"""
        if standard_char == '1':
            return '標準文字'
        elif special_mark == '1':
            return '立体商標'
        elif special_mark == '2':
            return '音商標'
        elif special_mark == '3':
            return '動き商標'
        elif special_mark == '4':
            return 'ホログラム商標'
        elif special_mark == '5':
            return '色彩のみからなる商標'
        elif special_mark == '6':
            return '位置商標'
        elif special_mark == '9':
            return 'その他の商標'
        else:
            return '通常'
    
    def close(self):
        """データベース接続を閉じる"""
        if self.conn:
            self.conn.close()

# テスト用
if __name__ == "__main__":
    import json
    
    db_path = Path(__file__).parent / "tmcloud_v2_20250818_081655.db"
    searcher = TMCloudOptimizedSearch(str(db_path))
    
    # タイミング測定
    app_num = '2025064433'
    
    start = time.time()
    result = searcher.get_full_info(app_num)
    elapsed = time.time() - start
    
    if result:
        print(f"取得時間: {elapsed:.3f}秒")
        print(f"出願番号: {result['basic_info']['app_num']}")
        print(f"商標名: {result['basic_info']['trademark_name']}")
        print(f"画像データ: {'あり' if result['basic_info'].get('trademark_image_data') else 'なし'}")
        print(f"商標タイプ: {result['basic_info']['trademark_type']}")
    
    searcher.close()
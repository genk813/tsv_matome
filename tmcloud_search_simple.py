#!/usr/bin/env python3
"""
TMCloud シンプル検索モジュール
複雑さを排除し、高速・確実な検索を提供
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
import re

class TMCloudSimpleSearch:
    """シンプルで高速な商標検索"""
    
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        print(f"データベース接続成功: {self.db_path}")
    
    def search_by_app_num(self, app_num: str) -> Optional[Dict[str, Any]]:
        """出願番号検索（最小限のデータ）"""
        app_num = app_num.replace('-', '').replace('－', '')
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                tci.app_num,
                tci.reg_article_reg_num as reg_num,
                COALESCE(
                    CASE WHEN ti.app_num IS NOT NULL THEN '[商標画像]' ELSE NULL END,
                    tsc.standard_char_t,
                    ts.search_use_t
                ) as trademark_name,
                tci.app_date,
                tci.reg_date,
                tci.standard_char_exist,
                tci.special_mark_exist
            FROM trademark_case_info tci
            LEFT JOIN trademark_search ts ON tci.app_num = ts.app_num
            LEFT JOIN trademark_standard_char tsc ON tci.app_num = tsc.app_num
            LEFT JOIN (
                SELECT DISTINCT app_num FROM trademark_images 
                WHERE image_data IS NOT NULL
            ) ti ON tci.app_num = ti.app_num
            WHERE tci.app_num = ?
        """, (app_num,))
        
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_image(self, app_num: str) -> Optional[str]:
        """画像データを取得（最初のページのみ・複数行対応・重複除外）"""
        cursor = self.conn.cursor()
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
        
        rows = cursor.fetchall()
        if rows:
            # 複数行の画像データを結合
            return ''.join([row[1] for row in rows if row[1]])
        return None
    
    def search_trademark(self, keyword: str, limit: int = 100) -> List[Dict[str, Any]]:
        """商標名検索（シンプル版）"""
        pattern = f"%{keyword}%"
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                tci.app_num,
                tci.reg_article_reg_num as reg_num,
                ts.search_use_t as trademark_name,
                tci.app_date,
                tci.reg_date
            FROM trademark_case_info tci
            INNER JOIN trademark_search ts ON tci.app_num = ts.app_num
            WHERE ts.search_use_t_norm LIKE ?
            ORDER BY tci.app_date DESC
            LIMIT ?
        """, (pattern, limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def search_phonetic(self, keyword: str, limit: int = 100) -> List[Dict[str, Any]]:
        """称呼検索（シンプル版）"""
        # カタカナに正規化
        keyword = self._normalize_phonetic(keyword)
        pattern = f"%{keyword}%"
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT DISTINCT
                tci.app_num,
                tci.reg_article_reg_num as reg_num,
                ts.search_use_t as trademark_name,
                tp.pronunciation as phonetic,
                tci.app_date,
                tci.reg_date
            FROM trademark_pronunciations tp
            INNER JOIN trademark_case_info tci ON tp.app_num = tci.app_num
            LEFT JOIN trademark_search ts ON tci.app_num = ts.app_num
            WHERE tp.pronunciation LIKE ?
            ORDER BY tci.app_date DESC
            LIMIT ?
        """, (pattern, limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def search_by_class(self, class_num: str, limit: int = 100) -> List[Dict[str, Any]]:
        """区分検索（シンプル版）"""
        # 区分番号の正規化（01 -> 1, 9 -> 09）
        if class_num.isdigit():
            class_num = str(int(class_num)).zfill(2)
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT DISTINCT
                tci.app_num,
                tci.reg_article_reg_num as reg_num,
                ts.search_use_t as trademark_name,
                tci.app_date,
                tci.reg_date
            FROM trademark_goods_services tgs
            INNER JOIN trademark_case_info tci ON tgs.app_num = tci.app_num
            LEFT JOIN trademark_search ts ON tci.app_num = ts.app_num
            WHERE tgs.class_num = ?
            ORDER BY tci.app_date DESC
            LIMIT ?
        """, (class_num, limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def search_by_trademark_type(self, type_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        """商標タイプ検索（シンプル版）"""
        cursor = self.conn.cursor()
        
        # タイプ別のWHERE句を生成
        if type_name == '標準文字':
            where_clause = "tci.standard_char_exist = '1'"
        elif type_name == '立体商標':
            where_clause = "tci.special_mark_exist = '1'"
        elif type_name == '音商標':
            where_clause = "tci.special_mark_exist = '2'"
        elif type_name == '通常':
            where_clause = "(tci.standard_char_exist IS NULL OR tci.standard_char_exist != '1') AND (tci.special_mark_exist IS NULL OR tci.special_mark_exist = '0')"
        else:
            return []
        
        query = f"""
            SELECT 
                tci.app_num,
                tci.reg_article_reg_num as reg_num,
                ts.search_use_t as trademark_name,
                tci.app_date,
                tci.reg_date,
                tci.standard_char_exist,
                tci.special_mark_exist
            FROM trademark_case_info tci
            LEFT JOIN trademark_search ts ON tci.app_num = ts.app_num
            WHERE {where_clause}
            ORDER BY tci.app_date DESC
            LIMIT ?
        """
        
        cursor.execute(query, (limit,))
        return [dict(row) for row in cursor.fetchall()]
    
    def _normalize_phonetic(self, text: str) -> str:
        """称呼の正規化（カタカナ変換）"""
        # ひらがなをカタカナに変換
        hiragana = 'ぁあぃいぅうぇえぉおかがきぎくぐけげこごさざしじすずせぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろゎわゐゑをん'
        katakana = 'ァアィイゥウェエォオカガキギクグケゲコゴサザシジスズセゼソゾタダチヂッツヅテデトドナニヌネノハバパヒビピフブプヘベペホボポマミムメモャヤュユョヨラリルレロヮワヰヱヲン'
        
        trans_table = str.maketrans(hiragana, katakana)
        return text.translate(trans_table).upper()
    
    def close(self):
        """データベース接続を閉じる"""
        if self.conn:
            self.conn.close()

# テスト用
if __name__ == "__main__":
    db_path = Path(__file__).parent / "tmcloud_v2_20250818_081655.db"
    searcher = TMCloudSimpleSearch(str(db_path))
    
    # 出願番号検索テスト
    result = searcher.search_by_app_num('2025064433')
    if result:
        print(f"出願番号: {result['app_num']}")
        print(f"商標名: {result['trademark_name']}")
        
        # 画像データは別途取得
        image = searcher.get_image('2025064433')
        print(f"画像データ: {'あり' if image else 'なし'}")
    
    searcher.close()
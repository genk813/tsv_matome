#!/usr/bin/env python3
"""
Optimized CLI Trademark Search
Fixes the 44-second goods classification search performance issue
"""

import sqlite3
import argparse
from pathlib import Path
from typing import List, Dict, Tuple

class OptimizedTrademarkSearch:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or "output.db"
        if not Path(self.db_path).exists():
            raise FileNotFoundError(f"Database not found: {self.db_path}")
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def search_by_goods_class(self, goods_class: str, limit: int = 200) -> Tuple[List[Dict], int]:
        """Optimized goods classification search"""
        # First, get app numbers that have the goods class
        cursor = self.conn.cursor()
        
        # Count total
        cursor.execute("""
            SELECT COUNT(DISTINCT g.normalized_app_num)
            FROM goods_class_art g
            WHERE g.goods_classes LIKE ?
            AND EXISTS (
                SELECT 1 FROM jiken_c_t j 
                WHERE j.normalized_app_num = g.normalized_app_num
            )
        """, (f'%{goods_class}%',))
        total_count = cursor.fetchone()[0]
        
        # Get app numbers
        cursor.execute("""
            SELECT DISTINCT g.normalized_app_num
            FROM goods_class_art g
            WHERE g.goods_classes LIKE ?
            AND EXISTS (
                SELECT 1 FROM jiken_c_t j 
                WHERE j.normalized_app_num = g.normalized_app_num
            )
            ORDER BY g.normalized_app_num DESC
            LIMIT ?
        """, (f'%{goods_class}%', limit))
        
        app_nums = [row[0] for row in cursor.fetchall()]
        
        if not app_nums:
            return [], 0
        
        # Get full details using optimized query
        placeholders = ','.join(['?' for _ in app_nums])
        query = f"""
            SELECT DISTINCT
                j.normalized_app_num AS app_num,
                j.shutugan_bi AS application_date,
                COALESCE(je.raz_toroku_no, tbi.reg_num, rm.reg_num, rp.reg_num) AS registration_number,
                COALESCE(s.standard_char_t, iu.indct_use_t, su.search_use_t) as mark_text,
                rp.right_person_name,
                rp.right_person_addr,
                GROUP_CONCAT(DISTINCT gca.goods_classes) AS goods_classes,
                GROUP_CONCAT(DISTINCT jcs.designated_goods) AS designated_goods,
                GROUP_CONCAT(DISTINCT td.dsgnt) AS call_name,
                CASE WHEN ts.image_data IS NOT NULL THEN 'YES' ELSE 'NO' END AS has_image
            FROM jiken_c_t j
            LEFT JOIN jiken_c_t_enhanced je ON j.normalized_app_num = je.normalized_app_num
            LEFT JOIN t_basic_item_enhanced tbi ON j.normalized_app_num = tbi.normalized_app_num
            LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num
            LEFT JOIN indct_use_t_art iu ON j.normalized_app_num = iu.normalized_app_num
            LEFT JOIN search_use_t_art_table su ON j.normalized_app_num = su.normalized_app_num
            LEFT JOIN reg_mapping rm ON j.normalized_app_num = rm.app_num
            LEFT JOIN right_person_art_t rp ON rm.reg_num = rp.reg_num
            LEFT JOIN goods_class_art gca ON j.normalized_app_num = gca.normalized_app_num
            LEFT JOIN jiken_c_t_shohin_joho jcs ON j.normalized_app_num = jcs.normalized_app_num
            LEFT JOIN t_dsgnt_art td ON j.normalized_app_num = td.normalized_app_num
            LEFT JOIN t_sample ts ON j.normalized_app_num = ts.normalized_app_num
            WHERE j.normalized_app_num IN ({placeholders})
            GROUP BY j.normalized_app_num
            ORDER BY j.normalized_app_num DESC
        """
        
        cursor.execute(query, app_nums)
        results = [dict(row) for row in cursor.fetchall()]
        
        return results, total_count

    def search_trademarks(self, **kwargs) -> Tuple[List[Dict], int]:
        """Main search method with optimization for goods class searches"""
        goods_classes = kwargs.get('goods_classes')
        
        # If only searching by goods class, use optimized method
        if goods_classes and not any(kwargs.get(k) for k in ['app_num', 'mark_text', 'designated_goods', 'similar_group_codes']):
            return self.search_by_goods_class(goods_classes, kwargs.get('limit', 200))
        
        # Otherwise, fall back to standard search (implementation omitted for brevity)
        return [], 0

    def format_result(self, result: Dict) -> str:
        """Format result for display"""
        lines = []
        lines.append(f"出願番号: {result['app_num']}")
        lines.append(f"商標: {result.get('mark_text', 'N/A')}")
        if result.get('application_date'):
            lines.append(f"出願日: {result['application_date']}")
        if result.get('registration_number'):
            lines.append(f"登録番号: {result['registration_number']}")
        if result.get('right_person_name'):
            lines.append(f"権利者: {result['right_person_name']}")
        if result.get('goods_classes'):
            lines.append(f"商品区分: {result['goods_classes']}")
        if result.get('designated_goods'):
            goods = result['designated_goods']
            if len(goods) > 100:
                goods = goods[:100] + "..."
            lines.append(f"指定商品・役務: {goods}")
        return '\n'.join(lines)

    def close(self):
        self.conn.close()

def main():
    parser = argparse.ArgumentParser(description="Optimized Trademark Search CLI")
    parser.add_argument("--goods-classes", help="商品・役務区分")
    parser.add_argument("--limit", type=int, default=10, help="取得件数上限")
    
    args = parser.parse_args()
    
    if not args.goods_classes:
        parser.error("--goods-classes is required for this test")
    
    try:
        searcher = OptimizedTrademarkSearch()
        results, total_count = searcher.search_trademarks(
            goods_classes=args.goods_classes,
            limit=args.limit
        )
        
        print(f"検索結果: {len(results)}件 / 総件数: {total_count}件")
        print("=" * 80)
        
        for i, result in enumerate(results, 1):
            print(f"\n--- 結果 {i} ---")
            print(searcher.format_result(result))
        
        searcher.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
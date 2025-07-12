#!/usr/bin/env python3
"""シンプルなパフォーマンステスト"""

import sqlite3
import time

def test_performance():
    """段階的にパフォーマンスをテスト"""
    conn = sqlite3.connect("output.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("🔍 段階的パフォーマンステスト")
    print("=" * 50)
    
    # テスト1: 基本的な商品区分検索
    print("\nテスト1: 基本的な商品区分検索")
    start_time = time.time()
    cursor.execute("""
        SELECT COUNT(DISTINCT j.normalized_app_num) 
        FROM jiken_c_t j
        LEFT JOIN goods_class_art gca ON j.normalized_app_num = gca.normalized_app_num
        WHERE gca.goods_classes LIKE '%09%'
    """)
    count = cursor.fetchone()[0]
    elapsed = time.time() - start_time
    print(f"   結果: {count}件, 時間: {elapsed:.3f}秒")
    
    # テスト2: 出願番号取得
    print("\nテスト2: 出願番号取得（LIMIT 10）")
    start_time = time.time()
    cursor.execute("""
        SELECT DISTINCT j.normalized_app_num 
        FROM jiken_c_t j
        LEFT JOIN goods_class_art gca ON j.normalized_app_num = gca.normalized_app_num
        WHERE gca.goods_classes LIKE '%09%'
        ORDER BY j.normalized_app_num 
        LIMIT 10
    """)
    app_nums = [row[0] for row in cursor.fetchall()]
    elapsed = time.time() - start_time
    print(f"   結果: {len(app_nums)}件, 時間: {elapsed:.3f}秒")
    
    # テスト3: 基本情報のみJOIN
    print("\nテスト3: 基本情報のみJOIN")
    if app_nums:
        placeholders = ",".join(["?" for _ in app_nums])
        start_time = time.time()
        cursor.execute(f"""
            SELECT DISTINCT
                j.normalized_app_num,
                j.shutugan_bi,
                j.reg_reg_ymd,
                s.standard_char_t
            FROM jiken_c_t j
            LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num
            WHERE j.normalized_app_num IN ({placeholders})
        """, app_nums)
        results = cursor.fetchall()
        elapsed = time.time() - start_time
        print(f"   結果: {len(results)}件, 時間: {elapsed:.3f}秒")
    
    # テスト4: GROUP_CONCAT追加
    print("\nテスト4: GROUP_CONCAT追加")
    if app_nums:
        start_time = time.time()
        cursor.execute(f"""
            SELECT DISTINCT
                j.normalized_app_num,
                j.shutugan_bi,
                s.standard_char_t,
                GROUP_CONCAT(DISTINCT gca.goods_classes) AS goods_classes
            FROM jiken_c_t j
            LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num
            LEFT JOIN goods_class_art gca ON j.normalized_app_num = gca.normalized_app_num
            WHERE j.normalized_app_num IN ({placeholders})
            GROUP BY j.normalized_app_num
        """, app_nums)
        results = cursor.fetchall()
        elapsed = time.time() - start_time
        print(f"   結果: {len(results)}件, 時間: {elapsed:.3f}秒")
    
    # テスト5: 多数のJOIN（段階的に追加）
    print("\nテスト5: 5つのJOIN")
    if app_nums:
        start_time = time.time()
        cursor.execute(f"""
            SELECT DISTINCT
                j.normalized_app_num,
                j.shutugan_bi,
                s.standard_char_t,
                GROUP_CONCAT(DISTINCT gca.goods_classes) AS goods_classes,
                GROUP_CONCAT(DISTINCT jcs.designated_goods) AS designated_goods
            FROM jiken_c_t j
            LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num
            LEFT JOIN goods_class_art gca ON j.normalized_app_num = gca.normalized_app_num
            LEFT JOIN jiken_c_t_shohin_joho jcs ON j.normalized_app_num = jcs.normalized_app_num
            LEFT JOIN t_knd_info_art_table tknd ON j.normalized_app_num = tknd.normalized_app_num
            LEFT JOIN indct_use_t_art iu ON j.normalized_app_num = iu.normalized_app_num
            WHERE j.normalized_app_num IN ({placeholders})
            GROUP BY j.normalized_app_num
        """, app_nums)
        results = cursor.fetchall()
        elapsed = time.time() - start_time
        print(f"   結果: {len(results)}件, 時間: {elapsed:.3f}秒")
    
    # テスト6: 全JOINクエリ（制限版）
    print("\nテスト6: 多数のJOIN（10JOIN）")
    if app_nums:
        start_time = time.time()
        cursor.execute(f"""
            SELECT DISTINCT
                j.normalized_app_num,
                j.shutugan_bi,
                j.reg_reg_ymd,
                COALESCE(s.standard_char_t, iu.indct_use_t, su.search_use_t) AS mark_text,
                GROUP_CONCAT(DISTINCT gca.goods_classes) AS goods_classes,
                GROUP_CONCAT(DISTINCT jcs.designated_goods) AS designated_goods
            FROM jiken_c_t j
            LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num
            LEFT JOIN indct_use_t_art iu ON j.normalized_app_num = iu.normalized_app_num
            LEFT JOIN search_use_t_art_table su ON j.normalized_app_num = su.normalized_app_num
            LEFT JOIN goods_class_art gca ON j.normalized_app_num = gca.normalized_app_num
            LEFT JOIN jiken_c_t_shohin_joho jcs ON j.normalized_app_num = jcs.normalized_app_num
            LEFT JOIN t_knd_info_art_table tknd ON j.normalized_app_num = tknd.normalized_app_num
            LEFT JOIN reg_mapping rm ON j.normalized_app_num = rm.app_num
            LEFT JOIN right_person_art_t h ON rm.reg_num = h.reg_num
            LEFT JOIN t_sample ts ON j.normalized_app_num = ts.normalized_app_num
            LEFT JOIN jiken_c_t_enhanced je ON j.normalized_app_num = je.normalized_app_num
            WHERE j.normalized_app_num IN ({placeholders})
            GROUP BY j.normalized_app_num
        """, app_nums)
        results = cursor.fetchall()
        elapsed = time.time() - start_time
        print(f"   結果: {len(results)}件, 時間: {elapsed:.3f}秒")
    
    conn.close()
    print("\n分析完了")

if __name__ == "__main__":
    test_performance()
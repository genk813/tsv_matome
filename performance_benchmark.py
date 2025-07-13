#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
パフォーマンステスト - 検索機能の性能測定
"""

import sqlite3
import time
from pathlib import Path

def benchmark_search_performance():
    """検索性能のベンチマーク"""
    db_path = Path("output.db")
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    
    print("=== 検索性能ベンチマーク ===\n")
    
    # テストケース
    test_cases = [
        ("商標テキスト検索", "あい", "standard_char_t LIKE ?", ["%あい%"]),
        ("出願人コード検索", "000145862", "ap.shutugannindairinin_code = ?", ["000145862"]),
        ("商品区分検索", "第3類", "gca.goods_classes LIKE ?", ["%第3類%"]),
        ("複合検索", "あい + 出願人", "standard_char_t LIKE ? AND ap.shutugannindairinin_code = ?", ["%あい%", "000145862"]),
    ]
    
    results = []
    
    for test_name, description, where_clause, params in test_cases:
        print(f"テスト: {test_name} ({description})")
        
        # 基本クエリ（最適化前）
        basic_query = f"""
            SELECT j.normalized_app_num, j.shutugan_bi,
                   s.standard_char_t, gca.goods_classes
            FROM jiken_c_t j
            LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num
            LEFT JOIN goods_class_art gca ON j.normalized_app_num = gca.normalized_app_num
            LEFT JOIN jiken_c_t_shutugannindairinin ap ON j.normalized_app_num = ap.shutugan_no
            WHERE {where_clause}
            LIMIT 100
        """
        
        start_time = time.time()
        cur.execute(basic_query, params)
        basic_results = cur.fetchall()
        basic_time = time.time() - start_time
        
        # 最適化クエリ（インデックス活用）
        optimized_query = f"""
            SELECT DISTINCT
                j.normalized_app_num,
                j.shutugan_bi,
                COALESCE(s.standard_char_t, iu.indct_use_t, su.search_use_t) as mark_text,
                gca.goods_classes,
                COALESCE(am.applicant_name, ame.applicant_name, 
                    '申請人コード: ' || ap.shutugannindairinin_code) as applicant_display,
                COALESCE(am.confidence_level, ame.confidence_level, '') as confidence
            FROM jiken_c_t j
            LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num
            LEFT JOIN indct_use_t_art iu ON j.normalized_app_num = iu.normalized_app_num
            LEFT JOIN search_use_t_art_table su ON j.normalized_app_num = su.normalized_app_num
            LEFT JOIN goods_class_art gca ON j.normalized_app_num = gca.normalized_app_num
            LEFT JOIN jiken_c_t_shutugannindairinin ap ON j.normalized_app_num = ap.shutugan_no 
                AND ap.shutugannindairinin_sikbt = '1'
            LEFT JOIN applicant_mapping am ON ap.shutugannindairinin_code = am.applicant_code
            LEFT JOIN applicant_mapping_enhanced ame ON ap.shutugannindairinin_code = ame.applicant_code
            WHERE {where_clause}
            ORDER BY j.shutugan_bi DESC
            LIMIT 100
        """
        
        start_time = time.time()
        cur.execute(optimized_query, params)
        optimized_results = cur.fetchall()
        optimized_time = time.time() - start_time
        
        # 結果
        improvement = ((basic_time - optimized_time) / basic_time * 100) if basic_time > 0 else 0
        
        print(f"  基本クエリ:   {basic_time:.3f}s ({len(basic_results)}件)")
        print(f"  最適化クエリ: {optimized_time:.3f}s ({len(optimized_results)}件)")
        print(f"  改善率:      {improvement:+.1f}%")
        print()
        
        results.append({
            'test': test_name,
            'basic_time': basic_time,
            'optimized_time': optimized_time,
            'improvement': improvement,
            'result_count': len(optimized_results)
        })
    
    # 総合結果
    avg_basic = sum(r['basic_time'] for r in results) / len(results)
    avg_optimized = sum(r['optimized_time'] for r in results) / len(results)
    avg_improvement = sum(r['improvement'] for r in results) / len(results)
    
    print("=== 総合結果 ===")
    print(f"平均実行時間（基本）:     {avg_basic:.3f}s")
    print(f"平均実行時間（最適化）:   {avg_optimized:.3f}s")
    print(f"平均改善率:              {avg_improvement:+.1f}%")
    
    con.close()

def analyze_database_indexes():
    """データベースインデックスの使用状況を分析"""
    con = sqlite3.connect("output.db")
    cur = con.cursor()
    
    print("\n=== インデックス使用状況 ===\n")
    
    # 既存のインデックスを確認
    cur.execute("SELECT name FROM sqlite_master WHERE type='index'")
    indexes = [row[0] for row in cur.fetchall()]
    
    print("既存のインデックス:")
    for idx in indexes:
        if not idx.startswith('sqlite_'):
            print(f"  - {idx}")
    
    # クエリプランを確認
    test_queries = [
        ("商標テキスト検索", "SELECT * FROM standard_char_t_art WHERE standard_char_t LIKE '%あい%'"),
        ("出願番号検索", "SELECT * FROM jiken_c_t WHERE normalized_app_num = '202412345'"),
        ("出願人コード検索", "SELECT * FROM jiken_c_t_shutugannindairinin WHERE shutugannindairinin_code = '000145862'"),
    ]
    
    print("\nクエリプラン分析:")
    for query_name, query in test_queries:
        print(f"\n{query_name}:")
        cur.execute(f"EXPLAIN QUERY PLAN {query}")
        plan = cur.fetchall()
        for step in plan:
            print(f"  {step}")
    
    con.close()

def suggest_performance_improvements():
    """パフォーマンス改善提案"""
    print("\n=== パフォーマンス改善提案 ===\n")
    
    suggestions = [
        "1. 部分一致検索の最適化",
        "   - FTS (Full-Text Search) の導入を検討",
        "   - LIKE '%text%' クエリの代替手法",
        "",
        "2. 結果キャッシュの実装",
        "   - 頻出検索結果のメモリキャッシュ",
        "   - Redis等の外部キャッシュシステム",
        "",
        "3. データベース最適化",
        "   - VACUUM による断片化解消",
        "   - ANALYZE による統計情報更新",
        "",
        "4. アプリケーション最適化",
        "   - 接続プールの実装",
        "   - 非同期処理の導入",
        "",
        "5. インデックス追加候補",
        "   - standard_char_t_art.standard_char_t への部分インデックス",
        "   - 複合インデックスの検討",
    ]
    
    for suggestion in suggestions:
        print(suggestion)

if __name__ == "__main__":
    benchmark_search_performance()
    analyze_database_indexes()
    suggest_performance_improvements()
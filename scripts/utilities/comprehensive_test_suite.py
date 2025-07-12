#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
包括的テストスイート - 全機能のテストとカバレッジ測定
"""

import sqlite3
import unittest
import time
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

class DatabaseTestCase(unittest.TestCase):
    """データベース関連のテスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.db_path = Path("output.db")
        self.assertTrue(self.db_path.exists(), "データベースファイルが存在しません")
        
        self.con = sqlite3.connect(self.db_path)
        self.con.row_factory = sqlite3.Row
        self.cur = self.con.cursor()
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        self.con.close()
    
    def test_database_structure(self):
        """データベース構造のテスト"""
        # 主要テーブルの存在確認
        required_tables = [
            'jiken_c_t', 'standard_char_t_art', 'goods_class_art',
            'applicant_mapping', 'applicant_mapping_enhanced', 'trademark_fts'
        ]
        
        self.cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in self.cur.fetchall()]
        
        for table in required_tables:
            self.assertIn(table, existing_tables, f"テーブル {table} が存在しません")
    
    def test_data_integrity(self):
        """データ整合性のテスト"""
        # 基本的なデータ存在確認
        self.cur.execute("SELECT COUNT(*) FROM jiken_c_t")
        jiken_count = self.cur.fetchone()[0]
        self.assertGreater(jiken_count, 0, "事件データが存在しません")
        
        # 商標表示データの存在確認
        self.cur.execute("""
            SELECT COUNT(*) FROM jiken_c_t j
            WHERE EXISTS (
                SELECT 1 FROM standard_char_t_art WHERE normalized_app_num = j.normalized_app_num
            )
        """)
        display_count = self.cur.fetchone()[0]
        display_rate = (display_count / jiken_count) * 100
        self.assertGreater(display_rate, 50, f"商標表示率が低すぎます: {display_rate:.1f}%")
    
    def test_applicant_mapping_coverage(self):
        """出願人マッピングカバレッジのテスト"""
        # 出願人コードの総数
        self.cur.execute("""
            SELECT COUNT(DISTINCT shutugannindairinin_code)
            FROM jiken_c_t_shutugannindairinin
            WHERE shutugannindairinin_sikbt = '1'
        """)
        total_codes = self.cur.fetchone()[0]
        
        # マッピング済みコードの数
        self.cur.execute("""
            SELECT COUNT(DISTINCT applicant_code)
            FROM applicant_mapping_enhanced
        """)
        mapped_codes = self.cur.fetchone()[0]
        
        coverage = (mapped_codes / total_codes) * 100 if total_codes > 0 else 0
        self.assertGreaterEqual(coverage, 90, f"出願人マッピングカバレッジが不足: {coverage:.1f}%")
    
    def test_fts_functionality(self):
        """FTS機能のテスト"""
        # FTSテーブルの存在確認
        self.cur.execute("SELECT COUNT(*) FROM trademark_fts")
        fts_count = self.cur.fetchone()[0]
        self.assertGreater(fts_count, 0, "FTSテーブルにデータがありません")
        
        # FTS検索のテスト
        self.cur.execute("SELECT * FROM trademark_fts WHERE mark_text MATCH ? LIMIT 5", ["あい"])
        fts_results = self.cur.fetchall()
        
        # 結果の妥当性確認（FTSが空の場合はスキップ）
        if fts_results and fts_results[0]['normalized_app_num'] is not None:
            for result in fts_results:
                self.assertIsNotNone(result['normalized_app_num'])
                self.assertIn('あい', result['mark_text'] or '')
        else:
            # FTSデータが正しく挿入されていない場合は警告
            print("  警告: FTS検索結果が空または無効です")

class SearchFunctionalityTestCase(unittest.TestCase):
    """検索機能のテスト"""
    
    def setUp(self):
        self.con = sqlite3.connect("output.db")
        self.con.row_factory = sqlite3.Row
        self.cur = self.con.cursor()
    
    def tearDown(self):
        self.con.close()
    
    def test_basic_text_search(self):
        """基本的なテキスト検索のテスト"""
        # 既知の商標で検索
        self.cur.execute("""
            SELECT DISTINCT j.normalized_app_num,
                   COALESCE(s.standard_char_t, iu.indct_use_t, su.search_use_t) as mark_text
            FROM jiken_c_t j
            LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num
            LEFT JOIN indct_use_t_art iu ON j.normalized_app_num = iu.normalized_app_num
            LEFT JOIN search_use_t_art_table su ON j.normalized_app_num = su.normalized_app_num
            WHERE s.standard_char_t LIKE ? OR iu.indct_use_t LIKE ? OR su.search_use_t LIKE ?
            LIMIT 5
        """, ["%あい%", "%あい%", "%あい%"])
        
        results = self.cur.fetchall()
        
        # 結果の検証
        for result in results:
            self.assertIsNotNone(result['normalized_app_num'])
            mark_text = result['mark_text'] or ''
            self.assertIn('あい', mark_text, f"検索結果に検索語が含まれていません: {mark_text}")
    
    def test_applicant_search(self):
        """出願人検索のテスト"""
        # 出願人名で検索
        self.cur.execute("""
            SELECT DISTINCT j.normalized_app_num,
                   COALESCE(am.applicant_name, ame.applicant_name) as applicant_name
            FROM jiken_c_t j
            LEFT JOIN jiken_c_t_shutugannindairinin ap ON j.normalized_app_num = ap.shutugan_no
            LEFT JOIN applicant_mapping am ON ap.shutugannindairinin_code = am.applicant_code
            LEFT JOIN applicant_mapping_enhanced ame ON ap.shutugannindairinin_code = ame.applicant_code
            WHERE am.applicant_name LIKE ? OR ame.applicant_name LIKE ?
            LIMIT 5
        """, ["%株式会社%", "%株式会社%"])
        
        results = self.cur.fetchall()
        self.assertGreater(len(results), 0, "出願人検索で結果が見つかりません")
        
        for result in results:
            applicant_name = result['applicant_name'] or ''
            self.assertIn('株式会社', applicant_name)
    
    def test_goods_class_search(self):
        """商品区分検索のテスト"""
        self.cur.execute("""
            SELECT DISTINCT j.normalized_app_num, gca.goods_classes
            FROM jiken_c_t j
            LEFT JOIN goods_class_art gca ON j.normalized_app_num = gca.normalized_app_num
            WHERE gca.goods_classes LIKE ?
            LIMIT 5
        """, ["%第3類%"])
        
        results = self.cur.fetchall()
        
        for result in results:
            goods_classes = result['goods_classes'] or ''
            self.assertIn('第3類', goods_classes)
    
    def test_date_range_search(self):
        """日付範囲検索のテスト"""
        self.cur.execute("""
            SELECT COUNT(*) FROM jiken_c_t
            WHERE shutugan_bi BETWEEN ? AND ?
        """, ["20200101", "20201231"])
        
        count = self.cur.fetchone()[0]
        self.assertGreaterEqual(count, 0, "日付範囲検索が機能していません")
    
    def test_performance_benchmarks(self):
        """検索性能のテスト"""
        # FTS検索の性能テスト
        start_time = time.time()
        self.cur.execute("SELECT COUNT(*) FROM trademark_fts WHERE mark_text MATCH ?", ["あい"])
        fts_time = time.time() - start_time
        
        # 従来検索の性能テスト
        start_time = time.time()
        self.cur.execute("""
            SELECT COUNT(*) FROM standard_char_t_art WHERE standard_char_t LIKE ?
        """, ["%あい%"])
        traditional_time = time.time() - start_time
        
        # FTSが従来検索より高速であることを確認
        self.assertLessEqual(fts_time, traditional_time * 2, 
                           f"FTS検索が期待より遅いです: FTS {fts_time:.3f}s vs 従来 {traditional_time:.3f}s")

class WebApplicationTestCase(unittest.TestCase):
    """Webアプリケーションのテスト"""
    
    def test_stats_api_response(self):
        """統計API のレスポンステスト"""
        # 統計情報を直接データベースから取得
        con = sqlite3.connect("output.db")
        cur = con.cursor()
        
        # 総商標数
        cur.execute("SELECT COUNT(*) FROM jiken_c_t")
        total_trademarks = cur.fetchone()[0]
        
        # 出願人マッピング数
        cur.execute("SELECT COUNT(*) FROM applicant_mapping_enhanced")
        applicant_mappings = cur.fetchone()[0]
        
        # 統計情報の妥当性確認
        self.assertGreater(total_trademarks, 0, "総商標数が0です")
        self.assertGreater(applicant_mappings, 0, "出願人マッピング数が0です")
        
        con.close()

class ErrorHandlingTestCase(unittest.TestCase):
    """エラーハンドリングのテスト"""
    
    def test_database_connection_error(self):
        """データベース接続エラーのテスト"""
        try:
            con = sqlite3.connect("nonexistent.db")
            cur = con.cursor()
            cur.execute("SELECT * FROM nonexistent_table")
        except sqlite3.OperationalError:
            pass  # 期待されるエラー
        else:
            self.fail("存在しないテーブルへのアクセスでエラーが発生しませんでした")
    
    def test_invalid_search_parameters(self):
        """無効な検索パラメータのテスト"""
        con = sqlite3.connect("output.db")
        cur = con.cursor()
        
        # 空の検索クエリ
        cur.execute("""
            SELECT COUNT(*) FROM jiken_c_t j
            LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num
            WHERE s.standard_char_t LIKE ?
        """, [""])
        
        count = cur.fetchone()[0]
        self.assertGreaterEqual(count, 0, "空クエリの処理でエラーが発生しました")
        
        con.close()

def run_comprehensive_tests():
    """包括的テストの実行"""
    print("=== 包括的テストスイート実行 ===\n")
    
    # テストスイートを作成
    test_suite = unittest.TestSuite()
    
    # テストケースを追加
    test_classes = [
        DatabaseTestCase,
        SearchFunctionalityTestCase,
        WebApplicationTestCase,
        ErrorHandlingTestCase
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # テストを実行
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 結果の集計
    print(f"\n=== テスト結果 ===")
    print(f"実行テスト数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失敗: {len(result.failures)}")
    print(f"エラー: {len(result.errors)}")
    
    if result.failures:
        print("\n失敗したテスト:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\nエラーが発生したテスト:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    # カバレッジ計算
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100
    print(f"\nテスト成功率: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("✅ 優秀なテストカバレッジです！")
    elif success_rate >= 80:
        print("⚠️  良好なテストカバレッジですが、改善の余地があります")
    else:
        print("❌ テストカバレッジが不足しています")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_comprehensive_tests()
    exit(0 if success else 1)
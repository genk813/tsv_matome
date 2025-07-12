#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
自走・自己改善システム
商標検索システムを自動的にテスト・分析・改善する
"""

import json
import time
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime
import subprocess
import sys

from autonomous_test_system import AutonomousTestSystem
from cli_trademark_search import TrademarkSearchCLI

class SelfImprovingSystem:
    """自走・自己改善システム"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or Path("output.db")
        self.test_system = AutonomousTestSystem(db_path)
        self.history_file = Path("improvement_history.json")
        self.load_history()
        
    def load_history(self):
        """改善履歴の読み込み"""
        if self.history_file.exists():
            with open(self.history_file, 'r', encoding='utf-8') as f:
                self.history = json.load(f)
        else:
            self.history = {
                'sessions': [],
                'total_improvements': 0,
                'best_performance': None
            }
    
    def save_history(self):
        """改善履歴の保存"""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
    
    def define_evaluation_metrics(self) -> Dict[str, Any]:
        """評価指標の定義"""
        return {
            'performance': {
                'max_acceptable_time': 5.0,  # 最大許容実行時間（秒）
                'target_success_rate': 95.0,  # 目標成功率（%）
                'max_memory_usage': 100,  # 最大メモリ使用量（MB）
            },
            'data_quality': {
                'min_mark_text_coverage': 90.0,  # 商標文字表示率（%）
                'min_valid_app_nums': 95.0,  # 有効な出願番号率（%）
                'max_duplicate_rate': 5.0,  # 重複結果の最大率（%）
            },
            'search_effectiveness': {
                'min_relevant_results': 80.0,  # 関連性のある結果の最小率（%）
                'max_false_positives': 20.0,  # 偽陽性の最大率（%）
                'min_recall_rate': 70.0,  # 再現率の最小値（%）
            },
            'system_stability': {
                'max_error_rate': 5.0,  # エラー率の最大値（%）
                'min_uptime': 99.0,  # 最小稼働時間（%）
                'max_timeout_rate': 2.0,  # タイムアウト率の最大値（%）
            }
        }
    
    def analyze_database_performance(self) -> Dict[str, Any]:
        """データベースパフォーマンスの分析"""
        print("🔍 データベースパフォーマンス分析中...")
        
        searcher = TrademarkSearchCLI(self.db_path)
        conn = searcher.get_db_connection()
        cursor = conn.cursor()
        
        analysis = {
            'table_stats': {},
            'index_efficiency': {},
            'query_patterns': {},
            'recommendations': []
        }
        
        # テーブル統計
        tables = ['jiken_c_t', 'standard_char_t_art', 'goods_class_art', 
                 'jiken_c_t_shohin_joho', 't_knd_info_art_table']
        
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                analysis['table_stats'][table] = count
            except sqlite3.Error as e:
                analysis['table_stats'][table] = f"Error: {e}"
        
        # インデックス効率性チェック
        common_queries = [
            ("出願番号検索", "SELECT * FROM jiken_c_t WHERE normalized_app_num = ?"),
            ("商標文字検索", "SELECT * FROM standard_char_t_art WHERE standard_char_t LIKE ?"),
            ("商品区分検索", "SELECT * FROM goods_class_art WHERE goods_classes LIKE ?")
        ]
        
        for query_name, query in common_queries:
            try:
                start_time = time.time()
                cursor.execute(f"EXPLAIN QUERY PLAN {query}", ("test",))
                plan = cursor.fetchall()
                end_time = time.time()
                
                analysis['index_efficiency'][query_name] = {
                    'plan_time': end_time - start_time,
                    'uses_index': any('INDEX' in str(row) for row in plan),
                    'plan': [str(row) for row in plan]
                }
            except sqlite3.Error:
                analysis['index_efficiency'][query_name] = "Error analyzing"
        
        # 推奨事項の生成
        if analysis['table_stats'].get('goods_class_art', 0) > 10000:
            analysis['recommendations'].append("商品区分テーブルが大きいため、部分インデックスの追加を検討")
        
        slow_queries = [name for name, data in analysis['index_efficiency'].items() 
                       if isinstance(data, dict) and not data.get('uses_index', True)]
        if slow_queries:
            analysis['recommendations'].append(f"インデックス未使用クエリ: {', '.join(slow_queries)}")
        
        conn.close()
        return analysis
    
    def identify_improvement_opportunities(self, test_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """改善機会の特定"""
        opportunities = []
        metrics = self.define_evaluation_metrics()
        
        # パフォーマンス改善機会
        if test_results.get('performance_metrics', {}).get('average_time', 0) > metrics['performance']['max_acceptable_time']:
            opportunities.append({
                'type': 'performance',
                'priority': 'high',
                'issue': '平均実行時間が目標値を超過',
                'current_value': test_results['performance_metrics']['average_time'],
                'target_value': metrics['performance']['max_acceptable_time'],
                'solutions': [
                    'クエリの最適化',
                    'インデックスの追加',
                    '結果セットの制限'
                ]
            })
        
        # 成功率の改善機会
        if test_results.get('success_rate', 0) < metrics['performance']['target_success_rate']:
            opportunities.append({
                'type': 'reliability',
                'priority': 'high',
                'issue': 'テスト成功率が目標値を下回る',
                'current_value': test_results['success_rate'],
                'target_value': metrics['performance']['target_success_rate'],
                'solutions': [
                    'エラーハンドリングの改善',
                    'データ整合性の確認',
                    'タイムアウト時間の調整'
                ]
            })
        
        # データ品質の改善機会
        quality_issues = []
        for result in test_results.get('detailed_results', []):
            if result.get('issues'):
                quality_issues.extend(result['issues'])
        
        if quality_issues:
            opportunities.append({
                'type': 'data_quality',
                'priority': 'medium',
                'issue': f'データ品質問題が{len(quality_issues)}件検出',
                'current_value': len(quality_issues),
                'target_value': 0,
                'solutions': [
                    'データクレンジング',
                    'バリデーション強化',
                    'データソースの確認'
                ]
            })
        
        return opportunities
    
    def implement_automatic_improvements(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """自動改善の実装"""
        implemented_improvements = []
        
        for opportunity in opportunities:
            if opportunity['type'] == 'performance' and opportunity['priority'] == 'high':
                # インデックス最適化の実行
                improvement = self.optimize_database_indexes()
                if improvement['success']:
                    implemented_improvements.append({
                        'opportunity': opportunity,
                        'action': 'database_optimization',
                        'result': improvement,
                        'timestamp': datetime.now().isoformat()
                    })
            
            elif opportunity['type'] == 'data_quality':
                # データクレンジングの実行
                improvement = self.clean_database_data()
                if improvement['success']:
                    implemented_improvements.append({
                        'opportunity': opportunity,
                        'action': 'data_cleaning',
                        'result': improvement,
                        'timestamp': datetime.now().isoformat()
                    })
        
        return implemented_improvements
    
    def optimize_database_indexes(self) -> Dict[str, Any]:
        """データベースインデックスの最適化"""
        print("⚡ データベースインデックス最適化中...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 使用頻度の高いクエリ用のインデックスを追加
            new_indexes = [
                "CREATE INDEX IF NOT EXISTS idx_goods_classes_search ON goods_class_art(goods_classes)",
                "CREATE INDEX IF NOT EXISTS idx_mark_text_search ON standard_char_t_art(standard_char_t)",
                "CREATE INDEX IF NOT EXISTS idx_designated_goods_search ON jiken_c_t_shohin_joho(designated_goods)"
            ]
            
            created_indexes = []
            for index_sql in new_indexes:
                try:
                    cursor.execute(index_sql)
                    created_indexes.append(index_sql.split()[-1])  # インデックス名を抽出
                except sqlite3.Error as e:
                    print(f"   ⚠️  インデックス作成エラー: {e}")
            
            # VACUUM実行で最適化
            cursor.execute("VACUUM")
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'created_indexes': created_indexes,
                'actions': ['新規インデックス作成', 'データベース最適化(VACUUM)']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def clean_database_data(self) -> Dict[str, Any]:
        """データベースデータのクレンジング"""
        print("🧹 データベースデータクレンジング中...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cleaning_actions = []
            
            # 重複データの削除
            tables_to_clean = ['jiken_c_t', 'standard_char_t_art', 'goods_class_art']
            for table in tables_to_clean:
                try:
                    # 重複チェック（例：jiken_c_tの場合）
                    if table == 'jiken_c_t':
                        cursor.execute("""
                            DELETE FROM jiken_c_t WHERE rowid NOT IN (
                                SELECT MIN(rowid) FROM jiken_c_t 
                                GROUP BY normalized_app_num
                            )
                        """)
                        if cursor.rowcount > 0:
                            cleaning_actions.append(f"{table}: {cursor.rowcount}件の重複削除")
                except sqlite3.Error:
                    pass
            
            # 不正データの修正
            cursor.execute("""
                UPDATE jiken_c_t 
                SET normalized_app_num = REPLACE(normalized_app_num, '-', '')
                WHERE normalized_app_num LIKE '%-%'
            """)
            if cursor.rowcount > 0:
                cleaning_actions.append(f"出願番号正規化: {cursor.rowcount}件")
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'actions': cleaning_actions
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def run_improvement_cycle(self) -> Dict[str, Any]:
        """改善サイクルの実行"""
        print("🔄 自動改善サイクル開始")
        print("=" * 80)
        
        cycle_start = time.time()
        
        # 1. 現状のテストを実行
        print("1️⃣ 現状テスト実行中...")
        baseline_results = self.test_system.run_full_test_suite()
        
        # 2. データベース分析
        print("\n2️⃣ データベース分析中...")
        db_analysis = self.analyze_database_performance()
        
        # 3. 改善機会の特定
        print("\n3️⃣ 改善機会の特定中...")
        opportunities = self.identify_improvement_opportunities(baseline_results)
        
        if opportunities:
            print(f"   🎯 {len(opportunities)}件の改善機会を発見")
            for i, opp in enumerate(opportunities, 1):
                print(f"      {i}. {opp['issue']} (優先度: {opp['priority']})")
        else:
            print("   ✨ 改善機会は見つかりませんでした")
        
        # 4. 自動改善の実装
        improvements = []
        if opportunities:
            print("\n4️⃣ 自動改善実装中...")
            improvements = self.implement_automatic_improvements(opportunities)
            
            for improvement in improvements:
                print(f"   ✅ {improvement['action']}: {improvement['result'].get('actions', [])}")
        
        # 5. 改善後のテスト
        post_improvement_results = None
        if improvements:
            print("\n5️⃣ 改善後テスト実行中...")
            # テストシステムを再初期化（DB変更を反映）
            self.test_system.close()
            self.test_system = AutonomousTestSystem(self.db_path)
            post_improvement_results = self.test_system.run_full_test_suite()
        
        cycle_end = time.time()
        
        # 6. 結果の記録
        session_record = {
            'timestamp': datetime.now().isoformat(),
            'cycle_duration': cycle_end - cycle_start,
            'baseline_results': baseline_results,
            'db_analysis': db_analysis,
            'opportunities': opportunities,
            'improvements': improvements,
            'post_improvement_results': post_improvement_results,
            'performance_delta': self.calculate_performance_delta(baseline_results, post_improvement_results)
        }
        
        self.history['sessions'].append(session_record)
        self.history['total_improvements'] += len(improvements)
        
        # ベストパフォーマンスの更新
        current_performance = post_improvement_results or baseline_results
        if (not self.history['best_performance'] or 
            current_performance['success_rate'] > self.history['best_performance']['success_rate']):
            self.history['best_performance'] = current_performance
        
        self.save_history()
        
        # 7. サマリーの表示
        self.print_cycle_summary(session_record)
        
        return session_record
    
    def calculate_performance_delta(self, before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
        """パフォーマンス変化の計算"""
        if not after:
            return {}
        
        delta = {}
        
        # 成功率の変化
        before_success = before.get('success_rate', 0)
        after_success = after.get('success_rate', 0)
        delta['success_rate_change'] = after_success - before_success
        
        # 実行時間の変化
        before_time = before.get('performance_metrics', {}).get('average_time', 0)
        after_time = after.get('performance_metrics', {}).get('average_time', 0)
        delta['avg_time_change'] = after_time - before_time
        
        # 失敗件数の変化
        before_failures = before.get('failed_tests', 0)
        after_failures = after.get('failed_tests', 0)
        delta['failure_count_change'] = after_failures - before_failures
        
        return delta
    
    def print_cycle_summary(self, session_record: Dict[str, Any]):
        """サイクル結果のサマリー表示"""
        print("\n" + "=" * 80)
        print("📊 改善サイクル結果サマリー")
        print("=" * 80)
        
        improvements = session_record['improvements']
        delta = session_record['performance_delta']
        
        print(f"実行時間: {session_record['cycle_duration']:.2f}秒")
        print(f"実装された改善: {len(improvements)}件")
        
        if delta:
            print(f"\n📈 パフォーマンス変化:")
            if delta.get('success_rate_change', 0) != 0:
                change = delta['success_rate_change']
                symbol = "📈" if change > 0 else "📉"
                print(f"  {symbol} 成功率: {change:+.1f}%")
            
            if delta.get('avg_time_change', 0) != 0:
                change = delta['avg_time_change']
                symbol = "🐌" if change > 0 else "⚡"
                print(f"  {symbol} 平均実行時間: {change:+.2f}秒")
            
            if delta.get('failure_count_change', 0) != 0:
                change = delta['failure_count_change']
                symbol = "😞" if change > 0 else "😊"
                print(f"  {symbol} 失敗件数: {change:+d}件")
        
        print(f"\n🏆 総改善回数: {self.history['total_improvements']}回")
        
        if self.history['best_performance']:
            best = self.history['best_performance']
            print(f"🥇 最高成功率: {best['success_rate']:.1f}%")
    
    def run_continuous_improvement(self, cycles: int = 3, interval: int = 30):
        """継続的改善の実行"""
        print(f"🚀 継続的改善開始 ({cycles}サイクル, {interval}秒間隔)")
        print("=" * 80)
        
        for cycle in range(cycles):
            print(f"\n🔄 サイクル {cycle + 1}/{cycles}")
            
            try:
                session_record = self.run_improvement_cycle()
                
                # 次のサイクルまで待機
                if cycle < cycles - 1:
                    print(f"\n⏳ 次のサイクルまで{interval}秒待機...")
                    time.sleep(interval)
                    
            except Exception as e:
                print(f"❌ サイクル{cycle + 1}でエラー: {e}")
                continue
        
        print(f"\n🎉 継続的改善完了 ({cycles}サイクル)")
        self.print_final_summary()
    
    def print_final_summary(self):
        """最終サマリーの表示"""
        print("\n" + "=" * 80)
        print("🎯 最終改善サマリー")
        print("=" * 80)
        
        if not self.history['sessions']:
            print("実行されたサイクルがありません")
            return
        
        total_improvements = self.history['total_improvements']
        sessions_count = len(self.history['sessions'])
        
        print(f"実行サイクル数: {sessions_count}")
        print(f"総改善件数: {total_improvements}")
        
        if self.history['best_performance']:
            best = self.history['best_performance']
            print(f"最高達成成功率: {best['success_rate']:.1f}%")
            print(f"最高達成時の実行時間: {best.get('total_execution_time', 0):.2f}秒")
        
        # 改善トレンドの表示
        if len(self.history['sessions']) >= 2:
            first_session = self.history['sessions'][0]
            last_session = self.history['sessions'][-1]
            
            first_success = first_session['baseline_results']['success_rate']
            last_success = (last_session.get('post_improvement_results') or 
                          last_session['baseline_results'])['success_rate']
            
            total_improvement = last_success - first_success
            print(f"トータル成功率改善: {total_improvement:+.1f}%")
    
    def close(self):
        """リソースのクリーンアップ"""
        self.test_system.close()


def main():
    """メイン実行"""
    try:
        system = SelfImprovingSystem()
        
        # 引数による動作切り替え
        if len(sys.argv) > 1:
            if sys.argv[1] == "single":
                # 単発改善サイクル
                system.run_improvement_cycle()
            elif sys.argv[1] == "continuous":
                # 継続的改善（3サイクル、30秒間隔）
                cycles = int(sys.argv[2]) if len(sys.argv) > 2 else 3
                interval = int(sys.argv[3]) if len(sys.argv) > 3 else 30
                system.run_continuous_improvement(cycles, interval)
        else:
            # デフォルト：単発改善サイクル
            system.run_improvement_cycle()
        
        system.close()
        
    except KeyboardInterrupt:
        print("\n⚠️  ユーザーによる中断")
    except Exception as e:
        print(f"❌ システムエラー: {e}")
        exit(1)


if __name__ == "__main__":
    main()
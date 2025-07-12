#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
自動テストシステム
商標検索ツールを自動的にテストし、結果の品質や性能を評価する
"""

import json
import time
import random
import statistics
from pathlib import Path
from typing import List, Dict, Any, Tuple
from datetime import datetime
import sqlite3

from cli_trademark_search import TrademarkSearchCLI

class AutonomousTestSystem:
    """自動テストシステム"""
    
    def __init__(self, db_path: str = None):
        self.searcher = TrademarkSearchCLI(db_path)
        self.test_results = []
        self.performance_metrics = []
        
    def get_sample_data(self) -> Dict[str, List[str]]:
        """データベースからサンプルデータを取得"""
        conn = self.searcher.get_db_connection()
        
        samples = {
            'app_nums': [],
            'mark_texts': [],
            'goods_classes': [],
            'designated_goods': [],
            'similar_group_codes': []
        }
        
        # 出願番号のサンプル（固定の3件で高速化）
        result = self.searcher.query_db(
            "SELECT normalized_app_num FROM jiken_c_t LIMIT 3"
        )
        samples['app_nums'] = [r['normalized_app_num'] for r in result]
        
        # 商標文字のサンプル（固定データで高速化）
        samples['mark_texts'] = ['ソニー', 'トヨタ', 'ホンダ']
        
        # 商品区分のサンプル（固定データ）
        samples['goods_classes'] = ['9', '35', '42']
        
        # 指定商品のサンプル（固定データ）
        samples['designated_goods'] = ['コンピュータ', '電気通信機械器具', '自動車']
        
        # 類似群コードのサンプル（固定データ）
        samples['similar_group_codes'] = ['11C01', '35K03', '12A01']
        
        return samples
    
    def create_test_scenarios(self) -> List[Dict[str, Any]]:
        """テストシナリオを生成"""
        sample_data = self.get_sample_data()
        scenarios = []
        
        # 1. 基本検索テスト（各フィールド個別 - 軽量化）
        if sample_data['app_nums']:
            scenarios.append({
                'name': f'出願番号検索: {sample_data["app_nums"][0]}',
                'params': {'app_num': sample_data['app_nums'][0]},
                'expected_min_results': 1,
                'expected_max_time': 5.0
            })
        
        scenarios.append({
            'name': '商標文字検索: ソニー',
            'params': {'mark_text': 'ソニー', 'limit': 10},
            'expected_min_results': 0,
            'expected_max_time': 10.0
        })
        
        scenarios.append({
            'name': '商品区分検索: 9',
            'params': {'goods_classes': '9', 'limit': 10},
            'expected_min_results': 0,
            'expected_max_time': 10.0
        })
        
        # 2. 複合検索テスト（軽量化）
        scenarios.append({
            'name': '複合検索: 商標文字 + 商品区分',
            'params': {
                'mark_text': 'ソニー',
                'goods_classes': '9',
                'limit': 5
            },
            'expected_min_results': 0,
            'expected_max_time': 15.0
        })
        
        # 3. エラーケーステスト
        scenarios.append({
            'name': 'エラーケース: 存在しない出願番号',
            'params': {'app_num': '999999999'},
            'expected_min_results': 0,
            'expected_max_time': 5.0
        })
        
        return scenarios
    
    def run_single_test(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """単一テストの実行"""
        print(f"🧪 テスト実行: {scenario['name']}")
        
        start_time = time.time()
        try:
            results, total_count = self.searcher.search_trademarks(**scenario['params'])
            end_time = time.time()
            
            execution_time = end_time - start_time
            
            # 結果の評価
            test_result = {
                'scenario': scenario['name'],
                'params': scenario['params'],
                'success': True,
                'results_count': len(results),
                'total_count': total_count,
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat(),
                'issues': []
            }
            
            # 期待値チェック
            if len(results) < scenario.get('expected_min_results', 0):
                test_result['issues'].append(f"結果数が期待値未満: {len(results)} < {scenario['expected_min_results']}")
            
            if execution_time > scenario.get('expected_max_time', 30.0):
                test_result['issues'].append(f"実行時間が上限超過: {execution_time:.2f}s > {scenario['expected_max_time']}s")
            
            # データ品質チェック
            if results:
                quality_issues = self.check_data_quality(results)
                test_result['issues'].extend(quality_issues)
            
            print(f"   ✅ 成功: {len(results)}件 / {total_count}件 (実行時間: {execution_time:.2f}s)")
            if test_result['issues']:
                print(f"   ⚠️  問題: {'; '.join(test_result['issues'])}")
                
        except Exception as e:
            end_time = time.time()
            execution_time = end_time - start_time
            
            test_result = {
                'scenario': scenario['name'],
                'params': scenario['params'],
                'success': False,
                'error': str(e),
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat(),
                'issues': [f"実行エラー: {str(e)}"]
            }
            
            print(f"   ❌ エラー: {e}")
        
        return test_result
    
    def check_data_quality(self, results: List[Dict[str, Any]]) -> List[str]:
        """結果のデータ品質をチェック"""
        issues = []
        
        if not results:
            return issues
        
        # 必須フィールドのチェック
        required_fields = ['app_num']
        for i, result in enumerate(results[:5]):  # 最初の5件をチェック
            for field in required_fields:
                if not result.get(field):
                    issues.append(f"結果{i+1}: 必須フィールド '{field}' が空")
        
        # データの一貫性チェック
        app_nums = [r.get('app_num') for r in results if r.get('app_num')]
        if len(set(app_nums)) != len(app_nums):
            issues.append("重複した出願番号が結果に含まれる")
        
        # 商標表示の品質チェック
        no_mark_text_count = sum(1 for r in results if not r.get('mark_text'))
        if no_mark_text_count > len(results) * 0.5:
            issues.append(f"商標文字が表示されていない結果が多い: {no_mark_text_count}/{len(results)}")
        
        return issues
    
    def run_performance_test(self) -> Dict[str, Any]:
        """パフォーマンステストの実行"""
        print("🚀 パフォーマンステスト開始")
        
        # 連続検索テスト（軽量化）
        search_times = []
        for i in range(3):
            start_time = time.time()
            results, total = self.searcher.search_trademarks(mark_text="ソニー", limit=10)
            end_time = time.time()
            search_times.append(end_time - start_time)
            print(f"   検索{i+1}: {len(results)}件 ({search_times[-1]:.2f}s)")
        
        # 統計情報
        avg_time = statistics.mean(search_times)
        max_time = max(search_times)
        min_time = min(search_times)
        
        performance_result = {
            'test_type': 'performance',
            'search_count': len(search_times),
            'average_time': avg_time,
            'max_time': max_time,
            'min_time': min_time,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"   📊 平均: {avg_time:.2f}s, 最大: {max_time:.2f}s, 最小: {min_time:.2f}s")
        
        return performance_result
    
    def generate_improvement_suggestions(self) -> List[str]:
        """改善提案の生成"""
        suggestions = []
        
        if not self.test_results:
            return ["テスト結果がありません"]
        
        # 失敗したテストの分析
        failed_tests = [t for t in self.test_results if not t.get('success', True)]
        if failed_tests:
            suggestions.append(f"失敗したテスト: {len(failed_tests)}件 - エラーハンドリングの改善が必要")
        
        # 実行時間の分析
        slow_tests = [t for t in self.test_results if t.get('execution_time', 0) > 10.0]
        if slow_tests:
            suggestions.append(f"実行時間が遅いテスト: {len(slow_tests)}件 - クエリ最適化が必要")
        
        # データ品質の分析
        quality_issues = [t for t in self.test_results if t.get('issues', [])]
        if quality_issues:
            total_issues = sum(len(t.get('issues', [])) for t in quality_issues)
            suggestions.append(f"データ品質問題: {total_issues}件 - データ整合性の確認が必要")
        
        # パフォーマンス分析
        if self.performance_metrics:
            avg_time = self.performance_metrics[-1].get('average_time', 0)
            if avg_time > 5.0:
                suggestions.append(f"平均実行時間が遅い: {avg_time:.2f}s - インデックス追加を検討")
        
        if not suggestions:
            suggestions.append("現在のところ重大な問題は検出されていません")
        
        return suggestions
    
    def run_full_test_suite(self) -> Dict[str, Any]:
        """完全なテストスイートを実行"""
        print("🔍 自動テストシステム開始")
        print("=" * 80)
        
        start_time = time.time()
        
        # テストシナリオの生成
        scenarios = self.create_test_scenarios()
        print(f"📝 テストシナリオ: {len(scenarios)}件")
        
        # 各シナリオの実行
        for scenario in scenarios:
            test_result = self.run_single_test(scenario)
            self.test_results.append(test_result)
            time.sleep(0.5)  # データベース負荷軽減
        
        # パフォーマンステスト
        performance_result = self.run_performance_test()
        self.performance_metrics.append(performance_result)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 結果の集計
        successful_tests = sum(1 for t in self.test_results if t.get('success', False))
        failed_tests = len(self.test_results) - successful_tests
        
        # 改善提案の生成
        suggestions = self.generate_improvement_suggestions()
        
        # 総合結果
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_execution_time': total_time,
            'test_scenarios': len(scenarios),
            'successful_tests': successful_tests,
            'failed_tests': failed_tests,
            'success_rate': (successful_tests / len(self.test_results)) * 100,
            'performance_metrics': performance_result,
            'improvement_suggestions': suggestions,
            'detailed_results': self.test_results
        }
        
        # 結果の表示
        self.print_summary(summary)
        
        # 結果をファイルに保存
        self.save_results(summary)
        
        return summary
    
    def print_summary(self, summary: Dict[str, Any]):
        """テスト結果のサマリーを表示"""
        print("\n" + "=" * 80)
        print("📊 テスト結果サマリー")
        print("=" * 80)
        print(f"実行時間: {summary['total_execution_time']:.2f}秒")
        print(f"テスト件数: {summary['test_scenarios']}件")
        print(f"成功: {summary['successful_tests']}件")
        print(f"失敗: {summary['failed_tests']}件")
        print(f"成功率: {summary['success_rate']:.1f}%")
        
        perf = summary['performance_metrics']
        print(f"\n🚀 パフォーマンス:")
        print(f"  平均実行時間: {perf['average_time']:.2f}秒")
        print(f"  最大実行時間: {perf['max_time']:.2f}秒")
        print(f"  最小実行時間: {perf['min_time']:.2f}秒")
        
        print(f"\n💡 改善提案:")
        for i, suggestion in enumerate(summary['improvement_suggestions'], 1):
            print(f"  {i}. {suggestion}")
    
    def save_results(self, summary: Dict[str, Any]):
        """テスト結果をファイルに保存"""
        results_dir = Path("test_results")
        results_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = results_dir / f"test_results_{timestamp}.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 テスト結果を保存: {results_file}")
    
    def close(self):
        """リソースのクリーンアップ"""
        self.searcher.close()


def main():
    """メイン実行"""
    try:
        test_system = AutonomousTestSystem()
        summary = test_system.run_full_test_suite()
        test_system.close()
        
        # 改善が必要な場合は終了コード1
        if summary['failed_tests'] > 0 or summary['success_rate'] < 90:
            exit(1)
        else:
            exit(0)
            
    except Exception as e:
        print(f"❌ テストシステムエラー: {e}")
        exit(1)


if __name__ == "__main__":
    main()
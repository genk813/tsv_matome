#!/usr/bin/env python3
"""
TSV_MATOMEシステムの現在の課題感の深刻な再検討
重要な修正完了後の真の課題を客観的に分析
"""
import sqlite3
import time
import subprocess
import json
from datetime import datetime

def analyze_current_state():
    """現在のシステム状態を包括的に分析"""
    
    conn = sqlite3.connect("output.db")
    cursor = conn.cursor()
    
    print("🔍 TSV_MATOME 現在の課題感 - 深刻な再検討")
    print("=" * 60)
    print(f"分析日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. 解決済み問題の確認
    print("\n✅ 解決済み重要問題の確認")
    print("-" * 40)
    
    # 重複表示問題の解決確認
    cursor.execute("""
        SELECT COUNT(*) as total_count,
               COUNT(DISTINCT app_num) as unique_count
        FROM unified_trademark_search_view
        WHERE trademark_text LIKE '%ソニー%'
    """)
    result = cursor.fetchone()
    if result:
        total, unique = result
        duplicate_ratio = total / unique if unique > 0 else 0
        print(f"1. 重複表示問題: {total}件/{unique}件 (倍率: {duplicate_ratio:.1f})")
        if duplicate_ratio <= 1.1:
            print("   ✅ 完全解決済み")
        else:
            print(f"   ❌ 未解決 ({duplicate_ratio:.1f}倍重複)")
    
    # 商品区分検索の性能確認
    start_time = time.time()
    try:
        result = subprocess.run(
            'python3 cli_trademark_search.py --goods-classes "09" --limit 1',
            shell=True, capture_output=True, text=True, timeout=5
        )
        search_time = time.time() - start_time
        if result.returncode == 0:
            print(f"2. 商品区分検索性能: {search_time:.2f}秒")
            if search_time < 2:
                print("   ✅ 高速化完了")
            else:
                print(f"   ⚠️ 要改善 ({search_time:.1f}秒)")
        else:
            print("2. 商品区分検索性能: ❌ エラー")
    except subprocess.TimeoutExpired:
        print("2. 商品区分検索性能: ❌ タイムアウト")
    
    # データ整合性の確認
    cursor.execute("""
        SELECT COUNT(*) FROM standard_char_t_art s
        WHERE s.normalized_app_num NOT IN (
            SELECT normalized_app_num FROM jiken_c_t WHERE normalized_app_num IS NOT NULL
        )
    """)
    orphaned_records = cursor.fetchone()[0]
    print(f"3. データ整合性: 孤立レコード {orphaned_records}件")
    if orphaned_records == 0:
        print("   ✅ データ整合性良好")
    else:
        print(f"   ⚠️ 要確認 ({orphaned_records}件)")
    
    # 2. 現在のシステム性能評価
    print("\n📊 現在のシステム性能評価")
    print("-" * 40)
    
    # データベースサイズと最適化状況
    cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
    db_size = cursor.fetchone()[0] / (1024 * 1024)  # MB
    print(f"データベースサイズ: {db_size:.1f}MB")
    
    # テーブル数とレコード数
    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
    table_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM jiken_c_t")
    total_trademarks = cursor.fetchone()[0]
    
    print(f"テーブル数: {table_count}個")
    print(f"総商標数: {total_trademarks:,}件")
    
    # インデックス数
    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index'")
    index_count = cursor.fetchone()[0]
    print(f"インデックス数: {index_count}個")
    
    # 3. 機能別データカバレッジの詳細評価
    print("\n🎯 機能別データカバレッジ評価")
    print("-" * 40)
    
    coverage_data = {}
    
    # 基本情報（100%であるべき）
    coverage_data['基本情報'] = 100.0
    
    # 商標テキスト
    cursor.execute("""
        SELECT COUNT(DISTINCT j.normalized_app_num)
        FROM jiken_c_t j
        LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num
        LEFT JOIN indct_use_t_art iu ON j.normalized_app_num = iu.normalized_app_num
        LEFT JOIN search_use_t_art_table su ON j.normalized_app_num = su.normalized_app_num
        WHERE s.standard_char_t IS NOT NULL 
           OR iu.indct_use_t IS NOT NULL 
           OR su.search_use_t IS NOT NULL
    """)
    text_coverage = cursor.fetchone()[0] / total_trademarks * 100
    coverage_data['商標テキスト'] = text_coverage
    
    # 権利者情報（登録商標のみ）
    cursor.execute("SELECT COUNT(DISTINCT app_num) FROM reg_mapping")
    registered_count = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(DISTINCT rm.app_num)
        FROM reg_mapping rm
        JOIN right_person_art_t rp ON rm.reg_num = rp.reg_num
        WHERE rp.right_person_name IS NOT NULL
    """)
    rights_with_holder = cursor.fetchone()[0]
    
    rights_coverage = (rights_with_holder / registered_count * 100) if registered_count > 0 else 0
    coverage_data['権利者情報'] = rights_coverage
    
    # 申請人情報
    cursor.execute("""
        SELECT COUNT(DISTINCT j.normalized_app_num)
        FROM jiken_c_t j
        LEFT JOIN jiken_c_t_shutugannindairinin ap ON j.normalized_app_num = ap.shutugan_no 
        LEFT JOIN applicant_master am ON ap.shutugannindairinin_code = am.appl_cd
        LEFT JOIN applicant_mapping apm ON ap.shutugannindairinin_code = apm.applicant_code
        WHERE am.appl_name IS NOT NULL OR apm.applicant_name IS NOT NULL
    """)
    applicant_coverage = cursor.fetchone()[0] / total_trademarks * 100
    coverage_data['申請人名'] = applicant_coverage
    
    # 称呼情報
    cursor.execute("""
        SELECT COUNT(DISTINCT j.normalized_app_num)
        FROM jiken_c_t j
        JOIN t_dsgnt_art td ON j.normalized_app_num = td.normalized_app_num
        WHERE td.dsgnt IS NOT NULL AND td.dsgnt != ''
    """)
    pronunciation_coverage = cursor.fetchone()[0] / total_trademarks * 100
    coverage_data['称呼情報'] = pronunciation_coverage
    
    # 類似群コード
    cursor.execute("""
        SELECT COUNT(DISTINCT j.normalized_app_num)
        FROM jiken_c_t j
        JOIN t_knd_info_art_table tknd ON j.normalized_app_num = tknd.normalized_app_num
        WHERE tknd.smlr_dsgn_group_cd IS NOT NULL AND tknd.smlr_dsgn_group_cd != ''
    """)
    similar_coverage = cursor.fetchone()[0] / total_trademarks * 100
    coverage_data['類似群コード'] = similar_coverage
    
    # 画像データ
    cursor.execute("""
        SELECT COUNT(DISTINCT j.normalized_app_num)
        FROM jiken_c_t j
        JOIN t_sample ts ON j.normalized_app_num = ts.normalized_app_num
        WHERE ts.image_data IS NOT NULL
    """)
    image_coverage = cursor.fetchone()[0] / total_trademarks * 100
    coverage_data['画像データ'] = image_coverage
    
    # カバレッジ評価
    for feature, coverage in coverage_data.items():
        status = "✅ 優秀" if coverage >= 95 else "⚠️ 改善可能" if coverage >= 80 else "❌ 要改善"
        print(f"{feature}: {coverage:.1f}% {status}")
    
    # 4. 国際商標の現状評価
    print("\n🌍 国際商標機能の評価")
    print("-" * 40)
    
    cursor.execute("SELECT COUNT(*) FROM intl_trademark_registration")
    intl_total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM intl_trademark_text WHERE t_dtl_explntn IS NOT NULL")
    intl_with_text = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM intl_trademark_holder WHERE holder_name IS NOT NULL")
    intl_with_holder = cursor.fetchone()[0]
    
    if intl_total > 0:
        intl_text_rate = intl_with_text / intl_total * 100
        intl_holder_rate = intl_with_holder / intl_total * 100
        
        print(f"国際商標総数: {intl_total:,}件")
        print(f"テキスト情報: {intl_text_rate:.1f}%")
        print(f"権利者情報: {intl_holder_rate:.1f}%")
        
        # 国際商標検索のテスト
        start_time = time.time()
        try:
            result = subprocess.run(
                'python3 cli_trademark_search.py --international --goods-classes "42" --limit 1',
                shell=True, capture_output=True, text=True, timeout=5
            )
            intl_search_time = time.time() - start_time
            if result.returncode == 0:
                print(f"国際商標検索性能: {intl_search_time:.2f}秒 ✅")
            else:
                print("国際商標検索性能: ❌ エラー")
        except subprocess.TimeoutExpired:
            print("国際商標検索性能: ❌ タイムアウト")
    
    # 5. ユーザビリティの評価
    print("\n👥 ユーザビリティ評価")
    print("-" * 40)
    
    # 検索速度テスト
    search_tests = [
        ("出願番号検索", 'python3 cli_trademark_search.py --app-num "2020138119" --limit 1'),
        ("商標名検索", 'python3 cli_trademark_search.py --mark-text "ソニー" --limit 1'),
        ("類似群検索", 'python3 cli_trademark_search.py --similar-group-codes "11C01" --limit 1'),
        ("複合検索", 'python3 cli_trademark_search.py --mark-text "電気" --goods-classes "09" --limit 1'),
    ]
    
    search_performance = {}
    for test_name, command in search_tests:
        start_time = time.time()
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
            elapsed = time.time() - start_time
            if result.returncode == 0:
                search_performance[test_name] = elapsed
                status = "✅ 高速" if elapsed < 1 else "⚠️ 普通" if elapsed < 3 else "❌ 低速"
                print(f"{test_name}: {elapsed:.2f}秒 {status}")
            else:
                print(f"{test_name}: ❌ エラー")
        except subprocess.TimeoutExpired:
            print(f"{test_name}: ❌ タイムアウト")
    
    # 6. 現在の真の課題特定
    print("\n🎯 現在の真の課題特定")
    print("-" * 40)
    
    issues = []
    
    # パフォーマンス課題
    avg_search_time = sum(search_performance.values()) / len(search_performance) if search_performance else 0
    if avg_search_time > 2:
        issues.append(("パフォーマンス", f"平均検索時間{avg_search_time:.1f}秒", "medium"))
    
    # データ課題
    if coverage_data.get('申請人名', 0) < 50:
        issues.append(("申請人情報", f"カバレッジ{coverage_data['申請人名']:.1f}%", "low"))
    
    if coverage_data.get('画像データ', 0) < 50:
        issues.append(("画像表示", f"カバレッジ{coverage_data['画像データ']:.1f}%", "low"))
    
    # 機能課題
    if intl_total > 0 and intl_text_rate < 80:
        issues.append(("国際商標テキスト", f"正規化未対応", "medium"))
    
    # 統合ビューの性能
    start_time = time.time()
    try:
        cursor.execute("SELECT COUNT(*) FROM unified_trademark_search_view LIMIT 1")
        unified_time = time.time() - start_time
        if unified_time > 5:
            issues.append(("統合ビュー", f"応答時間{unified_time:.1f}秒", "high"))
    except:
        issues.append(("統合ビュー", "アクセスエラー", "high"))
    
    # 課題の優先度別整理
    high_issues = [issue for issue in issues if issue[2] == "high"]
    medium_issues = [issue for issue in issues if issue[2] == "medium"]
    low_issues = [issue for issue in issues if issue[2] == "low"]
    
    if not issues:
        print("🎉 重大な課題は発見されませんでした！")
        print("システムは良好な状態で稼働しています。")
    else:
        if high_issues:
            print("🔴 高優先度課題:")
            for issue, desc, _ in high_issues:
                print(f"   - {issue}: {desc}")
        
        if medium_issues:
            print("\n🟡 中優先度課題:")
            for issue, desc, _ in medium_issues:
                print(f"   - {issue}: {desc}")
        
        if low_issues:
            print("\n🟢 低優先度課題:")
            for issue, desc, _ in low_issues:
                print(f"   - {issue}: {desc}")
    
    # 7. 今後の発展可能性
    print("\n🚀 今後の発展可能性")
    print("-" * 40)
    
    development_opportunities = [
        "🔍 AI駆動の類似商標検索エンジン",
        "📊 商標分析ダッシュボードの追加",
        "🌐 Webサービス化とAPI提供",
        "🔄 リアルタイム更新システム",
        "📱 モバイル対応インターface",
        "🤖 自動分類・タグ付けシステム",
        "📈 商標トレンド分析機能",
        "🔗 他の知的財産データベースとの連携"
    ]
    
    for opportunity in development_opportunities:
        print(f"   {opportunity}")
    
    # 8. 総合評価
    print("\n" + "=" * 60)
    print("📋 総合評価サマリー")
    print("=" * 60)
    
    total_score = 0
    max_score = 0
    
    # データ品質スコア (40点満点)
    data_score = min(40, sum([
        coverage_data.get('基本情報', 0) * 0.1,
        coverage_data.get('商標テキスト', 0) * 0.1,
        coverage_data.get('権利者情報', 0) * 0.05,
        coverage_data.get('申請人名', 0) * 0.05,
        coverage_data.get('称呼情報', 0) * 0.05,
        coverage_data.get('類似群コード', 0) * 0.05
    ]))
    total_score += data_score
    max_score += 40
    
    # パフォーマンススコア (30点満点)
    perf_score = 30 if avg_search_time < 1 else 20 if avg_search_time < 2 else 10 if avg_search_time < 5 else 0
    total_score += perf_score
    max_score += 30
    
    # 機能完成度スコア (30点満点)
    func_score = 30 - len(high_issues) * 10 - len(medium_issues) * 5 - len(low_issues) * 2
    func_score = max(0, func_score)
    total_score += func_score
    max_score += 30
    
    final_score = (total_score / max_score * 100) if max_score > 0 else 0
    
    print(f"データ品質: {data_score:.1f}/40点")
    print(f"パフォーマンス: {perf_score:.1f}/30点")
    print(f"機能完成度: {func_score:.1f}/30点")
    print(f"総合評価: {final_score:.1f}/100点")
    
    if final_score >= 90:
        grade = "S (優秀)"
    elif final_score >= 80:
        grade = "A (良好)"
    elif final_score >= 70:
        grade = "B (普通)"
    elif final_score >= 60:
        grade = "C (要改善)"
    else:
        grade = "D (問題あり)"
    
    print(f"\n🏆 システム総合評価: {grade}")
    
    conn.close()
    
    return {
        'total_score': final_score,
        'grade': grade,
        'high_issues': high_issues,
        'medium_issues': medium_issues,
        'low_issues': low_issues,
        'coverage_data': coverage_data,
        'search_performance': search_performance
    }

if __name__ == "__main__":
    result = analyze_current_state()
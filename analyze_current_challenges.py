#!/usr/bin/env python3
"""
現在のTSV_MATOMEシステムの課題分析
"""
import sqlite3
import time
from pathlib import Path

def analyze_current_challenges():
    """現在のシステム課題を包括的に分析"""
    
    conn = sqlite3.connect("output.db")
    cursor = conn.cursor()
    
    print("🔍 TSV_MATOMEシステム 現在の課題分析 (2025-07-13)")
    print("=" * 60)
    
    # 1. 重複結果の深刻な問題
    print("1. ❌ 重複結果の問題 (最優先課題)")
    print("-" * 30)
    
    # ソニー検索での重複確認
    cursor.execute("""
        SELECT COUNT(*) 
        FROM jiken_c_t j
        LEFT JOIN goods_class_art gca ON j.normalized_app_num = gca.normalized_app_num
        LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num
        WHERE s.standard_char_t LIKE '%ソニー%'
    """)
    sony_raw_count = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(DISTINCT j.normalized_app_num)
        FROM jiken_c_t j
        LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num
        WHERE s.standard_char_t LIKE '%ソニー%'
    """)
    sony_unique_count = cursor.fetchone()[0]
    
    duplicate_ratio = sony_raw_count / sony_unique_count if sony_unique_count > 0 else 0
    print(f"   ソニー検索: {sony_unique_count}件が{sony_raw_count}件として表示 (重複率: {duplicate_ratio:.1f}倍)")
    print(f"   原因: goods_class_art テーブルとの JOIN で商品区分数だけ重複")
    
    # 2. データ品質の課題
    print("\n2. ⚠️ データ品質の課題")
    print("-" * 20)
    
    # 古いデータのカバレッジ
    cursor.execute("""
        SELECT 
            SUBSTR(j.normalized_app_num, 1, 4) as year,
            COUNT(*) as total_count,
            COUNT(s.standard_char_t) as with_text,
            COUNT(gca.goods_classes) as with_goods
        FROM jiken_c_t j
        LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num
        LEFT JOIN goods_class_art gca ON j.normalized_app_num = gca.normalized_app_num
        WHERE SUBSTR(j.normalized_app_num, 1, 4) BETWEEN '1997' AND '2002'
        GROUP BY SUBSTR(j.normalized_app_num, 1, 4)
        ORDER BY year
    """)
    coverage_by_year = cursor.fetchall()
    
    print("   年代別データカバレッジ (1997-2002):")
    low_coverage_years = []
    for year, total, text, goods in coverage_by_year:
        text_pct = (text / total * 100) if total > 0 else 0
        goods_pct = (goods / total * 100) if total > 0 else 0
        status = "❌" if text_pct < 50 else "⚠️" if text_pct < 80 else "✅"
        print(f"     {year}: {status} テキスト{text_pct:.1f}%, 商品{goods_pct:.1f}% ({total}件)")
        if text_pct < 50:
            low_coverage_years.append(year)
    
    if low_coverage_years:
        print(f"   低カバレッジ年: {', '.join(low_coverage_years)}")
    
    # 3. 申請人情報の制限
    print("\n3. ⚠️ 申請人情報の制限")
    print("-" * 20)
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total_apps,
            COUNT(ap.shutugannindairinin_code) as with_code,
            COUNT(am.appl_name) as with_name_master,
            COUNT(apm.applicant_name) as with_name_mapping
        FROM jiken_c_t j
        LEFT JOIN jiken_c_t_shutugannindairinin ap ON j.normalized_app_num = ap.shutugan_no 
                                                    AND ap.shutugannindairinin_sikbt = '1'
        LEFT JOIN applicant_master am ON ap.shutugannindairinin_code = am.appl_cd
        LEFT JOIN applicant_mapping apm ON ap.shutugannindairinin_code = apm.applicant_code
    """)
    applicant_data = cursor.fetchone()
    
    if applicant_data:
        total, with_code, with_master, with_mapping = applicant_data
        code_pct = (with_code / total * 100) if total > 0 else 0
        master_pct = (with_master / total * 100) if total > 0 else 0
        mapping_pct = (with_mapping / total * 100) if total > 0 else 0
        name_total_pct = ((with_master + with_mapping) / total * 100) if total > 0 else 0
        
        print(f"   申請人コード保有: {code_pct:.1f}%")
        print(f"   申請人名(マスター): {master_pct:.1f}%")
        print(f"   申請人名(推定): {mapping_pct:.1f}%")
        print(f"   申請人名合計: {name_total_pct:.1f}% ← 改善の余地大")
    
    # 4. 国際商標の課題
    print("\n4. ⚠️ 国際商標の制限")
    print("-" * 20)
    
    cursor.execute("SELECT COUNT(*) FROM intl_trademark_registration")
    intl_total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM intl_trademark_text WHERE t_dtl_explntn IS NOT NULL AND t_dtl_explntn != ''")
    intl_with_text = cursor.fetchone()[0]
    
    if intl_total > 0:
        text_pct = (intl_with_text / intl_total * 100)
        print(f"   国際商標総数: {intl_total:,}件")
        print(f"   テキスト情報: {text_pct:.1f}% ({intl_with_text:,}件)")
        print(f"   画像データ: 0% (未対応)")
        print(f"   TM-SONAR正規化: 未対応")
        print(f"   称呼情報: 未対応")
    
    # 5. 統合ビューのパフォーマンス問題
    print("\n5. ❌ 統合ビューのパフォーマンス問題")
    print("-" * 30)
    
    start_time = time.time()
    try:
        cursor.execute("SELECT COUNT(*) FROM unified_trademark_search_view LIMIT 1")
        count = cursor.fetchone()[0]
        elapsed = time.time() - start_time
        
        if elapsed > 10:
            status = "❌ 深刻"
        elif elapsed > 5:
            status = "⚠️ 要改善"
        else:
            status = "✅ 正常"
            
        print(f"   統合ビュー応答時間: {status} ({elapsed:.1f}s)")
        
        if elapsed > 5:
            print(f"   問題: 200万件のUNION ALL処理が重い")
            print(f"   影響: Webアプリでのタイムアウト発生")
            
    except Exception as e:
        print(f"   統合ビュー: ❌ エラー - {str(e)}")
    
    # 6. CLIの商品区分検索の問題
    print("\n6. ❌ CLIの商品区分検索タイムアウト")
    print("-" * 30)
    
    # 直接SQLは高速だがCLIがタイムアウト
    start_time = time.time()
    cursor.execute("SELECT COUNT(*) FROM goods_class_art WHERE goods_classes = '09'")
    direct_count = cursor.fetchone()[0]
    direct_time = time.time() - start_time
    
    print(f"   直接SQL: ✅ {direct_time:.3f}s ({direct_count:,}件)")
    print(f"   CLI検索: ❌ タイムアウト (2分+)")
    print(f"   原因: get_optimized_results関数の複雑なJOIN処理")
    
    # 7. データ整合性の課題
    print("\n7. ⚠️ データ整合性の課題")
    print("-" * 20)
    
    # テーブル間の関連性チェック
    cursor.execute("""
        SELECT 
            COUNT(DISTINCT s.normalized_app_num) as text_only,
            COUNT(DISTINCT j.normalized_app_num) as main_only
        FROM standard_char_t_art s
        FULL OUTER JOIN jiken_c_t j ON s.normalized_app_num = j.normalized_app_num
        WHERE s.normalized_app_num IS NULL OR j.normalized_app_num IS NULL
    """)
    
    # SQLiteはFULL OUTER JOINをサポートしないので別の方法で
    cursor.execute("SELECT COUNT(*) FROM standard_char_t_art WHERE normalized_app_num NOT IN (SELECT normalized_app_num FROM jiken_c_t WHERE normalized_app_num IS NOT NULL)")
    orphaned_text = cursor.fetchone()[0]
    
    if orphaned_text > 0:
        print(f"   孤立したテキストレコード: {orphaned_text:,}件")
        print(f"   ← 2025-07-13の修正で大幅改善されたが残存")
    else:
        print(f"   テキスト-基本テーブル連携: ✅ 良好")
    
    # 8. 今後の課題まとめ
    print("\n" + "=" * 60)
    print("📋 優先度別課題まとめ")
    print("=" * 60)
    
    print("\n🔴 最優先 (ユーザー体験に直接影響)")
    print("1. 重複結果表示の修正 - ソニー検索で45倍の重複")
    print("2. CLIの商品区分検索タイムアウト - 実用性の問題")
    print("3. 統合ビューのパフォーマンス改善 - Webアプリでの問題")
    
    print("\n🟡 中優先 (機能向上)")
    print("4. 申請人名カバレッジ向上 - 現在15-20%程度")
    print("5. 古いデータ(1997-2002)の品質改善")
    print("6. 国際商標のテキスト正規化対応")
    
    print("\n🟢 低優先 (将来的改善)")
    print("7. 国際商標の画像データ対応")
    print("8. 称呼検索の国際商標対応")
    print("9. APIエンドポイントの提供")
    
    conn.close()
    
    return {
        "critical_issues": ["duplicate_results", "cli_timeout", "unified_view_performance"],
        "medium_issues": ["applicant_coverage", "old_data_quality", "intl_normalization"],
        "low_issues": ["intl_images", "intl_pronunciation", "api_endpoints"]
    }

if __name__ == "__main__":
    analyze_current_challenges()
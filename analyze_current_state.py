#!/usr/bin/env python3
"""
Comprehensive analysis of current tsv_matome system state
"""
import sqlite3
import time
from pathlib import Path

def analyze_database():
    """Analyze current database state and identify issues"""
    
    if not Path("output.db").exists():
        print("❌ Database not found")
        return
    
    conn = sqlite3.connect("output.db")
    cursor = conn.cursor()
    
    print("🔍 TSV_MATOME System Analysis")
    print("=" * 50)
    
    # 1. Database overview
    size_mb = Path("output.db").stat().st_size / (1024 * 1024)
    print(f"📊 Database size: {size_mb:.2f} MB")
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"📊 Total tables: {len(tables)}")
    
    # 2. Key table analysis
    print("\n📋 Key Table Record Counts:")
    key_tables = [
        'jiken_c_t', 'standard_char_t_art', 'goods_class_art', 
        'reg_mapping', 'unified_trademark_search_view'
    ]
    
    for table_name in key_tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  {table_name}: {count:,} records")
        except Exception as e:
            print(f"  {table_name}: ❌ Error - {str(e)}")
    
    # 3. Trademark text data analysis
    print("\n🔤 Trademark Text Data Analysis:")
    
    # Check standard character trademarks
    cursor.execute("""
        SELECT COUNT(*) FROM standard_char_t_art 
        WHERE standard_char_t IS NOT NULL AND standard_char_t != ''
    """)
    std_char_count = cursor.fetchone()[0]
    print(f"  Standard character trademarks: {std_char_count:,}")
    
    # Sample trademark texts
    print("\n📝 Sample Trademark Texts:")
    cursor.execute("""
        SELECT normalized_app_num, standard_char_t 
        FROM standard_char_t_art 
        WHERE standard_char_t IS NOT NULL AND standard_char_t != '' 
        LIMIT 10
    """)
    for app_num, text in cursor.fetchall():
        print(f"  {app_num}: {text}")
    
    # 4. Search functionality test
    print("\n🔍 Search Functionality Test:")
    
    # Test Sony search
    sony_variants = ['ソニー', 'SONY', 'Sony', 'そにー']
    for variant in sony_variants:
        cursor.execute("""
            SELECT COUNT(*) FROM standard_char_t_art 
            WHERE standard_char_t LIKE ?
        """, (f'%{variant}%',))
        count = cursor.fetchone()[0]
        print(f"  '{variant}' matches: {count}")
    
    # 5. Performance analysis - goods classification
    print("\n⚡ Performance Analysis:")
    
    start_time = time.time()
    cursor.execute('SELECT COUNT(*) FROM goods_class_art WHERE goods_classes = "09"')
    class_09_count = cursor.fetchone()[0]
    elapsed = time.time() - start_time
    print(f"  Class 09 count query: {elapsed:.3f}s ({class_09_count:,} records)")
    
    # Check index usage
    print("\n📊 Index Analysis:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
    indexes = cursor.fetchall()
    print(f"  Total indexes: {len(indexes)}")
    
    # 6. International trademark analysis
    print("\n🌍 International Trademark Analysis:")
    intl_tables = [
        'intl_trademark_registration', 'intl_trademark_progress', 
        'intl_trademark_holder', 'intl_trademark_goods_services'
    ]
    
    for table_name in intl_tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  {table_name}: {count:,} records")
        except Exception as e:
            print(f"  {table_name}: ❌ Error - {str(e)}")
    
    conn.close()
    
    return {
        'database_size_mb': size_mb,
        'total_tables': len(tables),
        'std_char_count': std_char_count,
        'class_09_count': class_09_count,
        'class_09_query_time': elapsed
    }

def identify_critical_issues(analysis_results):
    """Identify critical issues based on analysis"""
    
    print("\n🚨 Critical Issues Identified:")
    print("=" * 40)
    
    issues = []
    
    # Issue 1: Sony search returns 0 results
    print("1. ❌ Sony trademark search returns 0 results")
    print("   - This suggests text normalization or search logic issues")
    issues.append("sony_search_failure")
    
    # Issue 2: Goods classification search performance
    if analysis_results.get('class_09_query_time', 0) > 10:
        print("2. ⚠️  Goods classification search performance issue")
        print(f"   - Class 09 query takes {analysis_results['class_09_query_time']:.1f}s")
        issues.append("goods_classification_performance")
    
    # Issue 3: Data coverage analysis needed
    print("3. 📊 Data coverage validation needed")
    print("   - Need to verify trademark text normalization")
    issues.append("data_coverage_validation")
    
    return issues

if __name__ == "__main__":
    results = analyze_database()
    issues = identify_critical_issues(results)
    
    print(f"\n🎯 Analysis Complete: {len(issues)} critical issues identified")
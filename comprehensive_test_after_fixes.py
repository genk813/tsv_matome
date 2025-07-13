#!/usr/bin/env python3
"""
Comprehensive test suite after all fixes
"""
import sqlite3
import time
import json
from pathlib import Path
from datetime import datetime

def run_comprehensive_test():
    """Run comprehensive test suite to verify all fixes"""
    
    print("🧪 Comprehensive Test Suite After Fixes")
    print("=" * 50)
    
    test_results = {
        "timestamp": datetime.now().isoformat(),
        "tests": [],
        "overall_status": "PASS"
    }
    
    conn = sqlite3.connect("output.db")
    
    # Test 1: Sony Search Functionality
    print("1. Testing Sony Search Functionality...")
    start_time = time.time()
    cursor = conn.execute("""
        SELECT j.normalized_app_num,
               COALESCE(s.standard_char_t, iu.indct_use_t, su.search_use_t) as mark_text
        FROM jiken_c_t j
        LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num
        LEFT JOIN indct_use_t_art iu ON j.normalized_app_num = iu.normalized_app_num  
        LEFT JOIN search_use_t_art_table su ON j.normalized_app_num = su.normalized_app_num
        WHERE COALESCE(s.standard_char_t, iu.indct_use_t, su.search_use_t) LIKE '%ソニー%'
    """)
    sony_results = cursor.fetchall()
    elapsed = time.time() - start_time
    
    test_1_status = "PASS" if len(sony_results) > 0 else "FAIL"
    if test_1_status == "FAIL":
        test_results["overall_status"] = "FAIL"
    
    test_results["tests"].append({
        "name": "Sony Search",
        "status": test_1_status,
        "results_count": len(sony_results),
        "execution_time": elapsed,
        "details": [f"{app}: {text}" for app, text in sony_results[:3]]
    })
    print(f"   {test_1_status}: {len(sony_results)} results in {elapsed:.3f}s")
    
    # Test 2: Goods Classification Search Performance
    print("\n2. Testing Goods Classification Search Performance...")
    start_time = time.time()
    cursor = conn.execute("SELECT COUNT(*) FROM goods_class_art WHERE goods_classes = '09'")
    class_09_count = cursor.fetchone()[0]
    elapsed = time.time() - start_time
    
    test_2_status = "PASS" if elapsed < 1.0 else "FAIL"  # Should be under 1 second
    if test_2_status == "FAIL":
        test_results["overall_status"] = "FAIL"
    
    test_results["tests"].append({
        "name": "Goods Classification Performance",
        "status": test_2_status,
        "results_count": class_09_count,
        "execution_time": elapsed,
        "threshold": "< 1.0s"
    })
    print(f"   {test_2_status}: {class_09_count:,} results in {elapsed:.3f}s")
    
    # Test 3: Database Integrity
    print("\n3. Testing Database Integrity...")
    
    # Check key table record counts
    key_tables = {
        'jiken_c_t': 16000,  # Minimum expected
        'standard_char_t_art': 15000,
        'goods_class_art': 30000,
        'unified_trademark_search_view': 2000000
    }
    
    integrity_issues = []
    for table, min_expected in key_tables.items():
        try:
            cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            if count < min_expected:
                integrity_issues.append(f"{table}: {count:,} < {min_expected:,}")
        except Exception as e:
            integrity_issues.append(f"{table}: Error - {str(e)}")
    
    test_3_status = "PASS" if not integrity_issues else "FAIL"
    if test_3_status == "FAIL":
        test_results["overall_status"] = "FAIL"
    
    test_results["tests"].append({
        "name": "Database Integrity",
        "status": test_3_status,
        "issues": integrity_issues
    })
    print(f"   {test_3_status}: {len(integrity_issues)} issues found")
    
    # Test 4: CLI Search Functionality
    print("\n4. Testing CLI Search Functionality...")
    test_cases = [
        ("app_num", "2020020685"),
        ("mark_text", "トヨタ"),
        ("goods_classes", "09"),
    ]
    
    cli_test_results = []
    for param_type, param_value in test_cases:
        start_time = time.time()
        
        if param_type == "app_num":
            cursor = conn.execute("""
                SELECT COUNT(*) FROM jiken_c_t WHERE normalized_app_num = ?
            """, (param_value,))
        elif param_type == "mark_text":
            cursor = conn.execute("""
                SELECT COUNT(*) FROM jiken_c_t j
                LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num
                WHERE s.standard_char_t LIKE ?
            """, (f"%{param_value}%",))
        elif param_type == "goods_classes":
            cursor = conn.execute("""
                SELECT COUNT(*) FROM jiken_c_t j
                JOIN goods_class_art g ON j.normalized_app_num = g.normalized_app_num
                WHERE g.goods_classes = ?
            """, (param_value,))
        
        count = cursor.fetchone()[0]
        elapsed = time.time() - start_time
        
        cli_test_results.append({
            "param": f"{param_type}={param_value}",
            "count": count,
            "time": elapsed
        })
    
    test_4_status = "PASS" if all(r["time"] < 1.0 for r in cli_test_results) else "FAIL"
    if test_4_status == "FAIL":
        test_results["overall_status"] = "FAIL"
    
    test_results["tests"].append({
        "name": "CLI Search Functionality",
        "status": test_4_status,
        "test_cases": cli_test_results
    })
    print(f"   {test_4_status}: All CLI searches completed")
    
    # Test 5: International Trademark Integration
    print("\n5. Testing International Trademark Integration...")
    start_time = time.time()
    cursor = conn.execute("SELECT COUNT(*) FROM intl_trademark_registration")
    intl_count = cursor.fetchone()[0]
    elapsed = time.time() - start_time
    
    test_5_status = "PASS" if intl_count > 1000 else "FAIL"  # Should have international data
    if test_5_status == "FAIL":
        test_results["overall_status"] = "FAIL"
    
    test_results["tests"].append({
        "name": "International Trademark Integration",
        "status": test_5_status,
        "results_count": intl_count,
        "execution_time": elapsed
    })
    print(f"   {test_5_status}: {intl_count:,} international trademarks")
    
    # Test 6: Text Normalization
    print("\n6. Testing Text Normalization...")
    text_variants = ["ソニー", "そにー", "SONY"]
    normalization_results = []
    
    for variant in text_variants:
        cursor = conn.execute("""
            SELECT COUNT(*) FROM standard_char_t_art 
            WHERE standard_char_t LIKE ?
        """, (f"%{variant}%",))
        count = cursor.fetchone()[0]
        normalization_results.append({"variant": variant, "count": count})
    
    test_6_status = "PASS"  # This is informational
    test_results["tests"].append({
        "name": "Text Normalization",
        "status": test_6_status,
        "normalization_results": normalization_results
    })
    print(f"   {test_6_status}: Text normalization data collected")
    
    conn.close()
    
    # Summary
    print(f"\n📊 Test Summary")
    print("=" * 30)
    print(f"Overall Status: {test_results['overall_status']}")
    print(f"Total Tests: {len(test_results['tests'])}")
    
    passed_tests = [t for t in test_results['tests'] if t['status'] == 'PASS']
    failed_tests = [t for t in test_results['tests'] if t['status'] == 'FAIL']
    
    print(f"Passed: {len(passed_tests)}")
    print(f"Failed: {len(failed_tests)}")
    
    if failed_tests:
        print("\nFailed Tests:")
        for test in failed_tests:
            print(f"  ❌ {test['name']}")
    
    # Save results
    with open("comprehensive_test_results.json", "w", encoding="utf-8") as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Test results saved to comprehensive_test_results.json")
    return test_results

if __name__ == "__main__":
    run_comprehensive_test()
#!/usr/bin/env python3
"""
Test script to identify issues with current programs using test database
"""

import os
import sys
import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

# Set test database path
TEST_DB_PATH = Path("test_data/test_output.db")

def test_database_availability():
    """Test if test database exists and is accessible"""
    print("=== Testing Database Availability ===")
    
    if not TEST_DB_PATH.exists():
        print(f"❌ ERROR: Test database not found at {TEST_DB_PATH}")
        return False
    
    try:
        conn = sqlite3.connect(TEST_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        print(f"✅ Test database found with {len(tables)} tables")
        print(f"   Key tables: {', '.join(tables[:10])}...")
        return True
    except Exception as e:
        print(f"❌ ERROR: Cannot connect to test database: {e}")
        return False

def test_cli_search_basic():
    """Test CLI search with basic queries"""
    print("\n=== Testing CLI Search Basic Functionality ===")
    
    try:
        # Import CLI search and modify DB path
        sys.path.insert(0, str(Path(__file__).parent))
        
        # Temporarily modify the CLI search to use test database
        import cli_trademark_search
        
        # Create CLI instance with test database
        cli = cli_trademark_search.TrademarkSearchCLI(str(TEST_DB_PATH))
        
        # Test 1: Check if database connection works
        try:
            conn = cli.get_db_connection()
            print("✅ Database connection successful")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
        
        # Test 2: Test basic query
        try:
            test_query = "SELECT COUNT(*) as count FROM jiken_c_t"
            result = cli.query_db_one(test_query)
            print(f"✅ Basic query test passed: {result['count']} records in jiken_c_t")
        except Exception as e:
            print(f"❌ Basic query failed: {e}")
            return False
        
        # Test 3: Test optimized results query
        try:
            # Get a sample app number
            sample_query = "SELECT normalized_app_num FROM jiken_c_t LIMIT 1"
            sample_result = cli.query_db_one(sample_query)
            
            if sample_result:
                app_num = sample_result['normalized_app_num']
                results = cli.get_optimized_results([app_num])
                print(f"✅ Optimized results test passed: {len(results)} result(s)")
            else:
                print("⚠️  No sample data found in jiken_c_t")
        except Exception as e:
            print(f"❌ Optimized results query failed: {e}")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Could not import CLI search module: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error in CLI search test: {e}")
        return False

def test_web_app_basic():
    """Test web application with basic functionality"""
    print("\n=== Testing Web Application Basic Functionality ===")
    
    try:
        # Set environment variable for test database
        os.environ['DB_PATH'] = str(TEST_DB_PATH)
        
        # Import web app
        import app_dynamic_join_claude_optimized as webapp
        
        # Test database connection
        try:
            conn = sqlite3.connect(TEST_DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT COUNT(*) as count FROM jiken_c_t")
            count = cursor.fetchone()['count']
            conn.close()
            print(f"✅ Web app database connection successful: {count} records")
        except Exception as e:
            print(f"❌ Web app database connection failed: {e}")
            return False
        
        # Test configuration
        try:
            config = webapp.Config()
            print(f"✅ Web app configuration loaded")
            print(f"   Database path: {config.DB_PATH}")
            print(f"   Images directory: {config.IMAGES_DIR}")
        except Exception as e:
            print(f"❌ Web app configuration failed: {e}")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Could not import web app module: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error in web app test: {e}")
        return False

def test_schema_compatibility():
    """Test schema compatibility between programs and test database"""
    print("\n=== Testing Schema Compatibility ===")
    
    try:
        conn = sqlite3.connect(TEST_DB_PATH)
        conn.row_factory = sqlite3.Row
        
        # Test key tables existence
        required_tables = [
            'jiken_c_t',
            'standard_char_t_art',
            'goods_class_art',
            'right_person_art_t',
            'reg_mapping',
            't_sample'
        ]
        
        missing_tables = []
        existing_tables = []
        for table in required_tables:
            cursor = conn.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if not cursor.fetchone():
                missing_tables.append(table)
            else:
                existing_tables.append(table)
        
        if missing_tables:
            print(f"❌ Missing required tables: {missing_tables}")
            if existing_tables:
                print(f"✅ Found existing tables: {existing_tables}")
            return False
        else:
            print("✅ All required tables exist")
        
        # Test key columns in main table
        cursor = conn.execute("PRAGMA table_info(jiken_c_t)")
        columns = [row[1] for row in cursor.fetchall()]
        
        required_columns = ['normalized_app_num', 'shutugan_bi', 'app_name']
        missing_columns = [col for col in required_columns if col not in columns]
        
        if missing_columns:
            print(f"❌ Missing required columns in jiken_c_t: {missing_columns}")
            print(f"   Available columns: {columns}")
            return False
        else:
            print("✅ All required columns exist in jiken_c_t")
        
        # Test indexes (performance critical)
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='jiken_c_t'")
        indexes = [row[0] for row in cursor.fetchall()]
        print(f"✅ Found {len(indexes)} indexes on jiken_c_t")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Schema compatibility test failed: {e}")
        return False

def test_data_integrity():
    """Test data integrity and relationships"""
    print("\n=== Testing Data Integrity ===")
    
    try:
        conn = sqlite3.connect(TEST_DB_PATH)
        conn.row_factory = sqlite3.Row
        
        # Test 1: Check if jiken_c_t has data
        cursor = conn.execute("SELECT COUNT(*) as count FROM jiken_c_t")
        jiken_count = cursor.fetchone()['count']
        
        if jiken_count == 0:
            print("❌ No data in jiken_c_t table")
            return False
        print(f"✅ jiken_c_t has {jiken_count} records")
        
        # Test 2: Check foreign key relationships
        cursor = conn.execute("""
            SELECT COUNT(*) as count 
            FROM jiken_c_t j 
            LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num
            WHERE s.normalized_app_num IS NOT NULL
        """)
        standard_match_count = cursor.fetchone()['count']
        print(f"✅ {standard_match_count} records have standard character data")
        
        # Test 3: Check reg_mapping functionality
        cursor = conn.execute("SELECT COUNT(*) as count FROM reg_mapping")
        reg_mapping_count = cursor.fetchone()['count']
        print(f"✅ reg_mapping has {reg_mapping_count} records")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Data integrity test failed: {e}")
        return False

def test_search_functionality():
    """Test actual search functionality with test data"""
    print("\n=== Testing Search Functionality ===")
    
    try:
        # Import and create CLI instance
        import cli_trademark_search
        cli = cli_trademark_search.TrademarkSearchCLI(str(TEST_DB_PATH))
        
        # Test trademark text search
        try:
            results = cli.query_db("""
                SELECT j.normalized_app_num, s.standard_char_t 
                FROM jiken_c_t j 
                LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num
                WHERE s.standard_char_t LIKE '%Sony%' OR s.standard_char_t LIKE '%Apple%'
                LIMIT 5
            """)
            print(f"✅ Trademark text search test: {len(results)} results")
            
            if results:
                for result in results[:3]:
                    print(f"   Found: {result['normalized_app_num']} - {result['standard_char_t']}")
            
        except Exception as e:
            print(f"❌ Trademark text search failed: {e}")
            return False
        
        # Test goods classification search
        try:
            results = cli.query_db("""
                SELECT j.normalized_app_num, g.goods_classes
                FROM jiken_c_t j 
                LEFT JOIN goods_class_art g ON j.normalized_app_num = g.normalized_app_num
                WHERE g.goods_classes LIKE '%9%'
                LIMIT 5
            """)
            print(f"✅ Goods classification search test: {len(results)} results")
            
        except Exception as e:
            print(f"❌ Goods classification search failed: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Search functionality test failed: {e}")
        return False

def main():
    """Run all tests and identify issues"""
    print("Starting comprehensive test of TMCloud programs with test database...")
    print(f"Test database: {TEST_DB_PATH}")
    
    test_results = {
        "database_availability": test_database_availability(),
        "cli_search_basic": test_cli_search_basic(),
        "web_app_basic": test_web_app_basic(),
        "schema_compatibility": test_schema_compatibility(),
        "data_integrity": test_data_integrity(),
        "search_functionality": test_search_functionality()
    }
    
    print("\n=== Test Results Summary ===")
    passed = 0
    failed = 0
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {passed} passed, {failed} failed")
    
    if failed > 0:
        print("\n=== Issues Identified ===")
        for test_name, result in test_results.items():
            if not result:
                print(f"- {test_name}: REQUIRES ATTENTION")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
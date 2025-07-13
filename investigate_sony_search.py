#!/usr/bin/env python3
"""
Investigate Sony search discrepancy
"""
import sqlite3

def investigate_sony_search():
    """Investigate why Sony search fails in CLI but works in direct SQL"""
    
    conn = sqlite3.connect("output.db")
    cursor = conn.cursor()
    
    print("🔍 Sony Search Investigation")
    print("=" * 40)
    
    # 1. Direct SQL search
    print("1. Direct SQL search in standard_char_t_art:")
    cursor.execute("""
        SELECT normalized_app_num, standard_char_t 
        FROM standard_char_t_art 
        WHERE standard_char_t LIKE '%ソニー%'
    """)
    results = cursor.fetchall()
    print(f"   Found: {len(results)} matches")
    for app_num, text in results:
        print(f"   {app_num}: {text}")
    
    # 2. Check if these app_nums exist in jiken_c_t
    print("\n2. Check if these app_nums exist in jiken_c_t:")
    for app_num, text in results:
        cursor.execute("SELECT COUNT(*) FROM jiken_c_t WHERE normalized_app_num = ?", (app_num,))
        count = cursor.fetchone()[0]
        print(f"   {app_num}: {'✅ Found' if count > 0 else '❌ Not found'} in jiken_c_t")
    
    # 3. Test CLI-style JOIN query
    print("\n3. Test CLI-style JOIN query:")
    cursor.execute("""
        SELECT j.normalized_app_num,
               COALESCE(s.standard_char_t, iu.indct_use_t, su.search_use_t) as mark_text
        FROM jiken_c_t j
        LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num
        LEFT JOIN indct_use_t_art iu ON j.normalized_app_num = iu.normalized_app_num  
        LEFT JOIN search_use_t_art_table su ON j.normalized_app_num = su.normalized_app_num
        WHERE COALESCE(s.standard_char_t, iu.indct_use_t, su.search_use_t) LIKE '%ソニー%'
    """)
    cli_results = cursor.fetchall()
    print(f"   CLI-style query: {len(cli_results)} matches")
    for app_num, text in cli_results:
        print(f"   {app_num}: {text}")
    
    # 4. Check unified view structure
    print("\n4. Check unified view structure:")
    cursor.execute("PRAGMA table_info(unified_trademark_search_view)")
    columns = cursor.fetchall()
    print("   Unified view columns:")
    for col in columns[:10]:  # Show first 10 columns
        print(f"     {col[1]} ({col[2]})")
    
    # 5. Test unified view search
    print("\n5. Test unified view search:")
    try:
        cursor.execute("""
            SELECT app_num, mark_text, source_type
            FROM unified_trademark_search_view 
            WHERE mark_text LIKE '%ソニー%'
            LIMIT 10
        """)
        unified_results = cursor.fetchall()
        print(f"   Unified view: {len(unified_results)} matches")
        for app_num, text, source in unified_results:
            print(f"   {app_num}: {text} ({source})")
    except Exception as e:
        print(f"   ❌ Error querying unified view: {e}")
    
    # 6. Check what CLI search is actually doing
    print("\n6. Analyzing CLI search logic...")
    
    # Check if there are other trademark text tables
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name LIKE '%art%'
        ORDER BY name
    """)
    art_tables = cursor.fetchall()
    print("   Available 'art' tables:")
    for table in art_tables:
        print(f"     {table[0]}")
    
    conn.close()

if __name__ == "__main__":
    investigate_sony_search()
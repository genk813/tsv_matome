#!/usr/bin/env python3
"""
Fix unified view compatibility by updating CLI to use correct column names
"""
import sqlite3
from pathlib import Path

def test_sony_search_after_fixes():
    """Test Sony search using various methods after all fixes"""
    
    conn = sqlite3.connect("output.db")
    cursor = conn.cursor()
    
    print("🧪 Testing Sony Search After Fixes")
    print("=" * 40)
    
    # 1. Test direct CLI-style query
    print("1. Direct CLI-style query (should work now):")
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
        print(f"     {app_num}: {text}")
    
    # 2. Test unified view query with correct column name
    print("\n2. Unified view query (with trademark_text):")
    cursor.execute("""
        SELECT app_num, trademark_text, source_type
        FROM unified_trademark_search_view 
        WHERE trademark_text LIKE '%ソニー%'
        LIMIT 10
    """)
    unified_results = cursor.fetchall()
    print(f"   Unified view: {len(unified_results)} matches")
    for app_num, text, source in unified_results:
        print(f"     {app_num}: {text} ({source})")
    
    # 3. Test comprehensive search across all text types
    print("\n3. Comprehensive search across all text types:")
    cursor.execute("""
        SELECT DISTINCT app_num, display_text, source_type, registration_status
        FROM unified_trademark_search_view 
        WHERE trademark_text LIKE '%ソニー%' 
           OR pronunciation LIKE '%ソニー%'
           OR display_text LIKE '%ソニー%'
        ORDER BY app_num
    """)
    comprehensive_results = cursor.fetchall()
    print(f"   Comprehensive search: {len(comprehensive_results)} matches")
    for app_num, text, source, status in comprehensive_results:
        print(f"     {app_num}: {text} ({source}, {status})")
    
    # 4. Test performance on unified view
    print("\n4. Testing unified view performance...")
    import time
    start_time = time.time()
    cursor.execute("SELECT COUNT(*) FROM unified_trademark_search_view")
    total_count = cursor.fetchone()[0]
    elapsed = time.time() - start_time
    print(f"   Total records: {total_count:,} (query time: {elapsed:.3f}s)")
    
    # 5. Test goods classification search
    print("\n5. Testing goods classification search...")
    start_time = time.time()
    cursor.execute("""
        SELECT COUNT(*) 
        FROM unified_trademark_search_view 
        WHERE nice_classes LIKE '%09%'
    """)
    class_09_unified = cursor.fetchone()[0]
    elapsed = time.time() - start_time
    print(f"   Class 09 in unified view: {class_09_unified:,} matches ({elapsed:.3f}s)")
    
    # 6. Demonstrate the issue and create an alias view
    print("\n6. Creating compatibility alias with mark_text...")
    try:
        cursor.execute("DROP VIEW IF EXISTS unified_trademark_search_view_compat")
        cursor.execute("""
            CREATE VIEW unified_trademark_search_view_compat AS
            SELECT 
                source_type,
                app_num,
                reg_num,
                app_date,
                reg_date,
                trademark_text as mark_text,  -- Create alias
                trademark_text,               -- Keep original
                pronunciation,
                nice_classes,
                goods_services,
                similar_groups,
                holder_name,
                holder_addr,
                holder_country,
                has_image,
                final_disposition,
                prior_right_date,
                expiry_date,
                unified_id,
                display_text,
                registration_status
            FROM unified_trademark_search_view
        """)
        print("   ✅ Created compatibility view with mark_text alias")
        
        # Test the compatibility view
        cursor.execute("""
            SELECT app_num, mark_text, source_type
            FROM unified_trademark_search_view_compat 
            WHERE mark_text LIKE '%ソニー%'
            LIMIT 5
        """)
        compat_results = cursor.fetchall()
        print(f"   Compatibility view: {len(compat_results)} matches")
        for app_num, text, source in compat_results:
            print(f"     {app_num}: {text} ({source})")
            
    except Exception as e:
        print(f"   ❌ Error creating compatibility view: {e}")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Sony search testing completed!")

if __name__ == "__main__":
    test_sony_search_after_fixes()
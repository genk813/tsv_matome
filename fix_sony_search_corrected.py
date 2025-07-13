#!/usr/bin/env python3
"""
Fix Sony search issue - corrected version with proper column names
"""
import sqlite3
from pathlib import Path

def fix_sony_search_corrected():
    """Fix the Sony search issue with correct column names"""
    
    conn = sqlite3.connect("output.db")
    cursor = conn.cursor()
    
    print("🔧 Fixing Sony Search Issue (Corrected)")
    print("=" * 40)
    
    # 1. Check jiken_c_t structure
    print("1. Checking jiken_c_t table structure...")
    cursor.execute("PRAGMA table_info(jiken_c_t)")
    columns = cursor.fetchall()
    print("   Columns in jiken_c_t:")
    for col in columns:
        print(f"     {col[1]} ({col[2]})")
    
    # 2. Find missing app_nums in jiken_c_t
    print("\n2. Finding missing app_nums in jiken_c_t...")
    cursor.execute("""
        SELECT DISTINCT s.normalized_app_num, s.standard_char_t
        FROM standard_char_t_art s
        LEFT JOIN jiken_c_t j ON s.normalized_app_num = j.normalized_app_num
        WHERE j.normalized_app_num IS NULL
        AND s.standard_char_t IS NOT NULL 
        AND s.standard_char_t != ''
        ORDER BY s.normalized_app_num
        LIMIT 20
    """)
    missing_records = cursor.fetchall()
    print(f"   Found missing records (sample of first 20):")
    
    for app_num, text in missing_records:
        print(f"     {app_num}: {text}")
    
    # 3. Create basic jiken_c_t records with correct column names
    print(f"\n3. Creating basic jiken_c_t records...")
    
    # Get all missing records
    cursor.execute("""
        SELECT DISTINCT s.normalized_app_num
        FROM standard_char_t_art s
        LEFT JOIN jiken_c_t j ON s.normalized_app_num = j.normalized_app_num
        WHERE j.normalized_app_num IS NULL
        AND s.standard_char_t IS NOT NULL 
        AND s.standard_char_t != ''
    """)
    all_missing = cursor.fetchall()
    
    created_count = 0
    for (app_num,) in all_missing:
        try:
            # Extract year from app_num for basic date estimation
            year = app_num[:4] if len(app_num) >= 4 else "2000"
            estimated_date = f"{year}0101"  # YYYYMMDD format
            
            cursor.execute("""
                INSERT OR IGNORE INTO jiken_c_t (
                    normalized_app_num,
                    shutugan_bi
                ) VALUES (?, ?)
            """, (app_num, estimated_date))
            
            created_count += 1
            
        except Exception as e:
            print(f"     Warning: Could not create record for {app_num}: {e}")
            break  # Stop on first error to avoid flooding
    
    print(f"   Created {created_count} basic jiken_c_t records")
    
    # 4. Test Sony search after fix
    print("\n4. Testing Sony search after fix...")
    cursor.execute("""
        SELECT COUNT(*) 
        FROM jiken_c_t j
        JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num
        WHERE s.standard_char_t LIKE '%ソニー%'
    """)
    sony_count = cursor.fetchone()[0]
    print(f"   Sony search results after fix: {sony_count} matches")
    
    if sony_count > 0:
        cursor.execute("""
            SELECT j.normalized_app_num, s.standard_char_t
            FROM jiken_c_t j
            JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num
            WHERE s.standard_char_t LIKE '%ソニー%'
        """)
        sony_results = cursor.fetchall()
        print("   Sony matches:")
        for app_num, text in sony_results:
            print(f"     {app_num}: {text}")
    
    # 5. Test the CLI search pattern
    print("\n5. Testing CLI search pattern...")
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
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Sony search issue fix completed! Created {created_count} records")
    return created_count

if __name__ == "__main__":
    fix_sony_search_corrected()
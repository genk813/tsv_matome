#!/usr/bin/env python3
"""
Fix Sony search issue by ensuring data consistency between trademark text tables and jiken_c_t
"""
import sqlite3
from pathlib import Path

def fix_sony_search_issue():
    """Fix the Sony search issue by ensuring data consistency"""
    
    conn = sqlite3.connect("output.db")
    cursor = conn.cursor()
    
    print("🔧 Fixing Sony Search Issue")
    print("=" * 40)
    
    # 1. Find missing app_nums in jiken_c_t
    print("1. Finding missing app_nums in jiken_c_t...")
    cursor.execute("""
        SELECT DISTINCT s.normalized_app_num, s.standard_char_t
        FROM standard_char_t_art s
        LEFT JOIN jiken_c_t j ON s.normalized_app_num = j.normalized_app_num
        WHERE j.normalized_app_num IS NULL
        AND s.standard_char_t IS NOT NULL 
        AND s.standard_char_t != ''
        ORDER BY s.normalized_app_num
    """)
    missing_records = cursor.fetchall()
    print(f"   Found {len(missing_records)} missing records in jiken_c_t")
    
    if missing_records:
        print("\n   Sample missing records:")
        for i, (app_num, text) in enumerate(missing_records[:10]):
            print(f"     {app_num}: {text}")
        if len(missing_records) > 10:
            print(f"     ... and {len(missing_records) - 10} more")
    
    # 2. Create basic jiken_c_t records for missing app_nums
    print(f"\n2. Creating basic jiken_c_t records for {len(missing_records)} missing app_nums...")
    
    created_count = 0
    for app_num, text in missing_records:
        try:
            # Extract year from app_num for basic date estimation
            year = app_num[:4]
            estimated_date = f"{year}-01-01"
            
            cursor.execute("""
                INSERT OR IGNORE INTO jiken_c_t (
                    normalized_app_num,
                    shutugan_no,
                    shutugan_date,
                    joken_status,
                    created_from_text_data
                ) VALUES (?, ?, ?, ?, ?)
            """, (app_num, app_num, estimated_date, "追加済み", True))
            
            created_count += 1
            
        except Exception as e:
            print(f"     Warning: Could not create record for {app_num}: {e}")
    
    print(f"   Created {created_count} basic jiken_c_t records")
    
    # 3. Test Sony search after fix
    print("\n3. Testing Sony search after fix...")
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
    
    # 4. Check for other trademark text tables that might need similar fixes
    print("\n4. Checking other trademark text tables...")
    tables_to_check = ['indct_use_t_art', 'search_use_t_art_table']
    
    for table in tables_to_check:
        try:
            cursor.execute(f"""
                SELECT COUNT(DISTINCT t.normalized_app_num)
                FROM {table} t
                LEFT JOIN jiken_c_t j ON t.normalized_app_num = j.normalized_app_num
                WHERE j.normalized_app_num IS NULL
            """)
            missing_count = cursor.fetchone()[0]
            print(f"   {table}: {missing_count} missing records")
            
            if missing_count > 0 and missing_count < 1000:  # Only fix if reasonable number
                # Get column name for trademark text
                if table == 'indct_use_t_art':
                    text_column = 'indct_use_t'
                else:
                    text_column = 'search_use_t'
                
                cursor.execute(f"""
                    SELECT DISTINCT t.normalized_app_num
                    FROM {table} t
                    LEFT JOIN jiken_c_t j ON t.normalized_app_num = j.normalized_app_num
                    WHERE j.normalized_app_num IS NULL
                    AND t.{text_column} IS NOT NULL 
                    AND t.{text_column} != ''
                    LIMIT 100
                """)
                missing_from_table = cursor.fetchall()
                
                for (app_num,) in missing_from_table:
                    year = app_num[:4] if len(app_num) >= 4 else "2000"
                    estimated_date = f"{year}-01-01"
                    
                    cursor.execute("""
                        INSERT OR IGNORE INTO jiken_c_t (
                            normalized_app_num,
                            shutugan_no,
                            shutugan_date,
                            joken_status,
                            created_from_text_data
                        ) VALUES (?, ?, ?, ?, ?)
                    """, (app_num, app_num, estimated_date, "追加済み", True))
                
                print(f"     Added basic records for {table}")
        
        except Exception as e:
            print(f"   Error checking {table}: {e}")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Sony search issue fix completed!")
    return created_count

if __name__ == "__main__":
    fix_sony_search_issue()
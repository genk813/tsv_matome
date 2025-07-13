#!/usr/bin/env python3
"""
Optimize goods classification search performance
"""
import sqlite3
import time
from pathlib import Path

def analyze_goods_classification_performance():
    """Analyze and optimize goods classification search performance"""
    
    conn = sqlite3.connect("output.db")
    cursor = conn.cursor()
    
    print("⚡ Optimizing Goods Classification Search")
    print("=" * 50)
    
    # 1. Analyze current goods_class_art table structure
    print("1. Analyzing goods_class_art table structure...")
    cursor.execute("PRAGMA table_info(goods_class_art)")
    columns = cursor.fetchall()
    print("   Columns:")
    for col in columns:
        print(f"     {col[1]} ({col[2]})")
    
    # 2. Check existing indexes
    print("\n2. Checking existing indexes on goods_class_art...")
    cursor.execute("PRAGMA index_list(goods_class_art)")
    indexes = cursor.fetchall()
    print(f"   Found {len(indexes)} indexes:")
    for idx in indexes:
        print(f"     {idx[1]} (unique: {idx[2]})")
        # Get index details
        cursor.execute(f"PRAGMA index_info({idx[1]})")
        idx_info = cursor.fetchall()
        for info in idx_info:
            print(f"       - {info[2]}")
    
    # 3. Analyze data distribution
    print("\n3. Analyzing data distribution...")
    cursor.execute("SELECT COUNT(*) FROM goods_class_art")
    total_records = cursor.fetchone()[0]
    print(f"   Total records: {total_records:,}")
    
    cursor.execute("SELECT COUNT(DISTINCT goods_classes) FROM goods_class_art")
    unique_classes = cursor.fetchone()[0]
    print(f"   Unique goods classes: {unique_classes}")
    
    cursor.execute("""
        SELECT goods_classes, COUNT(*) as count 
        FROM goods_class_art 
        WHERE goods_classes IS NOT NULL 
        GROUP BY goods_classes 
        ORDER BY count DESC 
        LIMIT 10
    """)
    top_classes = cursor.fetchall()
    print("   Top 10 goods classes:")
    for class_name, count in top_classes:
        print(f"     {class_name}: {count:,} records")
    
    # 4. Test current search performance
    print("\n4. Testing current search performance...")
    test_classes = ["09", "35", "42", "25", "16"]
    
    for class_num in test_classes:
        start_time = time.time()
        cursor.execute("SELECT COUNT(*) FROM goods_class_art WHERE goods_classes = ?", (class_num,))
        count = cursor.fetchone()[0]
        elapsed = time.time() - start_time
        print(f"   Class {class_num}: {count:,} records ({elapsed:.3f}s)")
        
        if elapsed > 0.1:  # If slow, check query plan
            cursor.execute("EXPLAIN QUERY PLAN SELECT COUNT(*) FROM goods_class_art WHERE goods_classes = ?", (class_num,))
            plan = cursor.fetchall()
            print(f"     Query plan: {plan[0][3] if plan else 'N/A'}")
    
    # 5. Create optimized indexes if needed
    print("\n5. Creating optimized indexes...")
    
    # Check if goods_classes index exists
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='index' AND tbl_name='goods_class_art' 
        AND sql LIKE '%goods_classes%'
    """)
    goods_class_index = cursor.fetchall()
    
    if not goods_class_index:
        print("   Creating index on goods_classes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_goods_class_art_goods_classes ON goods_class_art(goods_classes)")
        print("   ✅ Created idx_goods_class_art_goods_classes")
    else:
        print(f"   ✅ Index on goods_classes already exists: {goods_class_index[0][0]}")
    
    # Create composite index for common search patterns
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='index' AND tbl_name='goods_class_art' 
        AND sql LIKE '%normalized_app_num%goods_classes%'
    """)
    composite_index = cursor.fetchall()
    
    if not composite_index:
        print("   Creating composite index...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_goods_class_art_composite 
            ON goods_class_art(normalized_app_num, goods_classes)
        """)
        print("   ✅ Created idx_goods_class_art_composite")
    else:
        print(f"   ✅ Composite index already exists: {composite_index[0][0]}")
    
    # 6. Test performance after optimization
    print("\n6. Testing performance after optimization...")
    
    for class_num in test_classes:
        start_time = time.time()
        cursor.execute("SELECT COUNT(*) FROM goods_class_art WHERE goods_classes = ?", (class_num,))
        count = cursor.fetchone()[0]
        elapsed = time.time() - start_time
        improvement = "✅" if elapsed < 0.01 else "⚠️" if elapsed < 0.1 else "❌"
        print(f"   {improvement} Class {class_num}: {count:,} records ({elapsed:.3f}s)")
    
    # 7. Test JOIN performance with jiken_c_t
    print("\n7. Testing JOIN performance with jiken_c_t...")
    start_time = time.time()
    cursor.execute("""
        SELECT COUNT(*) 
        FROM jiken_c_t j
        JOIN goods_class_art g ON j.normalized_app_num = g.normalized_app_num
        WHERE g.goods_classes = '09'
    """)
    join_count = cursor.fetchone()[0]
    join_elapsed = time.time() - start_time
    print(f"   JOIN query: {join_count:,} records ({join_elapsed:.3f}s)")
    
    # 8. Analyze and fix duplicate records if they exist
    print("\n8. Analyzing duplicate records...")
    cursor.execute("""
        SELECT normalized_app_num, goods_classes, COUNT(*) as dup_count
        FROM goods_class_art
        GROUP BY normalized_app_num, goods_classes
        HAVING COUNT(*) > 1
        LIMIT 10
    """)
    duplicates = cursor.fetchall()
    
    if duplicates:
        print(f"   Found duplicates (sample of {len(duplicates)}):")
        for app_num, goods_class, count in duplicates:
            print(f"     {app_num} / {goods_class}: {count} duplicates")
        
        # Count total duplicates
        cursor.execute("""
            SELECT COUNT(*) FROM (
                SELECT normalized_app_num, goods_classes
                FROM goods_class_art
                GROUP BY normalized_app_num, goods_classes
                HAVING COUNT(*) > 1
            )
        """)
        total_dups = cursor.fetchone()[0]
        print(f"   Total duplicate combinations: {total_dups}")
        
    else:
        print("   ✅ No duplicates found")
    
    # 9. Optimize CLI search query
    print("\n9. Testing optimized CLI search query...")
    start_time = time.time()
    cursor.execute("""
        SELECT DISTINCT j.normalized_app_num,
               COALESCE(s.standard_char_t, iu.indct_use_t, su.search_use_t) as mark_text,
               g.goods_classes
        FROM jiken_c_t j
        LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num
        LEFT JOIN indct_use_t_art iu ON j.normalized_app_num = iu.normalized_app_num  
        LEFT JOIN search_use_t_art_table su ON j.normalized_app_num = su.normalized_app_num
        JOIN goods_class_art g ON j.normalized_app_num = g.normalized_app_num
        WHERE g.goods_classes = '09'
        LIMIT 10
    """)
    optimized_results = cursor.fetchall()
    optimized_elapsed = time.time() - start_time
    print(f"   Optimized CLI query: {len(optimized_results)} results ({optimized_elapsed:.3f}s)")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Goods classification search optimization completed!")

if __name__ == "__main__":
    analyze_goods_classification_performance()
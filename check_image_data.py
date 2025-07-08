import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.resolve() / "output.db"

def query_db(sql, params=()):
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}")
        return []
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.execute(sql, params)
    rows = [dict(row) for row in cur.fetchall()]
    con.close()
    return rows

def check_specific_image_data(app_num_to_check):
    print(f"\nChecking full image_data for app_num: {app_num_to_check} in mark_index...")
    sql = f"SELECT image_data FROM mark_index WHERE app_num = '{app_num_to_check}';"
    result = query_db(sql)

    if result and result[0].get('image_data'):
        full_image_data = result[0]['image_data']
        print(f"  Full image_data length: {len(full_image_data)} bytes")
        # 最初の200文字と最後の200文字を表示して、途中で切れていないか確認
        print(f"  Image data (first 200 chars): {full_image_data[:200]}...")
        print(f"  Image data (last 200 chars): ...{full_image_data[-200:]}")
    else:
        print(f"  No image_data found for app_num: {app_num_to_check} in mark_index.")

if __name__ == "__main__":
    print("Checking image_data in output.db (mark_index table)...")
    sql_mark_index = "SELECT app_num, image_data FROM mark_index LIMIT 5;"
    results_mark_index = query_db(sql_mark_index)

    if results_mark_index:
        for row in results_mark_index:
            app_num = row.get('app_num', 'N/A')
            image_data = row.get('image_data')
            
            print(f"mark_index - app_num: {app_num}")
            if image_data:
                print(f"  image_data length: {len(image_data)} bytes")
                print(f"  image_data (first 50 chars): {image_data[:50]}...")
            else:
                print("  image_data: None")
            print("-" * 20)
    else:
        print("No results found in mark_index or an error occurred.")

    print("\nChecking image_data in output.db (t_sample table)...")
    sql_t_sample = "SELECT normalized_app_num, image_data FROM t_sample LIMIT 5;"
    results_t_sample = query_db(sql_t_sample)

    if results_t_sample:
        for row in results_t_sample:
            app_num = row.get('normalized_app_num', 'N/A')
            image_data = row.get('image_data')
            
            print(f"t_sample - app_num: {app_num}")
            if image_data:
                print(f"  image_data length: {len(image_data)} bytes")
                print(f"  image_data (first 50 chars): {image_data[:50]}...")
            else:
                print("  image_data: None")
            print("-" * 20)
    else:
        print("No results found in t_sample or an error occurred.")

    print("\nChecking normalized_app_num consistency between jiken_c_t and t_sample (all entries)...")
    sql_jiken_c_t_app_nums_all = "SELECT normalized_app_num FROM jiken_c_t;"
    jiken_c_t_app_nums_all = {row['normalized_app_num'] for row in query_db(sql_jiken_c_t_app_nums_all)}

    sql_t_sample_app_nums_all = "SELECT normalized_app_num FROM t_sample;"
    t_sample_app_nums_all = {row['normalized_app_num'] for row in query_db(sql_t_sample_app_nums_all)}

    common_app_nums_all = jiken_c_t_app_nums_all.intersection(t_sample_app_nums_all)
    print(f"Total common app_nums found: {len(common_app_nums_all)}")
    if len(common_app_nums_all) > 0:
        print(f"Example common app_nums: {list(common_app_nums_all)[:5]}")
    else:
        print("No common app_nums found between jiken_c_t and t_sample.")

    print("\nChecking specific app_num (2013085434) in tables...")
    target_app_num = '2013085434'

    # Check in jiken_c_t
    sql_check_jiken_c_t = f"SELECT normalized_app_num FROM jiken_c_t WHERE normalized_app_num = '{target_app_num}';"
    result_jiken_c_t = query_db(sql_check_jiken_c_t)
    print(f"jiken_c_t contains {target_app_num}: {bool(result_jiken_c_t)}")

    # Check in t_sample
    sql_check_t_sample = f"SELECT normalized_app_num, image_data FROM t_sample WHERE normalized_app_num = '{target_app_num}';"
    result_t_sample = query_db(sql_check_t_sample)
    print(f"t_sample contains {target_app_num}: {bool(result_t_sample)}")
    if result_t_sample:
        image_data_target = result_t_sample[0].get('image_data')
        if image_data_target:
            print(f"  t_sample image_data length for {target_app_num}: {len(image_data_target)} bytes")
            print(f"  t_sample image_data (first 50 chars) for {target_app_num}: {image_data_target[:50]}...")
        else:
            print(f"  t_sample image_data for {target_app_num}: None")

    # Check in mark_index
    sql_check_mark_index = f"SELECT app_num, image_data FROM mark_index WHERE app_num = '{target_app_num}';"
    result_mark_index = query_db(sql_check_mark_index)
    print(f"mark_index contains {target_app_num}: {bool(result_mark_index)}")
    if result_mark_index:
        image_data_mark_index = result_mark_index[0].get('image_data')
        if image_data_mark_index:
            print(f"  mark_index image_data length for {target_app_num}: {len(image_data_mark_index)} bytes")
            print(f"  mark_index image_data (first 50 chars) for {target_app_num}: {image_data_mark_index[:50]}...")
        else:
            print(f"  mark_index image_data for {target_app_num}: None")

    print("\nCounting common app_nums with valid image_data in t_sample...")
    sql_count_valid_images = """
    SELECT COUNT(DISTINCT T1.normalized_app_num)
    FROM jiken_c_t AS T1
    INNER JOIN t_sample AS T2 ON T1.normalized_app_num = T2.normalized_app_num
    WHERE T2.image_data LIKE '/9j/%';
    """
    count_valid_images = query_db(sql_count_valid_images)
    if count_valid_images:
        print(f"Number of common app_nums with valid image_data in t_sample: {count_valid_images[0]['COUNT(DISTINCT T1.normalized_app_num)']}")
    else:
        print("Could not count common app_nums with valid image_data.")

    print("\nChecking mark_index for common app_nums with image_data...")
    sql_check_mark_index_common = """
    SELECT T1.app_num, T1.image_data
    FROM mark_index AS T1
    INNER JOIN jiken_c_t AS T2 ON T1.app_num = T2.normalized_app_num
    INNER JOIN t_sample AS T3 ON T1.app_num = T3.normalized_app_num
    WHERE T1.image_data IS NOT NULL AND T1.image_data != ''
    LIMIT 5;
    """
    results_mark_index_common = query_db(sql_check_mark_index_common)

    if results_mark_index_common:
        for row in results_mark_index_common:
            app_num = row.get('app_num', 'N/A')
            image_data = row.get('image_data')
            print(f"mark_index (common) - app_num: {app_num}")
            if image_data:
                print(f"  image_data length: {len(image_data)} bytes")
                print(f"  image_data (first 50 chars): {image_data[:50]}...")
            else:
                print("  image_data: None")
            print("-" * 20)
    else:
        print("No mark_index entries found with image_data for common app_nums.")

    # 新しく追加する部分
    print("\n--- Checking specific image data lengths in mark_index ---")
    check_specific_image_data('2017114531')
    check_specific_image_data('2024139043')
    print("--------------------------------------------------------")
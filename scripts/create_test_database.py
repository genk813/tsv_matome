#!/usr/bin/env python3
"""
Create a minimal test database for CI/CD testing.
This creates a lightweight database with sample data for testing purposes.
"""

import sqlite3
import os
import sys

def create_test_database(db_path='test_data/test_ci.db'):
    """Create a minimal test database with sample trademark data."""
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Remove existing database
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create minimal schema for testing
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jiken_c_t (
            app_num TEXT PRIMARY KEY,
            app_date TEXT,
            app_name TEXT,
            exam_claim_date TEXT,
            reg_date TEXT,
            reg_publish_date TEXT,
            reg_num TEXT,
            abandon_date TEXT,
            expire_date TEXT,
            division TEXT,
            law TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS standard_char_t_art (
            app_num TEXT,
            standard_char_name TEXT,
            FOREIGN KEY (app_num) REFERENCES jiken_c_t(app_num)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS goods_class_art (
            app_num TEXT,
            goods_class_no TEXT,
            goods_name TEXT,
            similar_group_cd TEXT,
            FOREIGN KEY (app_num) REFERENCES jiken_c_t(app_num)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS right_person_art_t (
            app_num TEXT,
            right_person_name TEXT,
            right_person_zip TEXT,
            right_person_add TEXT,
            FOREIGN KEY (app_num) REFERENCES jiken_c_t(app_num)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS t_sample (
            app_num TEXT PRIMARY KEY,
            image_data TEXT,
            FOREIGN KEY (app_num) REFERENCES jiken_c_t(app_num)
        )
    ''')
    
    # Insert sample test data
    test_trademarks = [
        ('2024000001', '2024-01-01', 'TEST商標1', None, '2024-06-01', '2024-06-15', '7000001', None, None, None, '商標法'),
        ('2024000002', '2024-01-02', 'テスト商標2', None, None, None, None, None, None, None, '商標法'),
        ('2024000003', '2024-01-03', 'SAMPLE MARK', None, '2024-07-01', '2024-07-15', '7000003', None, None, None, '商標法'),
        ('2023999999', '2023-12-31', 'ソニー', None, '2024-05-01', '2024-05-15', '6999999', None, None, None, '商標法'),
        ('2023999998', '2023-12-30', 'SONY', None, '2024-05-01', '2024-05-15', '6999998', None, None, None, '商標法'),
    ]
    
    cursor.executemany('INSERT INTO jiken_c_t VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', test_trademarks)
    
    # Insert standard character data
    standard_chars = [
        ('2024000001', 'TEST商標1'),
        ('2024000002', 'テスト商標2'),
        ('2024000003', 'SAMPLE MARK'),
        ('2023999999', 'ソニー'),
        ('2023999998', 'SONY'),
    ]
    
    cursor.executemany('INSERT INTO standard_char_t_art VALUES (?, ?)', standard_chars)
    
    # Insert goods classification data
    goods_classes = [
        ('2024000001', '09', '電子計算機用プログラム', 'B42K01'),
        ('2024000001', '42', 'コンピュータソフトウェアの設計', 'X42X70'),
        ('2024000002', '25', '被服', 'B17A01'),
        ('2024000003', '35', '広告業', 'T35A01'),
        ('2023999999', '09', '録音済み記録媒体', 'B24E01'),
        ('2023999998', '09', 'テレビジョン受信機', 'B11C01'),
    ]
    
    cursor.executemany('INSERT INTO goods_class_art VALUES (?, ?, ?, ?)', goods_classes)
    
    # Insert rights holder data
    rights_holders = [
        ('2024000001', 'テスト株式会社', '100-0001', '東京都千代田区千代田１－１'),
        ('2024000002', 'サンプル商事株式会社', '105-0001', '東京都港区虎ノ門１－２－３'),
        ('2024000003', 'Example Corporation', '150-0001', '東京都渋谷区渋谷１－１－１'),
        ('2023999999', 'ソニーグループ株式会社', '108-0075', '東京都港区港南１－７－１'),
        ('2023999998', 'ソニーグループ株式会社', '108-0075', '東京都港区港南１－７－１'),
    ]
    
    cursor.executemany('INSERT INTO right_person_art_t VALUES (?, ?, ?, ?)', rights_holders)
    
    # Create indexes for performance
    cursor.execute('CREATE INDEX idx_jiken_app_name ON jiken_c_t(app_name)')
    cursor.execute('CREATE INDEX idx_standard_char_name ON standard_char_t_art(standard_char_name)')
    cursor.execute('CREATE INDEX idx_goods_class_no ON goods_class_art(goods_class_no)')
    cursor.execute('CREATE INDEX idx_goods_name ON goods_class_art(goods_name)')
    cursor.execute('CREATE INDEX idx_similar_group ON goods_class_art(similar_group_cd)')
    cursor.execute('CREATE INDEX idx_right_person_name ON right_person_art_t(right_person_name)')
    
    # Create unified view
    cursor.execute('''
        CREATE VIEW IF NOT EXISTS unified_trademark_search AS
        SELECT 
            'domestic' as source_type,
            j.app_num,
            j.app_date,
            j.app_name as mark_text,
            j.reg_num,
            j.reg_date,
            rp.right_person_name as applicant_name,
            GROUP_CONCAT(DISTINCT g.goods_class_no) as class_numbers,
            GROUP_CONCAT(DISTINCT g.goods_name, '; ') as goods_services
        FROM jiken_c_t j
        LEFT JOIN right_person_art_t rp ON j.app_num = rp.app_num
        LEFT JOIN goods_class_art g ON j.app_num = g.app_num
        GROUP BY j.app_num
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"Test database created successfully at: {db_path}")
    print(f"Database size: {os.path.getsize(db_path) / 1024:.2f} KB")
    
    # Verify the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM jiken_c_t")
    count = cursor.fetchone()[0]
    print(f"Total test trademarks: {count}")
    
    cursor.execute("SELECT COUNT(*) FROM goods_class_art")
    count = cursor.fetchone()[0]
    print(f"Total goods/services entries: {count}")
    
    conn.close()
    
    return db_path

if __name__ == '__main__':
    # Allow custom path from command line
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'test_data/test_ci.db'
    create_test_database(db_path)
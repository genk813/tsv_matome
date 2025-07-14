#!/usr/bin/env python3
"""
データベースの実際のスキーマを確認
"""

import sqlite3
import json

def analyze_database():
    """データベースの構造を分析"""
    
    db_path = 'output.db'
    
    try:
        conn = sqlite3.connect(db_path)
        
        print("=== Database Analysis ===")
        
        # 全てのテーブル一覧
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
        
        print(f"\nFound {len(tables)} tables:")
        
        table_info = {}
        
        for (table,) in tables:
            print(f"\nTable: {table}")
            
            # テーブル情報を取得
            columns = conn.execute(f"PRAGMA table_info({table})").fetchall()
            row_count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            
            print(f"  Rows: {row_count}")
            print("  Columns:")
            
            column_info = []
            for col in columns:
                cid, name, type_, notnull, default, pk = col
                print(f"    {name} ({type_})")
                column_info.append({
                    'name': name,
                    'type': type_,
                    'notnull': bool(notnull),
                    'default': default,
                    'primary_key': bool(pk)
                })
            
            table_info[table] = {
                'row_count': row_count,
                'columns': column_info
            }
            
            # サンプルデータを少し表示
            if row_count > 0:
                sample = conn.execute(f"SELECT * FROM {table} LIMIT 2").fetchall()
                if sample:
                    print("  Sample data:")
                    for row in sample[:1]:  # 最初の1行だけ
                        sample_data = {}
                        for i, col_info in enumerate(column_info):
                            if i < len(row):
                                sample_data[col_info['name']] = str(row[i])[:50]  # 長すぎる場合は切り捨て
                        print(f"    {sample_data}")
        
        # 結果をJSONファイルに保存
        with open('database_schema_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(table_info, f, indent=2, ensure_ascii=False)
        
        print(f"\n=== Schema saved to database_schema_analysis.json ===")
        
        # 主要テーブルの確認
        main_tables = ['jiken_c_t', 'standard_char_t_art', 'goods_class_art', 't_sample']
        print("\n=== Main Tables Check ===")
        
        for table in main_tables:
            if table in [t[0] for t in tables]:
                cols = [col[1] for col in conn.execute(f"PRAGMA table_info({table})").fetchall()]
                print(f"{table}: {', '.join(cols[:5])}{'...' if len(cols) > 5 else ''}")
            else:
                print(f"{table}: NOT FOUND")
        
        conn.close()
        return table_info
        
    except Exception as e:
        print(f"Error analyzing database: {e}")
        return None

if __name__ == "__main__":
    analyze_database()
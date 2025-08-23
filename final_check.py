#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
出願番号2024061720の商標タイプ関連情報を取得
最終確認スクリプト
"""

import sqlite3
import sys
import os
from pathlib import Path

def main():
    # データベースファイル
    db_path = "C:/Users/ygenk/Desktop/TMCloud/tmcloud_v2_20250818_081655.db"
    
    # データベースファイルの存在確認
    if not os.path.exists(db_path):
        print(f"エラー: データベースファイルが見つかりません: {db_path}")
        return
    
    try:
        # データベースに接続
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 出願番号
        app_num = "2024061720"
        
        print(f"=== 出願番号 {app_num} の商標タイプ関連情報 ===\n")
        
        # 1. データベース内のテーブル一覧を確認
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = cursor.fetchall()
        print("データベース内のテーブル一覧:")
        for table in tables[:10]:  # 最初の10個だけ表示
            print(f"  - {table[0]}")
        if len(tables) > 10:
            print(f"  ... その他 {len(tables)-10} テーブル")
        print()
        
        # 2. trademark_case_infoテーブルの存在確認とカラム構造確認
        try:
            cursor.execute("PRAGMA table_info(trademark_case_info);")
            columns = cursor.fetchall()
            if columns:
                print("trademark_case_info テーブルのカラム構造:")
                target_columns = []
                for col in columns:
                    col_name = col[1]
                    if any(keyword in col_name.lower() for keyword in ['trademark', 'type', 'flag', 'standard', 'special', 'dimensional']):
                        target_columns.append(col_name)
                        print(f"  * {col_name}: {col[2]}")
                print()
                
                # 3. 出願番号2024061720のデータ取得
                if target_columns:
                    select_columns = ', '.join(target_columns)
                    query = f"SELECT app_num, {select_columns} FROM trademark_case_info WHERE app_num = ?"
                else:
                    query = "SELECT * FROM trademark_case_info WHERE app_num = ? LIMIT 1"
                
                cursor.execute(query, (app_num,))
                result = cursor.fetchone()
                
                if result:
                    print(f"出願番号 {app_num} の検索結果:")
                    print("-" * 50)
                    for key in result.keys():
                        value = result[key]
                        if value is not None and value != "":
                            print(f"{key}: {value}")
                        else:
                            print(f"{key}: (空/NULL)")
                    print()
                else:
                    print(f"出願番号 {app_num} はtrademark_case_infoテーブルに見つかりません\n")
            else:
                print("trademark_case_infoテーブルが見つかりません\n")
        
        except sqlite3.Error as e:
            print(f"trademark_case_infoテーブル確認エラー: {e}\n")
        
        # 4. trademark_basic_itemsテーブルも確認してみる
        try:
            cursor.execute("PRAGMA table_info(trademark_basic_items);")
            columns = cursor.fetchall()
            if columns:
                print("trademark_basic_items テーブルも存在します")
                cursor.execute("SELECT * FROM trademark_basic_items WHERE app_num = ? LIMIT 1", (app_num,))
                result = cursor.fetchone()
                if result:
                    print("trademark_basic_itemsから該当データ:")
                    for key in result.keys():
                        value = result[key]
                        if 'type' in key.lower() or 'flag' in key.lower():
                            print(f"  {key}: {value}")
            else:
                print("trademark_basic_itemsテーブルは存在しません")
        
        except sqlite3.Error:
            print("trademark_basic_itemsテーブル確認をスキップします")
        
        # 5. 類似の出願番号を検索
        print(f"\n2024年の出願番号のサンプル:")
        cursor.execute("SELECT app_num FROM trademark_case_info WHERE app_num LIKE '2024%' ORDER BY app_num LIMIT 5")
        similar_apps = cursor.fetchall()
        for app in similar_apps:
            print(f"  - {app[0]}")
        
        # 6. データベース統計
        cursor.execute("SELECT COUNT(*) FROM trademark_case_info")
        total_count = cursor.fetchone()[0]
        print(f"\n総レコード数: {total_count:,}")
        
    except sqlite3.Error as e:
        print(f"SQLiteエラー: {e}")
    except Exception as e:
        print(f"予期しないエラー: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
    
    print("\n=== 完了 ===")

if __name__ == "__main__":
    main()
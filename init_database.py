#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
データベース初期化スクリプト
output.dbのテーブル構造を作成し、インデックスを設定します。
"""

import sqlite3
import os
from pathlib import Path

def create_database(force=False):
    """データベースとテーブルを作成"""
    
    # データベースファイルのパス
    db_path = Path(__file__).parent / "output.db"
    schema_path = Path(__file__).parent / "create_schema.sql"
    
    print(f"データベースファイル: {db_path}")
    print(f"スキーマファイル: {schema_path}")
    
    # 既存のデータベースファイルを確認
    if db_path.exists():
        if not force:
            try:
                response = input("既存のデータベースファイルが存在します。上書きしますか？ (y/N): ")
                if response.lower() != 'y':
                    print("処理を中止しました。")
                    return False
            except EOFError:
                # 非対話環境では強制的に上書き
                print("非対話環境を検出しました。既存のデータベースを上書きします。")
        
        # 既存のファイルを削除
        os.remove(db_path)
        print("既存のデータベースファイルを削除しました。")
    
    # スキーマファイルの存在確認
    if not schema_path.exists():
        print(f"エラー: スキーマファイルが見つかりません: {schema_path}")
        return False
    
    try:
        # データベース接続
        conn = sqlite3.connect(db_path)
        print("データベースに接続しました。")
        
        # スキーマファイルを読み込んで実行
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        conn.executescript(schema_sql)
        print("データベーススキーマを作成しました。")
        
        # テーブル一覧を確認
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"作成されたテーブル数: {len(tables)}")
        for table in tables:
            print(f"  - {table[0]}")
        
        # インデックス一覧を確認
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'")
        indexes = cursor.fetchall()
        
        print(f"作成されたインデックス数: {len(indexes)}")
        for index in indexes[:5]:  # 最初の5個のみ表示
            print(f"  - {index[0]}")
        if len(indexes) > 5:
            print(f"  ... 他 {len(indexes) - 5} 個")
        
        conn.close()
        print("データベースの初期化が完了しました。")
        
        return True
        
    except Exception as e:
        print(f"エラー: {e}")
        return False

def test_database():
    """データベースの動作テスト"""
    
    db_path = Path(__file__).parent / "output.db"
    
    if not db_path.exists():
        print("データベースファイルが存在しません。")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 各テーブルのレコード数を確認
        tables = [
            'jiken_c_t',
            'standard_char_t_art',
            'goods_class_art',
            'jiken_c_t_shohin_joho',
            't_knd_info_art_table',
            'reg_mapping',
            'right_person_art_t',
            't_dsgnt_art',
            't_sample'
        ]
        
        print("テーブル別レコード数:")
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  {table}: {count} レコード")
            except Exception as e:
                print(f"  {table}: エラー - {e}")
        
        conn.close()
        print("データベーステストが完了しました。")
        
        return True
        
    except Exception as e:
        print(f"エラー: {e}")
        return False

if __name__ == "__main__":
    print("=== データベース初期化スクリプト ===")
    print()
    
    # コマンドライン引数をチェック
    import sys
    force = '--force' in sys.argv
    
    if create_database(force=force):
        print()
        print("=== データベーステスト ===")
        test_database()
        
        print()
        print("次のステップ:")
        print("1. TSVファイルをインポートしてデータを投入する")
        print("2. アプリケーションを起動する: python app_dynamic_join_claude_optimized.py")
        print("3. ブラウザで http://localhost:5002 にアクセスする")
    else:
        print("データベースの初期化に失敗しました。")
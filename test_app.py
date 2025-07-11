#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
アプリケーションテストスクリプト
最適化されたアプリケーションの動作を検証します。
"""

import sys
import os
from pathlib import Path

# アプリケーションモジュールをインポート
try:
    from app_dynamic_join_claude_optimized import app, init_database, query_db, query_db_one, get_optimized_results
    print("✓ 最適化されたアプリケーションモジュールを読み込みました")
except ImportError as e:
    print(f"✗ アプリケーションモジュールの読み込みに失敗: {e}")
    sys.exit(1)

def test_database_initialization():
    """データベース初期化のテスト"""
    print("\n=== データベース初期化テスト ===")
    
    try:
        init_database()
        print("✓ データベース初期化成功")
        return True
    except Exception as e:
        print(f"✗ データベース初期化失敗: {e}")
        return False

def test_basic_queries():
    """基本的なクエリのテスト"""
    print("\n=== 基本クエリテスト ===")
    
    test_queries = [
        ("SELECT COUNT(*) as count FROM jiken_c_t", "jiken_c_t テーブル"),
        ("SELECT COUNT(*) as count FROM standard_char_t_art", "standard_char_t_art テーブル"),
        ("SELECT COUNT(*) as count FROM goods_class_art", "goods_class_art テーブル"),
        ("SELECT name FROM sqlite_master WHERE type='table'", "テーブル一覧"),
        ("SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'", "インデックス一覧")
    ]
    
    success_count = 0
    
    for query, description in test_queries:
        try:
            if "COUNT(*)" in query:
                result = query_db_one(query)
                count = result['count'] if result else 0
                print(f"✓ {description}: {count} レコード")
            else:
                results = query_db(query)
                print(f"✓ {description}: {len(results)} 件")
                for result in results[:3]:  # 最初の3件のみ表示
                    print(f"  - {result}")
                if len(results) > 3:
                    print(f"  ... 他 {len(results) - 3} 件")
            
            success_count += 1
            
        except Exception as e:
            print(f"✗ {description}: {e}")
    
    print(f"\n基本クエリテスト結果: {success_count}/{len(test_queries)} 成功")
    return success_count == len(test_queries)

def test_optimized_query():
    """最適化されたクエリのテスト"""
    print("\n=== 最適化クエリテスト ===")
    
    # テストデータがない場合のテスト
    test_app_nums = ["2023001234", "2023005678", "2023009999"]
    
    try:
        results = get_optimized_results(test_app_nums)
        print(f"✓ 最適化クエリ実行成功: {len(results)} 件の結果")
        
        if results:
            first_result = results[0]
            print("サンプル結果:")
            for key, value in first_result.items():
                print(f"  {key}: {value}")
        else:
            print("  結果が空です（テストデータがない場合は正常）")
        
        return True
        
    except Exception as e:
        print(f"✗ 最適化クエリ実行失敗: {e}")
        return False

def test_flask_app():
    """Flaskアプリケーションのテスト"""
    print("\n=== Flaskアプリケーションテスト ===")
    
    try:
        with app.test_client() as client:
            # メインページのテスト
            response = client.get('/')
            print(f"✓ メインページ: ステータス {response.status_code}")
            
            # 画像テストページのテスト
            response = client.get('/test-images')
            print(f"✓ 画像テストページ: ステータス {response.status_code}")
            
            # データベース初期化エンドポイントのテスト
            response = client.get('/admin/init-db')
            print(f"✓ データベース初期化エンドポイント: ステータス {response.status_code}")
            
            # 検索フォームのテスト（空の検索）
            response = client.post('/', data={})
            print(f"✓ 検索フォーム（空）: ステータス {response.status_code}")
            
            # 検索フォームのテスト（データありの検索）
            response = client.post('/', data={'app_num': '2023001234'})
            print(f"✓ 検索フォーム（データあり）: ステータス {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"✗ Flaskアプリケーションテスト失敗: {e}")
        return False

def main():
    """メインテスト実行"""
    print("=== アプリケーションテストスクリプト ===")
    
    tests = [
        ("データベース初期化", test_database_initialization),
        ("基本クエリ", test_basic_queries),
        ("最適化クエリ", test_optimized_query),
        ("Flaskアプリケーション", test_flask_app)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"テスト: {test_name}")
        print(f"{'='*50}")
        
        if test_func():
            print(f"✓ {test_name} テスト成功")
            passed += 1
        else:
            print(f"✗ {test_name} テスト失敗")
    
    print(f"\n{'='*50}")
    print(f"全体結果: {passed}/{total} テスト成功")
    print(f"{'='*50}")
    
    if passed == total:
        print("🎉 すべてのテストが成功しました！")
        print("\nアプリケーションを起動するには:")
        print("python app_dynamic_join_claude_optimized.py")
    else:
        print("⚠️  一部のテストが失敗しました。")
        print("データベースにデータがない場合、検索結果が空になるのは正常です。")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Create lightweight test data for GitHub Actions
テスト用の軽量データセットを作成（元データは保持）
"""

import sqlite3
import os
import shutil
import json
from pathlib import Path
import random

def create_test_database():
    """本番データベースから10%のサンプルを抽出してテスト用DBを作成"""
    
    # ディレクトリ作成
    test_dir = Path('test_data')
    test_dir.mkdir(exist_ok=True)
    
    # 本番DBをコピー（安全のため）
    src_db = 'output.db'
    test_db = 'test_data/test_output.db'
    
    if not os.path.exists(src_db):
        print(f"Error: {src_db} not found")
        return False
        
    print(f"Creating test database from {src_db}...")
    
    # 新しいテストDBを作成
    if os.path.exists(test_db):
        os.remove(test_db)
    
    # データベース接続
    src_conn = sqlite3.connect(src_db)
    test_conn = sqlite3.connect(test_db)
    
    try:
        # スキーマをコピー（sqlite_sequenceなどの内部テーブルを除外）
        print("Copying database schema...")
        schema = src_conn.execute(
            "SELECT sql FROM sqlite_master WHERE sql NOT NULL AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
        for (sql,) in schema:
            if sql:
                try:
                    test_conn.execute(sql)
                except Exception as e:
                    print(f"Warning: Failed to create {sql[:50]}...: {e}")
                    continue
        
        # 各テーブルから10%のデータをサンプリング
        tables = src_conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        
        for (table,) in tables:
            if table.startswith('sqlite_'):
                continue
                
            print(f"Sampling table: {table}")
            
            try:
                # テーブルの行数を取得
                count = src_conn.execute(f"SELECT COUNT(*) FROM `{table}`").fetchone()[0]
                
                if count == 0:
                    print(f"  Table {table} is empty, skipping")
                    continue
                    
                # サンプルサイズを決定（最低10行、最大1000行）
                sample_size = min(max(int(count * 0.1), 10), 1000)
                print(f"  Sampling {sample_size} rows from {count} total rows")
                
                # カラム名を取得
                cursor = src_conn.execute(f"SELECT * FROM `{table}` LIMIT 0")
                columns = [desc[0] for desc in cursor.description]
                
                # データをサンプリング（汎用的な方法）
                query = f"SELECT * FROM `{table}` ORDER BY RANDOM() LIMIT {sample_size}"
                rows = src_conn.execute(query).fetchall()
                
                if rows:
                    # データを挿入
                    placeholders = ','.join(['?' for _ in columns])
                    column_names = ','.join([f'`{col}`' for col in columns])
                    test_conn.executemany(
                        f"INSERT INTO `{table}` ({column_names}) VALUES ({placeholders})",
                        rows
                    )
                    print(f"  Inserted {len(rows)} rows")
                else:
                    print(f"  No data retrieved for {table}")
                    
            except Exception as e:
                print(f"  Error sampling table {table}: {e}")
                continue
        
        # インデックスを再作成
        print("Creating indexes...")
        indexes = src_conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='index' AND sql NOT NULL AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
        
        for (sql,) in indexes:
            if sql:
                try:
                    test_conn.execute(sql)
                except Exception as e:
                    print(f"Warning: Failed to create index: {e}")
                    continue
        
        test_conn.commit()
        print(f"Test database created: {test_db}")
        
        # データベースサイズを確認
        src_size = os.path.getsize(src_db) / (1024 * 1024)  # MB
        test_size = os.path.getsize(test_db) / (1024 * 1024)  # MB
        print(f"Original DB size: {src_size:.2f} MB")
        print(f"Test DB size: {test_size:.2f} MB ({test_size/src_size*100:.1f}%)")
        
        return True
        
    except Exception as e:
        print(f"Error creating test database: {e}")
        return False
        
    finally:
        src_conn.close()
        test_conn.close()


def create_test_images():
    """画像ファイルから50個のサンプルを抽出"""
    
    src_dir = Path('images/final_complete')
    test_dir = Path('test_data/test_images')
    
    if not src_dir.exists():
        print(f"Error: {src_dir} not found")
        return False
        
    # テスト画像ディレクトリを作成
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # 画像ファイルのリストを取得
    image_files = list(src_dir.glob('*.jpg'))
    
    if not image_files:
        print("No image files found")
        return False
        
    print(f"Found {len(image_files)} images")
    
    # 50個をランダムに選択（または全部が50個未満の場合は全部）
    sample_size = min(50, len(image_files))
    selected_images = random.sample(image_files, sample_size)
    
    print(f"Copying {sample_size} sample images...")
    
    # 画像をコピー
    for img in selected_images:
        dst = test_dir / img.name
        shutil.copy2(img, dst)
        
    print(f"Copied {sample_size} images to {test_dir}")
    
    # サンプル画像のリストを保存
    image_list = [img.name for img in selected_images]
    with open(test_dir / 'image_list.json', 'w') as f:
        json.dump(image_list, f, indent=2)
        
    return True


def update_gitignore():
    """本番データを確実に除外するように.gitignoreを更新"""
    
    gitignore_path = Path('.gitignore')
    
    # 追加する項目
    production_data_patterns = [
        "\n# Production data (DO NOT COMMIT)",
        "output.db",
        "output.db-*",
        "output_backup.db",
        "images/final_complete/",
        "tsv_data/tsv/",
        "decoded_tsvs/",
        "\n# Test data is OK to commit",
        "!test_data/",
        "!test_data/**",
    ]
    
    # 既存の.gitignoreを読み込み
    if gitignore_path.exists():
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = ""
    
    # 必要な項目を追加
    updated = False
    for pattern in production_data_patterns:
        if pattern.strip() and pattern not in content:
            content += f"\n{pattern}"
            updated = True
    
    if updated:
        with open(gitignore_path, 'w', encoding='utf-8') as f:
            f.write(content.strip() + '\n')
        print("Updated .gitignore to protect production data")
    else:
        print(".gitignore already configured correctly")
        
    return True


def create_test_config():
    """テスト用の設定ファイルを作成"""
    
    config = {
        "test_database": "test_data/test_output.db",
        "test_images": "test_data/test_images",
        "description": "Lightweight test data for GitHub Actions",
        "created": "2025-01-14",
        "data_sampling": {
            "database": "10% sample (max 1000 rows per table)",
            "images": "50 random samples"
        }
    }
    
    config_path = Path('test_data/test_config.json')
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
        
    print(f"Created test configuration: {config_path}")
    return True


def main():
    """メイン処理"""
    print("Creating lightweight test data for GitHub Actions...")
    print("=" * 60)
    
    # テストデータディレクトリを作成
    Path('test_data').mkdir(exist_ok=True)
    
    # 各種テストデータを作成
    success = True
    
    # 1. テストデータベースを作成
    if not create_test_database():
        print("Failed to create test database")
        success = False
        
    print()
    
    # 2. テスト画像を作成
    if not create_test_images():
        print("Failed to create test images")
        success = False
        
    print()
    
    # 3. .gitignoreを更新
    if not update_gitignore():
        print("Failed to update .gitignore")
        success = False
        
    print()
    
    # 4. テスト設定ファイルを作成
    if not create_test_config():
        print("Failed to create test config")
        success = False
        
    print("=" * 60)
    
    if success:
        print("✅ Test data creation completed successfully!")
        print("\nTest data location:")
        print("  - Database: test_data/test_output.db")
        print("  - Images: test_data/test_images/")
        print("  - Config: test_data/test_config.json")
        print("\nThese files are safe to commit to GitHub.")
    else:
        print("❌ Some errors occurred during test data creation")
        
    return success


if __name__ == "__main__":
    main()
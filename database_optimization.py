#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
データベース最適化ツール
パフォーマンス問題とデータ整合性問題を解決
"""

import sqlite3
import time
from pathlib import Path
from typing import List, Dict, Any

class DatabaseOptimizer:
    """データベース最適化クラス"""
    
    def __init__(self, db_path: str = "output.db"):
        self.db_path = Path(db_path)
        
    def get_connection(self):
        """データベース接続を取得"""
        conn = sqlite3.connect(self.db_path)
        return conn
    
    def analyze_current_state(self):
        """現状分析"""
        print("🔍 データベース現状分析開始")
        print("=" * 60)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # テーブル一覧と行数
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = cursor.fetchall()
        
        print("\n📊 テーブル一覧と行数:")
        total_rows = 0
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            total_rows += count
            print(f"  {table[0]:25}: {count:,}行")
        
        print(f"\n総行数: {total_rows:,}行")
        
        # インデックス一覧
        cursor.execute("SELECT name, tbl_name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'")
        indexes = cursor.fetchall()
        print(f"\n🗂️ 既存インデックス数: {len(indexes)}")
        
        # データベースサイズ
        cursor.execute("PRAGMA page_count")
        page_count = cursor.fetchone()[0]
        cursor.execute("PRAGMA page_size") 
        page_size = cursor.fetchone()[0]
        db_size_mb = (page_count * page_size) / (1024 * 1024)
        print(f"📦 データベースサイズ: {db_size_mb:.1f}MB")
        
        conn.close()
    
    def fix_p1_missing_indexes(self):
        """P1: 不足インデックスを追加"""
        print("\n🔧 P1: 重要インデックスの追加")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 追加すべきインデックス
        new_indexes = [
            # Enhanced テーブルの主要列
            "CREATE INDEX IF NOT EXISTS idx_t_basic_enhanced_app_num ON t_basic_item_enhanced(app_num)",
            "CREATE INDEX IF NOT EXISTS idx_mgt_info_enhanced_app_num ON mgt_info_enhanced(app_num)",
            "CREATE INDEX IF NOT EXISTS idx_add_info_enhanced_app_num ON add_info_enhanced(app_num)",
            
            # 日付範囲検索用
            "CREATE INDEX IF NOT EXISTS idx_t_basic_enhanced_expire_dt ON t_basic_item_enhanced(conti_prd_expire_dt)",
            "CREATE INDEX IF NOT EXISTS idx_t_basic_enhanced_app_dt ON t_basic_item_enhanced(app_dt)",
            
            # 複合インデックス（よく一緒に使われる列）
            "CREATE INDEX IF NOT EXISTS idx_jiken_enhanced_app_reg ON jiken_c_t_enhanced(normalized_app_num, raz_toroku_no)",
            "CREATE INDEX IF NOT EXISTS idx_reg_mapping_composite ON reg_mapping(app_num, reg_num)",
            
            # 検索用インデックス
            "CREATE INDEX IF NOT EXISTS idx_right_person_name ON right_person_art_t(right_person_name)",
            "CREATE INDEX IF NOT EXISTS idx_applicant_master_cd ON applicant_master(appl_cd)",
        ]
        
        created_count = 0
        for index_sql in new_indexes:
            try:
                start_time = time.time()
                cursor.execute(index_sql)
                elapsed = time.time() - start_time
                index_name = index_sql.split()[5]  # Extract index name
                print(f"  ✅ {index_name}: {elapsed:.2f}秒")
                created_count += 1
            except Exception as e:
                print(f"  ❌ インデックス作成エラー: {e}")
        
        conn.commit()
        conn.close()
        print(f"📈 新規インデックス作成完了: {created_count}個")
    
    def fix_p2_column_naming(self):
        """P2: 列名統一（app_num → normalized_app_num）"""
        print("\n🔧 P2: 列名統一修正")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Enhanced テーブルの列名を統一
        tables_to_fix = [
            't_basic_item_enhanced',
            'mgt_info_enhanced', 
            'add_info_enhanced'
        ]
        
        fixed_count = 0
        for table in tables_to_fix:
            try:
                # テーブル構造を確認
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                
                # app_num列があるかチェック
                has_app_num = any(col[1] == 'app_num' for col in columns)
                
                if has_app_num:
                    print(f"  🔄 {table} の app_num → normalized_app_num")
                    
                    # 新しいテーブルを作成（列名変更）
                    column_defs = []
                    for col in columns:
                        col_name = col[1]
                        if col_name == 'app_num':
                            col_name = 'normalized_app_num'
                        column_defs.append(f"{col_name} {col[2]}")
                    
                    create_sql = f"CREATE TABLE {table}_new ({', '.join(column_defs)})"
                    cursor.execute(create_sql)
                    
                    # データをコピー
                    old_columns = [col[1] for col in columns]
                    new_columns = ['normalized_app_num' if col == 'app_num' else col for col in old_columns]
                    
                    copy_sql = f"""
                        INSERT INTO {table}_new ({', '.join(new_columns)})
                        SELECT {', '.join(old_columns)} FROM {table}
                    """
                    cursor.execute(copy_sql)
                    
                    # テーブルを置き換え
                    cursor.execute(f"DROP TABLE {table}")
                    cursor.execute(f"ALTER TABLE {table}_new RENAME TO {table}")
                    
                    fixed_count += 1
                    print(f"    ✅ 完了")
                else:
                    print(f"  ⏭️ {table}: すでに正しい列名")
                    
            except Exception as e:
                print(f"  ❌ {table} 修正エラー: {e}")
        
        conn.commit()
        conn.close()
        print(f"📝 列名統一完了: {fixed_count}テーブル")
    
    def fix_p5_duplicate_records(self):
        """P5: 重複レコードの除去"""
        print("\n🔧 P5: 重複レコード除去")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 重複があるテーブルを特定
        tables_to_check = [
            'standard_char_t_art',
            'indct_use_t_art', 
            'search_use_t_art_table',
            't_dsgnt_art'
        ]
        
        removed_count = 0
        for table in tables_to_check:
            try:
                # 重複を確認
                cursor.execute(f"""
                    SELECT normalized_app_num, COUNT(*) as cnt
                    FROM {table}
                    GROUP BY normalized_app_num
                    HAVING COUNT(*) > 1
                """)
                duplicates = cursor.fetchall()
                
                if duplicates:
                    print(f"  🔍 {table}: {len(duplicates)}個の重複グループ")
                    
                    # 重複を除去（ROWIDが最小のものを残す）
                    cursor.execute(f"""
                        DELETE FROM {table}
                        WHERE ROWID NOT IN (
                            SELECT MIN(ROWID)
                            FROM {table}
                            GROUP BY normalized_app_num
                        )
                    """)
                    
                    deleted = cursor.rowcount
                    removed_count += deleted
                    print(f"    ✅ {deleted}行削除")
                else:
                    print(f"  ⏭️ {table}: 重複なし")
                    
            except Exception as e:
                print(f"  ❌ {table} 重複除去エラー: {e}")
        
        conn.commit()
        conn.close()
        print(f"🗑️ 重複レコード除去完了: {removed_count}行")
    
    def fix_p4_normalize_goods_classes(self):
        """P4: 商品区分の正規化（参考実装）"""
        print("\n🔧 P4: 商品区分正規化の準備")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 現在の多値状況を分析
        cursor.execute("""
            SELECT goods_classes, COUNT(*) as cnt
            FROM goods_class_art
            WHERE goods_classes LIKE '%,%' OR goods_classes LIKE '%;%'
            GROUP BY goods_classes
            LIMIT 5
        """)
        multi_values = cursor.fetchall()
        
        if multi_values:
            print("  📊 多値データの例:")
            for mv in multi_values:
                print(f"    '{mv[0]}': {mv[1]}件")
            print("  💡 注意: 商品区分の正規化は影響範囲が大きいため、別途検討が必要")
        else:
            print("  ✅ 商品区分データは既に正規化済み")
        
        conn.close()
    
    def verify_optimizations(self):
        """最適化後の検証"""
        print("\n🔍 最適化効果の検証")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # インデックス数の確認
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'")
        index_count = cursor.fetchone()[0]
        print(f"📊 総インデックス数: {index_count}")
        
        # パフォーマンステスト
        test_queries = [
            ("基本検索", "SELECT COUNT(*) FROM t_basic_item_enhanced WHERE normalized_app_num = '2020138119'"),
            ("日付範囲検索", "SELECT COUNT(*) FROM t_basic_item_enhanced WHERE conti_prd_expire_dt BETWEEN '20250101' AND '20351231'"),
            ("複合検索", "SELECT COUNT(*) FROM jiken_c_t_enhanced je JOIN t_basic_item_enhanced tbi ON je.normalized_app_num = tbi.normalized_app_num WHERE je.raz_toroku_no IS NOT NULL"),
        ]
        
        for test_name, query in test_queries:
            start_time = time.time()
            try:
                cursor.execute(query)
                result = cursor.fetchone()[0]
                elapsed = time.time() - start_time
                print(f"  ⏱️ {test_name}: {elapsed:.3f}秒 (結果: {result:,}件)")
            except Exception as e:
                print(f"  ❌ {test_name}: エラー - {e}")
        
        # 重複チェック
        cursor.execute("""
            SELECT COUNT(*)
            FROM (
                SELECT normalized_app_num, COUNT(*) as cnt
                FROM standard_char_t_art
                GROUP BY normalized_app_num
                HAVING COUNT(*) > 1
            )
        """)
        remaining_duplicates = cursor.fetchone()[0]
        print(f"🔍 残存重複グループ: {remaining_duplicates}")
        
        conn.close()
    
    def run_optimization(self):
        """最適化の実行"""
        print("🚀 データベース最適化開始")
        print("=" * 60)
        
        self.analyze_current_state()
        
        # 優先度順に実行
        self.fix_p1_missing_indexes()
        self.fix_p2_column_naming() 
        self.fix_p5_duplicate_records()
        self.fix_p4_normalize_goods_classes()
        
        # VACUUM でデータベースを最適化
        print("\n🔧 データベースVACUUM実行中...")
        conn = self.get_connection()
        conn.execute("VACUUM")
        conn.close()
        print("✅ VACUUM完了")
        
        self.verify_optimizations()
        
        print("\n🎉 データベース最適化完了!")

def main():
    """メイン実行"""
    optimizer = DatabaseOptimizer()
    optimizer.run_optimization()

if __name__ == "__main__":
    main()
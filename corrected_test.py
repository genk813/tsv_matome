#!/usr/bin/env python3
"""
修正版：正しいフィールド名を使った立体商標判定テスト
"""

import sqlite3
import os

def test_3d_trademark():
    """立体商標のテストを実行（修正版）"""
    
    # データベースファイル候補
    db_candidates = [
        r"C:\Users\ygenk\Desktop\TMCloud\tmcloud_v2_20250818_081655.db",
        r"C:\Users\ygenk\Desktop\TMCloud\tmcloud_v2_20250805_232509.db"
    ]
    
    db_path = None
    for db in db_candidates:
        if os.path.exists(db):
            db_path = db
            print(f"データベース発見: {os.path.basename(db)}")
            break
    
    if not db_path:
        print("エラー: データベースが見つかりません")
        return False
    
    try:
        # データベース接続
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print("\n=== 出願番号2024061720のデータ確認（修正版） ===")
        
        # 正しいフィールド名を使用
        cursor.execute("""
            SELECT 
                app_num,
                standard_char_exist,
                special_mark_exist
            FROM trademark_case_info
            WHERE app_num = '2024061720'
        """)
        
        row = cursor.fetchone()
        if row:
            print(f"出願番号: {row['app_num']}")
            print(f"標準文字存在: {row['standard_char_exist']}")
            print(f"特殊商標識別: {row['special_mark_exist']}")
            
            # 立体商標判定（special_mark_exist=1なら立体商標等）
            if row['special_mark_exist'] == '1':
                print("\n✅ 結果: 立体商標として正しく判定されました")
                print("理由: special_mark_exist = '1' (特殊商標識別フラグ)")
                result = "SUCCESS"
            else:
                print("\n❌ 結果: 立体商標として判定されませんでした")
                print(f"理由: special_mark_exist = '{row['special_mark_exist']}'")
                result = "FAILED"
        else:
            print("❌ エラー: データが見つかりません")
            result = "NOT_FOUND"
        
        conn.close()
        
        # 結果をファイルに保存
        result_file = r"C:\Users\ygenk\Desktop\TMCloud\corrected_test_result.txt"
        with open(result_file, "w", encoding="utf-8") as f:
            f.write("=== 立体商標判定テスト結果（修正版） ===\n")
            f.write(f"データベース: {os.path.basename(db_path)}\n")
            f.write(f"出願番号: 2024061720\n")
            if row:
                f.write(f"標準文字存在: {row['standard_char_exist']}\n")
                f.write(f"特殊商標識別: {row['special_mark_exist']}\n")
            f.write(f"判定結果: {result}\n")
            if result == "SUCCESS":
                f.write("判定理由: special_mark_exist = '1' (立体商標等として識別)\n")
            elif result == "FAILED":
                f.write(f"判定理由: special_mark_exist = '{row['special_mark_exist'] if row else 'N/A'}'\n")
        
        print(f"結果を保存: {os.path.basename(result_file)}")
        return result == "SUCCESS"
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        return False

if __name__ == "__main__":
    print("TMCloud 立体商標判定テスト (修正版)")
    print("=" * 50)
    
    success = test_3d_trademark()
    
    print("\n" + "=" * 50)
    print(f"テスト完了: {'成功' if success else '失敗'}")
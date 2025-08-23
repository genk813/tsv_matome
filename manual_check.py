#!/usr/bin/env python3
"""
手動でデータベース確認し、結果をファイルに保存
"""

# 必要なモジュールをインポート
import sqlite3
import os
from pathlib import Path

# データベースファイルのパス候補
db_candidates = [
    Path(r"C:\Users\ygenk\Desktop\TMCloud\tmcloud_v2_20250818_081655.db"),
    Path(r"C:\Users\ygenk\Desktop\TMCloud\tmcloud_v2_20250805_232509.db")
]

result_lines = []
result_lines.append("=== TMCloud 立体商標判定テスト ===")

# データベースファイル確認
db_path = None
for db in db_candidates:
    result_lines.append(f"チェック中: {db.name}")
    if db.exists():
        db_path = db
        result_lines.append(f"✓ 発見: {db.name}")
        break
    else:
        result_lines.append(f"✗ 見つかりません: {db.name}")

if not db_path:
    result_lines.append("エラー: 利用可能なデータベースがありません")
    final_status = "ERROR_NO_DB"
else:
    try:
        # データベース接続
        result_lines.append(f"データベース接続: {db_path.name}")
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # 検索実行
        result_lines.append("出願番号2024061720を検索中...")
        cursor.execute("""
            SELECT 
                app_num,
                special_mark_type,
                dimensional_trademark_flag
            FROM trademark_case_info
            WHERE app_num = '2024061720'
        """)
        
        row = cursor.fetchone()
        
        if row:
            app_num, special_mark, dimensional_flag = row
            
            result_lines.append(f"出願番号: {app_num}")
            result_lines.append(f"特殊マーク種別: {special_mark}")
            result_lines.append(f"立体商標フラグ: {dimensional_flag}")
            
            # 立体商標判定
            is_3d_trademark = (special_mark == '1' or dimensional_flag == '1')
            
            if is_3d_trademark:
                result_lines.append("判定結果: ✓ 立体商標として正しく判定")
                if special_mark == '1':
                    result_lines.append("理由: special_mark_type = '1'")
                if dimensional_flag == '1':
                    result_lines.append("理由: dimensional_trademark_flag = '1'")
                final_status = "SUCCESS"
            else:
                result_lines.append("判定結果: ✗ 立体商標として判定されない")
                result_lines.append(f"詳細: special_mark={special_mark}, dimensional_flag={dimensional_flag}")
                final_status = "FAILED"
        else:
            result_lines.append("データが見つかりません")
            final_status = "NOT_FOUND"
        
        conn.close()
        
    except Exception as e:
        result_lines.append(f"エラー発生: {str(e)}")
        final_status = "ERROR"

# 結果をファイルに保存
result_lines.append(f"最終ステータス: {final_status}")

output_file = Path(r"C:\Users\ygenk\Desktop\TMCloud\manual_test_result.txt")
try:
    with open(output_file, "w", encoding="utf-8") as f:
        for line in result_lines:
            f.write(line + "\n")
    result_lines.append(f"結果保存完了: {output_file.name}")
except Exception as e:
    result_lines.append(f"ファイル保存エラー: {e}")

# コンソール出力
for line in result_lines:
    print(line)

print("テスト完了")
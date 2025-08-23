#!/usr/bin/env python3
"""
テスト実行と結果出力
"""
import subprocess
import sys
import os

# ディレクトリ移動
os.chdir(r"C:\Users\ygenk\Desktop\TMCloud")

# Pythonスクリプト実行
try:
    result = subprocess.run([
        sys.executable, 
        "direct_test_result.py"
    ], capture_output=True, text=True, encoding='utf-8')
    
    print("=== STDOUT ===")
    print(result.stdout)
    
    if result.stderr:
        print("=== STDERR ===")
        print(result.stderr)
    
    print(f"=== RETURN CODE: {result.returncode} ===")
    
    # 結果をファイルに保存
    with open("test_result.txt", "w", encoding='utf-8') as f:
        f.write(f"Return Code: {result.returncode}\n")
        f.write("STDOUT:\n")
        f.write(result.stdout)
        if result.stderr:
            f.write("\nSTDERR:\n")
            f.write(result.stderr)
    
    print("\n結果をtest_result.txtに保存しました")

except Exception as e:
    print(f"エラー: {e}")
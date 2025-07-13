#!/usr/bin/env python3
"""
包括的検索テスト - 様々なパターンでバグがないかを検証
"""
import subprocess
import sys
import time
import json

def run_search_test(test_name, command):
    """検索テストを実行"""
    print(f"\n{'='*60}")
    print(f"テスト: {test_name}")
    print(f"コマンド: {command}")
    print("-"*40)
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            # 結果から件数を抽出
            lines = result.stdout.strip().split('\n')
            result_line = next((line for line in lines if "検索結果:" in line), None)
            
            if result_line:
                print(f"✅ 成功 ({elapsed:.1f}秒)")
                print(f"   {result_line}")
                
                # 最初の結果を表示
                if "--- 結果 1 ---" in result.stdout:
                    first_result_start = result.stdout.index("--- 結果 1 ---")
                    first_result_end = result.stdout.find("\n--- 結果 2 ---", first_result_start)
                    if first_result_end == -1:
                        first_result_end = len(result.stdout)
                    first_result = result.stdout[first_result_start:first_result_end].strip()
                    print(f"\n   [最初の結果]")
                    for line in first_result.split('\n')[1:6]:  # 最初の5行
                        print(f"   {line}")
            else:
                print(f"⚠️ 結果形式エラー ({elapsed:.1f}秒)")
                print(f"   出力: {result.stdout[:200]}")
        else:
            print(f"❌ エラー ({elapsed:.1f}秒)")
            print(f"   エラー: {result.stderr[:200]}")
            
    except subprocess.TimeoutExpired:
        print(f"❌ タイムアウト (30秒)")
    except Exception as e:
        print(f"❌ 例外: {str(e)}")

def main():
    """様々なパターンでの包括的検索テスト"""
    
    print("🔍 TSV_MATOME 包括的検索テスト")
    print("="*60)
    
    tests = [
        # 1. 出願番号検索
        ("出願番号検索 - 完全一致", 
         'python3 cli_trademark_search.py --app-num "2020138119" --limit 5'),
        
        ("出願番号検索 - ハイフン付き",
         'python3 cli_trademark_search.py --app-num "2020-138119" --limit 5'),
        
        # 2. 商標テキスト検索
        ("商標検索 - 基本",
         'python3 cli_trademark_search.py --mark-text "アップル" --limit 3'),
        
        ("商標検索 - カタカナ",
         'python3 cli_trademark_search.py --mark-text "パナソニック" --limit 3'),
        
        ("商標検索 - ひらがな",
         'python3 cli_trademark_search.py --mark-text "さくら" --limit 3'),
        
        ("商標検索 - 英語",
         'python3 cli_trademark_search.py --mark-text "SONY" --limit 3'),
        
        ("商標検索 - 記号含む",
         'python3 cli_trademark_search.py --mark-text "＆" --limit 3'),
        
        # 3. 商品区分検索
        ("商品区分検索 - 単一",
         'python3 cli_trademark_search.py --goods-classes "09" --limit 3'),
        
        ("商品区分検索 - 複数",
         'python3 cli_trademark_search.py --goods-classes "09 42" --limit 3'),
        
        # 4. 類似群コード検索
        ("類似群コード検索 - 基本",
         'python3 cli_trademark_search.py --similar-group-codes "11C01" --limit 3'),
        
        ("類似群コード検索 - 複数",
         'python3 cli_trademark_search.py --similar-group-codes "11C01 09G55" --limit 3'),
        
        # 5. 指定商品検索
        ("指定商品検索 - 基本",
         'python3 cli_trademark_search.py --designated-goods "コンピュータ" --limit 3'),
        
        ("指定商品検索 - 複数キーワード",
         'python3 cli_trademark_search.py --designated-goods "電子 計算" --limit 3'),
        
        # 6. 複合検索
        ("複合検索 - 商標＋区分",
         'python3 cli_trademark_search.py --mark-text "東京" --goods-classes "43" --limit 3'),
        
        ("複合検索 - 商標＋類似群",
         'python3 cli_trademark_search.py --mark-text "電気" --similar-group-codes "11A01" --limit 3'),
        
        # 7. 国際商標検索
        ("国際商標検索 - 基本",
         'python3 cli_trademark_search.py --international --goods-classes "42" --limit 3'),
        
        ("国際商標検索 - 登録番号",
         'python3 cli_trademark_search.py --intl-reg-num "0489196" --limit 3'),
        
        # 8. エッジケース
        ("空文字検索防止テスト",
         'python3 cli_trademark_search.py --mark-text "" --limit 3'),
        
        ("特殊文字検索",
         'python3 cli_trademark_search.py --mark-text "™" --limit 3'),
        
        ("数字のみ検索",
         'python3 cli_trademark_search.py --mark-text "123" --limit 3'),
        
        # 9. 大量結果のページング
        ("ページング - オフセットなし",
         'python3 cli_trademark_search.py --goods-classes "35" --limit 5'),
        
        ("ページング - オフセット5",
         'python3 cli_trademark_search.py --goods-classes "35" --limit 5 --offset 5'),
    ]
    
    # テスト実行
    success_count = 0
    fail_count = 0
    timeout_count = 0
    
    for test_name, command in tests:
        try:
            run_search_test(test_name, command)
            
            # 結果を解析
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            if result.returncode == 0 and "検索結果:" in result.stdout:
                success_count += 1
            else:
                fail_count += 1
                
        except subprocess.TimeoutExpired:
            timeout_count += 1
        except:
            fail_count += 1
    
    # サマリー
    print("\n" + "="*60)
    print("📊 テスト結果サマリー")
    print("="*60)
    print(f"総テスト数: {len(tests)}")
    print(f"✅ 成功: {success_count}")
    print(f"❌ 失敗: {fail_count}")
    print(f"⏱️ タイムアウト: {timeout_count}")
    
    # 特定の問題チェック
    print("\n" + "="*60)
    print("🔎 特定の問題チェック")
    print("="*60)
    
    # 権利者情報の確認
    print("\n1. 権利者情報の取得確認")
    result = subprocess.run(
        'python3 cli_trademark_search.py --mark-text "ソニー" --limit 1 --format json',
        shell=True, capture_output=True, text=True
    )
    if result.returncode == 0:
        try:
            json_start = result.stdout.find('{')
            if json_start != -1:
                json_data = json.loads(result.stdout[json_start:])
                has_right_person = bool(json_data.get('right_person_name'))
                print(f"   権利者情報: {'✅ 取得可能' if has_right_person else '⚠️ 取得不可'}")
                if has_right_person:
                    print(f"   権利者名: {json_data.get('right_person_name')}")
        except:
            print("   ❌ JSON解析エラー")
    
    # 申請人情報の確認
    print("\n2. 申請人情報の取得確認")
    result = subprocess.run(
        'python3 cli_trademark_search.py --app-num "2020138119" --limit 1 --format json',
        shell=True, capture_output=True, text=True
    )
    if result.returncode == 0:
        try:
            json_start = result.stdout.find('{')
            if json_start != -1:
                json_data = json.loads(result.stdout[json_start:])
                has_applicant = bool(json_data.get('applicant_name'))
                print(f"   申請人情報: {'✅ 取得可能' if has_applicant else '⚠️ 取得不可'}")
                if has_applicant:
                    print(f"   申請人名: {json_data.get('applicant_name')}")
        except:
            print("   ❌ JSON解析エラー")
    
    # 称呼情報の確認
    print("\n3. 称呼情報の取得確認")
    result = subprocess.run(
        'python3 cli_trademark_search.py --mark-text "アップル" --limit 1 --format json',
        shell=True, capture_output=True, text=True
    )
    if result.returncode == 0:
        try:
            json_start = result.stdout.find('{')
            if json_start != -1:
                json_data = json.loads(result.stdout[json_start:])
                has_call_name = bool(json_data.get('call_name'))
                print(f"   称呼情報: {'✅ 取得可能' if has_call_name else '⚠️ 取得不可'}")
                if has_call_name:
                    print(f"   称呼: {json_data.get('call_name')}")
        except:
            print("   ❌ JSON解析エラー")

if __name__ == "__main__":
    main()
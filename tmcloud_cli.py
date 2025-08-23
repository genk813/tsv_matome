#!/usr/bin/env python3
"""
TMCloud コマンドラインインターフェース（Windows/Linux共通）
"""

import sys
import json
from pathlib import Path
from tmcloud_search_integrated import TMCloudIntegratedSearch

def main():
    """メイン関数"""
    
    # データベースファイルを探す
    db_files = [
        Path("tmcloud_v2_20250818_081655.db"),
        Path("tmcloud_v2_20250805_232509.db"),
        Path("/home/ygenk/TMCloud/tmcloud_v2_20250805_232509.db")  # WSL環境用
    ]
    
    db_path = None
    for db in db_files:
        if db.exists():
            db_path = db
            break
    
    if not db_path:
        print("エラー: データベースファイルが見つかりません")
        sys.exit(1)
    
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python tmcloud_cli.py <検索キーワード> [オプション]")
        print("\nオプション:")
        print("  --limit <数値>    検索結果の最大数")
        print("  --type <タイプ>   検索タイプ (text/phonetic/app_num/reg_num)")
        print("  --format <形式>   出力形式 (json/simple)")
        print("\n例:")
        print('  python tmcloud_cli.py "プル"')
        print('  python tmcloud_cli.py "2024061720"')
        print('  python tmcloud_cli.py "プル" --type phonetic --limit 5')
        sys.exit(0)
    
    # 引数をパース
    keyword = sys.argv[1]
    args = sys.argv[2:]
    kwargs = {}
    output_format = "simple"
    
    i = 0
    while i < len(args):
        if args[i] == "--limit" and i + 1 < len(args):
            kwargs["limit"] = int(args[i + 1])
            i += 2
        elif args[i] == "--type" and i + 1 < len(args):
            kwargs["type"] = args[i + 1]
            i += 2
        elif args[i] == "--format" and i + 1 < len(args):
            output_format = args[i + 1]
            i += 2
        else:
            i += 1
    
    # 検索実行
    try:
        searcher = TMCloudIntegratedSearch(str(db_path))
        results = searcher.search(keyword, **kwargs)
        
        if not results:
            print("検索結果が見つかりませんでした")
            return
        
        # 結果を表示
        if output_format == "json":
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            # シンプル形式で表示
            if isinstance(results, list):
                print(f"\n検索結果: {len(results)}件\n")
                for i, result in enumerate(results[:10], 1):  # 最初の10件のみ表示
                    print(f"[{i}] 出願番号: {result.get('app_num')}")
                    print(f"    商標名: {result.get('trademark_name', 'N/A')}")
                    print(f"    商標タイプ: {result.get('trademark_type', 'N/A')}")
                    print(f"    出願日: {result.get('app_date', 'N/A')}")
                    print(f"    最終処分: {result.get('final_disposition', 'N/A')}")
                    print()
                
                if len(results) > 10:
                    print(f"... 他 {len(results) - 10}件")
            else:
                # 単一結果
                print(f"\n出願番号: {results.get('app_num')}")
                print(f"商標名: {results.get('trademark_name', 'N/A')}")
                print(f"商標タイプ: {results.get('trademark_type', 'N/A')}")
                print(f"出願日: {results.get('app_date', 'N/A')}")
                print(f"登録日: {results.get('reg_date', 'N/A')}")
                print(f"最終処分: {results.get('final_disposition', 'N/A')}")
                
                # 商品・サービス
                if results.get('goods_services'):
                    print("\n商品・サービス:")
                    for class_num, items in results.get('goods_services', {}).items():
                        print(f"  区分{class_num}: {items[:100]}...")  # 最初の100文字
                
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
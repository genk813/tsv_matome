#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
自走商標検索システム - 統合ランチャー
CLI検索ツール、自動テスト、自己改善機能を統合したランチャー
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

def print_banner():
    """バナー表示"""
    print("=" * 80)
    print("🤖 自走商標検索システム v1.0")
    print("   - CLI商標検索ツール")
    print("   - 自動テスト機能")
    print("   - 自己改善システム")
    print("=" * 80)

def print_system_status():
    """システム状況の表示"""
    db_path = Path("output.db")
    print(f"📊 システム状況 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    print("-" * 50)
    
    # データベース状況
    if db_path.exists():
        size_mb = db_path.stat().st_size / 1024 / 1024
        print(f"✅ データベース: {db_path} ({size_mb:.1f}MB)")
    else:
        print(f"❌ データベース: {db_path} (存在しません)")
    
    # 履歴ファイル
    history_path = Path("improvement_history.json")
    if history_path.exists():
        print(f"✅ 改善履歴: {history_path}")
    else:
        print(f"📝 改善履歴: 未作成")
    
    # テスト結果ディレクトリ
    test_results_dir = Path("test_results")
    if test_results_dir.exists():
        test_files = list(test_results_dir.glob("*.json"))
        print(f"✅ テスト結果: {len(test_files)}件のレポート")
    else:
        print(f"📝 テスト結果: ディレクトリ未作成")

def search_mode(args):
    """検索モードの実行"""
    if args.html:
        print("🔍 HTML商標検索モード")
        import subprocess
        
        # HTML生成コマンドの構築
        cmd = [sys.executable, "search_results_html_generator.py"]
        if args.mark_text:
            cmd.extend(["--mark-text", args.mark_text])
        if args.app_num:
            cmd.extend(["--app-num", args.app_num])
        if args.goods_classes:
            cmd.extend(["--goods-classes", args.goods_classes])
        if args.designated_goods:
            cmd.extend(["--designated-goods", args.designated_goods])
        if args.limit:
            cmd.extend(["--limit", str(args.limit)])
        if args.output:
            cmd.extend(["--output", args.output])
        
        subprocess.run(cmd)
    else:
        print("🔍 CLI商標検索モード")
        print("例: --mark-text ソニー --limit 10")
        print("詳細は: python3 cli_trademark_search.py --help")
        print()
        import subprocess
        subprocess.run([sys.executable, "cli_trademark_search.py"] + sys.argv[2:])

def test_mode():
    """テストモードの実行"""
    print("🧪 自動テストモード")
    import subprocess
    subprocess.run([sys.executable, "autonomous_test_system.py"])

def improve_mode(args):
    """改善モードの実行"""
    if args.continuous:
        print(f"🔄 継続的改善モード ({args.cycles}サイクル)")
        import subprocess
        subprocess.run([sys.executable, "self_improving_system.py", "continuous", 
                       str(args.cycles), str(args.interval)])
    else:
        print("⚡ 単発改善モード")
        import subprocess
        subprocess.run([sys.executable, "self_improving_system.py", "single"])

def demo_mode():
    """デモモードの実行"""
    print("🎬 デモモード - 全機能を順次実行")
    print()
    
    # 1. システム状況確認
    print("1️⃣ システム状況確認")
    print_system_status()
    print()
    
    # 2. 簡単な検索テスト
    print("2️⃣ 商標検索テスト")
    import subprocess
    result = subprocess.run([
        sys.executable, "cli_trademark_search.py", 
        "--mark-text", "ソニー", "--limit", "3"
    ], capture_output=True, text=True)
    print(result.stdout)
    
    # 3. 自動テスト実行
    print("3️⃣ 自動テスト実行")
    subprocess.run([sys.executable, "autonomous_test_system.py"])
    print()
    
    # 4. 改善サイクル実行
    print("4️⃣ 改善サイクル実行")
    subprocess.run([sys.executable, "self_improving_system.py", "single"])

def main():
    """メイン処理"""
    print_banner()
    
    parser = argparse.ArgumentParser(description="自走商標検索システム")
    subparsers = parser.add_subparsers(dest='mode', help='実行モード')
    
    # ステータス表示
    subparsers.add_parser('status', help='システム状況を表示')
    
    # 検索モード
    search_parser = subparsers.add_parser('search', help='商標検索を実行')
    search_parser.add_argument('--mark-text', help='商標文字')
    search_parser.add_argument('--app-num', help='出願番号')
    search_parser.add_argument('--goods-classes', help='商品区分')
    search_parser.add_argument('--designated-goods', help='指定商品・役務')
    search_parser.add_argument('--limit', type=int, default=10, help='取得件数')
    search_parser.add_argument('--html', action='store_true', help='HTML形式で出力')
    search_parser.add_argument('--output', help='出力ファイル名（HTML形式の場合）')
    
    # テストモード
    subparsers.add_parser('test', help='自動テストを実行')
    
    # 改善モード
    improve_parser = subparsers.add_parser('improve', help='自己改善を実行')
    improve_parser.add_argument('--continuous', action='store_true', help='継続的改善')
    improve_parser.add_argument('--cycles', type=int, default=3, help='改善サイクル数')
    improve_parser.add_argument('--interval', type=int, default=30, help='サイクル間隔(秒)')
    
    # デモモード
    subparsers.add_parser('demo', help='全機能デモを実行')
    
    args = parser.parse_args()
    
    if not args.mode:
        parser.print_help()
        return
    
    try:
        if args.mode == 'status':
            print_system_status()
        elif args.mode == 'search':
            search_mode(args)
        elif args.mode == 'test':
            test_mode()
        elif args.mode == 'improve':
            improve_mode(args)
        elif args.mode == 'demo':
            demo_mode()
        else:
            parser.print_help()
            
    except KeyboardInterrupt:
        print("\n⚠️  ユーザーによる中断")
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
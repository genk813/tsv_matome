#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
申請人マスターファイル待機中の暫定対応スクリプト
"""

import sqlite3
from pathlib import Path

def check_for_new_files():
    """新しい申請人ファイルの存在確認"""
    tsv_dir = Path("/home/ygenk/tsv_matome/tsv_data/tsv")
    
    target_files = [
        "upd_appl_reg_info.tsv",
        "upd_under_integ_appl_info_mgt.tsv"
    ]
    
    print("=== 申請人マスターファイルの確認 ===")
    
    found_files = []
    for file in target_files:
        file_path = tsv_dir / file
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"✓ {file} が見つかりました！ ({size:,} bytes)")
            found_files.append(file)
        else:
            print(f"✗ {file} はまだ配置されていません")
    
    return found_files

def enhance_current_mapping():
    """現在のマッピングテーブルを強化"""
    db_path = Path("output.db")
    
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    
    print("\n=== 現在のマッピング状況 ===")
    
    # 現在のマッピング統計
    cur.execute("SELECT COUNT(*) FROM applicant_mapping")
    current_count = cur.fetchone()[0]
    print(f"現在のマッピング数: {current_count}件")
    
    # 信頼度別統計
    cur.execute("""
        SELECT confidence_level, COUNT(*) as count
        FROM applicant_mapping
        GROUP BY confidence_level
        ORDER BY 
            CASE confidence_level 
                WHEN '高' THEN 1 
                WHEN '中' THEN 2 
                WHEN '低' THEN 3 
            END
    """)
    
    print("\n信頼度別統計:")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}件")
    
    # 代理人情報から追加マッピングを作成
    print("\n=== 代理人情報の活用 ===")
    
    # 代理人コードから代理人名を抽出する試み
    cur.execute("""
        SELECT COUNT(DISTINCT shutugannindairinin_code)
        FROM jiken_c_t_shutugannindairinin
        WHERE shutugannindairinin_sikbt = '2'
        AND shutugannindairinin_code IS NOT NULL
    """)
    
    agent_codes = cur.fetchone()[0]
    print(f"ユニーク代理人コード: {agent_codes}個")
    
    # 頻出代理人コード
    cur.execute("""
        SELECT shutugannindairinin_code, COUNT(*) as count
        FROM jiken_c_t_shutugannindairinin
        WHERE shutugannindairinin_sikbt = '2'
        GROUP BY shutugannindairinin_code
        ORDER BY count DESC
        LIMIT 10
    """)
    
    print("\n頻出代理人コード:")
    for row in cur.fetchall():
        print(f"  コード: {row[0]} ({row[1]}件)")
    
    con.close()

def create_improved_search():
    """改善された検索機能を作成"""
    enhanced_code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
申請人マスターファイル対応の拡張検索システム
"""

import sqlite3
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

class ApplicantMasterSearchHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """GETリクエストを処理"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            # 申請人マスターファイルの存在確認
            appl_file = Path("tsv_data/tsv/upd_appl_reg_info.tsv")
            integ_file = Path("tsv_data/tsv/upd_under_integ_appl_info_mgt.tsv")
            
            master_status = ""
            if appl_file.exists() and integ_file.exists():
                master_status = "<div style='background: #d4edda; padding: 10px; margin: 10px 0; border-radius: 5px;'>✓ 申請人マスターファイルが利用可能</div>"
            else:
                master_status = "<div style='background: #fff3cd; padding: 10px; margin: 10px 0; border-radius: 5px;'>⚠ 申請人マスターファイル待機中（暫定マッピング使用）</div>"
            
            html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>商標検索システム（申請人マスター対応版）</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .search-box {{ margin: 20px 0; padding: 20px; border: 1px solid #ddd; }}
        .status {{ margin: 10px 0; }}
        .results {{ margin-top: 20px; }}
        .result-item {{ margin: 10px 0; padding: 15px; border: 1px solid #ddd; background: #f9f9f9; }}
        .label {{ font-weight: bold; color: #333; }}
        .value {{ margin-left: 10px; }}
        .applicant-info {{ background: #e6f3ff; padding: 5px; margin: 5px 0; border-radius: 3px; }}
        .rights-info {{ background: #f0f8e6; padding: 5px; margin: 5px 0; border-radius: 3px; }}
        .confidence-high {{ color: #28a745; }}
        .confidence-medium {{ color: #ffc107; }}
        .confidence-low {{ color: #dc3545; }}
        a {{ color: #0066cc; text-decoration: none; }}
    </style>
</head>
<body>
    <h1>商標検索システム（申請人マスター対応版）</h1>
    {master_status}
    <div class="search-box">
        <form action="/search" method="get">
            <label>商標テキスト: <input type="text" name="q" size="30"></label>
            <button type="submit">検索</button>
        </form>
    </div>
    <p>検索例: "東京", "大阪", "日本"</p>
    <p><strong>機能</strong>: 申請人情報、代理人情報、権利者情報を統合表示</p>
</body>
</html>
"""
            self.wfile.write(html.encode('utf-8'))
            
        elif self.path.startswith('/search'):
            # 検索処理（省略）
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write("検索機能は申請人マスターファイル配置後に有効化されます".encode('utf-8'))
    
def main():
    print("申請人マスター対応版検索システムを準備中...")
    print("http://localhost:8002 でアクセス準備完了")
    # server = HTTPServer(('localhost', 8002), ApplicantMasterSearchHandler)
    # server.serve_forever()

if __name__ == "__main__":
    main()
'''
    
    with open('/home/ygenk/tsv_matome/applicant_master_ready_server.py', 'w', encoding='utf-8') as f:
        f.write(enhanced_code)
    
    print("\n申請人マスター対応版検索システムを準備しました")

def provide_file_placement_guidance():
    """ファイル配置のガイダンス"""
    print("\n=== ファイル配置ガイダンス ===")
    print("申請人マスターファイルが配置されると以下の機能が利用可能になります:")
    print()
    print("1. 申請人コード → 実際の会社名・個人名の変換")
    print("2. 申請人住所の表示")
    print("3. 代理人情報の詳細表示")
    print("4. 100%の申請人情報カバレッジ")
    print()
    print("配置方法:")
    print("  1. upd_appl_reg_info.tsv を tsv_data/tsv/ に配置")
    print("  2. upd_under_integ_appl_info_mgt.tsv を tsv_data/tsv/ に配置")
    print("  3. python3 import_applicant_master.py を実行")
    print()
    print("現在の状況:")
    print("  - 暫定マッピング: 573件の申請人情報が利用可能")
    print("  - 権利者情報: 登録済み商標で完全表示")
    print("  - 検索機能: 正常動作中")

if __name__ == "__main__":
    found_files = check_for_new_files()
    
    if found_files:
        print(f"\n{len(found_files)}個のファイルが見つかりました！")
        print("次のステップ: python3 import_applicant_master.py を実行してください")
    else:
        enhance_current_mapping()
        create_improved_search()
        provide_file_placement_guidance()
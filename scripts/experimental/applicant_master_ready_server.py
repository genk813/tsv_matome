#!/usr/bin/env python3
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

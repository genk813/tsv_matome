#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡易Webサーバーテスト - Flask不要で基本的な検索機能を提供
"""

import sqlite3
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import json

class TrademarkSearchHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """GETリクエストを処理"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>商標検索システム</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .search-box { margin: 20px 0; padding: 20px; border: 1px solid #ddd; }
        .results { margin-top: 20px; }
        .result-item { margin: 10px 0; padding: 10px; border: 1px solid #eee; }
        .label { font-weight: bold; }
    </style>
</head>
<body>
    <h1>商標検索システム</h1>
    <div class="search-box">
        <form action="/search" method="get">
            <label>商標テキスト: <input type="text" name="q" size="30"></label>
            <button type="submit">検索</button>
        </form>
    </div>
    <p>検索例: "東京", "大阪", "日本"</p>
</body>
</html>
"""
            self.wfile.write(html.encode('utf-8'))
            
        elif self.path.startswith('/search'):
            # クエリパラメータを解析
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            search_term = params.get('q', [''])[0]
            
            # 検索実行
            results = self.search_trademarks(search_term)
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>検索結果 - 商標検索システム</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .results {{ margin-top: 20px; }}
        .result-item {{ margin: 10px 0; padding: 15px; border: 1px solid #ddd; background: #f9f9f9; }}
        .label {{ font-weight: bold; color: #333; }}
        .value {{ margin-left: 10px; }}
        a {{ color: #0066cc; text-decoration: none; }}
    </style>
</head>
<body>
    <h1>検索結果</h1>
    <p><a href="/">← 戻る</a></p>
    <p>検索語: <strong>{search_term}</strong></p>
    <p>検索結果: {len(results)}件</p>
    <div class="results">
"""
            
            for i, result in enumerate(results[:20], 1):  # 最大20件表示
                html += f"""
        <div class="result-item">
            <h3>結果 {i}</h3>
            <div><span class="label">出願番号:</span><span class="value">{result['app_num']}</span></div>
            <div><span class="label">商標:</span><span class="value">{result['mark_text'] or '(なし)'}</span></div>
            <div><span class="label">出願日:</span><span class="value">{result['app_date'] or ''}</span></div>
            <div><span class="label">登録日:</span><span class="value">{result['reg_date'] or '(未登録)'}</span></div>
            <div><span class="label">商品区分:</span><span class="value">{result['goods_classes'] or '(なし)'}</span></div>
            <div><span class="label">権利者:</span><span class="value">{result['right_person_name'] or '(情報なし)'}</span></div>
            <div><span class="label">権利者住所:</span><span class="value">{result['right_person_addr'] or '(情報なし)'}</span></div>
        </div>
"""
            
            html += """
    </div>
</body>
</html>
"""
            self.wfile.write(html.encode('utf-8'))
            
        else:
            self.send_response(404)
            self.end_headers()
    
    def search_trademarks(self, search_term):
        """商標を検索"""
        if not search_term:
            return []
            
        db_path = Path("output.db")
        if not db_path.exists():
            return []
            
        con = sqlite3.connect(db_path)
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        
        query = """
            SELECT DISTINCT
                j.normalized_app_num as app_num,
                j.shutugan_bi as app_date,
                j.reg_reg_ymd as reg_date,
                COALESCE(s.standard_char_t, iu.indct_use_t, su.search_use_t) as mark_text,
                gca.goods_classes,
                rp.right_person_name,
                rp.right_person_addr
            FROM jiken_c_t j
            LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num
            LEFT JOIN indct_use_t_art iu ON j.normalized_app_num = iu.normalized_app_num
            LEFT JOIN search_use_t_art_table su ON j.normalized_app_num = su.normalized_app_num
            LEFT JOIN goods_class_art gca ON j.normalized_app_num = gca.normalized_app_num
            LEFT JOIN reg_mapping rm ON j.normalized_app_num = rm.app_num
            LEFT JOIN right_person_art_t rp ON rm.reg_num = rp.reg_num
            WHERE 
                s.standard_char_t LIKE ? OR
                iu.indct_use_t LIKE ? OR
                su.search_use_t LIKE ?
            LIMIT 50
        """
        
        search_pattern = f"%{search_term}%"
        cur.execute(query, (search_pattern, search_pattern, search_pattern))
        
        results = []
        for row in cur.fetchall():
            results.append({
                'app_num': row['app_num'],
                'app_date': row['app_date'],
                'reg_date': row['reg_date'],
                'mark_text': row['mark_text'],
                'goods_classes': row['goods_classes'],
                'right_person_name': row['right_person_name'],
                'right_person_addr': row['right_person_addr']
            })
        
        con.close()
        return results

def main():
    """メイン関数"""
    print("商標検索システムを起動中...")
    print("http://localhost:8000 でアクセスしてください")
    print("Ctrl+C で終了")
    
    server = HTTPServer(('localhost', 8000), TrademarkSearchHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nサーバーを停止しました")

if __name__ == "__main__":
    main()
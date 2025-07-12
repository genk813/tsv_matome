#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
拡張検索アプリケーション - 改善された出願人表示と詳細検索機能
"""

import sqlite3
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import json
import re
from datetime import datetime

class EnhancedSearchHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """GETリクエストを処理"""
        if self.path == '/':
            self.send_home_page()
        elif self.path.startswith('/search'):
            self.handle_search()
        elif self.path.startswith('/detail'):
            self.handle_detail()
        elif self.path.startswith('/api/stats'):
            self.handle_stats()
        else:
            self.send_error(404)
    
    def send_home_page(self):
        """ホームページを送信"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>商標検索システム - 拡張版</title>
    <style>
        body { 
            font-family: 'メイリオ', Arial, sans-serif; 
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }
        .header {
            background-color: #2c3e50;
            color: white;
            padding: 20px;
            text-align: center;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .search-box {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        .search-form {
            display: grid;
            gap: 15px;
        }
        .form-group {
            display: grid;
            grid-template-columns: 150px 1fr;
            align-items: center;
            gap: 10px;
        }
        .form-group label {
            font-weight: bold;
            text-align: right;
        }
        input[type="text"], input[type="date"], select {
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }
        .search-buttons {
            grid-column: 2;
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }
        button {
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
        .btn-primary {
            background-color: #3498db;
            color: white;
        }
        .btn-secondary {
            background-color: #95a5a6;
            color: white;
        }
        button:hover {
            opacity: 0.9;
        }
        .stats-box {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }
        .stat-item {
            text-align: center;
            padding: 15px;
            border: 1px solid #ecf0f1;
            border-radius: 4px;
        }
        .stat-value {
            font-size: 32px;
            font-weight: bold;
            color: #3498db;
        }
        .stat-label {
            color: #7f8c8d;
            margin-top: 5px;
        }
        .help-text {
            color: #7f8c8d;
            font-size: 12px;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>商標検索システム - 拡張版</h1>
        <p>出願人情報の表示を強化し、詳細検索オプションを追加</p>
    </div>
    
    <div class="container">
        <div class="search-box">
            <h2>商標検索</h2>
            <form action="/search" method="get" class="search-form">
                <div class="form-group">
                    <label>商標テキスト:</label>
                    <div>
                        <input type="text" name="q" size="40" placeholder="例: 東京, コーヒー, ブランド名など">
                        <div class="help-text">商標名の一部を入力してください</div>
                    </div>
                </div>
                
                <div class="form-group">
                    <label>出願人名:</label>
                    <div>
                        <input type="text" name="applicant" size="40" placeholder="例: 株式会社, トヨタ, 資生堂など">
                        <div class="help-text">出願人名の一部を入力してください</div>
                    </div>
                </div>
                
                <div class="form-group">
                    <label>商品・役務区分:</label>
                    <select name="class">
                        <option value="">全ての区分</option>
                        <option value="1">第1類 - 化学品</option>
                        <option value="3">第3類 - 化粧品</option>
                        <option value="5">第5類 - 薬剤</option>
                        <option value="9">第9類 - 電気機械器具</option>
                        <option value="25">第25類 - 被服</option>
                        <option value="30">第30類 - 菓子、コーヒー</option>
                        <option value="35">第35類 - 広告、事業</option>
                        <option value="41">第41類 - 教育、娯楽</option>
                        <option value="42">第42類 - 科学技術</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>出願日:</label>
                    <div style="display: flex; gap: 10px; align-items: center;">
                        <input type="date" name="date_from">
                        <span>〜</span>
                        <input type="date" name="date_to">
                    </div>
                </div>
                
                <div class="form-group">
                    <label>表示件数:</label>
                    <select name="limit">
                        <option value="20">20件</option>
                        <option value="50">50件</option>
                        <option value="100">100件</option>
                    </select>
                </div>
                
                <div class="search-buttons">
                    <button type="submit" class="btn-primary">検索</button>
                    <button type="reset" class="btn-secondary">クリア</button>
                </div>
            </form>
        </div>
        
        <div class="stats-box" id="stats">
            <div class="stat-item">
                <div class="stat-value">-</div>
                <div class="stat-label">総商標数</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">-</div>
                <div class="stat-label">出願人マッピング</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">-</div>
                <div class="stat-label">商標表示率</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">-</div>
                <div class="stat-label">画像データ</div>
            </div>
        </div>
    </div>
    
    <script>
        // 統計情報を取得
        fetch('/api/stats')
            .then(response => response.json())
            .then(data => {
                document.querySelectorAll('.stat-value')[0].textContent = data.total_trademarks.toLocaleString();
                document.querySelectorAll('.stat-value')[1].textContent = data.applicant_mappings.toLocaleString();
                document.querySelectorAll('.stat-value')[2].textContent = data.display_rate + '%';
                document.querySelectorAll('.stat-value')[3].textContent = data.image_count.toLocaleString();
            });
    </script>
</body>
</html>
"""
        self.wfile.write(html.encode('utf-8'))
    
    def handle_search(self):
        """検索処理"""
        # URLパラメータを解析
        parsed_url = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed_url.query)
        
        # パラメータ取得
        search_text = params.get('q', [''])[0]
        applicant_name = params.get('applicant', [''])[0]
        goods_class = params.get('class', [''])[0]
        date_from = params.get('date_from', [''])[0]
        date_to = params.get('date_to', [''])[0]
        limit = int(params.get('limit', ['20'])[0])
        
        # データベース接続
        con = sqlite3.connect("output.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        
        # 検索クエリを構築
        query = """
            SELECT DISTINCT
                j.normalized_app_num,
                j.shutugan_bi,
                j.reg_reg_ymd,
                COALESCE(s.standard_char_t, iu.indct_use_t, su.search_use_t) as mark_text,
                gca.goods_classes,
                -- 出願人情報（拡張マッピングを使用）
                COALESCE(am.applicant_name, ame.applicant_name, 
                    '申請人コード: ' || ap.shutugannindairinin_code) as applicant_display,
                COALESCE(am.confidence_level, ame.confidence_level, '') as confidence,
                -- 権利者情報
                rp.right_person_name,
                -- 画像情報
                CASE WHEN ts.image_data IS NOT NULL THEN 1 ELSE 0 END as has_image
            FROM jiken_c_t j
            LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num
            LEFT JOIN indct_use_t_art iu ON j.normalized_app_num = iu.normalized_app_num
            LEFT JOIN search_use_t_art_table su ON j.normalized_app_num = su.normalized_app_num
            LEFT JOIN goods_class_art gca ON j.normalized_app_num = gca.normalized_app_num
            LEFT JOIN jiken_c_t_shutugannindairinin ap ON j.normalized_app_num = ap.shutugan_no 
                AND ap.shutugannindairinin_sikbt = '1'
            LEFT JOIN applicant_mapping am ON ap.shutugannindairinin_code = am.applicant_code
            LEFT JOIN applicant_mapping_enhanced ame ON ap.shutugannindairinin_code = ame.applicant_code
            LEFT JOIN reg_mapping rm ON j.normalized_app_num = rm.app_num
            LEFT JOIN right_person_art_t rp ON rm.reg_num = rp.reg_num
            LEFT JOIN t_sample ts ON j.normalized_app_num = ts.normalized_app_num
            WHERE 1=1
        """
        
        params_list = []
        
        # 商標テキスト検索
        if search_text:
            query += """ AND (
                s.standard_char_t LIKE ? OR
                iu.indct_use_t LIKE ? OR
                su.search_use_t LIKE ?
            )"""
            search_pattern = f"%{search_text}%"
            params_list.extend([search_pattern, search_pattern, search_pattern])
        
        # 出願人名検索
        if applicant_name:
            query += """ AND (
                am.applicant_name LIKE ? OR
                ame.applicant_name LIKE ? OR
                rp.right_person_name LIKE ?
            )"""
            applicant_pattern = f"%{applicant_name}%"
            params_list.extend([applicant_pattern, applicant_pattern, applicant_pattern])
        
        # 商品区分フィルタ
        if goods_class:
            query += " AND gca.goods_classes LIKE ?"
            params_list.append(f"%第{goods_class}類%")
        
        # 日付範囲フィルタ
        if date_from:
            query += " AND j.shutugan_bi >= ?"
            params_list.append(date_from.replace('-', ''))
        
        if date_to:
            query += " AND j.shutugan_bi <= ?"
            params_list.append(date_to.replace('-', ''))
        
        query += f" ORDER BY j.shutugan_bi DESC LIMIT {limit}"
        
        # 検索実行
        cur.execute(query, params_list)
        results = cur.fetchall()
        
        # 結果ページを生成
        self.send_search_results(results, search_text, applicant_name)
        
        con.close()
    
    def send_search_results(self, results, search_text, applicant_name):
        """検索結果を表示"""
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
        body {{ 
            font-family: 'メイリオ', Arial, sans-serif; 
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }}
        .header {{
            background-color: #2c3e50;
            color: white;
            padding: 20px;
            text-align: center;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        .search-summary {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .results {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .result-item {{
            border-bottom: 1px solid #ecf0f1;
            padding: 20px 0;
        }}
        .result-item:last-child {{
            border-bottom: none;
        }}
        .result-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        .app-num {{
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
        }}
        .mark-text {{
            font-size: 20px;
            color: #e74c3c;
            margin: 10px 0;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        .info-item {{
            display: flex;
            align-items: start;
        }}
        .info-label {{
            font-weight: bold;
            color: #7f8c8d;
            margin-right: 10px;
            min-width: 80px;
        }}
        .confidence {{
            font-size: 12px;
            padding: 2px 6px;
            border-radius: 3px;
            margin-left: 5px;
        }}
        .confidence.高 {{
            background-color: #27ae60;
            color: white;
        }}
        .confidence.中 {{
            background-color: #f39c12;
            color: white;
        }}
        .confidence.低 {{
            background-color: #e74c3c;
            color: white;
        }}
        .confidence.推定 {{
            background-color: #95a5a6;
            color: white;
        }}
        .has-image {{
            color: #3498db;
            font-size: 12px;
        }}
        .back-link {{
            display: inline-block;
            margin-bottom: 20px;
            color: #3498db;
            text-decoration: none;
        }}
        .back-link:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>検索結果</h1>
    </div>
    
    <div class="container">
        <a href="/" class="back-link">← 検索画面に戻る</a>
        
        <div class="search-summary">
            <h2>検索条件</h2>
            <p>
                {f'商標テキスト: 「{search_text}」' if search_text else ''}
                {f'出願人名: 「{applicant_name}」' if applicant_name else ''}
            </p>
            <p>検索結果: {len(results)}件</p>
        </div>
        
        <div class="results">
"""
        
        if not results:
            html += "<p>検索条件に一致する商標が見つかりませんでした。</p>"
        else:
            for result in results:
                # 日付フォーマット
                app_date = result['shutugan_bi']
                if app_date:
                    app_date = f"{app_date[:4]}/{app_date[4:6]}/{app_date[6:]}"
                
                reg_date = result['reg_reg_ymd']
                if reg_date:
                    reg_date = f"{reg_date[:4]}/{reg_date[4:6]}/{reg_date[6:]}"
                
                html += f"""
            <div class="result-item">
                <div class="result-header">
                    <span class="app-num">出願番号: {result['normalized_app_num']}</span>
                    {f'<span class="has-image">📷 画像あり</span>' if result['has_image'] else ''}
                </div>
                
                <div class="mark-text">
                    {result['mark_text'] or '（商標テキストなし）'}
                </div>
                
                <div class="info-grid">
                    <div class="info-item">
                        <span class="info-label">出願日:</span>
                        <span>{app_date or '不明'}</span>
                    </div>
                    
                    <div class="info-item">
                        <span class="info-label">登録日:</span>
                        <span>{reg_date or '未登録'}</span>
                    </div>
                    
                    <div class="info-item">
                        <span class="info-label">出願人:</span>
                        <span>
                            {result['applicant_display'] or '不明'}
                            {f'<span class="confidence {result["confidence"]}">{result["confidence"]}</span>' if result['confidence'] else ''}
                        </span>
                    </div>
                    
                    {f'''<div class="info-item">
                        <span class="info-label">権利者:</span>
                        <span>{result['right_person_name']}</span>
                    </div>''' if result['right_person_name'] else ''}
                    
                    <div class="info-item">
                        <span class="info-label">区分:</span>
                        <span>{result['goods_classes'] or '不明'}</span>
                    </div>
                </div>
            </div>
"""
        
        html += """
        </div>
    </div>
</body>
</html>
"""
        self.wfile.write(html.encode('utf-8'))
    
    def handle_stats(self):
        """統計情報API"""
        con = sqlite3.connect("output.db")
        cur = con.cursor()
        
        # 統計情報を取得
        stats = {}
        
        # 総商標数
        cur.execute("SELECT COUNT(*) FROM jiken_c_t")
        stats['total_trademarks'] = cur.fetchone()[0]
        
        # 出願人マッピング数
        cur.execute("SELECT COUNT(*) FROM applicant_mapping_enhanced")
        stats['applicant_mappings'] = cur.fetchone()[0]
        
        # 商標表示率
        cur.execute("""
            SELECT COUNT(*) FROM jiken_c_t j
            WHERE EXISTS (
                SELECT 1 FROM standard_char_t_art WHERE normalized_app_num = j.normalized_app_num
            ) OR EXISTS (
                SELECT 1 FROM indct_use_t_art WHERE normalized_app_num = j.normalized_app_num
            ) OR EXISTS (
                SELECT 1 FROM search_use_t_art_table WHERE normalized_app_num = j.normalized_app_num
            )
        """)
        display_count = cur.fetchone()[0]
        stats['display_rate'] = round((display_count / stats['total_trademarks']) * 100, 1)
        
        # 画像データ数
        cur.execute("SELECT COUNT(*) FROM t_sample WHERE image_data IS NOT NULL")
        stats['image_count'] = cur.fetchone()[0]
        
        con.close()
        
        # JSON レスポンス
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(stats).encode('utf-8'))
    
    def handle_detail(self):
        """詳細表示（今後実装）"""
        self.send_error(501, "詳細表示は開発中です")

def run_server(port=8002):
    """サーバーを起動"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, EnhancedSearchHandler)
    print(f"拡張検索サーバーを起動しました: http://localhost:{port}")
    print("Ctrl+C で停止")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
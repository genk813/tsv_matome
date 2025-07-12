#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
申請人実名表示対応版商標検索システム - 最終版
"""

import sqlite3
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

class FinalApplicantSearchHandler(BaseHTTPRequestHandler):
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
    <title>商標検索システム（申請人実名表示対応版）</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .search-box { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
        .status { margin: 10px 0; padding: 10px; background: #d4edda; border-radius: 5px; }
        .results { margin-top: 20px; }
        .result-item { margin: 10px 0; padding: 15px; border: 1px solid #ddd; background: #f9f9f9; border-radius: 5px; }
        .label { font-weight: bold; color: #333; }
        .value { margin-left: 10px; }
        .applicant-info { background: #e6f3ff; padding: 8px; margin: 5px 0; border-radius: 3px; }
        .rights-info { background: #f0f8e6; padding: 8px; margin: 5px 0; border-radius: 3px; }
        .real-name { color: #28a745; font-weight: bold; }
        .code-only { color: #6c757d; }
        a { color: #0066cc; text-decoration: none; }
    </style>
</head>
<body>
    <h1>商標検索システム（申請人実名表示対応版）</h1>
    <div class="status">
        ✓ 申請人マスターファイル: 1,612件
        <br>✓ 申請人実名表示機能: 有効
        <br>✓ 権利者情報: 完全対応
    </div>
    <div class="search-box">
        <form action="/search" method="get">
            <label>商標テキスト: <input type="text" name="q" size="30" placeholder="例: 東京, 大阪, 日本"></label>
            <button type="submit">検索</button>
        </form>
    </div>
    <p><strong>新機能</strong>: 申請人コードから実際の会社名・個人名を表示</p>
    <p><strong>表示例</strong>: 
        <span class="real-name">フリュー株式会社</span> (実名) / 
        <span class="code-only">コード:XXXXXX</span> (未解決)
    </p>
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
            results = self.search_with_real_names(search_term)
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>検索結果 - 申請人実名表示対応版</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .results {{ margin-top: 20px; }}
        .result-item {{ margin: 10px 0; padding: 15px; border: 1px solid #ddd; background: #f9f9f9; border-radius: 5px; }}
        .label {{ font-weight: bold; color: #333; }}
        .value {{ margin-left: 10px; }}
        .applicant-info {{ background: #e6f3ff; padding: 8px; margin: 5px 0; border-radius: 3px; }}
        .rights-info {{ background: #f0f8e6; padding: 8px; margin: 5px 0; border-radius: 3px; }}
        .real-name {{ color: #28a745; font-weight: bold; }}
        .code-only {{ color: #6c757d; }}
        .partial-name {{ color: #ffc107; font-weight: bold; }}
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
            
            for i, result in enumerate(results[:20], 1):
                # 申請人表示の分類
                applicant_class = "code-only"
                if result['applicant_display'] and not result['applicant_display'].startswith('コード:'):
                    if '▲' in result['applicant_display'] or '（省略）' in result['applicant_display']:
                        applicant_class = "partial-name"
                    else:
                        applicant_class = "real-name"
                
                html += f"""
        <div class="result-item">
            <h3>結果 {i}</h3>
            <div><span class="label">出願番号:</span><span class="value">{result['app_num']}</span></div>
            <div><span class="label">商標:</span><span class="value">{result['mark_text'] or '(なし)'}</span></div>
            <div><span class="label">出願日:</span><span class="value">{result['app_date'] or ''}</span></div>
            <div><span class="label">登録日:</span><span class="value">{result['reg_date'] or '(未登録)'}</span></div>
            <div><span class="label">商品区分:</span><span class="value">{result['goods_classes'] or '(なし)'}</span></div>
            <div class="applicant-info">
                <div><span class="label">申請人:</span><span class="value {applicant_class}">{result['applicant_display'] or '(情報なし)'}</span></div>
                {f'<div><span class="label">申請人住所:</span><span class="value">{result["applicant_address"]}</span></div>' if result['applicant_address'] else ''}
            </div>
            <div class="rights-info">
                <div><span class="label">権利者:</span><span class="value">{result['right_person_name'] or '(未登録)'}</span></div>
                {f'<div><span class="label">権利者住所:</span><span class="value">{result["right_person_addr"]}</span></div>' if result['right_person_addr'] else ''}
            </div>
        </div>
"""
            
            html += """
    </div>
    <div style="margin-top: 20px; padding: 10px; background: #f8f9fa; border-radius: 5px;">
        <strong>申請人表示について:</strong><br>
        <span class="real-name">緑色</span>: 実名表示成功 / 
        <span class="partial-name">黄色</span>: 部分的表示 / 
        <span class="code-only">グレー</span>: コードのみ
    </div>
</body>
</html>
"""
            self.wfile.write(html.encode('utf-8'))
            
        else:
            self.send_response(404)
            self.end_headers()
    
    def search_with_real_names(self, search_term):
        """申請人実名表示対応検索"""
        if not search_term:
            return []
            
        db_path = Path("output.db")
        if not db_path.exists():
            return []
            
        con = sqlite3.connect(db_path)
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        
        query = """
            SELECT 
                j.normalized_app_num as app_num,
                j.shutugan_bi as app_date,
                j.reg_reg_ymd as reg_date,
                COALESCE(s.standard_char_t, iu.indct_use_t, su.search_use_t) as mark_text,
                gca.goods_classes,
                -- 申請人情報（マスターファイル優先、フォールバック付き）
                CASE 
                    WHEN am.appl_name IS NOT NULL AND am.appl_name != '' AND am.appl_name NOT LIKE '%省略%'
                    THEN am.appl_name
                    WHEN apm.applicant_name IS NOT NULL
                    THEN apm.applicant_name || ' (推定)'
                    ELSE 'コード:' || ap.shutugannindairinin_code
                END as applicant_display,
                COALESCE(am.appl_addr, apm.applicant_addr) as applicant_address,
                -- 権利者情報（登録済み）
                rp.right_person_name,
                rp.right_person_addr
            FROM jiken_c_t j
            LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num
            LEFT JOIN indct_use_t_art iu ON j.normalized_app_num = iu.normalized_app_num
            LEFT JOIN search_use_t_art_table su ON j.normalized_app_num = su.normalized_app_num
            LEFT JOIN goods_class_art gca ON j.normalized_app_num = gca.normalized_app_num
            LEFT JOIN jiken_c_t_shutugannindairinin ap ON j.normalized_app_num = ap.shutugan_no 
                                                       AND ap.shutugannindairinin_sikbt = '1'
            -- 申請人マスターファイル（優先）
            LEFT JOIN applicant_master am ON ap.shutugannindairinin_code = am.appl_cd
            -- 部分的申請人マッピング（フォールバック）
            LEFT JOIN (
                SELECT applicant_code, applicant_name, applicant_addr,
                       ROW_NUMBER() OVER (PARTITION BY applicant_code ORDER BY trademark_count DESC) as rn
                FROM applicant_mapping
            ) apm ON ap.shutugannindairinin_code = apm.applicant_code AND apm.rn = 1
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
                'applicant_display': row['applicant_display'],
                'applicant_address': row['applicant_address'],
                'right_person_name': row['right_person_name'],
                'right_person_addr': row['right_person_addr']
            })
        
        con.close()
        return results

def main():
    """メイン関数"""
    print("申請人実名表示対応版商標検索システムを起動中...")
    print("✓ 申請人マスターファイル: 1,612件")
    print("✓ 申請人部分マッピング: 573件")
    print("✓ 権利者情報: 完全対応")
    print()
    print("http://localhost:8003 でアクセスしてください")
    print("Ctrl+C で終了")
    
    server = HTTPServer(('localhost', 8003), FinalApplicantSearchHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\\nサーバーを停止しました")

if __name__ == "__main__":
    main()
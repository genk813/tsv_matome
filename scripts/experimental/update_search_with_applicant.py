#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
from pathlib import Path

def update_search_functionality():
    """検索機能に出願人情報を追加"""
    db_path = Path("output.db")
    
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    
    # 出願人情報を含む拡張検索クエリ
    enhanced_search_query = """
        SELECT DISTINCT
            j.normalized_app_num as app_num,
            j.shutugan_bi as app_date,
            j.reg_reg_ymd as reg_date,
            -- 商標テキスト（優先順位: 標準文字 → 表示用 → 検索用）
            COALESCE(s.standard_char_t, iu.indct_use_t, su.search_use_t) as mark_text,
            -- 商品区分
            gca.goods_classes,
            -- 出願人情報
            GROUP_CONCAT(DISTINCT CASE WHEN ap.shutugannindairinin_sikbt = '1' 
                         THEN 'コード:' || ap.shutugannindairinin_code END) as applicant_codes,
            -- 代理人情報
            GROUP_CONCAT(DISTINCT CASE WHEN ap.shutugannindairinin_sikbt = '2' 
                         THEN 'コード:' || ap.shutugannindairinin_code END) as agent_codes,
            -- 権利者情報（登録済み）
            rp.right_person_name,
            rp.right_person_addr
        FROM jiken_c_t j
        LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num
        LEFT JOIN indct_use_t_art iu ON j.normalized_app_num = iu.normalized_app_num
        LEFT JOIN search_use_t_art_table su ON j.normalized_app_num = su.normalized_app_num
        LEFT JOIN goods_class_art gca ON j.normalized_app_num = gca.normalized_app_num
        LEFT JOIN jiken_c_t_shutugannindairinin ap ON j.normalized_app_num = ap.shutugan_no
        LEFT JOIN reg_mapping rm ON j.normalized_app_num = rm.app_num
        LEFT JOIN right_person_art_t rp ON rm.reg_num = rp.reg_num
        WHERE 
            s.standard_char_t LIKE ? OR
            iu.indct_use_t LIKE ? OR
            su.search_use_t LIKE ?
        GROUP BY j.normalized_app_num
        LIMIT 10
    """
    
    # テスト検索
    search_term = "東京"
    search_pattern = f"%{search_term}%"
    
    print(f"検索語: '{search_term}'")
    print("=" * 60)
    
    cur.execute(enhanced_search_query, (search_pattern, search_pattern, search_pattern))
    results = cur.fetchall()
    
    print(f"\n検索結果: {len(results)}件")
    
    for i, row in enumerate(results, 1):
        print(f"\n--- 結果 {i} ---")
        print(f"出願番号: {row['app_num']}")
        print(f"商標テキスト: {row['mark_text']}")
        print(f"出願日: {row['app_date']}")
        print(f"登録日: {row['reg_date'] if row['reg_date'] else '(未登録)'}")
        print(f"商品区分: {row['goods_classes'] if row['goods_classes'] else '(なし)'}")
        print(f"出願人: {row['applicant_codes'] if row['applicant_codes'] else '(情報なし)'}")
        print(f"代理人: {row['agent_codes'] if row['agent_codes'] else '(情報なし)'}")
        print(f"権利者: {row['right_person_name'] if row['right_person_name'] else '(情報なし)'}")
        print(f"権利者住所: {row['right_person_addr'] if row['right_person_addr'] else '(情報なし)'}")
    
    con.close()

def create_enhanced_web_server():
    """出願人情報を含む拡張Webサーバーを作成"""
    enhanced_server_code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
出願人情報対応版の商標検索システム
"""

import sqlite3
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

class EnhancedTrademarkSearchHandler(BaseHTTPRequestHandler):
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
    <title>商標検索システム（出願人情報対応版）</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .search-box { margin: 20px 0; padding: 20px; border: 1px solid #ddd; }
        .results { margin-top: 20px; }
        .result-item { margin: 10px 0; padding: 15px; border: 1px solid #ddd; background: #f9f9f9; }
        .label { font-weight: bold; color: #333; }
        .value { margin-left: 10px; }
        .applicant-info { background: #e6f3ff; padding: 5px; margin: 5px 0; }
        .rights-info { background: #f0f8e6; padding: 5px; margin: 5px 0; }
        a { color: #0066cc; text-decoration: none; }
    </style>
</head>
<body>
    <h1>商標検索システム（出願人情報対応版）</h1>
    <div class="search-box">
        <form action="/search" method="get">
            <label>商標テキスト: <input type="text" name="q" size="30"></label>
            <button type="submit">検索</button>
        </form>
    </div>
    <p>検索例: "東京", "大阪", "日本"</p>
    <p><strong>注意</strong>: 出願人・代理人の氏名は個人情報保護のため省略されており、コードで表示されます。</p>
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
            results = self.search_trademarks_enhanced(search_term)
            
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
        .applicant-info {{ background: #e6f3ff; padding: 5px; margin: 5px 0; border-radius: 3px; }}
        .rights-info {{ background: #f0f8e6; padding: 5px; margin: 5px 0; border-radius: 3px; }}
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
                html += f"""
        <div class="result-item">
            <h3>結果 {i}</h3>
            <div><span class="label">出願番号:</span><span class="value">{result['app_num']}</span></div>
            <div><span class="label">商標:</span><span class="value">{result['mark_text'] or '(なし)'}</span></div>
            <div><span class="label">出願日:</span><span class="value">{result['app_date'] or ''}</span></div>
            <div><span class="label">登録日:</span><span class="value">{result['reg_date'] or '(未登録)'}</span></div>
            <div><span class="label">商品区分:</span><span class="value">{result['goods_classes'] or '(なし)'}</span></div>
            <div class="applicant-info">
                <div><span class="label">出願人:</span><span class="value">{result['applicant_codes'] or '(情報なし)'}</span></div>
                <div><span class="label">代理人:</span><span class="value">{result['agent_codes'] or '(情報なし)'}</span></div>
            </div>
            <div class="rights-info">
                <div><span class="label">権利者:</span><span class="value">{result['right_person_name'] or '(情報なし)'}</span></div>
                <div><span class="label">権利者住所:</span><span class="value">{result['right_person_addr'] or '(情報なし)'}</span></div>
            </div>
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
    
    def search_trademarks_enhanced(self, search_term):
        """出願人情報を含む拡張検索"""
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
                GROUP_CONCAT(DISTINCT CASE WHEN ap.shutugannindairinin_sikbt = '1' 
                             THEN 'コード:' || ap.shutugannindairinin_code END) as applicant_codes,
                GROUP_CONCAT(DISTINCT CASE WHEN ap.shutugannindairinin_sikbt = '2' 
                             THEN 'コード:' || ap.shutugannindairinin_code END) as agent_codes,
                rp.right_person_name,
                rp.right_person_addr
            FROM jiken_c_t j
            LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num
            LEFT JOIN indct_use_t_art iu ON j.normalized_app_num = iu.normalized_app_num
            LEFT JOIN search_use_t_art_table su ON j.normalized_app_num = su.normalized_app_num
            LEFT JOIN goods_class_art gca ON j.normalized_app_num = gca.normalized_app_num
            LEFT JOIN jiken_c_t_shutugannindairinin ap ON j.normalized_app_num = ap.shutugan_no
            LEFT JOIN reg_mapping rm ON j.normalized_app_num = rm.app_num
            LEFT JOIN right_person_art_t rp ON rm.reg_num = rp.reg_num
            WHERE 
                s.standard_char_t LIKE ? OR
                iu.indct_use_t LIKE ? OR
                su.search_use_t LIKE ?
            GROUP BY j.normalized_app_num
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
                'applicant_codes': row['applicant_codes'],
                'agent_codes': row['agent_codes'],
                'right_person_name': row['right_person_name'],
                'right_person_addr': row['right_person_addr']
            })
        
        con.close()
        return results

def main():
    """メイン関数"""
    print("出願人情報対応版商標検索システムを起動中...")
    print("http://localhost:8001 でアクセスしてください")
    print("Ctrl+C で終了")
    
    server = HTTPServer(('localhost', 8001), EnhancedTrademarkSearchHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\\nサーバーを停止しました")

if __name__ == "__main__":
    main()
'''
    
    with open('enhanced_web_server.py', 'w', encoding='utf-8') as f:
        f.write(enhanced_server_code)
    
    print("出願人情報対応版Webサーバーを作成しました: enhanced_web_server.py")
    print("使用方法: python3 enhanced_web_server.py")

if __name__ == "__main__":
    print("=== 出願人情報を含む検索テスト ===")
    update_search_functionality()
    
    print("\n=== 拡張Webサーバーの作成 ===")
    create_enhanced_web_server()
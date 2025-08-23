#!/usr/bin/env python3
"""
TMCloud シンプルWEBインターフェース v2
最適化された検索モジュールを使用
"""

from flask import Flask, jsonify, request, Response
from pathlib import Path
import json
from tmcloud_search_optimized import TMCloudOptimizedSearch

app = Flask(__name__)

# データベースパス
DB_PATH = Path(__file__).parent / "tmcloud_v2_20250818_081655.db"

@app.route('/')
def index():
    """トップページ"""
    return """
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <title>TMCloud v2 - 高速商標検索</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .search-box { margin: 20px 0; padding: 20px; border: 1px solid #ddd; }
            input { padding: 10px; width: 300px; font-size: 16px; }
            button { padding: 10px 20px; font-size: 16px; margin-left: 10px; }
            .result { margin: 20px 0; padding: 20px; background: #f5f5f5; }
            .trademark-image { max-width: 200px; max-height: 200px; border: 1px solid #ccc; }
            .info-table { width: 100%; border-collapse: collapse; }
            .info-table td { padding: 8px; border: 1px solid #ddd; }
            .info-table td:first-child { font-weight: bold; width: 150px; background: #f0f0f0; }
        </style>
    </head>
    <body>
        <h1>TMCloud v2 - 高速商標検索</h1>
        
        <div class="search-box">
            <h2>出願番号検索</h2>
            <input type="text" id="app_num" placeholder="例: 2025064433">
            <button onclick="searchByAppNum()">検索</button>
        </div>
        
        <div class="search-box">
            <h2>商標名検索</h2>
            <input type="text" id="trademark" placeholder="例: プル">
            <button onclick="searchTrademark()">検索</button>
        </div>
        
        <div class="search-box">
            <h2>商標タイプ検索</h2>
            <select id="trademark_type">
                <option value="通常">通常</option>
                <option value="標準文字">標準文字</option>
                <option value="立体商標">立体商標</option>
                <option value="音商標">音商標</option>
            </select>
            <button onclick="searchByType()">検索</button>
        </div>
        
        <div id="results"></div>
        
        <script>
            async function searchByAppNum() {
                const app_num = document.getElementById('app_num').value;
                if (!app_num) return;
                
                const resultsDiv = document.getElementById('results');
                resultsDiv.innerHTML = '検索中...';
                
                try {
                    const response = await fetch(`/api/app_num/${app_num}`);
                    const data = await response.json();
                    
                    if (data.error) {
                        resultsDiv.innerHTML = `<div class="error">エラー: ${data.error}</div>`;
                    } else {
                        displayResult(data);
                    }
                } catch (error) {
                    resultsDiv.innerHTML = `<div class="error">エラー: ${error.message}</div>`;
                }
            }
            
            async function searchTrademark() {
                const keyword = document.getElementById('trademark').value;
                if (!keyword) return;
                
                const resultsDiv = document.getElementById('results');
                resultsDiv.innerHTML = '検索中...';
                
                try {
                    const response = await fetch(`/api/trademark/${encodeURIComponent(keyword)}`);
                    const data = await response.json();
                    
                    if (data.error) {
                        resultsDiv.innerHTML = `<div class="error">エラー: ${data.error}</div>`;
                    } else {
                        displayResults(data.results);
                    }
                } catch (error) {
                    resultsDiv.innerHTML = `<div class="error">エラー: ${error.message}</div>`;
                }
            }
            
            async function searchByType() {
                const type = document.getElementById('trademark_type').value;
                
                const resultsDiv = document.getElementById('results');
                resultsDiv.innerHTML = '検索中...';
                
                try {
                    const response = await fetch(`/api/type/${encodeURIComponent(type)}`);
                    const data = await response.json();
                    
                    if (data.error) {
                        resultsDiv.innerHTML = `<div class="error">エラー: ${data.error}</div>`;
                    } else {
                        displayResults(data.results);
                    }
                } catch (error) {
                    resultsDiv.innerHTML = `<div class="error">エラー: ${error.message}</div>`;
                }
            }
            
            function displayResult(data) {
                const resultsDiv = document.getElementById('results');
                const info = data.basic_info;
                
                let html = '<div class="result">';
                html += '<h3>検索結果</h3>';
                html += '<table class="info-table">';
                
                // 基本情報
                html += `<tr><td>出願番号</td><td>${info.app_num || 'N/A'}</td></tr>`;
                html += `<tr><td>出願日</td><td>${info.app_date || 'N/A'}</td></tr>`;
                html += `<tr><td>登録番号</td><td>${info.reg_num || 'N/A'}</td></tr>`;
                html += `<tr><td>登録日</td><td>${info.reg_date || 'N/A'}</td></tr>`;
                
                // 商標名または画像
                if (info.trademark_image_data) {
                    html += `<tr><td>商標</td><td>`;
                    html += `<img src="data:image/jpeg;base64,${info.trademark_image_data}" class="trademark-image">`;
                    html += `</td></tr>`;
                } else {
                    html += `<tr><td>商標名</td><td>${info.trademark_name || 'N/A'}</td></tr>`;
                }
                
                html += `<tr><td>商標タイプ</td><td>${info.trademark_type || 'N/A'}</td></tr>`;
                
                // 称呼
                if (info.phonetics && info.phonetics.length > 0) {
                    html += `<tr><td>称呼</td><td>${info.phonetics.join('、')}</td></tr>`;
                }
                
                // 出願人
                if (info.applicants && info.applicants.length > 0) {
                    html += `<tr><td>出願人</td><td>${info.applicants.join('、')}</td></tr>`;
                }
                
                // 区分
                if (info.classes && info.classes.length > 0) {
                    html += `<tr><td>区分</td><td>第${info.classes.join('、')}類</td></tr>`;
                }
                
                // 商品・役務
                if (info.goods_services) {
                    for (const [cls, goods] of Object.entries(info.goods_services)) {
                        html += `<tr><td>第${cls}類</td><td>${goods}</td></tr>`;
                    }
                }
                
                html += '</table>';
                html += '</div>';
                
                resultsDiv.innerHTML = html;
            }
            
            function displayResults(results) {
                const resultsDiv = document.getElementById('results');
                
                if (!results || results.length === 0) {
                    resultsDiv.innerHTML = '<div class="result">検索結果なし</div>';
                    return;
                }
                
                let html = '<div class="result">';
                html += `<h3>検索結果（${results.length}件）</h3>`;
                html += '<table class="info-table">';
                html += '<tr><th>出願番号</th><th>商標名</th><th>出願日</th><th>登録番号</th></tr>';
                
                for (const r of results.slice(0, 50)) {
                    html += '<tr>';
                    html += `<td>${r.app_num}</td>`;
                    html += `<td>${r.trademark_name || 'N/A'}</td>`;
                    html += `<td>${r.app_date || 'N/A'}</td>`;
                    html += `<td>${r.reg_num || 'N/A'}</td>`;
                    html += '</tr>';
                }
                
                html += '</table>';
                html += '</div>';
                
                resultsDiv.innerHTML = html;
            }
        </script>
    </body>
    </html>
    """

@app.route('/api/app_num/<app_num>')
def api_app_num(app_num):
    """出願番号API"""
    try:
        searcher = TMCloudOptimizedSearch(str(DB_PATH))
        result = searcher.get_full_info(app_num)
        searcher.close()
        
        if result:
            return jsonify(result)
        else:
            return jsonify({'error': 'データが見つかりません'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/trademark/<keyword>')
def api_trademark(keyword):
    """商標名検索API"""
    try:
        from tmcloud_search_simple import TMCloudSimpleSearch
        searcher = TMCloudSimpleSearch(str(DB_PATH))
        results = searcher.search_trademark(keyword, limit=100)
        searcher.close()
        
        return jsonify({'results': results, 'count': len(results)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/type/<type_name>')
def api_type(type_name):
    """商標タイプ検索API"""
    try:
        from tmcloud_search_simple import TMCloudSimpleSearch
        searcher = TMCloudSimpleSearch(str(DB_PATH))
        results = searcher.search_by_trademark_type(type_name, limit=100)
        searcher.close()
        
        return jsonify({'results': results, 'count': len(results)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/image/<app_num>')
def api_image(app_num):
    """画像データ取得API（別途）"""
    try:
        from tmcloud_search_simple import TMCloudSimpleSearch
        searcher = TMCloudSimpleSearch(str(DB_PATH))
        image_data = searcher.get_image(app_num)
        searcher.close()
        
        if image_data:
            return jsonify({'app_num': app_num, 'image_data': image_data})
        else:
            return jsonify({'error': '画像データがありません'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print(f"データベース: {DB_PATH}")
    print("サーバー起動中...")
    print("ブラウザで http://localhost:5001 を開いてください")
    app.run(debug=True, host='0.0.0.0', port=5001)
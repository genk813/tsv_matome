#!/usr/bin/env python3
"""
TMCloud 簡易Webインターフェース
将来のFlask Webサービスへの第一歩
"""

from flask import Flask, render_template_string, request, jsonify
from tmcloud_search_integrated import TMCloudIntegratedSearch
from pathlib import Path

app = Flask(__name__)

# データベースパス（変更可能）
DB_PATH = Path(__file__).parent / "tmcloud_v2_20250810_restored.db"

# HTMLテンプレート（シンプル版）
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>TMCloud 商標検索</title>
    <meta charset="utf-8">
    <style>
        body { font-family: sans-serif; margin: 20px; }
        .search-box { margin: 20px 0; padding: 20px; background: #f0f0f0; border-radius: 8px; }
        input[type="text"] { width: 300px; padding: 5px; }
        button { padding: 5px 15px; cursor: pointer; }
        button:hover { opacity: 0.9; }
        .result { border: 1px solid #ddd; margin: 10px 0; padding: 10px; border-radius: 4px; }
        .result h3 { margin: 0 0 10px 0; color: #333; }
        .field { margin: 5px 0; }
        .field-label { font-weight: bold; display: inline-block; width: 120px; }
        .goods-services { margin-left: 120px; }
        .similar-codes { margin-left: 120px; }
        #searchConditions { max-height: 400px; overflow-y: auto; }
        .condition-item { transition: all 0.3s ease; }
        .condition-item:hover { background: #e8f4f8 !important; }
    </style>
</head>
<body>
    <h1>TMCloud 商標検索システム</h1>
    
    <div class="search-box">
        <form id="searchForm">
            <label>検索タイプ: 
                <select name="search_type">
                    <option value="trademark">商標名</option>
                    <option value="phonetic">称呼</option>
                    <option value="app_num">出願番号</option>
                    <option value="reg_num">登録番号</option>
                    <option value="applicant">出願人</option>
                    <option value="similar_group">類似群コード</option>
                    <option value="goods_services">商品・役務</option>
                </select>
            </label>
            <input type="text" name="keyword" placeholder="検索キーワード" required>
            <button type="submit">検索</button>
        </form>
    </div>
    
    <!-- 複合条件検索 -->
    <div class="search-box" style="margin-top: 20px; background-color: #f0f8ff;">
        <h3>複合条件検索</h3>
        <form id="complexSearchForm">
            <div style="margin-bottom: 10px;">
                <label>演算子:
                    <select id="globalOperator">
                        <option value="AND">すべての条件を満たす（AND）</option>
                        <option value="OR">いずれかの条件を満たす（OR）</option>
                    </select>
                </label>
            </div>
            <div id="searchConditions">
                <!-- 動的に条件が追加される -->
            </div>
            <div style="margin-top: 10px;">
                <button type="button" onclick="addCondition()" style="background: #28a745; color: white; padding: 5px 10px;">+ 条件を追加</button>
                <button type="submit" style="margin-left: 10px;">検索実行</button>
            </div>
        </form>
    </div>
    
    <div id="results"></div>
    
    <script>
        // XSS対策用のエスケープ関数
        const esc = (s) => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;', "'":'&#39;'}[c]));
        
        // 条件のカウンター
        let conditionCount = 0;
        
        // 現在の検索結果を保持
        let currentSearchResults = null;
        
        // 検索タイプのオプション
        const searchTypes = [
            {value: 'trademark', label: '商標名'},
            {value: 'phonetic', label: '称呼'},
            {value: 'app_num', label: '出願番号'},
            {value: 'reg_num', label: '登録番号'},
            {value: 'class', label: '区分'},
            {value: 'applicant', label: '出願人'},
            {value: 'similar_group', label: '類似群コード'},
            {value: 'goods_services', label: '商品・役務'}
        ];
        
        // 条件を追加する関数
        function addCondition() {
            conditionCount++;
            const container = document.getElementById('searchConditions');
            const condDiv = document.createElement('div');
            condDiv.id = `condition_${conditionCount}`;
            condDiv.className = 'condition-item';
            condDiv.style.marginBottom = '10px';
            condDiv.style.padding = '10px';
            condDiv.style.background = '#f8f9fa';
            condDiv.style.border = '1px solid #dee2e6';
            condDiv.style.borderRadius = '4px';
            
            let optionsHtml = searchTypes.map(t => 
                `<option value="${t.value}">${t.label}</option>`
            ).join('');
            
            condDiv.innerHTML = `
                <label>条件${conditionCount}:
                    <select id="type_${conditionCount}">
                        ${optionsHtml}
                    </select>
                    <input type="text" id="keyword_${conditionCount}" placeholder="キーワード" style="width: 250px;">
                    <button type="button" onclick="removeCondition(${conditionCount})" style="background: #dc3545; color: white; padding: 3px 8px; margin-left: 10px;">削除</button>
                </label>
            `;
            
            container.appendChild(condDiv);
        }
        
        // 条件を削除する関数
        function removeCondition(id) {
            const elem = document.getElementById(`condition_${id}`);
            if (elem) {
                elem.remove();
            }
        }
        
        // 初期状態で2つの条件を追加
        window.addEventListener('DOMContentLoaded', () => {
            addCondition();
            addCondition();
        });
        
        document.getElementById('searchForm').onsubmit = async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = '検索中...';
            
            try {
                const response = await fetch('/search', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        search_type: formData.get('search_type'),
                        keyword: formData.get('keyword')
                    })
                });
                
                const data = await response.json();
                displayResults(data);
            } catch (error) {
                resultsDiv.innerHTML = 'エラー: ' + error.message;
            }
        };
        
        // 複合検索フォームの処理
        document.getElementById('complexSearchForm').onsubmit = async (e) => {
            e.preventDefault();
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = '検索中...';
            
            // すべての条件を収集
            const conditions = [];
            const conditionDivs = document.querySelectorAll('[id^="condition_"]');
            
            conditionDivs.forEach(div => {
                const id = div.id.split('_')[1];
                const type = document.getElementById(`type_${id}`)?.value;
                const keyword = document.getElementById(`keyword_${id}`)?.value;
                
                if (type && keyword) {
                    conditions.push({
                        type: type,
                        keyword: keyword
                    });
                }
            });
            
            const operator = document.getElementById('globalOperator').value;
            
            console.log('送信条件:', conditions, 'operator:', operator);  // デバッグ
            
            if (conditions.length === 0) {
                resultsDiv.innerHTML = '少なくとも1つの条件を入力してください';
                return;
            }
            
            try {
                const response = await fetch('/search_complex', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        conditions: conditions,
                        operator: operator,
                        sort_by: 'app_date_desc'  // デフォルトのソート
                    })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                console.log('複合検索結果:', data);  // デバッグ
                displayResults(data);
            } catch (error) {
                console.error('複合検索エラー:', error);
                resultsDiv.innerHTML = 'エラー: ' + error.message;
            }
        };
        
        function displayResults(data) {
            const resultsDiv = document.getElementById('results');
            
            if (data.error) {
                resultsDiv.innerHTML = `<div style="color: red">エラー: ${esc(data.error)}</div>`;
                return;
            }
            
            if (!data.results || data.results.length === 0) {
                resultsDiv.innerHTML = '<div>検索結果がありません。</div>';
                return;
            }
            
            // 検索結果を保持
            currentSearchResults = data;
            
            let html = `<h2>検索結果: ${esc(data.results.length)}件</h2>`;
            
            // 並び替えセレクタを追加
            html += `
                <div style="margin: 10px 0;">
                    <label>並び替え: 
                        <select id="sortSelector" onchange="sortResults()">
                            <option value="app_date_desc">出願日（新しい順）</option>
                            <option value="app_date_asc">出願日（古い順）</option>
                            <option value="reg_date_desc">登録日（新しい順）</option>
                            <option value="reg_date_asc">登録日（古い順）</option>
                            <option value="trademark_asc">商標名（A-Z）</option>
                            <option value="trademark_desc">商標名（Z-A）</option>
                        </select>
                    </label>
                </div>
            `;
            
            // 複合検索の場合、検索条件を表示
            if (data.search_type === 'complex') {
                html += '<div style="margin: 10px 0; padding: 15px; background: #e8f4f8; border-left: 4px solid #17a2b8; border-radius: 4px;">';
                html += '<strong>検索条件:</strong><br>';
                if (data.conditions && data.conditions.length > 0) {
                    const typeLabels = {
                        'trademark': '商標名',
                        'phonetic': '称呼',
                        'app_num': '出願番号',
                        'reg_num': '登録番号',
                        'class': '区分',
                        'applicant': '出願人',
                        'similar_group': '類似群コード',
                        'goods_services': '商品・役務'
                    };
                    const conditionsText = data.conditions.map(c => 
                        `${typeLabels[c.type] || c.type}「${esc(c.keyword)}」`
                    ).join(` ${data.operator || 'AND'} `);
                    html += conditionsText;
                }
                html += '</div>';
            }
            
            data.results.forEach((result, index) => {
                const info = result.basic_info || result;
                
                // 商標名または商標画像を表示
                let trademarkDisplay = '';
                if (info.trademark_name === '[商標画像]' && info.trademark_image_data) {
                    // Base64エンコードされた画像を表示
                    trademarkDisplay = `<img src="data:image/jpeg;base64,${info.trademark_image_data}" alt="商標画像" style="max-width: 200px; max-height: 200px; display: block; margin: 10px 0;">`;
                } else {
                    trademarkDisplay = esc(info.trademark_name || 'N/A');
                }
                
                html += `
                    <div class="result">
                        <h3>[${index + 1}] ${trademarkDisplay}</h3>
                        <div class="field"><span class="field-label">出願番号:</span> ${esc(info.app_num || 'N/A')}</div>
                        <div class="field"><span class="field-label">登録番号:</span> ${esc(info.reg_num || 'N/A')}</div>
                        <div class="field"><span class="field-label">出願日:</span> ${esc(info.app_date || 'N/A')}</div>
                        <div class="field"><span class="field-label">登録日:</span> ${esc(info.reg_date || 'N/A')}</div>
                        <div class="field"><span class="field-label">区分:</span> ${info.classes ? info.classes.map(c => esc(c)).join(', ') : 'N/A'}</div>
                `;
                
                if (info.phonetics && info.phonetics.length > 0) {
                    html += `<div class="field"><span class="field-label">称呼:</span> ${info.phonetics.map(p => esc(p)).join(', ')}</div>`;
                }
                
                // 出願人
                if (info.applicants && info.applicants.length > 0) {
                    html += `<div class="field"><span class="field-label">出願人:</span> ${info.applicants.map(a => esc(a)).join(', ')}</div>`;
                }
                
                // 代理人
                if (info.agents && info.agents.length > 0) {
                    html += `<div class="field"><span class="field-label">代理人:</span> ${info.agents.map(a => esc(a)).join(', ')}</div>`;
                }
                
                // 権利者
                if (info.right_holders && info.right_holders.length > 0) {
                    html += `<div class="field"><span class="field-label">権利者:</span> ${info.right_holders.map(r => esc(r)).join(', ')}</div>`;
                }
                
                // ステータス情報
                if (info.final_disposition_type) {
                    html += `<div class="field"><span class="field-label">最終処分コード:</span> ${esc(info.final_disposition_type)}</div>`;
                }
                if (info.final_disposition_article) {
                    html += `<div class="field"><span class="field-label">最終処分記事:</span> ${esc(info.final_disposition_article)}</div>`;
                }
                if (info.final_disposition_date) {
                    html += `<div class="field"><span class="field-label">最終処分日:</span> ${esc(info.final_disposition_date)}</div>`;
                }
                
                // 公報情報
                if (info.reg_article_gazette_date) {
                    html += `<div class="field"><span class="field-label">登録公報発行日:</span> ${esc(info.reg_article_gazette_date)}</div>`;
                }
                if (info.pub_article_gazette_date) {
                    html += `<div class="field"><span class="field-label">公開公報発行日:</span> ${esc(info.pub_article_gazette_date)}</div>`;
                }
                
                // 存続期間・分納情報
                if (info.conti_prd_expire_date) {
                    html += `<div class="field"><span class="field-label">存続期間満了日:</span> ${esc(info.conti_prd_expire_date)}</div>`;
                }
                if (info.next_pen_payment_limit_date) {
                    html += `<div class="field"><span class="field-label">次回分納期限日:</span> ${esc(info.next_pen_payment_limit_date)}</div>`;
                }
                
                // 出願種別・付加情報
                const appTypes = [];
                if (info.app_type1) appTypes.push(info.app_type1);
                if (info.app_type2) appTypes.push(info.app_type2);
                if (info.app_type3) appTypes.push(info.app_type3);
                if (info.app_type4) appTypes.push(info.app_type4);
                if (info.app_type5) appTypes.push(info.app_type5);
                if (appTypes.length > 0) {
                    html += `<div class="field"><span class="field-label">出願種別:</span> ${appTypes.map(t => esc(t)).join(', ')}</div>`;
                }
                if (info.orig_app_type) {
                    html += `<div class="field"><span class="field-label">元出願種別:</span> ${esc(info.orig_app_type)}</div>`;
                }
                if (info.article3_2_flag === '1') {
                    html += `<div class="field"><span class="field-label">3条2項適用:</span> あり</div>`;
                }
                if (info.article5_4_flag === '1') {
                    html += `<div class="field"><span class="field-label">5条4項適用:</span> あり</div>`;
                }
                
                // 審査・査定情報
                if (info.exam_type) {
                    html += `<div class="field"><span class="field-label">審査種別:</span> ${esc(info.exam_type)}</div>`;
                }
                if (info.decision_type) {
                    html += `<div class="field"><span class="field-label">査定種別:</span> ${esc(info.decision_type)}</div>`;
                }
                
                // 審判情報
                if (info.appeal_nums && info.appeal_nums.length > 0) {
                    html += `<div class="field"><span class="field-label">審判番号:</span> ${info.appeal_nums.map(n => esc(n)).join(', ')}</div>`;
                }
                if (info.appeal_types && info.appeal_types.length > 0) {
                    html += `<div class="field"><span class="field-label">審判種別:</span> ${info.appeal_types.map(t => esc(t)).join(', ')}</div>`;
                }
                
                // 出願人住所・国県コード
                if (info.applicant_addresses && info.applicant_addresses.length > 0) {
                    const nonEmptyAddresses = info.applicant_addresses.filter(a => a && a.trim());
                    if (nonEmptyAddresses.length > 0) {
                        html += `<div class="field"><span class="field-label">出願人住所:</span> ${nonEmptyAddresses.map(a => esc(a)).join(', ')}</div>`;
                    }
                }
                if (info.applicant_country_codes && info.applicant_country_codes.length > 0) {
                    const nonEmptyCodes = info.applicant_country_codes.filter(c => c && c.trim());
                    if (nonEmptyCodes.length > 0) {
                        html += `<div class="field"><span class="field-label">国県コード:</span> ${nonEmptyCodes.map(c => esc(c)).join(', ')}</div>`;
                    }
                }
                
                // 中間記録を審査・審判・登録に分けて表示
                if (info.progress_records) {
                    // バックエンドから分類済みのデータを受け取る
                    const examRecords = info.progress_records.exam || [];
                    const trialRecords = info.progress_records.trial || [];
                    const registrationRecords = info.progress_records.registration || [];
                    
                    // 審査中間記録
                    if (examRecords.length > 0) {
                        html += `<div class="field"><span class="field-label">審査中間記録 (${examRecords.length}件):</span><br>`;
                        examRecords.forEach(record => {
                            const [code, date] = record.split(':');
                            html += `&nbsp;&nbsp;• ${esc(code)} (${esc(date)})<br>`;
                        });
                        html += `</div>`;
                    }
                    
                    // 審判中間記録
                    if (trialRecords.length > 0) {
                        html += `<div class="field"><span class="field-label">審判中間記録 (${trialRecords.length}件):</span><br>`;
                        trialRecords.forEach(record => {
                            const [code, date] = record.split(':');
                            html += `&nbsp;&nbsp;• ${esc(code)} (${esc(date)})<br>`;
                        });
                        html += `</div>`;
                    }
                    
                    // 登録中間記録
                    if (registrationRecords.length > 0) {
                        html += `<div class="field"><span class="field-label">登録中間記録 (${registrationRecords.length}件):</span><br>`;
                        registrationRecords.forEach(record => {
                            const [code, date] = record.split(':');
                            html += `&nbsp;&nbsp;• ${esc(code)} (${esc(date)})<br>`;
                        });
                        html += `</div>`;
                    }
                }
                
                // 旧フィールド（互換性のため残す）
                if (info.disposition_code) {
                    html += `<div class="field"><span class="field-label">最終処分コード:</span> ${esc(info.disposition_code)}</div>`;
                }
                if (info.disposition_date) {
                    html += `<div class="field"><span class="field-label">最終処分日:</span> ${esc(info.disposition_date)}</div>`;
                }
                if (info.status) {
                    html += `<div class="field"><span class="field-label">ステータス:</span> ${esc(info.status)}</div>`;
                }
                
                if (info.goods_services) {
                    html += '<div class="field"><span class="field-label">商品・役務:</span></div>';
                    for (const [cls, goods] of Object.entries(info.goods_services)) {
                        // 全文表示（折りたたみ廃止）
                        html += `<div class="goods-services">区分${esc(cls)}: ${esc(goods)}</div>`;
                    }
                }
                
                if (info.similar_groups) {
                    html += '<div class="field"><span class="field-label">類似群コード:</span></div>';
                    for (const [cls, codes] of Object.entries(info.similar_groups)) {
                        html += `<div class="similar-codes">区分${esc(cls)}: ${codes.map(c => esc(c)).join(', ')}</div>`;
                    }
                }
                
                html += '</div>';
            });
            
            resultsDiv.innerHTML = html;
        }
        
        // 並び替え関数
        function sortResults() {
            if (!currentSearchResults || !currentSearchResults.results) return;
            
            const sortBy = document.getElementById('sortSelector').value;
            const results = [...currentSearchResults.results]; // コピーを作成
            
            // ソート処理
            results.sort((a, b) => {
                const infoA = a.basic_info || a;
                const infoB = b.basic_info || b;
                
                let valA, valB;
                
                switch(sortBy) {
                    case 'app_date_desc':
                        valA = infoA.app_date || '';
                        valB = infoB.app_date || '';
                        return valB.localeCompare(valA);
                    case 'app_date_asc':
                        valA = infoA.app_date || '';
                        valB = infoB.app_date || '';
                        return valA.localeCompare(valB);
                    case 'reg_date_desc':
                        valA = infoA.reg_date || '';
                        valB = infoB.reg_date || '';
                        return valB.localeCompare(valA);
                    case 'reg_date_asc':
                        valA = infoA.reg_date || '';
                        valB = infoB.reg_date || '';
                        return valA.localeCompare(valB);
                    case 'trademark_asc':
                        valA = infoA.trademark_name || '';
                        valB = infoB.trademark_name || '';
                        return valA.localeCompare(valB);
                    case 'trademark_desc':
                        valA = infoA.trademark_name || '';
                        valB = infoB.trademark_name || '';
                        return valB.localeCompare(valA);
                    default:
                        return 0;
                }
            });
            
            // ソート済みの結果で再表示
            const sortedData = {...currentSearchResults, results: results};
            displayResults(sortedData);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """トップページ"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/search', methods=['POST'])
def search():
    """検索API"""
    try:
        data = request.json
        search_type = data.get('search_type', 'trademark')
        keyword = data.get('keyword', '')
        
        if not keyword:
            return jsonify({'error': 'キーワードを入力してください'}), 400
        
        # 毎回新しい接続を作成（コネクション切れ対策）
        searcher = TMCloudIntegratedSearch(str(DB_PATH))
        
        if search_type == 'trademark':
            results = searcher.search_trademark_name(keyword, limit=3000, unified_format=True)
        elif search_type == 'phonetic':
            results = searcher.search_phonetic(keyword, limit=3000, unified_format=True)
        elif search_type == 'app_num':
            result = searcher.search_by_app_num(keyword, unified_format=True)  # 単一番号検索
            results = [result] if result else []  # リストに変換
        elif search_type == 'reg_num':
            result = searcher.search_by_reg_num(keyword, unified_format=True)  # 単一番号検索
            results = [result] if result else []  # リストに変換
        elif search_type == 'applicant':
            results = searcher.search_applicant(keyword, limit=3000, unified_format=True)
        elif search_type == 'similar_group':
            results = searcher.search_by_similar_group(keyword, limit=3000, unified_format=True)
        elif search_type == 'goods_services':
            results = searcher.search_goods_services(keyword, limit=3000, item_and=True, unified_format=True)
        else:
            return jsonify({'error': '不明な検索タイプ'})
        
        
        return jsonify({
            'results': results,
            'count': len(results),
            'search_type': search_type,
            'keyword': keyword
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/search_complex', methods=['POST'])
def search_complex():
    """複合条件検索API"""
    try:
        data = request.json
        conditions = data.get('conditions', [])
        operator = data.get('operator', 'AND')
        
        if not conditions:
            return jsonify({'error': '検索条件を入力してください'}), 400
        
        # 毎回新しい接続を作成
        searcher = TMCloudIntegratedSearch(str(DB_PATH))
        
        # 複合検索実行（より多くの結果を取得）
        results = searcher.search_complex(conditions, operator=operator, limit=3000, unified_format=True)
        
        return jsonify({
            'results': results,
            'count': len(results),
            'search_type': 'complex',
            'conditions': conditions,
            'operator': operator
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import os
    print(f"データベース: {DB_PATH}")
    print("サーバー起動中...")
    
    # 環境変数から設定を読み込み（本番対応）
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    host = os.environ.get('FLASK_HOST', '0.0.0.0')  # 全インターフェースでリッスン
    port = int(os.environ.get('FLASK_PORT', '5000'))
    
    print(f"ブラウザで http://{host}:{port} を開いてください")
    print("終了: Ctrl+C")
    app.run(debug=debug, host=host, port=port)
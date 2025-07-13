#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
改善版商標検索結果HTML生成ツール
レスポンシブデザイン + 折りたたみ機能付き
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from cli_trademark_search import TrademarkSearchCLI

class ImprovedSearchResultsHTMLGenerator:
    """改善版検索結果HTML生成クラス"""
    
    def __init__(self, output_dir: str = "search_results/html"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.searcher = TrademarkSearchCLI()
    
    def generate_html_template(self, search_params: Dict[str, Any], results: List[Dict[str, Any]], 
                              total_count: int) -> str:
        """改善されたHTML テンプレート生成"""
        
        # 検索条件の文字列化
        search_conditions = []
        if search_params.get('app_num'):
            search_conditions.append(f"出願番号: {search_params['app_num']}")
        if search_params.get('mark_text'):
            search_conditions.append(f"商標文字: {search_params['mark_text']}")
        if search_params.get('goods_classes'):
            search_conditions.append(f"商品区分: {search_params['goods_classes']}")
        if search_params.get('designated_goods'):
            search_conditions.append(f"指定商品: {search_params['designated_goods']}")
        if search_params.get('similar_group_codes'):
            search_conditions.append(f"類似群コード: {search_params['similar_group_codes']}")
        
        search_condition_text = " / ".join(search_conditions) if search_conditions else "全件検索"
        
        html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>商標検索結果 - {search_condition_text}</title>
    <style>
        * {{
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Hiragino Sans', 'Hiragino Kaku Gothic ProN', Meiryo, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f8f9fa;
            color: #333;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 3px solid #007bff;
        }}
        .header h1 {{
            color: #007bff;
            margin: 0;
            font-size: 2.5em;
            font-weight: 700;
        }}
        .search-info {{
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            border-left: 5px solid #2196f3;
        }}
        .search-info h2 {{
            margin: 0 0 10px 0;
            color: #1976d2;
            font-weight: 600;
        }}
        .results-summary {{
            background: linear-gradient(135deg, #f1f8e9 0%, #dcedc8 100%);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
            border-left: 5px solid #4caf50;
        }}
        .trademark-card {{
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
        }}
        .trademark-card:hover {{
            box-shadow: 0 6px 25px rgba(0,0,0,0.15);
            transform: translateY(-2px);
        }}
        .trademark-title {{
            font-size: 1.5em;
            font-weight: bold;
            color: #2e7d32;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 2px solid #81c784;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .trademark-info {{
            margin-bottom: 20px;
        }}
        .info-section {{
            margin-bottom: 20px;
            border: 1px solid #e9ecef;
            border-radius: 10px;
            overflow: hidden;
            background: #fafafa;
        }}
        .section-header {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 15px 20px;
            font-weight: 600;
            color: #495057;
            border-bottom: 1px solid #dee2e6;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: background-color 0.3s ease;
        }}
        .section-header:hover {{
            background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%);
        }}
        .section-content {{
            padding: 20px;
            background: white;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
        }}
        .info-item {{
            padding: 12px 16px;
            background-color: #ffffff;
            border-radius: 8px;
            border: 1px solid #e9ecef;
            border-left: 4px solid #6c757d;
            transition: all 0.2s ease;
        }}
        .info-item:hover {{
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transform: translateY(-1px);
        }}
        .info-label {{
            font-weight: 600;
            color: #495057;
            display: block;
            margin-bottom: 4px;
            font-size: 0.9em;
        }}
        .info-value {{
            color: #212529;
            font-size: 1em;
        }}
        .text-expandable {{
            position: relative;
        }}
        .text-content {{
            display: block;
            word-wrap: break-word;
        }}
        .text-content.collapsed {{
            max-height: 80px;
            overflow: hidden;
            position: relative;
        }}
        .text-content.collapsed::after {{
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 30px;
            background: linear-gradient(transparent, white);
        }}
        .expand-btn {{
            background: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.85em;
            padding: 6px 12px;
            margin-top: 8px;
            transition: background-color 0.3s ease;
        }}
        .expand-btn:hover {{
            background: #0056b3;
        }}
        .section-toggle {{
            font-size: 1.1em;
            color: #6c757d;
            transition: transform 0.3s ease;
        }}
        .section-collapsed .section-toggle {{
            transform: rotate(-90deg);
        }}
        .basic-info {{
            border-left-color: #28a745;
            background: linear-gradient(135deg, #f8fff9 0%, #f1f8f3 100%);
        }}
        .registration-info {{
            border-left-color: #007bff;
            background: linear-gradient(135deg, #f8fbff 0%, #f1f7ff 100%);
        }}
        .dates-info {{
            border-left-color: #17a2b8;
            background: linear-gradient(135deg, #f8fdfe 0%, #f1fafe 100%);
        }}
        .business-info {{
            border-left-color: #6f42c1;
            background: linear-gradient(135deg, #fbf9ff 0%, #f7f3ff 100%);
        }}
        .content-info {{
            border-left-color: #fd7e14;
            background: linear-gradient(135deg, #fff9f5 0%, #fef5f0 100%);
        }}
        .additional-info {{
            border-left-color: #6c757d;
            background: linear-gradient(135deg, #f9f9f9 0%, #f5f5f5 100%);
        }}
        .status-registered {{
            color: #2e7d32;
            font-weight: bold;
            background: #e8f5e8;
            padding: 4px 8px;
            border-radius: 4px;
        }}
        .status-pending {{
            color: #f57c00;
            font-weight: bold;
            background: #fff3e0;
            padding: 4px 8px;
            border-radius: 4px;
        }}
        .image-status {{
            display: inline-block;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 0.9em;
            font-weight: bold;
        }}
        .image-yes {{
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }}
        .image-no {{
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }}
        .app-num {{
            font-family: 'Courier New', monospace;
            background-color: #e3f2fd;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 0.95em;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e0e0e0;
            color: #6c757d;
        }}
        @media (max-width: 768px) {{
            .section-content {{
                grid-template-columns: 1fr;
            }}
            .container {{
                padding: 15px;
            }}
            .info-item {{
                margin-bottom: 8px;
            }}
            .trademark-title {{
                font-size: 1.3em;
            }}
        }}
        @media (max-width: 480px) {{
            .section-header {{
                padding: 12px 15px;
                font-size: 0.95em;
            }}
            .section-content {{
                padding: 15px;
            }}
            .info-item {{
                padding: 10px 12px;
                font-size: 0.9em;
            }}
            .trademark-title {{
                font-size: 1.2em;
            }}
        }}
        .no-results {{
            text-align: center;
            padding: 60px 20px;
            color: #6c757d;
            font-size: 1.2em;
        }}
    </style>
    <script>
        function toggleSection(sectionId) {{
            const content = document.getElementById(sectionId);
            const header = content.previousElementSibling;
            const toggle = header.querySelector('.section-toggle');
            
            if (content.style.display === 'none') {{
                content.style.display = 'block';
                toggle.textContent = '▼';
                header.classList.remove('section-collapsed');
            }} else {{
                content.style.display = 'none';
                toggle.textContent = '▶';
                header.classList.add('section-collapsed');
            }}
        }}
        
        function toggleText(btn) {{
            const content = btn.previousElementSibling;
            if (content.classList.contains('collapsed')) {{
                content.classList.remove('collapsed');
                btn.textContent = '折りたたむ';
            }} else {{
                content.classList.add('collapsed');
                btn.textContent = 'さらに表示';
            }}
        }}
        
        document.addEventListener('DOMContentLoaded', function() {{
            // 長いテキストを自動的に折りたたむ
            const textContents = document.querySelectorAll('.text-content');
            textContents.forEach(content => {{
                if (content.textContent.trim().length > 150) {{
                    content.classList.add('collapsed');
                    const btn = content.nextElementSibling;
                    if (btn && btn.classList.contains('expand-btn')) {{
                        btn.textContent = 'さらに表示';
                        btn.style.display = 'inline-block';
                    }}
                }}
            }});
        }});
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 商標検索結果</h1>
        </div>
        
        <div class="search-info">
            <h2>📋 検索条件</h2>
            <p><strong>{search_condition_text}</strong></p>
            <p>検索日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}</p>
        </div>
        
        <div class="results-summary">
            <h3>📊 検索結果サマリー</h3>
            <p><strong>{len(results)}件</strong> を表示中 （総件数: <strong>{total_count}件</strong>）</p>
        </div>
"""
        
        if results:
            html += self.generate_results_html(results)
        else:
            html += """
        <div class="no-results">
            <h3>😔 検索結果が見つかりません</h3>
            <p>検索条件を変更して再度お試しください。</p>
        </div>
"""
        
        html += f"""
        <div class="footer">
            <p>🤖 自走商標検索システム v2.0 | 生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>"""
        
        return html
    
    def generate_results_html(self, results: List[Dict[str, Any]]) -> str:
        """改善された検索結果のHTML生成"""
        html = ""
        
        for i, result in enumerate(results, 1):
            # 出願番号のフォーマット
            app_num = result.get('app_num', 'N/A')
            formatted_app_num = self.format_app_num(app_num)
            
            # 登録状況の判定
            reg_date = result.get('reg_date')
            if reg_date and reg_date.strip():
                status_class = "status-registered"
                status_text = f"登録済み ({self.format_date(reg_date)})"
            else:
                status_class = "status-pending"
                status_text = "未登録"
            
            # 画像有無
            has_image = result.get('has_image', 'NO')
            image_class = "image-yes" if has_image == 'YES' else "image-no"
            image_text = "あり" if has_image == 'YES' else "なし"
            
            html += f"""
        <div class="trademark-card">
            <div class="trademark-title">
                <span>🏷️</span>
                <span>{i}. {result.get('mark_text', '（商標文字なし）')}</span>
            </div>
            
            <div class="trademark-info">
                <!-- 基本情報セクション -->
                <div class="info-section">
                    <div class="section-header" onclick="toggleSection('basic-{i}')">
                        <span>📋 基本情報</span>
                        <span class="section-toggle">▼</span>
                    </div>
                    <div class="section-content" id="basic-{i}">
                        <div class="info-item basic-info">
                            <span class="info-label">出願番号</span>
                            <span class="info-value app-num">{formatted_app_num}</span>
                        </div>
                        <div class="info-item basic-info">
                            <span class="info-label">出願日</span>
                            <span class="info-value">{self.format_date(result.get('app_date', ''))}</span>
                        </div>
                        <div class="info-item basic-info">
                            <span class="info-label">登録状況</span>
                            <span class="info-value {status_class}">{status_text}</span>
                        </div>
                        <div class="info-item basic-info">
                            <span class="info-label">画像</span>
                            <span class="info-value"><span class="image-status {image_class}">{image_text}</span></span>
                        </div>
                    </div>
                </div>

                <!-- 登録情報セクション -->
                <div class="info-section">
                    <div class="section-header" onclick="toggleSection('registration-{i}')">
                        <span>📜 登録情報</span>
                        <span class="section-toggle">▼</span>
                    </div>
                    <div class="section-content" id="registration-{i}">
                        <div class="info-item registration-info">
                            <span class="info-label">登録番号</span>
                            <span class="info-value">{result.get('registration_number', 'N/A')}</span>
                        </div>
                        <div class="info-item registration-info">
                            <span class="info-label">登録公報発行日</span>
                            <span class="info-value">{self.format_date(result.get('reg_gazette_date', ''))}</span>
                        </div>
                        <div class="info-item registration-info">
                            <span class="info-label">公開日</span>
                            <span class="info-value">{self.format_date(result.get('publication_date', ''))}</span>
                        </div>
                    </div>
                </div>

                <!-- 重要日程セクション -->
                <div class="info-section">
                    <div class="section-header" onclick="toggleSection('dates-{i}')">
                        <span>📅 重要日程</span>
                        <span class="section-toggle">▼</span>
                    </div>
                    <div class="section-content" id="dates-{i}">
                        <div class="info-item dates-info">
                            <span class="info-label">先願権発生日</span>
                            <span class="info-value">{self.format_date(result.get('prior_right_date', ''))}</span>
                        </div>
                        <div class="info-item dates-info">
                            <span class="info-label">存続期間満了日</span>
                            <span class="info-value">{self.format_date(result.get('expiry_date', ''))}</span>
                        </div>
                        <div class="info-item dates-info">
                            <span class="info-label">更新申請日</span>
                            <span class="info-value">{self.format_date(result.get('renewal_application_date', ''))}</span>
                        </div>
                        <div class="info-item dates-info">
                            <span class="info-label">更新登録日</span>
                            <span class="info-value">{self.format_date(result.get('renewal_registration_date', ''))}</span>
                        </div>
                        <div class="info-item dates-info">
                            <span class="info-label">拒絶査定発送日</span>
                            <span class="info-value">{self.format_date(result.get('rejection_dispatch_date', ''))}</span>
                        </div>
                        <div class="info-item dates-info">
                            <span class="info-label">審判請求日</span>
                            <span class="info-value">{self.format_date(result.get('trial_request_date', ''))}</span>
                        </div>
                    </div>
                </div>
"""
            
            # 申請人・権利者情報セクション
            if result.get('applicant_name') or result.get('right_person_name'):
                html += f"""
                <!-- 申請人・権利者情報セクション -->
                <div class="info-section">
                    <div class="section-header" onclick="toggleSection('business-{i}')">
                        <span>🏢 申請人・権利者情報</span>
                        <span class="section-toggle">▼</span>
                    </div>
                    <div class="section-content" id="business-{i}">"""
                
                if result.get('applicant_name'):
                    html += f"""
                        <div class="info-item business-info">
                            <span class="info-label">申請人</span>
                            <span class="info-value">{result.get('applicant_name')}</span>
                        </div>"""
                
                if result.get('right_person_name'):
                    html += f"""
                        <div class="info-item business-info">
                            <span class="info-label">権利者</span>
                            <span class="info-value">{result.get('right_person_name')}</span>
                        </div>"""
                    
                    if result.get('right_person_addr'):
                        html += f"""
                        <div class="info-item business-info">
                            <span class="info-label">権利者住所</span>
                            <span class="info-value">{result.get('right_person_addr')}</span>
                        </div>"""
                
                html += """
                    </div>
                </div>"""
            
            # 商品・役務情報セクション
            html += f"""
                <!-- 商品・役務情報セクション -->
                <div class="info-section">
                    <div class="section-header" onclick="toggleSection('content-{i}')">
                        <span>📦 商品・役務情報</span>
                        <span class="section-toggle">▼</span>
                    </div>
                    <div class="section-content" id="content-{i}">"""
            
            # 商品区分と区分数
            if result.get('goods_classes'):
                goods_classes = result.get('goods_classes')
                class_count = len([cls.strip() for cls in goods_classes.split(',') if cls.strip()])
                
                html += f"""
                        <div class="info-item content-info">
                            <span class="info-label">商品区分</span>
                            <span class="info-value">{goods_classes}</span>
                        </div>
                        <div class="info-item content-info">
                            <span class="info-label">区分数</span>
                            <span class="info-value">{class_count}区分</span>
                        </div>"""
            
            # 称呼
            if result.get('call_name'):
                html += f"""
                        <div class="info-item content-info">
                            <span class="info-label">称呼</span>
                            <span class="info-value">{result.get('call_name')}</span>
                        </div>"""
            
            # 指定商品・役務（長い場合は省略）
            if result.get('designated_goods'):
                designated_goods = result.get('designated_goods')
                if len(designated_goods) > 200:
                    html += f"""
                        <div class="info-item content-info" style="grid-column: 1 / -1;">
                            <span class="info-label">指定商品・役務</span>
                            <div class="text-expandable">
                                <span class="text-content collapsed">{designated_goods}</span>
                                <button class="expand-btn" onclick="toggleText(this)">さらに表示</button>
                            </div>
                        </div>"""
                else:
                    html += f"""
                        <div class="info-item content-info" style="grid-column: 1 / -1;">
                            <span class="info-label">指定商品・役務</span>
                            <span class="info-value">{designated_goods}</span>
                        </div>"""
            
            # 類似群コード
            if result.get('similar_group_codes'):
                similar_codes = self.format_similar_codes(result.get('similar_group_codes'))
                html += f"""
                        <div class="info-item content-info" style="grid-column: 1 / -1;">
                            <span class="info-label">類似群コード</span>
                            <div class="info-value">{similar_codes}</div>
                        </div>"""
            
            html += """
                    </div>
                </div>"""
            
            # 審判・付加情報セクション
            if result.get('trial_type') or result.get('additional_info'):
                html += f"""
                <!-- 審判・付加情報セクション -->
                <div class="info-section">
                    <div class="section-header" onclick="toggleSection('additional-{i}')">
                        <span>⚖️ 審判・付加情報</span>
                        <span class="section-toggle">▼</span>
                    </div>
                    <div class="section-content" id="additional-{i}">"""
                
                if result.get('trial_type'):
                    html += f"""
                        <div class="info-item additional-info">
                            <span class="info-label">審判種別</span>
                            <span class="info-value">{result.get('trial_type')}</span>
                        </div>"""
                
                if result.get('additional_info'):
                    html += f"""
                        <div class="info-item additional-info">
                            <span class="info-label">付加情報</span>
                            <span class="info-value">{result.get('additional_info')}</span>
                        </div>"""
                
                html += """
                    </div>
                </div>"""
            
            html += """
            </div>
        </div>
"""
        
        return html
    
    def format_app_num(self, app_num: str) -> str:
        """出願番号のフォーマット"""
        if not app_num or len(app_num) < 4:
            return app_num or "N/A"
        return f"{app_num[:4]}-{app_num[4:]}"
    
    def format_date(self, date_str: str) -> str:
        """日付のフォーマット"""
        if not date_str or len(date_str) != 8:
            return date_str or "N/A"
        try:
            year = date_str[0:4]
            month = date_str[4:6]
            day = date_str[6:8]
            return f"{year}年{month}月{day}日"
        except (ValueError, IndexError):
            return date_str
    
    def format_similar_codes(self, codes_str: str) -> str:
        """類似群コードのフォーマット"""
        if not codes_str:
            return ""
        
        # コードを分割して見やすく整形
        codes = codes_str.split(',')
        formatted_codes = []
        
        for code in codes[:15]:  # 最初の15個まで表示
            code = code.strip()
            if code:
                formatted_codes.append(f'<span style="background-color: #f0f8ff; padding: 3px 8px; border-radius: 4px; margin: 2px; display: inline-block; border: 1px solid #e0e8f0; font-family: monospace; font-size: 0.9em;">{code}</span>')
        
        if len(codes) > 15:
            formatted_codes.append(f'<span style="color: #666; font-style: italic;">... 他{len(codes) - 15}件</span>')
        
        return ' '.join(formatted_codes)
    
    def search_and_generate_html(self, search_params: Dict[str, Any]) -> str:
        """検索実行してHTML生成"""
        print(f"🔍 検索実行中: {search_params}")
        
        results, total_count = self.searcher.search_trademarks(**search_params)
        
        print(f"✅ 検索完了: {len(results)}件 / {total_count}件")
        
        html_content = self.generate_html_template(search_params, results, total_count)
        
        return html_content
    
    def save_html_file(self, html_content: str, filename: str) -> Path:
        """HTMLファイルの保存"""
        if not filename.endswith('.html'):
            filename += '.html'
        
        file_path = self.output_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return file_path

def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(description="改善版商標検索結果HTML生成ツール")
    parser.add_argument("--mark-text", help="商標文字")
    parser.add_argument("--app-num", help="出願番号")
    parser.add_argument("--goods-classes", help="商品区分")
    parser.add_argument("--designated-goods", help="指定商品・役務")
    parser.add_argument("--similar-group-codes", help="類似群コード")
    parser.add_argument("--limit", type=int, default=50, help="取得件数上限")
    parser.add_argument("--output", help="出力ファイル名（自動生成される場合省略可）")
    parser.add_argument("--output-dir", default="search_results/html", help="出力ディレクトリ")
    
    args = parser.parse_args()
    
    # 検索条件のチェック
    search_conditions = [args.mark_text, args.app_num, args.goods_classes, 
                        args.designated_goods, args.similar_group_codes]
    if not any(search_conditions):
        parser.error("少なくとも1つの検索条件を指定してください")
    
    try:
        generator = ImprovedSearchResultsHTMLGenerator(args.output_dir)
        
        # 検索パラメータの構築
        search_params = {
            'limit': args.limit
        }
        if args.mark_text:
            search_params['mark_text'] = args.mark_text
        if args.app_num:
            search_params['app_num'] = args.app_num
        if args.goods_classes:
            search_params['goods_classes'] = args.goods_classes
        if args.designated_goods:
            search_params['designated_goods'] = args.designated_goods
        if args.similar_group_codes:
            search_params['similar_group_codes'] = args.similar_group_codes
        
        # HTML生成
        html_content = generator.search_and_generate_html(search_params)
        
        # ファイル名の決定
        if args.output:
            filename = args.output
        else:
            # 自動生成
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            search_key = args.mark_text or args.app_num or "search"
            filename = f"improved_trademark_search_{search_key}_{timestamp}.html"
        
        # ファイル保存
        file_path = generator.save_html_file(html_content, filename)
        
        print(f"💾 改善版HTMLファイルを保存: {file_path}")
        print(f"🌐 ブラウザで開くには: file://{file_path.absolute()}")
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        exit(1)

if __name__ == "__main__":
    main()
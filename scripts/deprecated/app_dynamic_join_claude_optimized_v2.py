#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
商標検索システム - Flask版最適化アプリケーション v2
今日の改善を統合：拡張出願人マッピング、FTS検索、詳細検索オプション
"""

import os
import logging
import sqlite3
import math
import re
from pathlib import Path
from flask import Flask, render_template, request, flash, send_from_directory, url_for, jsonify
from typing import List, Dict, Any, Optional, Tuple

# --- 設定クラス ---
class Config:
    DB_PATH = os.environ.get('DB_PATH', Path(__file__).parent.resolve() / "output.db")
    PER_PAGE_OPTIONS = [20, 50, 100, 200]
    DEFAULT_PER_PAGE = 50
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    MAX_SEARCH_TERM_LENGTH = 100
    MAX_RESULTS_PER_PAGE = 200
    # 画像関連設定
    IMAGES_DIR = os.environ.get('IMAGES_DIR', Path(__file__).parent.resolve() / "images" / "final_complete")
    SERVE_IMAGES = True

# --- アプリケーション初期化 ---
app = Flask(__name__)
app.config.from_object(Config)

# Jinjaテンプレートにbuilt-in関数を追加
app.jinja_env.globals.update(max=max, min=min, len=len)

# ログ設定
if app.debug:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

# --- データベース関連 ---
def get_db_connection():
    """データベース接続を取得"""
    if not Path(app.config['DB_PATH']).exists():
        logger.error(f"データベースファイルが見つかりません: {app.config['DB_PATH']}")
        return None
    
    try:
        con = sqlite3.connect(app.config['DB_PATH'])
        con.row_factory = sqlite3.Row
        return con
    except sqlite3.Error as e:
        logger.error(f"データベース接続エラー: {e}")
        return None

def get_simple_search_results(search_params: Dict[str, Any]) -> Tuple[List[Dict], int]:
    """
    シンプルな検索結果を取得（元のロジックベース）
    """
    con = get_db_connection()
    if not con:
        return [], 0
    
    try:
        cur = con.cursor()
        
        # 検索パラメータを取得
        search_text = search_params.get('search_text', '').strip()
        applicant_name = search_params.get('applicant_name', '').strip()
        goods_class = search_params.get('goods_class', '').strip()
        date_from = search_params.get('date_from', '').strip()
        date_to = search_params.get('date_to', '').strip()
        
        # 動的WHERE句の構築
        where_parts = ["1=1"]
        params = []
        from_parts = ["FROM jiken_c_t j"]
        
        # 商標文字（全商標タイプを検索）
        if search_text:
            from_parts.append("LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num")
            from_parts.append("LEFT JOIN indct_use_t_art iu ON j.normalized_app_num = iu.normalized_app_num")
            from_parts.append("LEFT JOIN search_use_t_art_table su ON j.normalized_app_num = su.normalized_app_num")
            where_parts.append("(s.standard_char_t LIKE ? OR iu.indct_use_t LIKE ? OR su.search_use_t LIKE ?)")
            search_pattern = f"%{search_text}%"
            params.extend([search_pattern, search_pattern, search_pattern])
        
        # 出願人名（基本的な検索）
        if applicant_name:
            from_parts.append("LEFT JOIN reg_mapping rm ON j.normalized_app_num = rm.app_num")
            from_parts.append("LEFT JOIN right_person_art_t rp ON rm.reg_num = rp.reg_num")
            where_parts.append("rp.right_person_name LIKE ?")
            params.append(f"%{applicant_name}%")
        
        # 商品・役務区分
        if goods_class:
            from_parts.append("LEFT JOIN goods_class_art gca ON j.normalized_app_num = gca.normalized_app_num")
            where_parts.append("gca.goods_classes LIKE ?")
            params.append(f"%第{goods_class}類%")
        
        # 日付範囲
        if date_from:
            where_parts.append("j.shutugan_bi >= ?")
            params.append(date_from.replace('-', ''))
        
        if date_to:
            where_parts.append("j.shutugan_bi <= ?")
            params.append(date_to.replace('-', ''))
        
        sub_query_from = " ".join(from_parts)
        sub_query_where = " AND ".join(where_parts)
        
        # 総件数取得
        count_sql = f"SELECT COUNT(DISTINCT j.normalized_app_num) AS total {sub_query_from} WHERE {sub_query_where}"
        cur.execute(count_sql, tuple(params))
        total_count = cur.fetchone()[0]
        
        if total_count == 0:
            return [], 0
        
        # ページネーション
        page = search_params.get('page', 1)
        per_page = search_params.get('per_page', app.config['DEFAULT_PER_PAGE'])
        offset = (page - 1) * per_page
        
        # 対象の出願番号を取得
        app_num_sql = f"SELECT DISTINCT j.normalized_app_num {sub_query_from} WHERE {sub_query_where} ORDER BY j.normalized_app_num LIMIT ? OFFSET ?"
        cur.execute(app_num_sql, tuple(params + [per_page, offset]))
        app_num_rows = cur.fetchall()
        app_nums = [row[0] for row in app_num_rows]
        
        if not app_nums:
            return [], total_count
        
        # 最適化された単一クエリで全データを取得（元のロジック）
        placeholders = ",".join("?" for _ in app_nums)
        results_sql = f"""
            SELECT
                j.normalized_app_num AS app_num,
                COALESCE(s.standard_char_t, iu.indct_use_t, su.search_use_t) AS mark_text,
                j.shutugan_bi AS app_date,
                j.reg_reg_ymd AS reg_date,
                h.reg_num AS reg_no,
                h.right_person_name AS owner_name,
                h.right_person_addr AS owner_addr,
                COALESCE(am.applicant_name, 'コード:' || ap.shutugannindairinin_code) as applicant_name,
                GROUP_CONCAT(DISTINCT gca.goods_classes) AS goods_classes,
                CASE WHEN ts.image_data IS NOT NULL THEN 1 ELSE 0 END as has_image
            FROM jiken_c_t AS j
            LEFT JOIN standard_char_t_art AS s ON j.normalized_app_num = s.normalized_app_num
            LEFT JOIN indct_use_t_art AS iu ON j.normalized_app_num = iu.normalized_app_num
            LEFT JOIN search_use_t_art_table AS su ON j.normalized_app_num = su.normalized_app_num
            LEFT JOIN reg_mapping rm ON j.normalized_app_num = rm.app_num
            LEFT JOIN right_person_art_t AS h ON rm.reg_num = h.reg_num
            LEFT JOIN jiken_c_t_shutugannindairinin ap ON j.normalized_app_num = ap.shutugan_no 
                                                       AND ap.shutugannindairinin_sikbt = '1'
            LEFT JOIN applicant_mapping am ON ap.shutugannindairinin_code = am.applicant_code
            LEFT JOIN goods_class_art AS gca ON j.normalized_app_num = gca.normalized_app_num
            LEFT JOIN t_sample AS ts ON j.normalized_app_num = ts.normalized_app_num
            WHERE j.normalized_app_num IN ({placeholders})
            GROUP BY j.normalized_app_num
            ORDER BY j.normalized_app_num
        """
        
        cur.execute(results_sql, tuple(app_nums))
        results = cur.fetchall()
        
        # 結果を辞書形式に変換
        enhanced_results = []
        for row in results:
            result = dict(row)
            
            # 日付フォーマット
            if result['app_date']:
                app_date = result['app_date']
                result['app_date_formatted'] = f"{app_date[:4]}/{app_date[4:6]}/{app_date[6:]}"
            
            if result['reg_date']:
                reg_date = result['reg_date']
                result['reg_date_formatted'] = f"{reg_date[:4]}/{reg_date[4:6]}/{reg_date[6:]}"
            
            # 画像パスを設定
            if result['has_image']:
                result['image_path'] = f"/images/{result['app_num']}.jpg"
            
            enhanced_results.append(result)
        
        return enhanced_results, total_count
        
    except sqlite3.Error as e:
        logger.error(f"検索エラー: {e}")
        return [], 0
    finally:
        con.close()

def get_enhanced_search_results(search_params: Dict[str, Any]) -> Tuple[List[Dict], int]:
    """
    拡張検索結果を取得（今日の改善を統合）
    """
    con = get_db_connection()
    if not con:
        return [], 0
    
    try:
        cur = con.cursor()
        
        # 検索パラメータを取得
        search_text = search_params.get('search_text', '').strip()
        applicant_name = search_params.get('applicant_name', '').strip()
        goods_class = search_params.get('goods_class', '').strip()
        date_from = search_params.get('date_from', '').strip()
        date_to = search_params.get('date_to', '').strip()
        use_fts = search_params.get('use_fts', True)
        
        # FTS検索を優先的に使用
        if use_fts and search_text:
            return get_fts_search_results(search_params)
        
        # 基本クエリ（拡張マッピングを使用）
        query = """
            SELECT DISTINCT
                j.normalized_app_num,
                j.shutugan_bi,
                j.reg_reg_ymd,
                -- 商標テキスト（優先順位付き）
                COALESCE(s.standard_char_t, iu.indct_use_t, su.search_use_t) as mark_text,
                -- 商品区分
                gca.goods_classes,
                -- 出願人情報（拡張マッピング使用）
                COALESCE(am.applicant_name, ame.applicant_name, 
                    '申請人コード: ' || ap.shutugannindairinin_code) as applicant_display,
                COALESCE(am.applicant_addr, ame.applicant_addr) as applicant_addr,
                COALESCE(am.confidence_level, ame.confidence_level, '') as confidence_level,
                -- 権利者情報
                rp.right_person_name,
                rp.right_person_addr,
                -- 画像情報
                CASE WHEN ts.image_data IS NOT NULL THEN 1 ELSE 0 END as has_image,
                -- 称呼情報
                GROUP_CONCAT(DISTINCT td.dsgnt_art) as call_signs,
                -- 類似群コード
                GROUP_CONCAT(DISTINCT tk.knd_info_art) as similar_codes,
                -- 指定商品・役務
                GROUP_CONCAT(DISTINCT sj.shohin_joho) as designated_goods
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
            LEFT JOIN t_dsgnt_art td ON j.normalized_app_num = td.normalized_app_num
            LEFT JOIN t_knd_info_art_table tk ON j.normalized_app_num = tk.normalized_app_num
            LEFT JOIN jiken_c_t_shohin_joho sj ON j.normalized_app_num = sj.normalized_app_num
            WHERE 1=1
        """
        
        params = []
        
        # 検索条件を追加
        if search_text:
            query += """ AND (
                s.standard_char_t LIKE ? OR
                iu.indct_use_t LIKE ? OR
                su.search_use_t LIKE ?
            )"""
            search_pattern = f"%{search_text}%"
            params.extend([search_pattern, search_pattern, search_pattern])
        
        if applicant_name:
            query += """ AND (
                am.applicant_name LIKE ? OR
                ame.applicant_name LIKE ? OR
                rp.right_person_name LIKE ?
            )"""
            applicant_pattern = f"%{applicant_name}%"
            params.extend([applicant_pattern, applicant_pattern, applicant_pattern])
        
        if goods_class:
            query += " AND gca.goods_classes LIKE ?"
            params.append(f"%第{goods_class}類%")
        
        if date_from:
            query += " AND j.shutugan_bi >= ?"
            params.append(date_from.replace('-', ''))
        
        if date_to:
            query += " AND j.shutugan_bi <= ?"
            params.append(date_to.replace('-', ''))
        
        # GROUP BY を追加
        query += " GROUP BY j.normalized_app_num"
        
        # 総件数を取得
        count_query = f"""
            SELECT COUNT(*) FROM (
                {query}
            )
        """
        
        cur.execute(count_query, params)
        total_count = cur.fetchone()[0]
        
        # 結果を取得
        query += " ORDER BY j.shutugan_bi DESC"
        
        # ページネーション
        page = search_params.get('page', 1)
        per_page = search_params.get('per_page', app.config['DEFAULT_PER_PAGE'])
        offset = (page - 1) * per_page
        
        query += f" LIMIT {per_page} OFFSET {offset}"
        
        cur.execute(query, params)
        results = cur.fetchall()
        
        # 結果を辞書形式に変換
        enhanced_results = []
        for row in results:
            result = dict(row)
            
            # 日付フォーマット
            if result['shutugan_bi']:
                app_date = result['shutugan_bi']
                result['app_date_formatted'] = f"{app_date[:4]}/{app_date[4:6]}/{app_date[6:]}"
            
            if result['reg_reg_ymd']:
                reg_date = result['reg_reg_ymd']
                result['reg_date_formatted'] = f"{reg_date[:4]}/{reg_date[4:6]}/{reg_date[6:]}"
            
            # 画像パスを設定
            if result['has_image']:
                result['image_path'] = f"/images/{result['normalized_app_num']}.jpg"
            
            enhanced_results.append(result)
        
        return enhanced_results, total_count
        
    except sqlite3.Error as e:
        logger.error(f"検索エラー: {e}")
        return [], 0
    finally:
        con.close()

def get_fts_search_results(search_params: Dict[str, Any]) -> Tuple[List[Dict], int]:
    """
    FTS（Full-Text Search）を使用した高速検索
    """
    con = get_db_connection()
    if not con:
        return [], 0
    
    try:
        cur = con.cursor()
        
        search_text = search_params.get('search_text', '').strip()
        applicant_name = search_params.get('applicant_name', '').strip()
        
        # FTS検索クエリ
        fts_query = """
            SELECT DISTINCT
                fts.normalized_app_num,
                j.shutugan_bi,
                j.reg_reg_ymd,
                fts.mark_text,
                fts.goods_classes,
                fts.applicant_name as applicant_display,
                -- 追加情報を取得
                rp.right_person_name,
                rp.right_person_addr,
                CASE WHEN ts.image_data IS NOT NULL THEN 1 ELSE 0 END as has_image,
                -- 信頼度レベル
                COALESCE(am.confidence_level, ame.confidence_level, '') as confidence_level
            FROM trademark_fts fts
            LEFT JOIN jiken_c_t j ON fts.normalized_app_num = j.normalized_app_num
            LEFT JOIN reg_mapping rm ON j.normalized_app_num = rm.app_num
            LEFT JOIN right_person_art_t rp ON rm.reg_num = rp.reg_num
            LEFT JOIN t_sample ts ON j.normalized_app_num = ts.normalized_app_num
            LEFT JOIN jiken_c_t_shutugannindairinin ap ON j.normalized_app_num = ap.shutugan_no
            LEFT JOIN applicant_mapping am ON ap.shutugannindairinin_code = am.applicant_code
            LEFT JOIN applicant_mapping_enhanced ame ON ap.shutugannindairinin_code = ame.applicant_code
            WHERE 1=1
        """
        
        params = []
        
        # FTS検索条件
        if search_text:
            fts_query += " AND fts.mark_text MATCH ?"
            params.append(search_text)
        
        if applicant_name:
            fts_query += " AND fts.applicant_name MATCH ?"
            params.append(applicant_name)
        
        # 総件数を取得
        count_query = f"SELECT COUNT(*) FROM ({fts_query})"
        cur.execute(count_query, params)
        total_count = cur.fetchone()[0]
        
        # 結果を取得
        fts_query += " ORDER BY j.shutugan_bi DESC"
        
        # ページネーション
        page = search_params.get('page', 1)
        per_page = search_params.get('per_page', app.config['DEFAULT_PER_PAGE'])
        offset = (page - 1) * per_page
        
        fts_query += f" LIMIT {per_page} OFFSET {offset}"
        
        cur.execute(fts_query, params)
        results = cur.fetchall()
        
        # 結果を辞書形式に変換
        enhanced_results = []
        for row in results:
            result = dict(row)
            
            # 日付フォーマット
            if result['shutugan_bi']:
                app_date = result['shutugan_bi']
                result['app_date_formatted'] = f"{app_date[:4]}/{app_date[4:6]}/{app_date[6:]}"
            
            if result['reg_reg_ymd']:
                reg_date = result['reg_reg_ymd']
                result['reg_date_formatted'] = f"{reg_date[:4]}/{reg_date[4:6]}/{reg_date[6:]}"
            
            # 画像パスを設定
            if result['has_image']:
                result['image_path'] = f"/images/{result['normalized_app_num']}.jpg"
            
            enhanced_results.append(result)
        
        return enhanced_results, total_count
        
    except sqlite3.Error as e:
        logger.error(f"FTS検索エラー: {e}")
        # FTSが失敗した場合は通常検索にフォールバック
        search_params['use_fts'] = False
        return get_enhanced_search_results(search_params)
    finally:
        con.close()

def get_system_stats() -> Dict[str, Any]:
    """システム統計情報を取得"""
    con = get_db_connection()
    if not con:
        return {}
    
    try:
        cur = con.cursor()
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
        
        # FTSテーブル件数
        try:
            cur.execute("SELECT COUNT(*) FROM trademark_fts")
            stats['fts_count'] = cur.fetchone()[0]
        except sqlite3.OperationalError:
            stats['fts_count'] = 0
        
        return stats
        
    except sqlite3.Error as e:
        logger.error(f"統計情報取得エラー: {e}")
        return {}
    finally:
        con.close()

# --- テンプレートフィルター ---
@app.template_filter('format_similar_code')
def format_similar_group_code(codes_str: Optional[str]) -> str:
    """類似群コードのフォーマット"""
    if not codes_str:
        return ""
    import re
    pattern = r'\d{2}[A-Z]\d{2}'
    found_codes = re.findall(pattern, codes_str)
    return " ".join(found_codes)

@app.template_filter('format_app_num')
def format_application_number(app_num: Optional[str]) -> str:
    """出願番号のフォーマット"""
    if not app_num or len(app_num) < 4:
        return app_num or ""
    return f"{app_num[:4]}-{app_num[4:]}"

@app.template_filter('format_date')
def format_date_string(date_str: Optional[str]) -> str:
    """日付文字列のフォーマット"""
    if not date_str or len(date_str) != 8:
        return date_str or ""
    try:
        year = date_str[0:4]
        month = date_str[4:6]
        day = date_str[6:8]
        return f"{year}/{month}/{day}"
    except (ValueError, IndexError) as e:
        logger.warning(f"Date formatting error for '{date_str}': {e}")
        return date_str

def is_standard_character(image_data: str) -> bool:
    """標準文字かどうかを判定"""
    if not image_data:
        return True
    
    # 標準文字の特徴的なパターン
    if (image_data.startswith("//") or 
        set(image_data.strip()) == {"/"} or 
        len(image_data.strip()) < 20 or
        image_data.count("/") / len(image_data) > 0.8):
        return True
    
    return False

# --- 画像関連 ---
def find_image_file(app_num: str) -> Optional[str]:
    """出願番号に対応する画像ファイルを検索"""
    if not app_num:
        return None
    
    normalized_num = app_num.replace("-", "").strip()
    images_dir = Path(app.config['IMAGES_DIR'])
    
    if not images_dir.exists():
        return None
    
    for ext in ['jpg', 'jpeg', 'png', 'gif']:
        image_path = images_dir / f"{normalized_num}.{ext}"
        if image_path.exists():
            return str(image_path)
    
    return None

# --- ルート定義 ---
@app.route('/', methods=['GET', 'POST'])
def index():
    """メインページ（検索機能統合）"""
    # 検索パラメータを取得（GET/POST両対応）
    if request.method == 'POST':
        search_params = {
            'search_text': request.form.get('q', '').strip(),
            'applicant_name': request.form.get('applicant', '').strip(),
            'goods_class': request.form.get('class', '').strip(),
            'date_from': request.form.get('date_from', '').strip(),
            'date_to': request.form.get('date_to', '').strip(),
            'page': int(request.form.get('page', 1)),
            'per_page': int(request.form.get('per_page', app.config['DEFAULT_PER_PAGE'])),
            'use_fts': False
        }
    else:  # GET request
        search_params = {
            'search_text': request.args.get('q', '').strip(),
            'applicant_name': request.args.get('applicant', '').strip(),
            'goods_class': request.args.get('class', '').strip(),
            'date_from': request.args.get('date_from', '').strip(),
            'date_to': request.args.get('date_to', '').strip(),
            'page': int(request.args.get('page', 1)),
            'per_page': int(request.args.get('per_page', app.config['DEFAULT_PER_PAGE'])),
            'use_fts': False
        }
    
    # 検索条件があるかチェック
    has_search_conditions = any([
        search_params['search_text'], 
        search_params['applicant_name'], 
        search_params['goods_class'],
        search_params['date_from'], 
        search_params['date_to']
    ])
    
    results = []
    total_count = 0
    search_stats = {}
    
    if has_search_conditions:
        # 検索実行（元のロジックを使用）
        results, total_count = get_simple_search_results(search_params)
        
        # ページネーション計算
        total_pages = math.ceil(total_count / search_params['per_page']) if total_count > 0 else 0
        
        # 検索統計
        search_stats = {
            'total_count': total_count,
            'current_page': search_params['page'],
            'total_pages': total_pages,
            'per_page': search_params['per_page'],
            'has_prev': search_params['page'] > 1,
            'has_next': search_params['page'] < total_pages,
            'prev_page': search_params['page'] - 1 if search_params['page'] > 1 else None,
            'next_page': search_params['page'] + 1 if search_params['page'] < total_pages else None
        }
    
    # 統計情報を取得
    stats = get_system_stats()
    
    return render_template('index_enhanced.html', 
                         stats=stats,
                         results=results,
                         search_params=search_params,
                         search_stats=search_stats)

@app.route('/search', methods=['GET', 'POST'])
def search():
    """検索処理"""
    # 検索パラメータを取得（GET/POST両対応）
    if request.method == 'POST':
        search_params = {
            'search_text': request.form.get('q', '').strip(),
            'applicant_name': request.form.get('applicant', '').strip(),
            'goods_class': request.form.get('class', '').strip(),
            'date_from': request.form.get('date_from', '').strip(),
            'date_to': request.form.get('date_to', '').strip(),
            'page': int(request.form.get('page', 1)),
            'per_page': int(request.form.get('per_page', app.config['DEFAULT_PER_PAGE'])),
            'use_fts': False
        }
    else:  # GET request
        search_params = {
            'search_text': request.args.get('q', '').strip(),
            'applicant_name': request.args.get('applicant', '').strip(),
            'goods_class': request.args.get('class', '').strip(),
            'date_from': request.args.get('date_from', '').strip(),
            'date_to': request.args.get('date_to', '').strip(),
            'page': int(request.args.get('page', 1)),
            'per_page': int(request.args.get('per_page', app.config['DEFAULT_PER_PAGE'])),
            'use_fts': False
        }
    
    # 検索実行（元のロジックを使用）  
    results, total_count = get_simple_search_results(search_params)
    
    # ページネーション計算
    total_pages = math.ceil(total_count / search_params['per_page'])
    
    # 検索統計
    search_stats = {
        'total_count': total_count,
        'current_page': search_params['page'],
        'total_pages': total_pages,
        'per_page': search_params['per_page'],
        'has_prev': search_params['page'] > 1,
        'has_next': search_params['page'] < total_pages,
        'prev_page': search_params['page'] - 1 if search_params['page'] > 1 else None,
        'next_page': search_params['page'] + 1 if search_params['page'] < total_pages else None
    }
    
    return render_template('index_enhanced.html',
                         results=results,
                         search_params=search_params,
                         search_stats=search_stats,
                         stats=get_system_stats())

@app.route('/api/stats')
def api_stats():
    """統計情報API"""
    stats = get_system_stats()
    return jsonify(stats)

@app.route('/images/<filename>')
def serve_image(filename):
    """画像ファイルの配信"""
    if not app.config['SERVE_IMAGES']:
        return "画像配信は無効化されています", 404
    
    try:
        return send_from_directory(app.config['IMAGES_DIR'], filename)
    except FileNotFoundError:
        return "画像が見つかりません", 404

@app.route('/detail/<app_num>')
def detail(app_num):
    """商標詳細ページ"""
    # 詳細情報を取得
    search_params = {
        'search_text': '',
        'applicant_name': '',
        'goods_class': '',
        'date_from': '',
        'date_to': '',
        'page': 1,
        'per_page': 1,
        'use_fts': False
    }
    
    # 特定の出願番号で検索
    con = get_db_connection()
    if not con:
        flash('データベースエラーが発生しました', 'error')
        return render_template('error.html')
    
    try:
        cur = con.cursor()
        
        # 詳細情報を取得
        detail_query = """
            SELECT DISTINCT
                j.normalized_app_num,
                j.shutugan_bi,
                j.reg_reg_ymd,
                COALESCE(s.standard_char_t, iu.indct_use_t, su.search_use_t) as mark_text,
                gca.goods_classes,
                COALESCE(am.applicant_name, ame.applicant_name, 
                    '申請人コード: ' || ap.shutugannindairinin_code) as applicant_display,
                COALESCE(am.applicant_addr, ame.applicant_addr) as applicant_addr,
                COALESCE(am.confidence_level, ame.confidence_level, '') as confidence_level,
                rp.right_person_name,
                rp.right_person_addr,
                CASE WHEN ts.image_data IS NOT NULL THEN 1 ELSE 0 END as has_image,
                GROUP_CONCAT(DISTINCT td.dsgnt_art) as call_signs,
                GROUP_CONCAT(DISTINCT tk.knd_info_art) as similar_codes,
                GROUP_CONCAT(DISTINCT sj.shohin_joho) as designated_goods
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
            LEFT JOIN t_dsgnt_art td ON j.normalized_app_num = td.normalized_app_num
            LEFT JOIN t_knd_info_art_table tk ON j.normalized_app_num = tk.normalized_app_num
            LEFT JOIN jiken_c_t_shohin_joho sj ON j.normalized_app_num = sj.normalized_app_num
            WHERE j.normalized_app_num = ?
            GROUP BY j.normalized_app_num
        """
        
        cur.execute(detail_query, [app_num])
        result = cur.fetchone()
        
        if not result:
            flash('指定された商標が見つかりません', 'error')
            return render_template('error.html')
        
        # 結果を辞書形式に変換
        detail_data = dict(result)
        
        # 日付フォーマット
        if detail_data['shutugan_bi']:
            app_date = detail_data['shutugan_bi']
            detail_data['app_date_formatted'] = f"{app_date[:4]}/{app_date[4:6]}/{app_date[6:]}"
        
        if detail_data['reg_reg_ymd']:
            reg_date = detail_data['reg_reg_ymd']
            detail_data['reg_date_formatted'] = f"{reg_date[:4]}/{reg_date[4:6]}/{reg_date[6:]}"
        
        # 画像パスを設定
        if detail_data['has_image']:
            detail_data['image_path'] = f"/images/{detail_data['normalized_app_num']}.jpg"
        
        return render_template('detail.html', detail=detail_data)
        
    except sqlite3.Error as e:
        logger.error(f"詳細情報取得エラー: {e}")
        flash('データベースエラーが発生しました', 'error')
        return render_template('error.html')
    finally:
        con.close()

# --- エラーハンドラ ---
@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', error_message="ページが見つかりません"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error_message="内部サーバーエラーが発生しました"), 500

# --- メイン実行 ---
if __name__ == '__main__':
    logger.info("商標検索システム v2 を起動しています...")
    
    # データベースの存在確認
    if not Path(app.config['DB_PATH']).exists():
        logger.error(f"データベースファイルが見つかりません: {app.config['DB_PATH']}")
        print("エラー: データベースファイルが見つかりません")
        print("init_database.py を実行してデータベースを初期化してください")
        exit(1)
    
    # 統計情報を表示
    stats = get_system_stats()
    print(f"システム統計:")
    print(f"  総商標数: {stats.get('total_trademarks', 0):,}")
    print(f"  出願人マッピング: {stats.get('applicant_mappings', 0):,}")
    print(f"  商標表示率: {stats.get('display_rate', 0)}%")
    print(f"  画像データ: {stats.get('image_count', 0):,}")
    print(f"  FTS件数: {stats.get('fts_count', 0):,}")
    
    # サーバー起動
    app.run(debug=True, host='0.0.0.0', port=5002)
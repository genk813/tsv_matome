#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
import sqlite3
import math
import re
from pathlib import Path
from flask import Flask, render_template, request, flash, send_from_directory, url_for
from typing import List, Dict, Any, Optional, Tuple

# --- 設定クラス ---
class Config:
    DB_PATH = os.environ.get('DB_PATH', Path(__file__).parent.resolve() / "output.db")
    PER_PAGE_OPTIONS = [20, 50, 100, 200]
    DEFAULT_PER_PAGE = 200
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
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- 画像関連ユーティリティ ---
def find_image_file(app_num: str) -> Optional[str]:
    """出願番号に対応する画像ファイルを検索"""
    if not app_num:
        return None
    
    # 出願番号を正規化（ハイフンを除去）
    normalized_num = app_num.replace("-", "").strip()
    
    # 画像ディレクトリが存在するかチェック
    images_dir = Path(app.config['IMAGES_DIR'])
    if not images_dir.exists():
        logger.warning(f"Images directory not found: {images_dir}")
        return None
    
    # 対応する画像ファイルを検索
    possible_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'tiff']
    
    for ext in possible_extensions:
        image_path = images_dir / f"{normalized_num}.{ext}"
        if image_path.exists():
            return f"{normalized_num}.{ext}"
    
    return None

def get_image_url(app_num: str) -> Optional[str]:
    """画像URLを取得"""
    image_filename = find_image_file(app_num)
    if image_filename:
        return url_for('serve_image', filename=image_filename)
    return None

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

# --- テンプレートフィルター ---
@app.template_filter('format_similar_code')
def format_similar_group_code(codes_str: Optional[str]) -> str:
    """類似群コードのフォーマット"""
    if not codes_str:
        return ""
    pattern = r'\d{2}[A-Z]\d{2}'
    found_codes = re.findall(pattern, codes_str)
    return " ".join(found_codes)

@app.template_filter('format_app_num')
def format_application_number(app_num: Optional[str]) -> str:
    """出願番号のフォーマット"""
    if not app_num or len(app_num) < 4:
        return app_num or ""
    
    # 2023123456 → 2023-123456
    if len(app_num) >= 8 and app_num.isdigit():
        year = app_num[:4]
        number = app_num[4:]
        return f"{year}-{number}"
    
    return app_num

@app.template_filter('format_date')
def format_date(date_str: Optional[str]) -> str:
    """日付のフォーマット"""
    if not date_str:
        return ""
    
    # 20231225 → 2023-12-25
    if len(date_str) == 8 and date_str.isdigit():
        year = date_str[:4]
        month = date_str[4:6]
        day = date_str[6:8]
        return f"{year}-{month}-{day}"
    
    return date_str

# --- データベース関連 ---
def get_db_connection():
    """データベース接続を取得"""
    db_path = app.config['DB_PATH']
    if not Path(db_path).exists():
        raise FileNotFoundError(f"Database file not found: {db_path}")
    
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    return con

def query_db(sql, params=()):
    """データベースクエリ実行"""
    logger.info(f"Executing SQL: {sql}")
    logger.info(f"With params: {params}")
    
    con = get_db_connection()
    try:
        cur = con.execute(sql, params)
        rows = [dict(row) for row in cur.fetchall()]
        logger.info(f"Query returned {len(rows)} rows")
        return rows
    except Exception as e:
        logger.error(f"Database query error: {e}")
        raise
    finally:
        con.close()

def query_db_one(sql, params=()):
    """データベースクエリ実行（1行のみ）"""
    logger.info(f"Executing SQL (one): {sql}")
    logger.info(f"With params (one): {params}")
    
    con = get_db_connection()
    try:
        cur = con.execute(sql, params)
        row = cur.fetchone()
        return dict(row) if row else None
    except Exception as e:
        logger.error(f"Database query error: {e}")
        raise
    finally:
        con.close()

def get_simple_results(app_nums):
    """シンプルな検索結果取得（申請人実名表示対応）"""
    if not app_nums:
        return []
    
    placeholders = ",".join("?" for _ in app_nums)
    
    # シンプルで高速なクエリ
    simple_sql = f"""
        SELECT
            j.normalized_app_num AS app_num,
            COALESCE(
                NULLIF(s.standard_char_t, ''),
                NULLIF(iu.indct_use_t, ''),
                NULLIF(su.search_use_t, '')
            ) AS mark_text,
            j.shutugan_bi AS app_date,
            j.reg_reg_ymd AS reg_date,
            
            -- 申請人情報（安全な取得）
            COALESCE(am.appl_name, 'コード:' || ap.shutugannindairinin_code) as applicant_name,
            am.appl_addr as applicant_addr,
            
            -- 権利者情報（安全な取得）
            h.right_person_name AS owner_name,
            h.right_person_addr AS owner_addr,
            
            -- 商品区分（簡単な取得）
            gca.goods_classes,
            
            -- 画像データ
            ts.image_data AS image_data_sample
            
        FROM jiken_c_t AS j
        LEFT JOIN standard_char_t_art AS s ON j.normalized_app_num = s.normalized_app_num
        LEFT JOIN indct_use_t_art AS iu ON j.normalized_app_num = iu.normalized_app_num
        LEFT JOIN search_use_t_art_table AS su ON j.normalized_app_num = su.normalized_app_num
        LEFT JOIN jiken_c_t_shutugannindairinin ap ON j.normalized_app_num = ap.shutugan_no 
                                                   AND ap.shutugannindairinin_sikbt = '1'
        LEFT JOIN applicant_master am ON ap.shutugannindairinin_code = am.appl_cd
        LEFT JOIN reg_mapping rm ON j.normalized_app_num = rm.app_num
        LEFT JOIN right_person_art_t AS h ON rm.reg_num = h.reg_num
        LEFT JOIN goods_class_art AS gca ON j.normalized_app_num = gca.normalized_app_num
        LEFT JOIN t_sample AS ts ON j.normalized_app_num = ts.normalized_app_num
        
        WHERE j.normalized_app_num IN ({placeholders})
        ORDER BY j.normalized_app_num
        LIMIT 100
    """
    
    try:
        results = query_db(simple_sql, tuple(app_nums))
        
        # 各結果に画像情報を追加
        for result in results:
            app_num = result.get('app_num', '')
            if app_num:
                result['image_url'] = get_image_url(app_num)
                result['has_image'] = find_image_file(app_num) is not None
                result['is_standard_char'] = is_standard_character(result.get('image_data_sample', ''))
        
        return results
    except Exception as e:
        logger.error(f"Error in get_simple_results: {e}")
        return []

# --- 画像配信ルート ---
@app.route('/images/<filename>')
def serve_image(filename):
    """画像ファイルを配信"""
    try:
        images_dir = Path(app.config['IMAGES_DIR'])
        return send_from_directory(images_dir, filename)
    except Exception as e:
        logger.error(f"Error serving image {filename}: {e}")
        return "Image not found", 404

# --- 検索関連 ---
def search_by_app_num(app_num: str) -> List[str]:
    """出願番号で検索"""
    if not app_num:
        return []
    
    # 出願番号を正規化
    normalized_num = app_num.replace("-", "").strip()
    
    if len(normalized_num) < 4:
        return []
    
    # 部分一致検索
    sql = """
        SELECT normalized_app_num
        FROM jiken_c_t
        WHERE normalized_app_num LIKE ?
        ORDER BY normalized_app_num
        LIMIT 50
    """
    
    try:
        results = query_db(sql, (f"%{normalized_num}%",))
        return [row['normalized_app_num'] for row in results]
    except Exception as e:
        logger.error(f"Error in search_by_app_num: {e}")
        return []

def search_by_mark_text(mark_text: str) -> List[str]:
    """商標文字で検索"""
    if not mark_text:
        return []
    
    search_pattern = f"%{mark_text}%"
    
    # 3つのテーブルで検索
    sql = """
        SELECT DISTINCT j.normalized_app_num
        FROM jiken_c_t j
        LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num
        LEFT JOIN indct_use_t_art iu ON j.normalized_app_num = iu.normalized_app_num
        LEFT JOIN search_use_t_art_table su ON j.normalized_app_num = su.normalized_app_num
        WHERE 
            s.standard_char_t LIKE ? OR
            iu.indct_use_t LIKE ? OR
            su.search_use_t LIKE ?
        ORDER BY j.normalized_app_num
        LIMIT 50
    """
    
    try:
        results = query_db(sql, (search_pattern, search_pattern, search_pattern))
        return [row['normalized_app_num'] for row in results]
    except Exception as e:
        logger.error(f"Error in search_by_mark_text: {e}")
        return []

def search_by_goods_classes(goods_classes: str) -> List[str]:
    """商品区分で検索"""
    if not goods_classes:
        return []
    
    search_pattern = f"%{goods_classes}%"
    
    sql = """
        SELECT DISTINCT j.normalized_app_num
        FROM jiken_c_t j
        LEFT JOIN goods_class_art gca ON j.normalized_app_num = gca.normalized_app_num
        WHERE gca.goods_classes LIKE ?
        ORDER BY j.normalized_app_num
        LIMIT 50
    """
    
    try:
        results = query_db(sql, (search_pattern,))
        return [row['normalized_app_num'] for row in results]
    except Exception as e:
        logger.error(f"Error in search_by_goods_classes: {e}")
        return []

# --- メインルート ---
@app.route('/', methods=['GET', 'POST'])
def index():
    """メインページ"""
    if request.method == 'GET':
        return render_template('index_enhanced.html',
                             results=[], 
                             total_results=0,
                             per_page_options=app.config['PER_PAGE_OPTIONS'],
                             per_page=app.config['DEFAULT_PER_PAGE'])
    
    # POST処理
    try:
        # 検索条件を取得
        app_num = request.form.get('app_num', '').strip()
        mark_text = request.form.get('mark_text', '').strip()
        goods_classes = request.form.get('goods_classes', '').strip()
        
        # 検索実行
        app_nums = set()
        
        if app_num:
            app_nums.update(search_by_app_num(app_num))
        
        if mark_text:
            app_nums.update(search_by_mark_text(mark_text))
        
        if goods_classes:
            app_nums.update(search_by_goods_classes(goods_classes))
        
        if not app_nums:
            flash("検索条件に一致する結果が見つかりませんでした。", "info")
            return render_template('index_enhanced.html',
                                 results=[], 
                                 total_results=0,
                                 kw_app=app_num,
                                 kw_mark=mark_text,
                                 kw_goods_classes=goods_classes,
                                 per_page_options=app.config['PER_PAGE_OPTIONS'],
                                 per_page=app.config['DEFAULT_PER_PAGE'])
        
        # 結果を取得
        results = get_simple_results(list(app_nums))
        
        logger.info(f"Search completed: {len(results)} results found")
        
        return render_template('index_enhanced.html',
                             results=results,
                             total_results=len(results),
                             current_page=1,
                             total_pages=1,
                             kw_app=app_num,
                             kw_mark=mark_text,
                             kw_goods_classes=goods_classes,
                             per_page_options=app.config['PER_PAGE_OPTIONS'],
                             per_page=app.config['DEFAULT_PER_PAGE'])
    
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        flash(f"検索中にエラーが発生しました: {str(e)}", "error")
        return render_template('index_enhanced.html',
                             results=[], 
                             total_results=0,
                             per_page_options=app.config['PER_PAGE_OPTIONS'],
                             per_page=app.config['DEFAULT_PER_PAGE'])

if __name__ == '__main__':
    try:
        # データベース接続テスト
        con = get_db_connection()
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM jiken_c_t")
        total_records = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM applicant_master")
        applicant_records = cur.fetchone()[0]
        con.close()
        
        print(f"=== 商標検索システム（申請人実名表示対応） ===")
        print(f"✓ データベース接続: 成功")
        print(f"✓ 総商標件数: {total_records:,}")
        print(f"✓ 申請人マスター: {applicant_records:,}")
        print(f"✓ サーバー: http://localhost:5002")
        print(f"Ctrl+C で終了")
        
        app.run(debug=True, host='0.0.0.0', port=5002)
    except Exception as e:
        print(f"❌ エラー: {e}")
        print("データベースファイルが見つからないか、テーブルが存在しません。")
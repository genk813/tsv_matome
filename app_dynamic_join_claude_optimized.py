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
    DB_PATH = Path(os.environ.get('DB_PATH', Path(__file__).parent.resolve() / "output.db"))
    PER_PAGE_OPTIONS = [20, 50, 100, 200]
    DEFAULT_PER_PAGE = 200
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    MAX_SEARCH_TERM_LENGTH = 100
    MAX_RESULTS_PER_PAGE = 200
    # 画像関連設定
    IMAGES_DIR = Path(os.environ.get('IMAGES_DIR', Path(__file__).parent.resolve() / "images" / "final_complete"))
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

# --- データベース関連 ---
def init_database():
    """データベースを初期化"""
    db_path = app.config['DB_PATH']
    schema_path = Path(__file__).parent / 'create_schema.sql'
    
    if not db_path.exists() or db_path.stat().st_size == 0:
        logger.info(f"Initializing database at {db_path}")
        if schema_path.exists():
            con = sqlite3.connect(db_path)
            with open(schema_path, 'r', encoding='utf-8') as f:
                con.executescript(f.read())
            con.close()
            logger.info("Database schema created successfully")
        else:
            logger.error(f"Schema file not found at {schema_path}")
            raise FileNotFoundError(f"Schema file not found at {schema_path}")

def get_db_connection():
    """データベース接続を取得"""
    db_path = app.config['DB_PATH']
    if not db_path.exists() or db_path.stat().st_size == 0:
        init_database()
    
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    return con

def query_db(sql, params=()):
    """データベースクエリ実行"""
    logger.debug(f"Executing SQL: {sql}")
    logger.debug(f"With params: {params}")
    
    con = get_db_connection()
    try:
        cur = con.execute(sql, params)
        rows = [dict(row) for row in cur.fetchall()]
        return rows
    except Exception as e:
        logger.error(f"Database query error: {e}")
        raise
    finally:
        con.close()

def query_db_one(sql, params=()):
    """データベースクエリ実行（1行のみ）"""
    logger.debug(f"Executing SQL (one): {sql}")
    logger.debug(f"With params (one): {params}")
    
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

def get_optimized_results(app_nums):
    """最適化された単一クエリで全データを取得"""
    if not app_nums:
        return []
    
    placeholders = ",".join("?" for _ in app_nums)
    
    # 単一の最適化されたクエリで全データを取得（商標表示優先順位対応 + 申請人実名表示）
    optimized_sql = f"""
        SELECT
            j.normalized_app_num AS app_num,
            -- 商標表示の優先順位: 標準文字 > 表示用商標 > 検索用商標
            COALESCE(
                NULLIF(s.standard_char_t, ''),
                NULLIF(iu.indct_use_t, ''),
                NULLIF(su.search_use_t, '')
            ) AS mark_text,
            j.shutugan_bi AS app_date,
            j.reg_reg_ymd AS reg_date,
            h.reg_num AS reg_no,
            h.right_person_name AS owner_name,
            h.right_person_addr AS owner_addr,
            
            -- 申請人情報（マスターファイル優先、フォールバック付き）
            CASE 
                WHEN am.appl_name IS NOT NULL AND am.appl_name != '' AND am.appl_name NOT LIKE '%省略%'
                THEN am.appl_name
                WHEN apm.applicant_name IS NOT NULL
                THEN apm.applicant_name || ' (推定)'
                ELSE 'コード:' || ap.shutugannindairinin_code
            END as applicant_name,
            COALESCE(am.appl_addr, apm.applicant_addr) as applicant_addr,
            
            -- 商品・役務区分（GROUP_CONCAT）
            GROUP_CONCAT(DISTINCT gca.goods_classes) AS goods_classes,
            
            -- 類似群コード（GROUP_CONCAT）
            GROUP_CONCAT(DISTINCT tknd.smlr_dsgn_group_cd) AS similar_group_codes,
            
            -- 指定商品・役務（GROUP_CONCAT）
            GROUP_CONCAT(DISTINCT jcs.designated_goods) AS designated_goods,
            
            -- 称呼（GROUP_CONCAT）
            GROUP_CONCAT(DISTINCT td.dsgnt) AS call_name,
            
            -- 画像データ（最初のレコードのみ）
            MIN(ts.image_data) AS image_data_sample
            
        FROM jiken_c_t AS j
        LEFT JOIN standard_char_t_art AS s ON j.normalized_app_num = s.normalized_app_num
        LEFT JOIN indct_use_t_art AS iu ON j.normalized_app_num = iu.normalized_app_num
        LEFT JOIN search_use_t_art_table AS su ON j.normalized_app_num = su.normalized_app_num
        -- 権利者情報: reg_mapping経由で正確にマッチング
        LEFT JOIN reg_mapping rm ON j.normalized_app_num = rm.app_num
        LEFT JOIN right_person_art_t AS h ON rm.reg_num = h.reg_num
        -- 申請人情報
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
        -- 商品区分: 出願番号または登録番号でマッチング  
        LEFT JOIN goods_class_art AS gca ON (j.normalized_app_num = gca.normalized_app_num OR
                                           (j.reg_reg_ymd IS NOT NULL AND gca.reg_num IS NOT NULL))
        LEFT JOIN t_knd_info_art_table AS tknd ON j.normalized_app_num = tknd.normalized_app_num
        LEFT JOIN jiken_c_t_shohin_joho AS jcs ON j.normalized_app_num = jcs.normalized_app_num
        LEFT JOIN t_dsgnt_art AS td ON j.normalized_app_num = td.normalized_app_num
        LEFT JOIN t_sample AS ts ON j.normalized_app_num = ts.normalized_app_num
        
        WHERE j.normalized_app_num IN ({placeholders})
        GROUP BY j.normalized_app_num
        ORDER BY j.normalized_app_num
    """
    
    results = query_db(optimized_sql, tuple(app_nums))
    
    # 各結果に画像情報を追加
    for result in results:
        app_num = result.get('app_num', '')
        if app_num:
            result['image_url'] = get_image_url(app_num)
            result['has_image'] = find_image_file(app_num) is not None
            result['is_standard_char'] = is_standard_character(result.get('image_data_sample', ''))
    
    return results

# --- 画像配信ルート ---
@app.route('/images/<filename>')
def serve_image(filename):
    """画像ファイルを配信"""
    try:
        images_dir = app.config['IMAGES_DIR']
        return send_from_directory(images_dir, filename)
    except Exception as e:
        logger.error(f"Error serving image {filename}: {e}")
        return "Image not found", 404

# --- メインルート ---
@app.route("/", methods=["GET", "POST"])
def index():
    """メインの検索ページ"""
    # フォームデータの初期化
    kw_app = ""
    kw_mark = ""
    kw_goods_classes = ""
    kw_designated_goods = ""
    kw_similar_group_codes = ""
    
    results = []
    error = None
    total_results = 0
    current_page = 1
    per_page = app.config['DEFAULT_PER_PAGE']
    total_pages = 0
    
    # リクエストデータの取得
    if request.method == "POST":
        kw_app = request.form.get("app_num", "").strip()
        kw_mark = request.form.get("mark_text", "").strip()
        kw_goods_classes = request.form.get("goods_classes", "").strip()
        kw_designated_goods = request.form.get("designated_goods", "").strip()
        kw_similar_group_codes = request.form.get("similar_group_codes", "").strip()
        try:
            current_page = int(request.form.get("page", 1))
            per_page = int(request.form.get("per_page", app.config['DEFAULT_PER_PAGE']))
        except (ValueError, TypeError):
            current_page = 1
            per_page = app.config['DEFAULT_PER_PAGE']
    else:  # GET request
        kw_app = request.args.get("app_num", "").strip()
        kw_mark = request.args.get("mark_text", "").strip()
        kw_goods_classes = request.args.get("goods_classes", "").strip()
        kw_designated_goods = request.args.get("designated_goods", "").strip()
        kw_similar_group_codes = request.args.get("similar_group_codes", "").strip()
        try:
            current_page = int(request.args.get("page", 1))
            per_page = int(request.args.get("per_page", app.config['DEFAULT_PER_PAGE']))
        except (ValueError, TypeError):
            current_page = 1
            per_page = app.config['DEFAULT_PER_PAGE']
    
    # パラメータ検証
    if current_page < 1:
        current_page = 1
    if per_page not in app.config['PER_PAGE_OPTIONS']:
        per_page = app.config['DEFAULT_PER_PAGE']
    
    # 検索条件があるかチェック
    has_search_conditions = any([kw_app, kw_mark, kw_goods_classes, kw_designated_goods, kw_similar_group_codes])
    
    if has_search_conditions:
        try:
            # 動的WHERE句の構築
            where_parts = ["1=1"]
            params = []
            from_parts = ["FROM jiken_c_t j"]
            
            # 出願番号
            if kw_app:
                where_parts.append("j.normalized_app_num = ?")
                params.append(kw_app.replace("-", ""))
            
            # 商標文字（全商標タイプを検索）
            if kw_mark:
                from_parts.append("LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num")
                from_parts.append("LEFT JOIN indct_use_t_art iu ON j.normalized_app_num = iu.normalized_app_num")
                from_parts.append("LEFT JOIN search_use_t_art_table su ON j.normalized_app_num = su.normalized_app_num")
                where_parts.append("(s.standard_char_t LIKE ? OR iu.indct_use_t LIKE ? OR su.search_use_t LIKE ?)")
                params.extend([f"%{kw_mark}%", f"%{kw_mark}%", f"%{kw_mark}%"])
            
            # 商品・役務区分
            if kw_goods_classes:
                from_parts.append("LEFT JOIN goods_class_art AS gca ON j.normalized_app_num = gca.normalized_app_num")
                terms = kw_goods_classes.split()
                for term in terms:
                    where_parts.append("gca.goods_classes LIKE ?")
                    params.append(f"%{term}%")
            
            # 指定商品・役務名
            if kw_designated_goods:
                from_parts.append("LEFT JOIN jiken_c_t_shohin_joho AS jcs ON j.normalized_app_num = jcs.normalized_app_num")
                terms = kw_designated_goods.split()
                for term in terms:
                    where_parts.append("jcs.designated_goods LIKE ?")
                    params.append(f"%{term}%")
            
            # 類似群コード
            if kw_similar_group_codes:
                from_parts.append("LEFT JOIN t_knd_info_art_table AS tknd ON j.normalized_app_num = tknd.normalized_app_num")
                terms = kw_similar_group_codes.split()
                for term in terms:
                    where_parts.append("tknd.smlr_dsgn_group_cd LIKE ?")
                    params.append(f"%{term}%")
            
            sub_query_from = " ".join(from_parts)
            sub_query_where = " AND ".join(where_parts)
            
            # 総件数取得
            count_sql = f"SELECT COUNT(DISTINCT j.normalized_app_num) AS total {sub_query_from} WHERE {sub_query_where}"
            count_result = query_db_one(count_sql, tuple(params))
            total_results = count_result['total'] if count_result else 0
            
            if total_results > 0:
                total_pages = math.ceil(total_results / per_page)
                offset = (current_page - 1) * per_page
                
                # 対象の出願番号を取得
                app_num_sql = f"SELECT DISTINCT j.normalized_app_num {sub_query_from} WHERE {sub_query_where} ORDER BY j.normalized_app_num LIMIT ? OFFSET ?"
                app_num_rows = query_db(app_num_sql, tuple(params + [per_page, offset]))
                app_nums = [row['normalized_app_num'] for row in app_num_rows]
                
                if app_nums:
                    # 最適化された単一クエリで全データを取得
                    results = get_optimized_results(app_nums)
                    
                    # デバッグログ
                    logger.debug(f"Optimized query returned {len(results)} results")
                    
                    # Noneや不正な結果をフィルタリング
                    results = [r for r in results if r and r.get('app_num')]
                    logger.debug(f"Final results count: {len(results)}")
            
            # 検索結果メッセージ
            if total_results == 0:
                flash("検索条件に一致する商標が見つかりませんでした。", 'info')
            elif not results:
                flash("データの取得中にエラーが発生しました。データベースが空の可能性があります。", 'error')
                logger.error("Results is empty despite total_results > 0")
            else:
                image_count = sum(1 for result in results if result.get('has_image', False))
                flash(f"{total_results}件の商標が見つかりました。（画像付き: {image_count}件）", 'success')
                
        except Exception as e:
            logger.error(f"Search error: {e}")
            if "no such table" in str(e).lower():
                error = "データベースが初期化されていないか、データがインポートされていません。"
            else:
                error = "検索中にエラーが発生しました。"
            flash(error, 'error')
    
    # テンプレートのレンダリング
    return render_template(
        "index_enhanced.html",
        results=results,
        kw_app=kw_app,
        kw_mark=kw_mark,
        kw_goods_classes=kw_goods_classes,
        kw_designated_goods=kw_designated_goods,
        kw_similar_group_codes=kw_similar_group_codes,
        error=error,
        total_results=total_results,
        current_page=current_page,
        per_page=per_page,
        total_pages=total_pages,
        per_page_options=app.config['PER_PAGE_OPTIONS']
    )

@app.route("/test-images")
def test_images():
    """画像配信テスト"""
    try:
        images_dir = Path(app.config['IMAGES_DIR'])
        if not images_dir.exists():
            return f"Images directory not found: {images_dir}"
        
        # 画像ファイル一覧を取得
        image_files = []
        for ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'tiff']:
            image_files.extend(images_dir.glob(f"*.{ext}"))
        
        # 最初の10個の画像をテスト表示
        test_images = image_files[:10]
        
        html = "<h2>画像配信テスト</h2>"
        html += f"<p>画像ディレクトリ: {images_dir}</p>"
        html += f"<p>総画像数: {len(image_files)}</p>"
        html += "<h3>サンプル画像:</h3>"
        
        for img_file in test_images:
            img_url = url_for('serve_image', filename=img_file.name)
            app_num = img_file.stem
            html += f'<div style="margin: 10px; padding: 10px; border: 1px solid #ccc;">'
            html += f'<p>出願番号: {app_num}</p>'
            html += f'<img src="{img_url}" alt="{app_num}" style="max-width: 200px; max-height: 200px;">'
            html += f'</div>'
        
        return html
        
    except Exception as e:
        return f"Error: {str(e)}"

@app.route("/admin/init-db")
def init_db_route():
    """データベース初期化エンドポイント"""
    try:
        init_database()
        return "Database initialized successfully"
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        return f"Database initialization failed: {e}", 500

if __name__ == "__main__":
    # 起動時テスト
    try:
        # データベース初期化を確認
        init_database()
        
        test_result = query_db_one("SELECT COUNT(*) as count FROM jiken_c_t LIMIT 1")
        logger.info(f"Database test - jiken_c_t records: {test_result['count'] if test_result else 'None'}")
        
        images_dir = Path(app.config['IMAGES_DIR'])
        if images_dir.exists():
            image_count = len(list(images_dir.glob("*.jpg"))) + len(list(images_dir.glob("*.jpeg"))) + len(list(images_dir.glob("*.png")))
            logger.info(f"Images directory found: {images_dir} ({image_count} images)")
        else:
            logger.warning(f"Images directory not found: {images_dir}")
            
    except Exception as e:
        logger.error(f"Startup test failed: {e}")
        logger.info("Database will be initialized on first use")
    
    port = int(os.environ.get('PORT', 5002))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    app.run(debug=debug, port=port, host='0.0.0.0')
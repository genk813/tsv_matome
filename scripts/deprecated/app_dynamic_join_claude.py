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
def query_db(sql, params=()):
    """データベースクエリ実行"""
    logger.debug(f"Executing SQL: {sql}")
    logger.debug(f"With params: {params}")
    
    db_path = app.config['DB_PATH']
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found at {db_path}")
    
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    cur = con.execute(sql, params)
    rows = [dict(row) for row in cur.fetchall()]
    con.close()
    return rows

def query_db_one(sql, params=()):
    """データベースクエリ実行（1行のみ）"""
    logger.debug(f"Executing SQL (one): {sql}")
    logger.debug(f"With params (one): {params}")
    
    db_path = app.config['DB_PATH']
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found at {db_path}")
    
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    cur = con.execute(sql, params)
    row = cur.fetchone()
    con.close()
    return dict(row) if row else None

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
            
            # 商標文字
            if kw_mark:
                from_parts.append("LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num")
                where_parts.append("s.standard_char_t LIKE ?")
                params.append(f"%{kw_mark}%")
            
            # 商品・役務区分
            if kw_goods_classes:
                from_parts.append("""
                    LEFT JOIN (
                        SELECT normalized_app_num, GROUP_CONCAT(DISTINCT goods_classes) AS concatenated_classes
                        FROM goods_class_art
                        GROUP BY normalized_app_num
                    ) AS grouped_gca ON j.normalized_app_num = grouped_gca.normalized_app_num
                """)
                terms = kw_goods_classes.split()
                for term in terms:
                    where_parts.append("grouped_gca.concatenated_classes LIKE ?")
                    params.append(f"%{term}%")
            
            # 指定商品・役務名
            if kw_designated_goods:
                from_parts.append("""
                    LEFT JOIN (
                        SELECT normalized_app_num, GROUP_CONCAT(DISTINCT designated_goods) AS concatenated_goods
                        FROM jiken_c_t_shohin_joho
                        GROUP BY normalized_app_num
                    ) AS grouped_sg ON j.normalized_app_num = grouped_sg.normalized_app_num
                """)
                terms = kw_designated_goods.split()
                for term in terms:
                    where_parts.append("grouped_sg.concatenated_goods LIKE ?")
                    params.append(f"%{term}%")
            
            # 類似群コード
            if kw_similar_group_codes:
                from_parts.append("""
                    LEFT JOIN (
                        SELECT normalized_app_num, GROUP_CONCAT(DISTINCT smlr_dsgn_group_cd) AS concatenated_codes
                        FROM t_knd_info_art_table
                        GROUP BY normalized_app_num
                    ) AS grouped_tknd ON j.normalized_app_num = grouped_tknd.normalized_app_num
                """)
                terms = kw_similar_group_codes.split()
                for term in terms:
                    where_parts.append("grouped_tknd.concatenated_codes LIKE ?")
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
                    # 詳細情報を取得
                    placeholders = ",".join("?" for _ in app_nums)
                    
                    # メインクエリ
                    main_sql = f"""
                        SELECT
                            j.normalized_app_num   AS app_num,
                            s.standard_char_t       AS mark_text,
                            j.shutugan_bi           AS app_date,
                            j.reg_reg_ymd           AS reg_date,
                            r.reg_num               AS reg_no,
                            h.right_person_name     AS owner_name,
                            h.right_person_addr     AS owner_addr
                        FROM jiken_c_t AS j
                        LEFT JOIN standard_char_t_art AS s ON j.normalized_app_num = s.normalized_app_num
                        LEFT JOIN reg_mapping AS r ON j.normalized_app_num = r.app_num
                        LEFT JOIN right_person_art_t AS h ON r.reg_num = h.reg_num
                        WHERE j.normalized_app_num IN ({placeholders})
                        GROUP BY j.normalized_app_num
                        ORDER BY j.normalized_app_num
                    """
                    
                    results = query_db(main_sql, tuple(app_nums))
                    
                    # デバッグログ
                    logger.debug(f"Query returned {len(results)} results")
                    
                    # 各結果に画像情報と関連データを追加
                    for i, result in enumerate(results):
                        try:
                            app_num = result.get('app_num', '')
                            if not app_num:
                                logger.warning(f"Result {i} has no app_num")
                                continue
                            
                            # 画像情報
                            result['image_url'] = get_image_url(app_num)
                            result['has_image'] = find_image_file(app_num) is not None
                            
                            # 商品・役務区分
                            try:
                                goods_sql = "SELECT GROUP_CONCAT(DISTINCT goods_classes) AS val FROM goods_class_art WHERE normalized_app_num = ?"
                                goods_result = query_db_one(goods_sql, (app_num,))
                                result['goods_classes'] = goods_result['val'] if goods_result and goods_result['val'] else ""
                            except Exception as e:
                                logger.warning(f"Failed to get goods_classes for {app_num}: {e}")
                                result['goods_classes'] = ""
                            
                            # 類似群コード
                            try:
                                similar_sql = "SELECT GROUP_CONCAT(DISTINCT smlr_dsgn_group_cd) AS val FROM t_knd_info_art_table WHERE normalized_app_num = ?"
                                similar_result = query_db_one(similar_sql, (app_num,))
                                result['similar_group_codes'] = similar_result['val'] if similar_result and similar_result['val'] else ""
                            except Exception as e:
                                logger.warning(f"Failed to get similar_group_codes for {app_num}: {e}")
                                result['similar_group_codes'] = ""
                            
                            # 指定商品・役務
                            try:
                                designated_sql = "SELECT GROUP_CONCAT(DISTINCT designated_goods) AS val FROM jiken_c_t_shohin_joho WHERE normalized_app_num = ?"
                                designated_result = query_db_one(designated_sql, (app_num,))
                                result['designated_goods'] = designated_result['val'] if designated_result and designated_result['val'] else ""
                            except Exception as e:
                                logger.warning(f"Failed to get designated_goods for {app_num}: {e}")
                                result['designated_goods'] = ""
                            
                            # 称呼
                            try:
                                call_sql = "SELECT GROUP_CONCAT(DISTINCT dsgnt) AS val FROM t_dsgnt_art WHERE normalized_app_num = ?"
                                call_result = query_db_one(call_sql, (app_num,))
                                result['call_name'] = call_result['val'] if call_result and call_result['val'] else ""
                            except Exception as e:
                                logger.warning(f"Failed to get call_name for {app_num}: {e}")
                                result['call_name'] = ""
                            
                            # 標準文字判定
                            try:
                                image_data_sql = "SELECT GROUP_CONCAT(image_data, '') AS val FROM t_sample WHERE normalized_app_num = ? ORDER BY rec_seq_num"
                                image_data_result = query_db_one(image_data_sql, (app_num,))
                                image_data_for_check = image_data_result['val'] if image_data_result and image_data_result['val'] else ""
                                result['is_standard_char'] = is_standard_character(image_data_for_check)
                            except Exception as e:
                                logger.warning(f"Failed to get image_data for {app_num}: {e}")
                                result['is_standard_char'] = True
                                
                        except Exception as e:
                            logger.error(f"Error processing result {i}: {e}")
                            continue
                    
                    # Noneや不正な結果をフィルタリング
                    results = [r for r in results if r and r.get('app_num')]
                    logger.debug(f"Final results count: {len(results)}")
            
            # 検索結果メッセージ
            if total_results == 0:
                flash("検索条件に一致する商標が見つかりませんでした。", 'info')
            elif not results:
                flash("データの取得中にエラーが発生しました。", 'error')
                logger.error("Results is empty despite total_results > 0")
            else:
                image_count = sum(1 for result in results if result.get('has_image', False))
                flash(f"{total_results}件の商標が見つかりました。（画像付き: {image_count}件）", 'success')
                
        except Exception as e:
            logger.error(f"Search error: {e}")
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

if __name__ == "__main__":
    # 起動時テスト
    try:
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
    
    port = int(os.environ.get('PORT', 5002))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    app.run(debug=debug, port=port, host='0.0.0.0')
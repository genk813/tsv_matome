#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request
import sqlite3
from pathlib import Path
import math
import re

app = Flask(__name__)

# --- テンプレートフィルター (変更なし) ---
@app.template_filter('format_similar_code')
def format_similar_group_code(codes_str):
    if not codes_str:
        return ""
    pattern = r'\d{2}[A-Z]\d{2}'
    found_codes = re.findall(pattern, codes_str)
    return " ".join(found_codes)

@app.template_filter('format_app_num')
def format_application_number(app_num):
    if not app_num or len(app_num) < 4:
        return app_num
    return f"{app_num[:4]}-{app_num[4:]}"

@app.template_filter('format_date')
def format_date_string(date_str):
    if not date_str or len(date_str) != 8:
        return date_str
    try:
        year = date_str[0:4]
        month = date_str[4:6]
        day = date_str[6:8]
        return f"{year}/{month}/{day}"
    except:
        return date_str

# --- データベース関連 (変更なし) ---
DB_PATH = Path(__file__).parent.resolve() / "output.db"
PER_PAGE_OPTIONS = [20, 50, 100, 200]
DEFAULT_PER_PAGE = 50

def query_db(sql, params=()):
    print(f"Executing SQL: {sql}")
    print(f"With params: {params}")
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found at {DB_PATH}")
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.execute(sql, params)
    rows = [dict(row) for row in cur.fetchall()]
    con.close()
    return rows

def query_db_one(sql, params=()):
    print(f"Executing SQL (one): {sql}")
    print(f"With params (one): {params}")
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found at {DB_PATH}")
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.execute(sql, params)
    row = cur.fetchone()
    con.close()
    return dict(row) if row else None

# --- メインの検索ロジック (ここからが大きな変更点) ---
@app.route("/", methods=["GET", "POST"])
def index():
    # --- フォームデータの受け取り (変更なし) ---
    kw_app = ""
    kw_mark = ""
    kw_goods_classes = ""
    kw_designated_goods = ""
    kw_similar_group_codes = ""
    results = []
    error = None
    total_results = 0
    current_page = 1
    per_page = DEFAULT_PER_PAGE
    total_pages = 0

    if request.method == "POST":
        kw_app = request.form.get("app_num", "").strip()
        kw_mark = request.form.get("mark_text", "").strip()
        kw_goods_classes = request.form.get("goods_classes", "").strip()
        kw_designated_goods = request.form.get("designated_goods", "").strip()
        kw_similar_group_codes = request.form.get("similar_group_codes", "").strip()
        current_page = int(request.form.get("page", 1))
        per_page = int(request.form.get("per_page", DEFAULT_PER_PAGE))
    else: # GET request
        kw_app = request.args.get("app_num", "").strip()
        kw_mark = request.args.get("mark_text", "").strip()
        kw_goods_classes = request.args.get("goods_classes", "").strip()
        kw_designated_goods = request.args.get("designated_goods", "").strip()
        kw_similar_group_codes = request.args.get("similar_group_codes", "").strip()
        current_page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", DEFAULT_PER_PAGE))

    if current_page < 1: current_page = 1
    if per_page not in PER_PAGE_OPTIONS: per_page = DEFAULT_PER_PAGE
    offset = (current_page - 1) * per_page

    # GETリクエストで検索条件が指定されていない場合、初期表示では結果を表示しない
    if request.method == "GET" and not (kw_app or kw_mark or kw_goods_classes or kw_designated_goods or kw_similar_group_codes):
        results = []
        total_results = 0
        total_pages = 0
        # これにより、以降のデータベースクエリが実行されなくなる
        return render_template("index_enhanced.html",
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
                               per_page_options=PER_PAGE_OPTIONS)

    # --- SQLクエリの構築 (ここが核心) ---

    # 1. SELECT句: 必要なカラムを明示的に指定
    select_clause = """
        SELECT
            j.normalized_app_num   AS app_num,
            s.standard_char_t       AS mark_text,
            
            j.shutugan_bi           AS app_date,
            j.reg_reg_ymd           AS reg_date,
            r.reg_num               AS reg_no,
            h.right_person_name     AS owner_name,
            h.right_person_addr     AS owner_addr,
            sd.shohyonoshousaina_setumei AS detailed_description,
            j.raz_kohohakko_bi      AS reg_pub_date,
            j.pcz_kokaikohohakko_bi AS pub_date,
            tbi.prior_app_right_occr_dt AS prior_app_date,
            tbi.conti_prd_expire_dt AS expiry_date,
            j.kubun_su              AS class_count,
            tai.right_request       AS additional_info,
            tknd.knd                AS intl_class_version, -- 国際分類版表示
            iut.search_use_t        AS trademark_kana
    """

    # 2. FROM句とJOIN: 必要なテーブルをすべて結合
    from_clause = """
        FROM jiken_c_t AS j
        LEFT JOIN standard_char_t_art           AS s ON j.normalized_app_num = s.normalized_app_num
        LEFT JOIN reg_mapping                   AS r ON j.normalized_app_num = r.app_num
        LEFT JOIN right_person_art_t            AS h ON r.reg_num          = h.reg_num
        LEFT JOIN jiken_c_t_shohin_joho         AS sg ON j.normalized_app_num = sg.normalized_app_num
        LEFT JOIN goods_class_art               AS gca ON j.normalized_app_num = gca.normalized_app_num
        LEFT JOIN t_basic_item_art              AS tbi ON j.normalized_app_num = tbi.normalized_app_num
        LEFT JOIN t_add_info                    AS tai ON j.normalized_app_num = tai.normalized_app_num
        LEFT JOIN t_knd_info_art_table          AS tknd ON j.normalized_app_num = tknd.normalized_app_num
        LEFT JOIN jiken_c_t_shousaina_setumei   AS sd  ON j.normalized_app_num = sd.normalized_app_num
        LEFT JOIN search_use_t_art_table        AS iut ON j.normalized_app_num = iut.normalized_app_num
        -- LEFT JOIN t_dsgnt_art                   AS td ON j.normalized_app_num = td.normalized_app_num -- 称呼は個別取得に変更
    """

    

    # --- クエリの実行 ---
    try:
        # 動的にWHERE句を組み立てるため、サブクエリで対象のapp_numを絞り込む
        sub_query_from_parts = ["FROM jiken_c_t j"]
        sub_query_where_parts = ["1=1"] # Always true to allow easy ANDing
        sub_query_params = []

        if kw_app:
            sub_query_where_parts.append("j.normalized_app_num = ?")
            sub_query_params.append(kw_app.replace("-", ""))
        if kw_mark:
            sub_query_from_parts.append("LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num")
            sub_query_where_parts.append("s.standard_char_t LIKE ?")
            sub_query_params.append(f"%{kw_mark}%")

        if kw_goods_classes:
            sub_query_from_parts.append("""
                LEFT JOIN (
                    SELECT normalized_app_num, GROUP_CONCAT(DISTINCT goods_classes) AS concatenated_classes
                    FROM goods_class_art
                    GROUP BY normalized_app_num
                ) AS grouped_gca ON j.normalized_app_num = grouped_gca.normalized_app_num
            """)
            terms = kw_goods_classes.split()
            for term in terms:
                sub_query_where_parts.append("grouped_gca.concatenated_classes LIKE ?")
                sub_query_params.append(f"%{term}%")

        if kw_designated_goods:
            sub_query_from_parts.append("""
                LEFT JOIN (
                    SELECT normalized_app_num, GROUP_CONCAT(DISTINCT designated_goods) AS concatenated_goods
                    FROM jiken_c_t_shohin_joho
                    GROUP BY normalized_app_num
                ) AS grouped_sg ON j.normalized_app_num = grouped_sg.normalized_app_num
            """)
            terms = kw_designated_goods.split()
            for term in terms:
                sub_query_where_parts.append("grouped_sg.concatenated_goods LIKE ?")
                sub_query_params.append(f"%{term}%")

        if kw_similar_group_codes:
            sub_query_from_parts.append("""
                LEFT JOIN (
                    SELECT normalized_app_num, GROUP_CONCAT(DISTINCT smlr_dsgn_group_cd) AS concatenated_codes
                    FROM t_knd_info_art_table
                    GROUP BY normalized_app_num
                ) AS grouped_tknd ON j.normalized_app_num = grouped_tknd.normalized_app_num
            """)
            terms = kw_similar_group_codes.split()
            for term in terms:
                sub_query_where_parts.append("grouped_tknd.concatenated_codes LIKE ?")
                sub_query_params.append(f"%{term}%")

        sub_query_from = " ".join(sub_query_from_parts)
        sub_query_where = " AND ".join(sub_query_where_parts)

        # 総件数取得
        count_sql = f"SELECT COUNT(DISTINCT j.normalized_app_num) AS total {sub_query_from} WHERE {sub_query_where}"
        count_result = query_db_one(count_sql, tuple(sub_query_params))
        total_results = count_result['total'] if count_result else 0
        total_pages = math.ceil(total_results / per_page) if total_results > 0 else 0

        if total_results > 0:
            # 1. 対象の出願番号リストを取得
            app_num_sql = f"SELECT DISTINCT j.normalized_app_num {sub_query_from} WHERE {sub_query_where} ORDER BY j.normalized_app_num LIMIT ? OFFSET ?"
            app_num_rows = query_db(app_num_sql, tuple(sub_query_params + [per_page, offset]))
            app_nums = [row['normalized_app_num'] for row in app_num_rows]

            if app_nums:
                placeholders = ",".join("?" for _ in app_nums)

                # 2. 基本情報を取得
                main_sql = f"{select_clause} {from_clause} WHERE j.normalized_app_num IN ({placeholders}) GROUP BY j.normalized_app_num ORDER BY j.normalized_app_num"
                results = query_db(main_sql, tuple(app_nums))
                results_map = {row['app_num']: row for row in results}

                # 3. GROUP_CONCATが必要な情報と画像を一括で取得
                # 画像データ (連結処理)
                image_sql = f"""SELECT normalized_app_num, GROUP_CONCAT(image_data, '') AS val FROM (
                                SELECT normalized_app_num, image_data, rec_seq_num FROM t_sample 
                                WHERE normalized_app_num IN ({placeholders}) ORDER BY normalized_app_num, CAST(rec_seq_num AS INTEGER)
                            ) GROUP BY normalized_app_num"""
                image_map = {row['normalized_app_num']: row['val'] for row in query_db(image_sql, app_nums)}

                # 類似群コード
                similar_codes_sql = f"SELECT normalized_app_num, GROUP_CONCAT(DISTINCT smlr_dsgn_group_cd) AS val FROM t_knd_info_art_table WHERE normalized_app_num IN ({placeholders}) GROUP BY normalized_app_num"
                similar_codes_map = {row['normalized_app_num']: row['val'] for row in query_db(similar_codes_sql, app_nums)}

                # 商品・役務区分
                goods_classes_sql = f"SELECT normalized_app_num, GROUP_CONCAT(DISTINCT goods_classes) AS val FROM goods_class_art WHERE normalized_app_num IN ({placeholders}) GROUP BY normalized_app_num"
                goods_classes_map = {row['normalized_app_num']: row['val'] for row in query_db(goods_classes_sql, app_nums)}

                # 指定商品・役務名
                designated_goods_sql = f"SELECT normalized_app_num, GROUP_CONCAT(DISTINCT designated_goods) AS val FROM jiken_c_t_shohin_joho WHERE normalized_app_num IN ({placeholders}) GROUP BY normalized_app_num"
                designated_goods_map = {row['normalized_app_num']: row['val'] for row in query_db(designated_goods_sql, app_nums)}
                
                # 称呼
                call_names_sql = f"SELECT normalized_app_num, GROUP_CONCAT(DISTINCT dsgnt) AS val FROM t_dsgnt_art WHERE normalized_app_num IN ({placeholders}) GROUP BY normalized_app_num"
                call_names_map = {row['normalized_app_num']: row['val'] for row in query_db(call_names_sql, app_nums)}

                # 4. 全情報を結合
                final_results = []
                for app_num in app_nums:
                    row = results_map.get(app_num)
                    if row:
                        row['image_data'] = image_map.get(app_num, '')
                        row['similar_group_codes'] = similar_codes_map.get(app_num, '')
                        row['goods_classes'] = goods_classes_map.get(app_num, '')
                        row['designated_goods'] = designated_goods_map.get(app_num, '')
                        row['call_name'] = call_names_map.get(app_num, '')
                        final_results.append(row)
                results = final_results

    except (FileNotFoundError, sqlite3.Error) as e:
        error = str(e)
        results = []
        total_results = 0
        total_pages = 0

    # --- レンダリング (変更なし) ---
    return render_template("index_enhanced.html",
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
                           per_page_options=PER_PAGE_OPTIONS)

if __name__ == "__main__":
    app.run(debug=True, port=5002) # ポートを5002に変更して、元のアプリと同時に動かせるようにする

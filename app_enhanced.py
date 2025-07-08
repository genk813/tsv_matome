#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request
import sqlite3
from pathlib import Path
import math

app = Flask(__name__)
import re

@app.template_filter('format_similar_code')
def format_similar_group_code(codes_str):
    if not codes_str:
        return ""
    # 類似群コードのパターン (例: 11C01, 35A01)
    # 連続するコードをすべて抽出し、スペースで結合する
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
        return date_str # 不正な形式の場合はそのまま返す
    try:
        year = date_str[0:4]
        month = date_str[4:6]
        day = date_str[6:8]
        return f"{year}/{month}/{day}"
    except:
        return date_str # 変換エラーの場合もそのまま返す
# スクリプトの場所を基準にDBパスを解決
DB_PATH = Path(__file__).parent.resolve() / "output.db"

PER_PAGE_OPTIONS = [20, 50, 100, 200]
DEFAULT_PER_PAGE = 50

def query_db(sql, params=()):
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found at {DB_PATH}")
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.execute(sql, params)
    rows = [dict(row) for row in cur.fetchall()]
    con.close()
    return rows

def query_db_one(sql, params=()):
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found at {DB_PATH}")
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.execute(sql, params)
    row = cur.fetchone()
    con.close()
    return dict(row) if row else None

@app.route("/", methods=["GET", "POST"])
def index():
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
        results = [] # 初期表示時に結果を表示しない
        total_results = 0 # 初期表示時に総件数を0にする
        total_pages = 0 # 初期表示時に総ページ数を0にする

    # ページと表示件数のバリデーション
    if current_page < 1: current_page = 1
    if per_page not in PER_PAGE_OPTIONS: per_page = DEFAULT_PER_PAGE

    offset = (current_page - 1) * per_page

    base_sql = "FROM mark_index WHERE 1=1"
    params = []

    if kw_app:
        base_sql += " AND app_num = ?"
        params.append(kw_app)
    if kw_mark:
        base_sql += " AND mark_text LIKE ?"
        params.append(f"%{kw_mark}%")
    if kw_goods_classes:
        base_sql += " AND goods_classes LIKE ?"
        params.append(f"%{kw_goods_classes}%")
    if kw_designated_goods:
        base_sql += " AND designated_goods LIKE ?"
        params.append(f"%{kw_designated_goods}%")
    if kw_similar_group_codes:
        base_sql += " AND similar_group_codes LIKE ?"
        params.append(f"%{kw_similar_group_codes}%")

    # 総件数取得
    count_sql = f"SELECT COUNT(*) {base_sql}"
    try:
        count_result = query_db_one(count_sql, params)
        total_results = count_result['COUNT(*)'] if count_result else 0
        total_pages = math.ceil(total_results / per_page) if total_results > 0 else 0
    except (FileNotFoundError, sqlite3.Error) as e:
        error = str(e)
        total_results = 0
        total_pages = 0

    # 検索結果取得
    if total_results > 0: # 結果がある場合のみクエリを実行
        sql = f"SELECT * {base_sql} LIMIT ? OFFSET ?"
        try:
            results = query_db(sql, params + [per_page, offset])
        except (FileNotFoundError, sqlite3.Error) as e:
            error = str(e)
            results = []

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
    app.run(debug=False, port=5001)
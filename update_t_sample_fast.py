#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
update_t_sample_fast.py

output.db の t_sample テーブルを upd_t_sample.tsv の内容で高速に更新するスクリプト。
mark_index の再構築は行わない。
"""
import sqlite3
from pathlib import Path
import pandas as pd
import io

# --- 追加: Pillow関連のimportと設定 ---
import base64
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
# --- 追加ここまで ---

# --- 設定 ---
SCRIPT_DIR = Path(__file__).parent.resolve()
DB_PATH    = SCRIPT_DIR / "output.db"
TSV_PATH   = SCRIPT_DIR / "decoded_tsvs" / "upd_t_sample.txt"

# ヘッダゆれ吸収マップ
COMMON_RENAME = {
    "shutugan_no":    "app_num",
    "shutugan_bango": "app_num",
    "標準文字":       "standard_char_t",
    "出願日":         "shutugan_bi",
    "toroku_bi":      "reg_reg_ymd",
    "raz_toroku_no":  "reg_num",
    "rui": "goods_classes", # 商品・役務区分
    "desig_goods_or_desig_wrk_class": "goods_classes", # 商品・役務区分
    "shohinekimumeisho": "designated_goods", # 指定商品・役務名
}

def update_t_sample_table(con: sqlite3.Connection):
    """upd_t_sample.tsv を読み込んで t_sample テーブルを上書き"""
    if not TSV_PATH.exists():
        raise FileNotFoundError(f"TSV file not found: {TSV_PATH}")

    tbl = "t_sample"

    df = pd.read_csv(
        TSV_PATH,
        sep="\t",
        header=0,
        dtype=str
    ).fillna("")

    df.columns = df.columns.str.strip()
    df.rename(columns=COMMON_RENAME, inplace=True)

    if 'image_data' in df.columns:
        df['image_data'] = df['image_data'].apply(lambda x: '' if str(x).startswith('//') else x)
        print(f"Debug: Filtered image_data for {TSV_PATH.name}. Valid images: {df['image_data'].apply(lambda x: 1 if x else 0).sum()} / Total: {len(df)}")

    if 'app_num' in df.columns:
        df['normalized_app_num'] = df['app_num'].str.replace(r'\D', '', regex=True).str.lstrip('0')
        df['normalized_app_num'] = df['normalized_app_num'].apply(lambda x: '0' if x == '' or x is None else x)

    cols_sql = ", ".join(f'"{c}" TEXT' for c in df.columns)
    con.execute(f'DROP TABLE IF EXISTS "{tbl}"')
    con.execute(f'CREATE TABLE "{tbl}" ({cols_sql});')
    df.to_sql(tbl, con, if_exists="append", index=False)
    print(f"Imported {TSV_PATH.name} -> `{tbl}`")

def main():
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}. Please run build_enhanced_index.py first.")
        return

    with sqlite3.connect(DB_PATH) as con:
        update_t_sample_table(con)
    print("\noutput.db の t_sample テーブルが更新されました。")


if __name__ == '__main__':
    main()

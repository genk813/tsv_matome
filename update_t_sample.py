#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
update_t_sample.py

output.db の t_sample テーブルと mark_index テーブルを
upd_t_sample.tsv の内容で更新する高速なスクリプト。

- t_sample テーブルを upd_t_sample.tsv の内容で上書き
- mark_index テーブルを再構築

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

def build_mark_index(con: sqlite3.Connection):
    """mark_index テーブルを作成"""
    # 必須テーブルチェック
    for tbl, reqs in [
        ('jiken_c_t',      ['normalized_app_num', 'shutugan_bi']),
        ('standard_char_t_art', ['normalized_app_num', 'standard_char_t']),
    ]:
        cols = {c[1] for c in con.execute(f'PRAGMA table_info("{tbl}")')}
        if not set(reqs) <= cols:
            print(f"Required columns {reqs} missing in {tbl}")
            return

    sql = '''
DROP TABLE IF EXISTS mark_index;
CREATE TABLE mark_index AS
SELECT
  j.normalized_app_num   AS app_num,
  s.standard_char_t       AS mark_text,
  CASE WHEN ts.image_data_full = '' THEN NULL ELSE ts.image_data_full END AS image_data,
  j.shutugan_bi           AS app_date,
  j.reg_reg_ymd           AS reg_date,
  r.reg_num               AS reg_no,
  h.right_person_name     AS owner_name,
  h.right_person_addr     AS owner_addr,
  sd.shohyonoshousaina_setumei        AS detailed_description,
  j.raz_kohohakko_bi                  AS reg_pub_date,       -- 登録公報発行日
  j.pcz_kokaikohohakko_bi             AS pub_date,           -- 公開日
  tbi.prior_app_right_occr_dt         AS prior_app_date,     -- 先願権発生日
  tbi.conti_prd_expire_dt             AS expiry_date,        -- 存続期間満了日
  j.kubun_su                          AS class_count,        -- 区分数
  tai.right_request                   AS additional_info,    -- 付加情報 (暫定),
  tknd.knd                            AS intl_class_version, -- 国際分類版表示 (暫定)
  GROUP_CONCAT(DISTINCT tknd.smlr_dsgn_group_cd) AS similar_group_codes,
  GROUP_CONCAT(DISTINCT gca.goods_classes) AS goods_classes,
  GROUP_CONCAT(DISTINCT sg.designated_goods) AS designated_goods,
  iut.search_use_t AS trademark_kana,
  GROUP_CONCAT(DISTINCT td.dsgnt) AS call_name
FROM jiken_c_t                          AS j
LEFT JOIN standard_char_t_art           AS s ON j.normalized_app_num = s.normalized_app_num
LEFT JOIN reg_mapping                   AS r ON j.normalized_app_num = r.app_num
LEFT JOIN right_person_art_t            AS h ON r.reg_num          = h.reg_num
LEFT JOIN jiken_c_t_shohin_joho         AS sg ON j.normalized_app_num = sg.normalized_app_num
LEFT JOIN goods_class_art               AS gca ON j.normalized_app_num = gca.normalized_app_num
LEFT JOIN t_basic_item_art            AS tbi ON j.normalized_app_num = tbi.normalized_app_num
LEFT JOIN t_add_info                  AS tai ON j.normalized_app_num = tai.normalized_app_num
LEFT JOIN t_knd_info_art_table        AS tknd ON j.normalized_app_num = tknd.normalized_app_num
LEFT JOIN jiken_c_t_shousaina_setumei AS sd  ON j.normalized_app_num = sd.normalized_app_num
LEFT JOIN search_use_t_art_table AS iut ON j.normalized_app_num = iut.normalized_app_num
LEFT JOIN t_dsgnt_art AS td ON j.normalized_app_num = td.normalized_app_num
LEFT JOIN (
    SELECT
        normalized_app_num,
        GROUP_CONCAT(image_data, '') AS image_data_full
    FROM (
        SELECT normalized_app_num, image_data, rec_seq_num
        FROM t_sample
        ORDER BY normalized_app_num, CAST(rec_seq_num AS INTEGER)
    )
    GROUP BY normalized_app_num
) AS ts ON j.normalized_app_num = ts.normalized_app_num
GROUP BY j.normalized_app_num;
'''
    con.executescript(sql)

    # インデックス貼り
    for col in ['app_num', 'mark_text', 'app_date', 'reg_date', 'reg_no']:
        con.execute(f"CREATE INDEX IF NOT EXISTS idx_mark_{col} ON mark_index({col})")
    print("mark_index table created")

def main():
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}. Please run build_enhanced_index.py first.")
        return

    with sqlite3.connect(DB_PATH) as con:
        update_t_sample_table(con)
        build_mark_index(con)
    print("\noutput.db has been updated with the new t_sample data.")


if __name__ == '__main__':
    main()

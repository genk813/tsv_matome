#!/usr/bin/env python3
# -*- coding: utf-8 -#
"""
build_enhanced_index.py

1) tsv/ 以下の *.tsv をすべて UTF-8 に正規化して読み込み、
   app_num, standard_char_t, shutugan_bi, reg_num といった必要列を含むテーブルを再作成
2) 明示的に定義したテーブル群 (REG_MAP_TABLES) から
   normalized_app_num／reg_num を UNION して reg_mapping テーブルを作成
3) jiken_c_t (出願日＋登録日) と standard_char_t_art (標準文字) を LEFT JOIN、
   reg_mapping を LEFT JOIN、right_person_art_t を reg_num で LEFT JOIN、
   goods_class_art／jiken_c_t_shohin_joho を LEFT JOIN して
   mark_index テーブルを作成 (出願番号, 商標, 出願日, 登録日, 登録番号, 権利者, 商品区分, 指定商品)
4) 各種インデックスを貼って高速検索を実現

"""
import sqlite3
from pathlib import Path
import pandas as pd
import io

# --- 設定 ---
SCRIPT_DIR = Path(__file__).parent.resolve()
DB_PATH    = SCRIPT_DIR / "output.db"
TSV_DIR    = SCRIPT_DIR / "tsv"

# reg_mapping に使うテーブル一覧 (normalized_app_num と reg_num を含むもの)
REG_MAP_TABLES = [
    "jiken_c_t",
    "mgt_info_t",
    "mrgn_t_rwrt_app_num",
    "prog_info_div_t",
    "trnsfr_rcpt_info_t",
]

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

# 必須列
REQUIRED_COLS = ["app_num", "standard_char_t", "shutugan_bi"]


def import_all_tsv(con: sqlite3.Connection):
    """
    tsv/*.tsv をエンコーディング検出つきで読み込んでテーブル化。
    """
    DECODED_TSV_DIR = SCRIPT_DIR / "decoded_tsvs"
    if not DECODED_TSV_DIR.exists():
        raise FileNotFoundError(f"Decoded TSV directory not found: {DECODED_TSV_DIR}")

    for tsv_file in sorted(DECODED_TSV_DIR.glob("*.txt")):
        tbl = tsv_file.stem.replace("_decoded", "").replace("upd_", "").replace("del_", "")

        # Pandas に流し込む
        df = pd.read_csv(
            tsv_file,
            sep="\t",
            header=0,
            dtype=str
        ).fillna("")

        # 以下、従来どおりの列トリム＆正規化処理へ
        df.columns = df.columns.str.strip()
        df.rename(columns=COMMON_RENAME, inplace=True)

        # --- デバッグ用ログ追加 (ここから) ---
        if tbl == "t_sample" and 'image_data' in df.columns:
            print(f"\n--- Debug: {tsv_file.name} - image_data samples ---")
            for i, val in enumerate(df['image_data'].head(5)):
                print(f"  Row {i}: {val[:100]}... (length: {len(val)})")
            print("--------------------------------------------------")
        # --- デバッグ用ログ追加 (ここまで) ---

        # … (normalized_app_num/reg_num 処理、to_sql など) …
        # 例：
        if 'app_num' in df.columns:
            # 数字以外の文字をすべて削除し、先頭のゼロを削除する
            df['normalized_app_num'] = df['app_num'].str.replace(r'\D', '', regex=True).str.lstrip('0')
            # 空白や'0'だけのものは'0'に統一
            df['normalized_app_num'] = df['normalized_app_num'].apply(lambda x: '0' if x == '' or x is None else x)

        # reg_num が存在する場合、正規化された reg_num を追加
        if 'reg_num' in df.columns:
            df['reg_num'] = df['reg_num'].str.strip()

        cols_sql = ", ".join(f'"{c}" TEXT' for c in df.columns)
        con.execute(f'DROP TABLE IF EXISTS "{tbl}"')
        con.execute(f'CREATE TABLE "{tbl}" ({cols_sql});')
        df.to_sql(tbl, con, if_exists="append", index=False)
        print(f"Imported {tsv_file.name} -> `{tbl}`")


def build_reg_mapping(con: sqlite3.Connection):
    """REG_MAP_TABLES から reg_mapping を作成"""
    selects = []
    for t in REG_MAP_TABLES:
        # テーブル存在チェック
        tables = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table';")]
        if t not in tables:
            continue
        cols = {c[1] for c in con.execute(f'PRAGMA table_info("{t}")')}
        if {'normalized_app_num', 'reg_num'} <= cols:
            selects.append(f'SELECT normalized_app_num AS app_num, reg_num FROM "{t}" WHERE reg_num != \'\'')

    if not selects:
        print("No reg_mapping source tables found.")
        return

    union_sql = '\nUNION\n'.join(selects)
    sql = f"""
DROP TABLE IF EXISTS reg_mapping;
CREATE TABLE reg_mapping AS
{union_sql};
"""
    con.executescript(sql)
    con.execute("CREATE INDEX IF NOT EXISTS idx_reg_app ON reg_mapping(app_num)")
    con.execute("CREATE INDEX IF NOT EXISTS idx_reg_num ON reg_mapping(reg_num)")
    print("reg_mapping table created")


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
  ts.image_data_full      AS image_data,
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
  tknd.knd                            AS intl_class_version, -- 国際分類版表示 (暫定),
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

    # --- デバッグ用ログ追加 (ここから) ---
    print("\n--- Debug: mark_index - image_data_full samples ---")
    cur = con.execute("SELECT app_num, image_data FROM mark_index LIMIT 5;")
    for i, row in enumerate(cur.fetchall()):
        app_num = row['app_num']
        image_data = row['image_data']
        if image_data:
            print(f"  App Num: {app_num}, image_data (first 100 chars): {image_data[:100]}... (length: {len(image_data)})")
        else:
            print(f"  App Num: {app_num}, image_data: None")
    print("--------------------------------------------------")
    # --- デバッグ用ログ追加 (ここまで) ---

    # インデックス貼り
    for col in ['app_num', 'mark_text', 'app_date', 'reg_date', 'reg_no']:
        con.execute(f"CREATE INDEX IF NOT EXISTS idx_mark_{col} ON mark_index({col})")
    print("mark_index table created")


def main():
    if DB_PATH.exists():
        DB_PATH.unlink()
    with sqlite3.connect(DB_PATH) as con:
        import_all_tsv(con)
        build_reg_mapping(con)
        build_mark_index(con)
    print("\noutput.db is ready. mark_index をご確認ください.")


if __name__ == '__main__':
    main()

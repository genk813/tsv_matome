-- output.db用のスキーマ定義
-- 商標データベース用テーブル作成スクリプト

-- メインテーブル：事件情報
CREATE TABLE IF NOT EXISTS jiken_c_t (
    normalized_app_num TEXT PRIMARY KEY,
    shutugan_bi TEXT,           -- 出願日
    reg_reg_ymd TEXT            -- 登録日
);

-- 標準文字商標テーブル
CREATE TABLE IF NOT EXISTS standard_char_t_art (
    normalized_app_num TEXT,
    standard_char_t TEXT,       -- 商標文字
    FOREIGN KEY (normalized_app_num) REFERENCES jiken_c_t(normalized_app_num)
);

-- 商品・役務区分テーブル
CREATE TABLE IF NOT EXISTS goods_class_art (
    processing_type TEXT,       -- 処理種別
    law_cd TEXT,               -- 四法コード
    reg_num TEXT,              -- 登録番号
    split_num TEXT,            -- 分割番号
    normalized_app_num TEXT,   -- 出願番号（正規化）
    goods_cls_art_upd_ymd TEXT, -- 更新年月日
    mu_num TEXT,               -- MU番号
    goods_classes TEXT,        -- 指定商品又は指定役務の区分
    FOREIGN KEY (normalized_app_num) REFERENCES jiken_c_t(normalized_app_num)
);

-- 指定商品・役務情報テーブル
CREATE TABLE IF NOT EXISTS jiken_c_t_shohin_joho (
    normalized_app_num TEXT,
    designated_goods TEXT,      -- 指定商品・役務
    FOREIGN KEY (normalized_app_num) REFERENCES jiken_c_t(normalized_app_num)
);

-- 類似群コードテーブル
CREATE TABLE IF NOT EXISTS t_knd_info_art_table (
    normalized_app_num TEXT,
    smlr_dsgn_group_cd TEXT,    -- 類似群コード
    FOREIGN KEY (normalized_app_num) REFERENCES jiken_c_t(normalized_app_num)
);

-- 登録マッピングテーブル
CREATE TABLE IF NOT EXISTS reg_mapping (
    app_num TEXT,
    reg_num TEXT,
    FOREIGN KEY (app_num) REFERENCES jiken_c_t(normalized_app_num)
);

-- 権利者情報テーブル
CREATE TABLE IF NOT EXISTS right_person_art_t (
    processing_type TEXT,       -- 処理種別
    law_cd TEXT,               -- 四法コード
    reg_num TEXT,              -- 登録番号
    split_num TEXT,            -- 分割番号
    normalized_app_num TEXT,   -- 出願番号（正規化）
    rec_num TEXT,              -- レコード番号
    pe_num TEXT,               -- PE番号
    right_psn_art_upd_ymd TEXT, -- 更新年月日
    right_person_appl_id TEXT,  -- 権利者申請人ID
    right_person_addr_len TEXT, -- 権利者住所レングス
    right_person_addr TEXT,     -- 権利者住所
    right_person_name_len TEXT, -- 権利者氏名レングス
    right_person_name TEXT,     -- 権利者氏名
    FOREIGN KEY (normalized_app_num) REFERENCES jiken_c_t(normalized_app_num)
);

-- 称呼テーブル
CREATE TABLE IF NOT EXISTS t_dsgnt_art (
    normalized_app_num TEXT,
    dsgnt TEXT,                 -- 称呼
    FOREIGN KEY (normalized_app_num) REFERENCES jiken_c_t(normalized_app_num)
);

-- サンプル・画像データテーブル
CREATE TABLE IF NOT EXISTS t_sample (
    normalized_app_num TEXT,
    image_data TEXT,            -- 画像データ
    rec_seq_num INTEGER,        -- レコード順序番号
    FOREIGN KEY (normalized_app_num) REFERENCES jiken_c_t(normalized_app_num)
);

-- 表示用商標テーブル
CREATE TABLE IF NOT EXISTS indct_use_t_art (
    normalized_app_num TEXT,
    indct_use_t TEXT,           -- 表示用商標
    FOREIGN KEY (normalized_app_num) REFERENCES jiken_c_t(normalized_app_num)
);

-- 検索用商標テーブル
CREATE TABLE IF NOT EXISTS search_use_t_art_table (
    normalized_app_num TEXT,
    search_use_t_seq INTEGER,   -- 検索用商標順序
    search_use_t TEXT,          -- 検索用商標
    FOREIGN KEY (normalized_app_num) REFERENCES jiken_c_t(normalized_app_num)
);

-- パフォーマンス向上のためのインデックス
CREATE INDEX IF NOT EXISTS idx_jiken_c_t_app_num ON jiken_c_t(normalized_app_num);
CREATE INDEX IF NOT EXISTS idx_standard_char_app_num ON standard_char_t_art(normalized_app_num);
CREATE INDEX IF NOT EXISTS idx_standard_char_text ON standard_char_t_art(standard_char_t);
CREATE INDEX IF NOT EXISTS idx_goods_class_app_num ON goods_class_art(normalized_app_num);
CREATE INDEX IF NOT EXISTS idx_goods_class_classes ON goods_class_art(goods_classes);
CREATE INDEX IF NOT EXISTS idx_shohin_joho_app_num ON jiken_c_t_shohin_joho(normalized_app_num);
CREATE INDEX IF NOT EXISTS idx_shohin_joho_goods ON jiken_c_t_shohin_joho(designated_goods);
CREATE INDEX IF NOT EXISTS idx_knd_info_app_num ON t_knd_info_art_table(normalized_app_num);
CREATE INDEX IF NOT EXISTS idx_knd_info_code ON t_knd_info_art_table(smlr_dsgn_group_cd);
CREATE INDEX IF NOT EXISTS idx_reg_mapping_app_num ON reg_mapping(app_num);
CREATE INDEX IF NOT EXISTS idx_reg_mapping_reg_num ON reg_mapping(reg_num);
CREATE INDEX IF NOT EXISTS idx_right_person_reg_num ON right_person_art_t(reg_num);
CREATE INDEX IF NOT EXISTS idx_right_person_app_num ON right_person_art_t(normalized_app_num);
CREATE INDEX IF NOT EXISTS idx_dsgnt_app_num ON t_dsgnt_art(normalized_app_num);
CREATE INDEX IF NOT EXISTS idx_sample_app_num ON t_sample(normalized_app_num);
CREATE INDEX IF NOT EXISTS idx_indct_use_app_num ON indct_use_t_art(normalized_app_num);
CREATE INDEX IF NOT EXISTS idx_indct_use_text ON indct_use_t_art(indct_use_t);
CREATE INDEX IF NOT EXISTS idx_search_use_app_num ON search_use_t_art_table(normalized_app_num);
CREATE INDEX IF NOT EXISTS idx_search_use_text ON search_use_t_art_table(search_use_t);

-- 申請人関連テーブル
CREATE TABLE IF NOT EXISTS jiken_c_t_shutugannindairinin (
    shutugan_no TEXT,              -- 出願番号
    shutugannindairinin_code TEXT, -- 申請人コード
    shutugannindairinin_sikbt TEXT, -- 申請人識別区分
    FOREIGN KEY (shutugan_no) REFERENCES jiken_c_t(normalized_app_num)
);

CREATE TABLE IF NOT EXISTS applicant_master (
    appl_cd TEXT PRIMARY KEY,      -- 申請人コード
    appl_name TEXT,               -- 申請人名
    appl_addr TEXT                -- 申請人住所
);

CREATE TABLE IF NOT EXISTS applicant_mapping (
    applicant_code TEXT,          -- 申請人コード
    applicant_name TEXT,          -- 申請人名
    applicant_addr TEXT,          -- 申請人住所
    trademark_count INTEGER       -- 商標件数
);

-- 検索最適化用のVIEW
CREATE VIEW IF NOT EXISTS v_goods_classes AS
SELECT 
    normalized_app_num,
    GROUP_CONCAT(DISTINCT goods_classes) AS concatenated_classes
FROM goods_class_art
GROUP BY normalized_app_num;

CREATE VIEW IF NOT EXISTS v_designated_goods AS
SELECT 
    normalized_app_num,
    GROUP_CONCAT(DISTINCT designated_goods) AS concatenated_goods
FROM jiken_c_t_shohin_joho
GROUP BY normalized_app_num;

CREATE VIEW IF NOT EXISTS v_similar_group_codes AS
SELECT 
    normalized_app_num,
    GROUP_CONCAT(DISTINCT smlr_dsgn_group_cd) AS concatenated_codes
FROM t_knd_info_art_table
GROUP BY normalized_app_num;

-- 追加のパフォーマンス向上インデックス
CREATE INDEX IF NOT EXISTS idx_shutugannindairinin_app_num ON jiken_c_t_shutugannindairinin(shutugan_no);
CREATE INDEX IF NOT EXISTS idx_shutugannindairinin_code ON jiken_c_t_shutugannindairinin(shutugannindairinin_code);
CREATE INDEX IF NOT EXISTS idx_applicant_mapping_code ON applicant_mapping(applicant_code);
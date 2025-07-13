-- Phase 2: 国際商標データベーススキーマ
-- Madrid Protocol (マドプロ) 国際商標データ用テーブル

-- 1. 国際商標登録管理情報 (org_reg_mgt_info)
CREATE TABLE IF NOT EXISTS intl_trademark_registration (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    add_del_id TEXT,                    -- 追加削除識別
    intl_reg_num TEXT NOT NULL,         -- 国際登録番号 (主キー)
    intl_reg_num_updt_cnt_sign_cd TEXT, -- 更新回数記号コード
    intl_reg_num_split_sign_cd TEXT,    -- 分割記号コード
    app_num TEXT,                       -- 庁内整理番号（出願番号）
    app_num_split_sign_cd TEXT,         -- 出願番号分割記号コード
    app_date TEXT,                      -- 出願年月日
    intl_reg_date TEXT,                 -- 国際登録日
    effective_date TEXT,                -- 効力発生日
    basic_app_ctry_cd TEXT,             -- 基礎出願国コード
    basic_app_num TEXT,                 -- 基礎出願番号
    basic_app_date TEXT,                -- 基礎出願日
    basic_reg_ctry_cd TEXT,             -- 基礎登録国コード
    basic_reg_num TEXT,                 -- 基礎登録番号
    basic_reg_date TEXT,                -- 基礎登録日
    rep_figure_num TEXT,                -- 代表図形番号
    vienna_class TEXT,                  -- ウィーン分類
    color_claim_flg TEXT,               -- 色彩主張フラグ
    app_lang_cd TEXT,                   -- 出願言語コード
    second_lang_cd TEXT,                -- 第二言語コード
    define_flg TEXT,                    -- 確定フラグ
    updt_year_month_day TEXT,           -- 更新年月日
    batch_updt_year_month_day TEXT,     -- バッチ更新年月日
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(intl_reg_num, intl_reg_num_updt_cnt_sign_cd, intl_reg_num_split_sign_cd)
);

-- 2. 国際商標進行情報 (prog_info)
CREATE TABLE IF NOT EXISTS intl_trademark_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    add_del_id TEXT,
    intl_reg_num TEXT NOT NULL,         -- 国際登録番号
    intl_reg_num_updt_cnt_sign_cd TEXT,
    intl_reg_num_split_sign_cd TEXT,
    prog_seq TEXT,                      -- 進行順序
    prog_cd TEXT,                       -- 進行コード
    prog_date TEXT,                     -- 進行年月日
    prog_content TEXT,                  -- 進行内容
    define_flg TEXT,
    updt_year_month_day TEXT,
    batch_updt_year_month_day TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (intl_reg_num) REFERENCES intl_trademark_registration(intl_reg_num)
);

-- 3. 国際商標権者名義・住所 (set_crr_nm_addr)
CREATE TABLE IF NOT EXISTS intl_trademark_holder (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    add_del_id TEXT,
    intl_reg_num TEXT NOT NULL,         -- 国際登録番号
    intl_reg_num_updt_cnt_sign_cd TEXT,
    intl_reg_num_split_sign_cd TEXT,
    holder_seq TEXT,                    -- 権者順序
    holder_name TEXT,                   -- 権者名
    holder_name_japanese TEXT,          -- 権者名和訳
    holder_addr TEXT,                   -- 権者住所
    holder_addr_japanese TEXT,          -- 権者住所和訳
    holder_ctry_cd TEXT,                -- 権者国コード
    define_flg TEXT,
    updt_year_month_day TEXT,
    batch_updt_year_month_day TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (intl_reg_num) REFERENCES intl_trademark_registration(intl_reg_num)
);

-- 4. 国際商標指定商品・サービス (set_dsgn_gds_srvc)
CREATE TABLE IF NOT EXISTS intl_trademark_goods_services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    add_del_id TEXT,
    intl_reg_num TEXT NOT NULL,         -- 国際登録番号
    intl_reg_num_updt_cnt_sign_cd TEXT,
    intl_reg_num_split_sign_cd TEXT,
    aft_desig_year_month_day TEXT,      -- 事後指定年月日
    temp_principal_reg_id_flg TEXT,     -- 仮・本登録識別フラグ
    indct_seq TEXT,                     -- 表示順序
    goods_seq TEXT,                     -- 指定商品順序
    goods_class TEXT,                   -- 商品・サービス分類（マドプロ分類）
    goods_content TEXT,                 -- 指定商品・サービス内容
    intl_reg_rec_dt TEXT,              -- 国際登録記録日
    define_flg TEXT,
    updt_year_month_day TEXT,
    batch_updt_year_month_day TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (intl_reg_num) REFERENCES intl_trademark_registration(intl_reg_num)
);

-- 5. 国際商標第一表示部（商標テキスト） (set_frst_indct)
CREATE TABLE IF NOT EXISTS intl_trademark_text (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    add_del_id TEXT,
    intl_reg_num TEXT NOT NULL,         -- 国際登録番号
    intl_reg_num_updt_cnt_sign_cd TEXT,
    intl_reg_num_split_sign_cd TEXT,
    aft_desig_year_month_day TEXT,      -- 事後指定年月日
    temp_principal_reg_id_flg TEXT,     -- 仮・本登録識別フラグ
    indct_seq TEXT,                     -- 表示順序
    finl_dcsn_year_month_day TEXT,      -- 査定年月日
    trial_dcsn_year_month_day TEXT,     -- 審決年月日
    pri_app_gvrn_cntrcntry_cd TEXT,     -- 優先権出願官庁締約国等コード
    pri_app_year_month_day TEXT,        -- 優先権出願年月日
    pri_clim_cnt TEXT,                  -- 優先権主張件数
    special_t_typ_flg TEXT,             -- 特殊商標のタイプフラグ
    group_cert_warranty_flg TEXT,       -- 団体証明保証フラグ
    define_flg TEXT,                    -- 確定フラグ
    updt_year_month_day TEXT,           -- 更新年月日
    batch_updt_year_month_day TEXT,     -- バッチ更新年月日
    t_dtl_explntn TEXT,                 -- 商標の詳細な説明（商標テキスト）
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (intl_reg_num) REFERENCES intl_trademark_registration(intl_reg_num)
);

-- インデックス作成
CREATE INDEX IF NOT EXISTS idx_intl_reg_num ON intl_trademark_registration(intl_reg_num);
CREATE INDEX IF NOT EXISTS idx_intl_prog_reg_num ON intl_trademark_progress(intl_reg_num);
CREATE INDEX IF NOT EXISTS idx_intl_holder_reg_num ON intl_trademark_holder(intl_reg_num);
CREATE INDEX IF NOT EXISTS idx_intl_goods_reg_num ON intl_trademark_goods_services(intl_reg_num);
CREATE INDEX IF NOT EXISTS idx_intl_goods_class ON intl_trademark_goods_services(goods_class);
CREATE INDEX IF NOT EXISTS idx_intl_text_reg_num ON intl_trademark_text(intl_reg_num);
CREATE INDEX IF NOT EXISTS idx_intl_text_dtl ON intl_trademark_text(t_dtl_explntn);

-- 検索用ビュー（国際商標統合検索）
CREATE VIEW IF NOT EXISTS intl_trademark_search_view AS
SELECT 
    r.intl_reg_num,
    r.app_num,
    r.app_date,
    r.intl_reg_date,
    r.basic_app_ctry_cd,
    r.basic_reg_ctry_cd,
    h.holder_name,
    h.holder_name_japanese,
    t.t_dtl_explntn as trademark_text,
    GROUP_CONCAT(g.goods_class) as goods_classes,
    GROUP_CONCAT(g.goods_content) as goods_content
FROM intl_trademark_registration r
LEFT JOIN intl_trademark_holder h ON r.intl_reg_num = h.intl_reg_num
LEFT JOIN intl_trademark_goods_services g ON r.intl_reg_num = g.intl_reg_num  
LEFT JOIN intl_trademark_text t ON r.intl_reg_num = t.intl_reg_num
WHERE r.define_flg = '1'  -- 確定フラグが立っているもののみ
GROUP BY r.intl_reg_num, r.app_num, r.app_date, r.intl_reg_date, 
         r.basic_app_ctry_cd, r.basic_reg_ctry_cd, h.holder_name, 
         h.holder_name_japanese, t.t_dtl_explntn;
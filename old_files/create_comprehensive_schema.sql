-- TMCloud 包括的データベーススキーマ
-- TSV_FILES_COMPLETE_SPECIFICATION.mdに基づく全82テーブルの定義

-- ===================================
-- 1. 商標基本情報テーブル (core_trademark)
-- ===================================

-- 事件フォルダ_商標（主テーブル）
CREATE TABLE IF NOT EXISTS jiken_c_t (
    masterkosin_nitiji TEXT,
    yonpo_code TEXT,
    shutugan_no TEXT PRIMARY KEY,
    shutugan_bi TEXT,
    shutugan_shubetu1 TEXT,
    shutugan_shubetu2 TEXT,
    shutugan_shubetu3 TEXT,
    shutugan_shubetu4 TEXT,
    shutugan_shubetu5 TEXT,
    seiri_no TEXT,
    saishushobun_shubetu TEXT,
    saishushobun_bi TEXT,
    raz_toroku_no TEXT,
    raz_bunkatu_no TEXT,
    bogo_no TEXT,
    toroku_bi TEXT,
    raz_sotugo_su TEXT,
    raz_nenkantugo_su TEXT,
    raz_kohohakko_bi TEXT,
    tantokan_code TEXT,
    pcz_kokaikohohakko_bi TEXT,
    kubun_su TEXT,
    torokusateijikubun_su TEXT,
    hyojunmoji_umu TEXT,
    rittaishohyo_umu TEXT,
    hyoshosikisai_umu TEXT,
    shohyoho3jo2ko_flag TEXT,
    shohyoho5jo4ko_flag TEXT,
    genshutugan_shubetu TEXT,
    genshutuganyonpo_code TEXT,
    genshutugan_no TEXT,
    sokyu_bi TEXT,
    obz_shutugan_no TEXT,
    obz_toroku_no TEXT,
    obz_bunkatu_no TEXT,
    kosintoroku_no TEXT,
    pez_bunkatu_no TEXT,
    pez_bogo_no TEXT,
    kakikaetoroku_no TEXT,
    ktz_bunkatu_no TEXT,
    ktz_bogo_no TEXT,
    krz_kojoryozokuihan_flag TEXT,
    sokisinsa_mark TEXT,
    tekiyohoki_kubun TEXT,
    sinsa_shubetu TEXT,
    sosho_code TEXT,
    satei_shubetu TEXT,
    igiken_su TEXT,
    igiyuko_su TEXT
);

-- 商標テキスト関連テーブル
CREATE TABLE IF NOT EXISTS standard_char_t_art (
    add_del_id TEXT,
    app_num TEXT,
    split_num TEXT,
    sub_data_num TEXT,
    standard_char_t TEXT,
    PRIMARY KEY (app_num, split_num, sub_data_num)
);

CREATE TABLE IF NOT EXISTS indct_use_t_art (
    add_del_id TEXT,
    app_num TEXT,
    split_num TEXT,
    sub_data_num TEXT,
    indct_use_t TEXT,
    PRIMARY KEY (app_num, split_num, sub_data_num)
);

CREATE TABLE IF NOT EXISTS search_use_t_art_table (
    add_del_id TEXT,
    app_num TEXT,
    split_num TEXT,
    sub_data_num TEXT,
    search_use_t TEXT,
    PRIMARY KEY (app_num, split_num, sub_data_num)
);

-- ===================================
-- 2. 分類・商品情報テーブル (classification)
-- ===================================

-- 商品情報（重要：rui列を含む）
CREATE TABLE IF NOT EXISTS jiken_c_t_shohin_joho (
    yonpo_code TEXT,
    shutugan_no TEXT,
    rui TEXT,  -- 類（区分）
    lengthchoka_flag TEXT,
    shohinekimumeisho TEXT,
    abz_junjo_no TEXT,
    PRIMARY KEY (yonpo_code, shutugan_no, abz_junjo_no)
);

-- 商品区分記事
CREATE TABLE IF NOT EXISTS goods_class_art (
    processing_type TEXT,
    law_cd TEXT,
    reg_num TEXT,
    split_num TEXT,
    app_num TEXT,
    goods_cls_art_upd_ymd TEXT,
    mu_num TEXT,
    desig_goods_or_desig_wrk_class TEXT,
    PRIMARY KEY (law_cd, reg_num, split_num, app_num, mu_num)
);

-- 類似群コード情報
CREATE TABLE IF NOT EXISTS t_knd_info_art_table (
    add_del_id TEXT,
    app_num TEXT,
    split_num TEXT,
    smlr_dsgn_group_cd TEXT,
    PRIMARY KEY (app_num, split_num)
);

-- ===================================
-- 3. 出願人・代理人情報 (applicant_agent)
-- ===================================

-- 申請人登録情報（マスタ）
CREATE TABLE IF NOT EXISTS appl_reg_info (
    data_id_cd TEXT,
    appl_cd TEXT PRIMARY KEY,
    appl_name TEXT,
    appl_cana_name TEXT,
    appl_postcode TEXT,
    appl_addr TEXT,
    wes_join_name TEXT,
    wes_join_addr TEXT,
    integ_appl_cd TEXT,
    dbl_reg_integ_mgt_srl_num TEXT
);

-- 出願人代理人情報
CREATE TABLE IF NOT EXISTS jiken_c_t_shutugannindairinin (
    yonpo_code TEXT,
    shutugan_no TEXT,
    shutugannindairinin_sikbt TEXT,
    shutugannindairinin_code TEXT,
    gez_henko_no TEXT,
    gez_kohokan_kubun TEXT,
    gez_kokken_code TEXT,
    daihyoshutugannin_sikibetu TEXT,
    jokishutugannin_nanmei TEXT,
    dairininhoka_nanmei TEXT,
    dairinin_shubetu TEXT,
    dairininsikaku_shubetu TEXT,
    shutugannindairinin_jusho TEXT,
    shutugannindairinin_simei TEXT,
    gez_junjo_no TEXT,
    PRIMARY KEY (yonpo_code, shutugan_no, gez_junjo_no)
);

-- 代理人記事（商標）
CREATE TABLE IF NOT EXISTS atty_art_t (
    processing_type TEXT,
    law_cd TEXT,
    reg_num TEXT,
    split_num TEXT,
    app_num TEXT,
    rec_num TEXT,
    pe_num TEXT,
    atty_art_upd_ymd TEXT,
    atty_appl_id TEXT,
    atty_typ TEXT,
    atty_name_len TEXT,
    atty_name TEXT,
    PRIMARY KEY (law_cd, reg_num, split_num, app_num, rec_num, pe_num)
);

-- 権利者記事（商標）
CREATE TABLE IF NOT EXISTS right_person_art_t (
    processing_type TEXT,
    law_cd TEXT,
    reg_num TEXT,
    split_num TEXT,
    app_num TEXT,
    rec_num TEXT,
    pe_num TEXT,
    right_person_art_upd_ymd TEXT,
    right_person_appl_id TEXT,
    right_person_name_len TEXT,
    right_person_name TEXT,
    right_person_addr_len TEXT,
    right_person_addr TEXT,
    share TEXT,
    postcode TEXT,
    PRIMARY KEY (law_cd, reg_num, split_num, app_num, rec_num, pe_num)
);

-- ===================================
-- 4. 国際商標関連 (international)
-- ===================================

-- 国際商標登録原簿マスタ_原簿管理情報
CREATE TABLE IF NOT EXISTS intl_t_org_org_reg_mgt_info (
    add_del_id TEXT,
    intl_reg_num TEXT,
    intl_reg_num_updt_cnt_sign_cd TEXT,
    intl_reg_num_split_sign_cd TEXT,
    aft_desig_year_month_day TEXT,
    intl_reg_year_month_day TEXT,
    jpo_rfr_num TEXT,
    jpo_rfr_num_split_sign_cd TEXT,
    set_reg_year_month_day TEXT,
    right_ersr_id TEXT,
    right_disppr_year_month_day TEXT,
    close_reg_year_month_day TEXT,
    inspct_prhbt_flg TEXT,
    define_flg TEXT,
    updt_year_month_day TEXT,
    batch_updt_year_month_day TEXT,
    PRIMARY KEY (intl_reg_num, intl_reg_num_updt_cnt_sign_cd, intl_reg_num_split_sign_cd, aft_desig_year_month_day, define_flg)
);

-- 指定国官庁マスタ_マーク
CREATE TABLE IF NOT EXISTS design_state_gvrnmnt_mstr_mk (
    jpo_rfr_num TEXT,
    jpo_rfr_num_split_sign_cd TEXT,
    history_num TEXT,
    standard_char_declarat_flg TEXT,
    color_clim_detail TEXT,
    color_clim_detail_japanese TEXT,
    emblem_transliterat_detail TEXT,
    three_dmns_emblem_flg TEXT,
    sound_t_flg TEXT,
    group_cert_warranty_flg TEXT,
    emblem_doc_detail TEXT,
    emblem_doc_detail_japanese TEXT,
    vienna_class TEXT,
    exam_art_03_prgrph_02_flg TEXT,
    exam_color_proviso_apply_flg TEXT,
    exam_art_09_prgrph_01_flg TEXT,
    acclrtd_exam_class TEXT,
    define_flg TEXT,
    updt_year_month_day TEXT,
    batch_updt_year_month_day TEXT,
    special_t_typ TEXT,
    t_dtl_explntn TEXT,
    t_dtl_explntn_japanese TEXT,
    dtl_explntn_doc_submt_dt TEXT,
    color_chk_box TEXT,
    disclaimer TEXT,
    opt_emblem_doc_detail TEXT,
    opt_emblem_doc_detail_jp TEXT,
    PRIMARY KEY (jpo_rfr_num, jpo_rfr_num_split_sign_cd, history_num, define_flg)
);

-- ===================================
-- 5. ステータス管理 (status_management)
-- ===================================

-- 管理情報（商標）
CREATE TABLE IF NOT EXISTS mgt_info_t (
    processing_type TEXT,
    law_cd TEXT,
    reg_num TEXT,
    split_num TEXT,
    app_num TEXT,
    latest_flg TEXT,
    entry_id TEXT,
    mgt_info_art_upd_ymd TEXT,
    app_ymd TEXT,
    app_typ TEXT,
    sec_reg_split_num TEXT,
    prev_app_num TEXT,
    prev_app_ymd TEXT,
    pri_app_occr_ymd TEXT,
    open_pubctn_publ_ymd TEXT,
    vew_pubctn_publ_ymd TEXT,
    pre_exam_rjct_dspch_ymd TEXT,
    rjct_fin_dspch_ymd TEXT,
    reg_pubctn_publ_ymd TEXT,
    old_law_abst_class TEXT,
    set_reg_ymd TEXT,
    right_ersr_ymd TEXT,
    right_disppr_ymd TEXT,
    rights_duration_exp_ymd TEXT,
    intl_reg_num TEXT,
    intl_reg_split_sign TEXT,
    intl_reg_ymd TEXT,
    jpo_rfr_num TEXT,
    jpo_rfr_num_split_sign TEXT,
    aft_desig_ymd TEXT,
    exam_final_dspst_ymd TEXT,
    reg_dcsn_ymd TEXT,
    installments_id TEXT,
    installments_exp_dt TEXT,
    standard_char_decrlrt_id TEXT,
    installments_clr_id TEXT,
    PRIMARY KEY (law_cd, reg_num, split_num, app_num)
);

-- 発送書類
CREATE TABLE IF NOT EXISTS hssu_syri (
    skbt_flg TEXT,
    hssu_syri_bngu TEXT PRIMARY KEY,
    snpn_bngu TEXT,
    tyukn_cd TEXT,
    gnsyri_bngu TEXT,
    syri_hssu_dt TEXT,
    atsk_sybt TEXT,
    ig_tuzsy_bngu TEXT,
    snk_snsi_bngu TEXT,
    uktk_syri_bngu TEXT,
    kan_dt TEXT,
    yuku_flg TEXT,
    tiou_mk TEXT,
    etrn_kns_flg TEXT,
    syri_ztti_rrk_bngu TEXT,
    syri_fomt_sybt TEXT,
    kusn_ntz_bat TEXT
);

-- ===================================
-- 6. その他重要なテーブル
-- ===================================

-- 商標見本（画像データ）
CREATE TABLE IF NOT EXISTS t_sample (
    add_del_id TEXT,
    app_num TEXT PRIMARY KEY,
    trademark_sample_type TEXT,
    size TEXT,
    image_data TEXT  -- Base64エンコードされた画像
);

-- 商標称呼記事
CREATE TABLE IF NOT EXISTS t_dsgnt_art (
    add_del_id TEXT,
    app_num TEXT,
    split_num TEXT,
    dsgnt TEXT,  -- 称呼（読み方）
    PRIMARY KEY (app_num, split_num)
);

-- インデックスの作成
CREATE INDEX IF NOT EXISTS idx_jiken_shutugan_bi ON jiken_c_t(shutugan_bi);
CREATE INDEX IF NOT EXISTS idx_jiken_toroku_no ON jiken_c_t(raz_toroku_no);
CREATE INDEX IF NOT EXISTS idx_standard_char_app_num ON standard_char_t_art(app_num);
CREATE INDEX IF NOT EXISTS idx_indct_use_app_num ON indct_use_t_art(app_num);
CREATE INDEX IF NOT EXISTS idx_search_use_app_num ON search_use_t_art_table(app_num);
CREATE INDEX IF NOT EXISTS idx_shohin_joho_shutugan ON jiken_c_t_shohin_joho(shutugan_no);
CREATE INDEX IF NOT EXISTS idx_shohin_joho_rui ON jiken_c_t_shohin_joho(rui);
CREATE INDEX IF NOT EXISTS idx_appl_name ON appl_reg_info(appl_name);
CREATE INDEX IF NOT EXISTS idx_appl_cd ON appl_reg_info(appl_cd);

-- ビューの作成（検索用統合ビュー）
CREATE VIEW IF NOT EXISTS trademark_search_view AS
SELECT 
    j.shutugan_no AS app_num,
    j.shutugan_bi AS app_date,
    j.raz_toroku_no AS reg_num,
    j.toroku_bi AS reg_date,
    COALESCE(s.standard_char_t, i.indct_use_t, su.search_use_t) AS mark_text,
    GROUP_CONCAT(DISTINCT sh.rui || ':' || sh.shohinekimumeisho) AS goods_services,
    j.saishushobun_shubetu AS final_status
FROM jiken_c_t j
LEFT JOIN standard_char_t_art s ON j.shutugan_no = s.app_num
LEFT JOIN indct_use_t_art i ON j.shutugan_no = i.app_num
LEFT JOIN search_use_t_art_table su ON j.shutugan_no = su.app_num
LEFT JOIN jiken_c_t_shohin_joho sh ON j.shutugan_no = sh.shutugan_no
GROUP BY j.shutugan_no;
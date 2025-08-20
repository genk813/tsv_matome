-- TMCloud Database Schema v2 (Complete from Design Document)
-- Based on tmcloud_schema_v2_design.md

CREATE TABLE trademark_standard_char (
    app_num TEXT NOT NULL,              -- 出願番号（10桁）
    split_num TEXT,                     -- 分割番号（31桁）
    sub_data_num TEXT,                  -- サブデータ番号
    standard_char_t TEXT,               -- 標準文字商標（最大127文字）
    add_del_id TEXT,                    -- 追加削除識別（0:追加、1:削除）
    
    PRIMARY KEY (app_num, split_num, sub_data_num)
);

CREATE TABLE trademark_display (
    app_num TEXT NOT NULL,              -- 出願番号（10桁）
    split_num TEXT,                     -- 分割番号（31桁）
    sub_data_num TEXT,                  -- サブデータ番号（9桁）
    indct_use_t TEXT,                   -- 表示用商標（256桁）
    add_del_id TEXT,                    -- 追加削除識別
    
    PRIMARY KEY (app_num, split_num, sub_data_num)
);

CREATE TABLE trademark_search (
    app_num TEXT NOT NULL,              -- 出願番号（10桁）
    split_num TEXT,                     -- 分割番号（31桁）
    sub_data_num TEXT,                  -- サブデータ番号
    search_seq_num INTEGER NOT NULL,    -- 検索用商標順序
    search_use_t TEXT,                  -- 検索用商標
    add_del_id TEXT,                    -- 追加削除識別
    
    PRIMARY KEY (app_num, split_num, sub_data_num, search_seq_num)
);

CREATE TABLE trademark_pronunciations (
    app_num TEXT,                       -- 出願番号（10桁、正規化済み）※登録ベースのテーブルではNULL可
    split_num TEXT,                     -- 分割番号
    sub_data_num TEXT,                  -- サブデータ番号
    pronunciation_seq_num INTEGER NOT NULL,  -- 称呼順序（1～複数）
    pronunciation TEXT,                 -- 称呼（カタカナ）
    add_del_id TEXT,                    -- 追加削除識別（0:追加、1:削除）
    
    PRIMARY KEY (app_num, split_num, sub_data_num, pronunciation_seq_num)
);

CREATE TABLE trademark_detailed_descriptions (
    law_code TEXT NOT NULL,             -- 四法コード（全行「4」）
    app_num TEXT,                       -- 出願番号（10桁、正規化済み）※登録ベースのテーブルではNULL可
    history_num INTEGER NOT NULL,       -- 履歴番号（1-2）
    creation_date TEXT,                 -- 作成日（YYYYMMDD）
    length_exceed_flag TEXT,            -- レングス超過フラグ（全行「0」）
    detailed_description TEXT,          -- 商標の詳細な説明
    
    PRIMARY KEY (law_code, app_num, history_num)
);

CREATE TABLE trademark_goods_services (
    law_code TEXT NOT NULL,             -- 四法コード（全行「4」）
    app_num TEXT,                       -- 出願番号（10桁、正規化済み）※登録ベースのテーブルではNULL可
    class_num TEXT NOT NULL,            -- 類番号（01-45）
    goods_seq_num TEXT NOT NULL,        -- 商品情報記事順序番号（abz_junjo_no）
    length_exceed_flag TEXT,            -- レングス超過フラグ（0:通常、1:継続行）
    goods_services_name TEXT,           -- 商品・役務名称（最大5500文字）
    
    PRIMARY KEY (law_code, app_num, goods_seq_num)
);

CREATE TABLE trademark_goods_classes (
    law_code TEXT NOT NULL,             -- 四法コード（全行「4」）
    reg_num TEXT NOT NULL,              -- 登録番号（7桁）
    split_num TEXT NOT NULL,            -- 分割番号（31桁）
    app_num TEXT,                       -- 出願番号（10桁、正規化済み）※登録ベースのテーブルではNULL可
    mu_num TEXT NOT NULL,               -- MU番号（区分の連番 000,001,002...）
    goods_class_art_upd_date TEXT,      -- 更新年月日（YYYYMMDD）
    class_num_registered TEXT,          -- 指定商品又は指定役務の区分（01-45）
    processing_type TEXT,               -- 処理種別（全行「0」）
    
    PRIMARY KEY (law_code, reg_num, split_num, app_num, mu_num)
);

CREATE TABLE trademark_similar_group_codes (
    app_num TEXT,                       -- 出願番号（10桁、正規化済み）※登録ベースのテーブルではNULL可
    split_num TEXT,                     -- 分割番号
    sub_data_num TEXT,                  -- サブデータ番号
    class_num TEXT NOT NULL,            -- 類番号（01-45）
    similar_group_codes TEXT,           -- 類似群コード（カンマ区切り、例："30A01,31A03,32F03"）
    add_del_id TEXT,                    -- 追加削除識別（0:追加、1:削除）
    
    PRIMARY KEY (app_num, split_num, sub_data_num, class_num)
);

CREATE TABLE trademark_vienna_codes (
    add_del_id TEXT,                    -- 追加削除識別（0:追加、1:削除）
    app_num TEXT,                       -- 出願番号（10桁、正規化済み）※登録ベースのテーブルではNULL可
    split_num TEXT,                     -- 分割番号
    sub_data_num TEXT,                  -- サブデータ番号
    large_class TEXT NOT NULL,          -- 大分類（01-29）
    mid_class TEXT NOT NULL,            -- 中分類
    small_class TEXT NOT NULL,          -- 小分類
    complement_sub_class TEXT,          -- 補助小分類
    
    PRIMARY KEY (app_num, split_num, sub_data_num, large_class, mid_class, small_class, complement_sub_class)
);

CREATE TABLE trademark_right_goods (
    processing_type TEXT,               -- 処理種別（全行「0」）
    law_code TEXT NOT NULL,             -- 四法コード（全行「4」）
    reg_num TEXT NOT NULL,              -- 登録番号（7桁）
    split_num TEXT NOT NULL,            -- 分割番号（31桁）
    app_num TEXT,                       -- 出願番号（10桁、正規化済み）※登録ベースのテーブルではNULL可
    class_num_registered TEXT NOT NULL, -- 商品・役務区分（01-45）
    rec_num TEXT NOT NULL,              -- レコード番号（00固定）
    master_update_date TEXT,            -- マスタ更新日（YYYYMMDD）
    goods_name_length TEXT,             -- 商品・役務名レングス
    goods_name TEXT,                    -- 商品・役務名（最大12000文字）
    
    PRIMARY KEY (law_code, reg_num, split_num, app_num, class_num_registered, rec_num)
);

CREATE TABLE trademark_right_holders (
    processing_type TEXT,               -- 処理種別（削除・修正等のコード）
    law_code TEXT NOT NULL,             -- 四法コード（全行「4」）
    reg_num TEXT NOT NULL,              -- 登録番号（7桁）
    split_num TEXT NOT NULL,            -- 分割番号（31桁、通常は0埋め）
    app_num TEXT,                       -- 出願番号（10桁、正規化済み）※登録ベースのテーブルではNULL可
    rec_num TEXT NOT NULL,              -- レコード番号（主キー、「00」固定）
    pe_num TEXT NOT NULL,               -- ＰＥ番号（主キー、「000」固定）
    right_person_update_date TEXT,      -- 権利者記事部作成更新年月日（YYYYMMDD）
    right_person_id TEXT,               -- 権利者申請人ＩＤ（9桁）
    right_person_addr_len TEXT,         -- 権利者住所レングス
    right_person_addr TEXT,             -- 権利者住所（最大1000文字）
    right_person_name_len TEXT,         -- 権利者氏名レングス
    right_person_name TEXT,             -- 権利者氏名（最大1000文字）
    
    PRIMARY KEY (law_code, reg_num, split_num, app_num, rec_num, pe_num)
);

CREATE TABLE trademark_applicants_agents (
    law_code TEXT NOT NULL,             -- 四法コード（全行「4」）
    app_num TEXT,                       -- 出願番号（10桁、正規化済み）※登録ベースのテーブルではNULL可
    applicant_agent_type TEXT NOT NULL, -- 出願人代理人識別（1=出願人、2=代理人）
    applicant_agent_code TEXT,          -- 出願人代理人コード（9桁）
    change_num TEXT,                    -- 出願人代理人記事変更番号
    individual_corp_type TEXT,          -- 出願人代理人記事個法官区分
    country_prefecture_code TEXT,       -- 出願人代理人記事国県コード
    representative_flag TEXT,           -- 代表出願人識別（0=通常、1=代表）
    num_above_applicants TEXT,          -- 上記出願人何名
    num_other_agents TEXT,              -- 代理人外何名
    applicant_agent_profession_type TEXT, -- 代理人種別（1=弁理士等）
    applicant_agent_qualification_type TEXT, -- 代理人資格種別
    applicant_agent_address TEXT,       -- 出願人代理人住所（※現在は「（省略）」）
    applicant_agent_name TEXT,          -- 出願人代理人氏名（※現在は空欄）
    applicant_agent_seq_num TEXT NOT NULL, -- 記事順序番号
    
    PRIMARY KEY (law_code, app_num, applicant_agent_seq_num)
);

CREATE TABLE trademark_attorney_articles (
    processing_type TEXT,               -- 処理種別（全行「0」）
    law_code TEXT NOT NULL,             -- 四法コード（全行「4」）
    reg_num TEXT NOT NULL,              -- 登録番号（7桁）
    split_num TEXT NOT NULL,            -- 分割番号（31桁）
    app_num TEXT,                       -- 出願番号（10桁、正規化済み）※登録ベースのテーブルではNULL可
    rec_num TEXT NOT NULL,              -- レコード番号（主キー、「00」固定）
    attorney_seq_num TEXT NOT NULL,     -- PE番号（000から連番、筆頭代理人が000）
    attorney_update_date TEXT,          -- 代理人記事更新日（YYYYMMDD）
    attorney_appl_id TEXT,              -- 代理人申請人ID（9桁）
    attorney_type TEXT,                 -- 代理人種別（全行「1」）
    attorney_name_length TEXT,          -- 代理人氏名レングス
    attorney_name TEXT,                 -- 代理人氏名（弁理士名・事務所名）
    
    PRIMARY KEY (law_code, reg_num, split_num, app_num, rec_num, attorney_seq_num)
);

CREATE TABLE trademark_case_info (
    master_update_datetime TEXT,         -- マスタ更新日時（YYYYMMDDHHmmss）
    law_code TEXT NOT NULL,             -- 四法コード（全行「4」）
    app_num TEXT NOT NULL,              -- 出願番号（10桁、正規化済み）
    app_date TEXT,                      -- 出願日（YYYYMMDD）
    app_type1 TEXT,                     -- 出願種別1（01=通常出願が99.5%）
    app_type2 TEXT,                     -- 出願種別2
    app_type3 TEXT,                     -- 出願種別3
    app_type4 TEXT,                     -- 出願種別4
    app_type5 TEXT,                     -- 出願種別5
    reference_num TEXT,                 -- 整理番号
    final_disposition_type TEXT,        -- 最終処分種別（A01=登録査定等）
    final_disposition_date TEXT,        -- 最終処分日（YYYYMMDD）
    reg_article_reg_num TEXT,           -- 登録記事登録番号（7桁）
    reg_article_split_num TEXT,         -- 登録記事分割番号（31桁）
    defensive_num TEXT,                 -- 防護番号（3桁）
    reg_date TEXT,                      -- 登録日（YYYYMMDD）
    reg_article_total_num TEXT,         -- 登録記事総通号数（6桁）
    reg_article_annual_num TEXT,        -- 登録記事年間通号数（6桁）
    reg_article_gazette_date TEXT,      -- 登録記事公報発行日（YYYYMMDD）
    examiner_code TEXT,                 -- 担当官コード（4桁）
    pub_article_gazette_date TEXT,      -- 公開公報記事公開公報発行日（YYYYMMDD）
    class_count TEXT,                   -- 区分数（3桁）
    reg_decision_class_count TEXT,      -- 登録査定時区分数（3桁）
    standard_char_exist TEXT,           -- 標準文字有無（1=標準文字商標）
    special_mark_exist TEXT,            -- 特殊商標識別（1=立体商標等）
    color_exist TEXT,                   -- 標章色彩有無（1=色彩付き）
    article3_2_flag TEXT,               -- 商標法3条2項フラグ（使用による識別力）
    article5_4_flag TEXT,               -- 色彩の但し書フラグ（商標法5条4項）
    orig_app_type TEXT,                 -- 原出願種別（分割・変更の元出願）
    orig_app_law_code TEXT,             -- 原出願四法コード（1桁）
    orig_app_num TEXT,                  -- 原出願番号（10桁）
    retroactive_date TEXT,              -- 遡及日（YYYYMMDD）
    defensive_orig_app_num TEXT,        -- 防護原登録記事出願番号
    defensive_orig_reg_num TEXT,        -- 防護原登録記事登録番号
    defensive_orig_split_num TEXT,      -- 防護原登録記事分割番号（31桁）
    renewal_reg_num TEXT,               -- 更新登録番号（7桁）
    renewal_split_num TEXT,             -- 更新登録記事分割番号（31桁）
    renewal_defensive_num TEXT,         -- 更新登録記事防護番号（3桁）
    rewrite_reg_num TEXT,               -- 書換登録番号（7桁）
    rewrite_split_num TEXT,             -- 書換登録記事分割番号（31桁）
    rewrite_defensive_num TEXT,         -- 書換登録記事防護番号（3桁）
    public_order_violation_flag TEXT,   -- 公序良俗違反フラグ（1=違反あり）
    accelerated_exam_mark TEXT,         -- 早期審査マーク（1=早期審査対象）
    applicable_law_class TEXT,          -- 適用法規区分（1桁）
    exam_type TEXT,                     -- 審査種別（2桁）
    litigation_code TEXT,               -- 訴訟コード（1桁）
    decision_type TEXT,                 -- 査定種別（1桁）
    opposition_count TEXT,              -- 異議件数（2桁）
    opposition_valid_count TEXT,        -- 異議有効数（2桁）
    
    PRIMARY KEY (law_code, app_num)
);

CREATE TABLE trademark_basic_items (
    add_del_id TEXT,                    -- 追加削除識別（0=追加、1=削除）
    mgt_num TEXT NOT NULL,              -- 管理番号（7桁、主キー）
    rec_status_id TEXT,                 -- レコード状態識別（1または2）
    app_num TEXT,                       -- 出願番号（10桁、正規化済み）
    reg_num TEXT,                       -- 登録番号（7桁、未登録は0000000）
    split_num TEXT,                     -- 分割番号（ほぼ空欄）
    defensive_num TEXT,                 -- 防護番号（000固定）
    app_typ_sec TEXT,                   -- 出願種別防護（0固定）
    app_typ_split TEXT,                 -- 出願種別分割（0固定）
    app_typ_complement_rjct TEXT,       -- 出願種別補却（0固定）
    app_typ_chan TEXT,                  -- 出願種別変更（0固定）
    app_typ_priorty TEXT,               -- 出願種別優先（0固定）
    app_typ_group TEXT,                 -- 出願種別団体（0固定）
    app_typ_area_group TEXT,            -- 出願種別地域団体（0固定）
    app_date TEXT,                      -- 出願日（YYYYMMDD）
    prior_app_right_occr_date TEXT,     -- 先願権発生日（YYYYMMDD）
    rjct_finl_dcsn_dsptch_date TEXT,    -- 拒絶査定発送日（YYYYMMDD）
    final_disposition_code TEXT,        -- 最終処分コード
    final_disposition_date TEXT,        -- 最終処分日（YYYYMMDD）
    rewrite_app_num TEXT,               -- 書換申請番号（0000000000固定）
    old_law TEXT,                       -- 旧法類
    ver_num TEXT,                       -- 版コード（C1固定）
    intl_reg_num TEXT,                  -- 国際登録番号（0000000固定）
    intl_reg_split_num TEXT,            -- 国際登録分割番号
    intl_reg_date TEXT,                 -- 国際登録日（YYYYMMDD）
    rec_latest_updt_date TEXT,          -- レコード最新更新日（YYYYMMDD）
    conti_prd_expire_date TEXT,         -- 存続期間満了日（YYYYMMDD）
    instllmnt_expr_date_aft_des_date TEXT,  -- 分納満了日／事後指定日（YYYYMMDD）
    installments_id TEXT,               -- 分納識別（0固定）
    set_reg_date TEXT,                  -- 設定登録日（YYYYMMDD）
    
    PRIMARY KEY (mgt_num)
);

CREATE TABLE trademark_first_display (
    processing_type TEXT,               -- 処理種別（全行「0」）
    law_code TEXT NOT NULL,             -- 四法コード（全行「4」）
    reg_num TEXT NOT NULL,              -- 登録番号（7桁）
    split_num TEXT NOT NULL,            -- 分割番号（31桁）
    history_num TEXT NOT NULL,          -- 履歴番号（「0」固定）
    master_update_date TEXT,            -- マスタ更新年月日（YYYYMMDD）
    cancel_disposal_flag TEXT,          -- 取消及び廃棄識別
    intl_reg_num TEXT,                  -- 国際登録番号
    intl_reg_date TEXT,                 -- 国際登録年月日（YYYYMMDD）
    after_designation_date TEXT,        -- 事後指定年月日（YYYYMMDD）
    
    PRIMARY KEY (law_code, reg_num, split_num, history_num)
);

CREATE TABLE trademark_management_info (
    processing_type TEXT,               -- 処理種別（全行「0」）
    law_code TEXT NOT NULL,             -- 四法コード（全行「4」）
    reg_num TEXT NOT NULL,              -- 登録番号（7桁）
    split_num TEXT NOT NULL,            -- 分割番号（31桁）
    master_update_date TEXT,            -- マスタ更新日（YYYYMMDD）
    tscript_inspct_prhbt_flg TEXT,      -- 謄本閲覧禁止の有無
    conti_prd_expire_date TEXT,         -- 存続期間満了日（YYYYMMDD）
    next_pen_payment_limit_date TEXT,  -- 次期年金納付期限日（YYYYMMDD）
    last_pymnt_yearly TEXT,             -- 最終納付年分
    share_rate TEXT,                    -- 持分の割合
    pblc_prvt_trnsfr_reg_date TEXT,     -- 官民移転登録日（YYYYMMDD）
    right_ersr_id TEXT,                 -- 本権利抹消識別
    right_disppr_date TEXT,             -- 本権利消滅日（YYYYMMDD）
    close_orgnl_reg_trnsfr_rec_flg TEXT, -- 閉鎖原簿移記の有無
    close_reg_date TEXT,                -- 閉鎖登録日（YYYYMMDD）
    gvrnmnt_relation_id_flg TEXT,       -- 官庁関係識別の有無
    pen_suppl_flg TEXT,                 -- 年金補充の有無
    apply_law TEXT,                     -- 適用法規
    group_t_flg TEXT,                   -- 団体商標の有無
    special_mark_exist TEXT,            -- 特殊商標識別
    standard_char_exist TEXT,           -- 標準文字商標の有無
    area_group_t_flg TEXT,              -- 地域団体商標の有無
    trust_reg_flg TEXT,                 -- 信託登録の有無
    app_num TEXT,                       -- 出願番号（10桁、正規化済み）※登録ベースのテーブルではNULL可
    recvry_num TEXT,                    -- 回復番号
    app_date TEXT,                      -- 出願日（YYYYMMDD）
    app_exam_pub_num TEXT,              -- 出願公告番号
    app_exam_pub_date TEXT,             -- 出願公告日（YYYYMMDD）
    final_decision_date TEXT,           -- 査定日（YYYYMMDD）
    trial_decision_date TEXT,           -- 審決日（YYYYMMDD）
    set_reg_date TEXT,                  -- 設定登録日（YYYYMMDD）
    t_rewrite_app_num TEXT,             -- 商標書換申請番号
    t_rewrite_app_date TEXT,            -- 商標書換申請日（YYYYMMDD）
    t_rewrite_final_decision_date TEXT, -- 商標書換査定日（YYYYMMDD）
    t_rewrite_trial_decision_date TEXT, -- 商標書換審決日（YYYYMMDD）
    t_rewrite_reg_date TEXT,            -- 商標書換登録日（YYYYMMDD）
    invent_title_etc_len TEXT,          -- 発明の名称（等）レングス
    pri_cntry_name_cd TEXT,             -- 優先権国名コード
    pri_claim_date TEXT,                -- 優先権主張日（YYYYMMDD）
    pri_clim_cnt TEXT,                  -- 優先権主張件数
    
    PRIMARY KEY (law_code, reg_num, split_num, app_num)
);

CREATE TABLE trademark_updates (
    processing_type TEXT,               -- 処理種別（全行「0」）
    law_code TEXT NOT NULL,             -- 四法コード（全行「4」）
    reg_num TEXT NOT NULL,              -- 登録番号（7桁）
    split_num TEXT NOT NULL,            -- 分割番号（31桁）
    app_num TEXT,                       -- 出願番号（10桁）※NULL可
    pe_num TEXT NOT NULL,               -- PE番号（3桁、000-007等）
    t_updt_art_update_date TEXT,        -- 商標更新記事部作成更新日（YYYYMMDD）
    t_updt_app_num TEXT,                -- 商標更新出願番号
    t_updt_temp_reg_flg TEXT,           -- 商標更新仮登録の有無
    t_updt_title_chan_flg TEXT,         -- 商標更新名称変更の有無
    t_updt_recovery_num TEXT,           -- 商標更新回復番号
    t_updt_app_date TEXT,               -- 商標更新出願日/申請日（YYYYMMDD）
    t_updt_final_decision_date TEXT,    -- 商標更新査定日（YYYYMMDD）
    t_updt_trial_decision_date TEXT,    -- 商標更新審決日（YYYYMMDD）
    t_updt_reg_date TEXT,               -- 商標更新登録日（YYYYMMDD）
    mu_num TEXT NOT NULL,               -- MU番号（000固定）
    
    PRIMARY KEY (law_code, reg_num, split_num, app_num, pe_num, mu_num)
);

CREATE TABLE trademark_progress_info (
    processing_type TEXT,               -- 処理種別（全行「0」）
    law_code TEXT NOT NULL,             -- 四法コード（全行「4」）
    reg_num TEXT NOT NULL,              -- 登録番号（7桁）
    split_num TEXT NOT NULL,            -- 分割番号（31桁）
    app_num TEXT,                       -- 出願番号（10桁、正規化済み）※登録ベースのテーブルではNULL可
    rec_num TEXT NOT NULL,              -- レコード番号
    pe_num TEXT NOT NULL,               -- PE番号（3桁連番）
    progress_update_date TEXT,          -- 経過情報部更新日（YYYYMMDD）
    reg_intermediate_code TEXT,         -- 登録中間コード（R350等）
    correspondence_mark TEXT,           -- 対応マーク
    process_date TEXT,                  -- 受付/納付/発送日（YYYYMMDD）
    progress_app_num TEXT,              -- 経過情報部出願番号
    receipt_num TEXT,                   -- 受付番号（共用）
    
    PRIMARY KEY (law_code, reg_num, split_num, app_num, rec_num, pe_num)
);

CREATE TABLE trademark_rewrite_applications (
    processing_type TEXT,               -- 処理種別（全行「0」）
    law_code TEXT NOT NULL,             -- 四法コード（全行「4」）
    reg_num TEXT NOT NULL,              -- 登録番号（7桁）
    split_num TEXT NOT NULL,            -- 分割番号（31桁）
    app_num TEXT NOT NULL,              -- 出願番号（10桁）
    mrgn_info_update_date TEXT,         -- 欄外情報部更新日（YYYYMMDD）
    mu_num TEXT NOT NULL,               -- MU番号（全行「000」）
    rewrite_app_num TEXT,               -- 欄外商標書換申請番号（全行「0000000000」）
    
    PRIMARY KEY (law_code, reg_num, split_num, app_num, mu_num)
);

CREATE TABLE trademark_transfer_receipts (
    processing_type TEXT,               -- 処理種別（全行「0」）
    law_code TEXT NOT NULL,             -- 四法コード（全行「4」）
    reg_num TEXT NOT NULL,              -- 登録番号（7桁）
    split_num TEXT NOT NULL,            -- 分割番号（31桁）
    app_num TEXT NOT NULL,              -- 出願番号（10桁）
    mrgn_info_update_date TEXT,         -- 欄外情報部更新日（YYYYMMDD）
    mu_num TEXT NOT NULL,               -- MU番号（全行「000」）
    transfer_receipt_info TEXT,         -- 移転受付情報（受付番号＋日付＋移転名称）
    
    PRIMARY KEY (law_code, reg_num, split_num, app_num, mu_num)
);

CREATE TABLE trademark_appeal_cases (
    delete_flag TEXT,                   -- 削除フラグ（0=有効、1=削除）
    appeal_num TEXT NOT NULL,           -- 審判番号（10桁）
    app_num TEXT,                       -- 出願番号（10桁）
    law_division TEXT,                  -- 四法区分（1=特許、4=商標）
    reg_num TEXT,                       -- 登録番号（7桁、多くは空欄）
    split_num TEXT,                     -- 分割番号（ほぼ空欄）
    similar_num TEXT,                   -- 類似番号（ほぼ空欄）
    defensive_num TEXT,                 -- 防護番号（ほぼ空欄）
    appeal_level_type TEXT,             -- 審級種別（全行「1」）
    appeal_type TEXT,                   -- 審判種別（3桁コード）
    appeal_request_date TEXT,           -- 審判請求日（YYYYMMDD）
    app_num_division TEXT,              -- 出願番号区分（1,2）
    appeal_final_disposition_code TEXT, -- 審判事件最終処分コード（2桁）
    final_disposition_confirm_date TEXT, -- 最終処分確定日（YYYYMMDD、多くは空欄）
    update_datetime TEXT,               -- 更新日時（YYYYMMDDHHMMSS）
    
    PRIMARY KEY (appeal_num)
);

CREATE TABLE trademark_decision_classifications (
    delete_flag TEXT,                   -- 削除フラグ（0=有効、1=削除）
    appeal_num TEXT NOT NULL,           -- 審判番号（10桁）
    decision_num TEXT NOT NULL,         -- 審決番号（2桁、ほぼ「01」）
    repeat_num TEXT NOT NULL,           -- 繰返番号（連番）
    law_division TEXT,                  -- 四法区分（全行「1」=特許）
    applied_law_identification TEXT,    -- 適用法規識別（ほぼ空欄）
    appeal_level_type TEXT,             -- 審級種別（全行「1」）
    appeal_type TEXT,                   -- 審判種別（3桁コード）
    judgment_item_code TEXT,            -- 判示事項コード（3桁）
    decision_classification_conclusion_code TEXT, -- 審決分類結論コード
    auxiliary_classification_identification TEXT, -- 補助分類識別
    update_datetime TEXT,               -- 更新日時（YYYYMMDDHHMMSS）
    
    PRIMARY KEY (appeal_num, decision_num, repeat_num)
);

CREATE TABLE trademark_oppositions (
    delete_flag TEXT,                   -- 削除フラグ（0=有効、1=削除）
    appeal_num TEXT NOT NULL,           -- 審判番号（10桁）
    opposition_num TEXT NOT NULL,       -- 申立番号（3桁、001-004等の連番）
    opposition_app_date TEXT,           -- 異議申立日（YYYYMMDD）
    opposition_final_disposition_code TEXT, -- 異議申立最終処分コード（2桁、06,07,08等）
    final_disposition_confirm_date TEXT, -- 最終処分確定日（YYYYMMDD、多くは空欄）
    update_datetime TEXT,               -- 更新日時（YYYYMMDDHHMMSS）
    
    PRIMARY KEY (appeal_num, opposition_num)
);

CREATE TABLE trademark_opposition_decisions (
    delete_flag TEXT NOT NULL,          -- 削除フラグ（0=有効、1=削除）
    appeal_num TEXT NOT NULL,           -- 審判番号（snpn_bngu、10桁）
    opposition_num TEXT NOT NULL,       -- 申立番号（mustt_bngu、3桁、001〜003等）
    decision_num TEXT NOT NULL,         -- 異議決定番号（ig_ktti_bngu、2桁、全て「01」）
    dispatch_doc_num TEXT,              -- 発送書類番号（hssu_syri_bngu、11桁）
    decision_confirmation_status TEXT,  -- 異議決定確定ステータス（ig_ktti_kkti_stat、2桁、「01」または空白）
    update_datetime TEXT,               -- 更新日時（kusn_ntz_bat、YYYYMMDDHHMMSS）
    
    PRIMARY KEY (appeal_num, opposition_num, decision_num)
);
CREATE INDEX idx_trademark_opposition_decisions_appeal ON trademark_opposition_decisions(appeal_num);
CREATE INDEX idx_trademark_opposition_decisions_status ON trademark_opposition_decisions(decision_confirmation_status);

CREATE TABLE trademark_draft_records (
    -- 主キーカラム
    law_code TEXT NOT NULL,                          -- 四法コード（yonpo_code → law_code）
    app_num TEXT NOT NULL,                           -- 出願番号（shutugan_no → app_num）
    folder_creation_seq_num INTEGER NOT NULL,        -- フォルダ別作成順序番号（folderbetusakusejnj_no）
    
    -- 日付カラム
    creation_date TEXT,                              -- 作成日（sakusei_bi）
    draft_date TEXT,                                 -- 起案日（kian_bi）
    dispatch_date TEXT,                              -- 発送日（hasso_bi）
    
    -- 書類関連カラム
    intermediate_doc_code TEXT,                      -- 中間書類コード（chukanshorui_code）
    response_mark TEXT,                              -- 対応マーク（taio_mark）
    document_num TEXT,                               -- 書類番号（shorui_no）
    corresponding_doc_num TEXT,                      -- 対応書類番号（taioshorui_no）
    document_type TEXT,                              -- 書類種別（shorui_shubetu）
    
    -- その他カラム
    objection_num TEXT,                              -- 異議番号（aaz_igi_no）
    rejection_reason_code TEXT,                      -- 拒絶理由条文コード（kyozeturiyujobun_code）
    version_num TEXT,                                -- バージョン番号（version_no）
    
    PRIMARY KEY (law_code, app_num, folder_creation_seq_num)
);

CREATE TABLE trademark_application_records (
    law_code TEXT NOT NULL,                          -- 四法コード（全行「4」）
    app_num TEXT NOT NULL,                           -- 出願番号（10桁、正規化済み）
    folder_creation_seq_num INTEGER NOT NULL,        -- フォルダ別作成順序番号（4桁連番）
    creation_date TEXT,                              -- 作成日（YYYYMMDD）
    intermediate_doc_code TEXT,                      -- 中間書類コード（例：A63）
    correspondence_mark TEXT,                        -- 対応マーク
    dispatch_date TEXT,                              -- 差出日（YYYYMMDD）
    receipt_date TEXT,                               -- 受付日（YYYYMMDD）
    opposition_num TEXT,                             -- 異議番号
    doc_num TEXT,                                    -- 書類番号（11桁）
    procedure_complete_mark TEXT,                    -- 方式完マーク（0/1）
    order_complete_flag TEXT,                        -- 指令完フラグ
    corresponding_doc_num TEXT,                      -- 対応書類番号
    doc_type TEXT,                                   -- 書類種別（1,8等）
    version_num TEXT,                                -- バージョン番号（0001,0002等）
    viewing_restriction_flag TEXT,                   -- 閲覧禁止フラグ（全行「0」）
    
    PRIMARY KEY (law_code, app_num, folder_creation_seq_num)
);

CREATE TABLE trademark_priority_claims (
    law_code TEXT NOT NULL,                    -- 四法コード（全行「4」）
    app_num TEXT NOT NULL,                     -- 出願番号（10桁、正規化済み）
    priority_seq_num INTEGER NOT NULL,         -- 優先権記事順序番号（現在は全行1）
    priority_app_num TEXT,                     -- 優先権出願番号（最大20桁）
    priority_date TEXT,                        -- 優先権主張日（YYYYMMDD）
    priority_country_code TEXT,                -- 優先権国コード（例：JM、NZ）
    
    PRIMARY KEY (law_code, app_num, priority_seq_num)
);

CREATE TABLE trademark_gazette_publications (
    law_code TEXT NOT NULL,                          -- 四法コード（全行「4」）
    app_num TEXT NOT NULL,                           -- 出願番号（10桁、正規化済み）
    gazette_seq_num INTEGER NOT NULL,                -- 公報発行情報記事順序番号（全行「1」）
    total_serial_num TEXT,                           -- 公報発行情報記事総通号数（6桁）
    annual_serial_num TEXT,                          -- 公報発行情報記事年間通号数（6桁）
    dept_serial_num TEXT,                            -- 部門別通号数
    dept_annual_serial_num TEXT,                     -- 部門別年間通号数
    gazette_publication_date TEXT,                   -- 公報発行情報記事公報発行日（YYYYMMDD）
    correction_type TEXT,                            -- 正誤識別（全行「00」）
    gazette_type TEXT,                               -- 公報発行情報記事公報識別（例：4A010）
    
    PRIMARY KEY (law_code, app_num, gazette_seq_num)
);

CREATE TABLE applicant_registration_info (
    data_id_code TEXT,                               -- データ識別コード（全行「520010」）
    applicant_code TEXT NOT NULL,                    -- 申請人コード（9桁）
    applicant_name TEXT,                             -- 申請人氏名（日本語/英語/中国語等）
    applicant_kana_name TEXT,                        -- 申請人カナ氏名（日本の申請人のみ）
    applicant_postal_code TEXT,                      -- 申請人郵便番号（日本の住所のみ）
    applicant_address TEXT,                          -- 申請人住所（国内外の住所）
    roman_name TEXT,                                 -- ローマ字氏名
    roman_address TEXT,                              -- ローマ字住所（多くは「（省略）」）
    integrated_applicant_code TEXT,                  -- 統合申請人コード
    double_reg_integration_num INTEGER,              -- 二重登録統合管理通番（ほぼ0）
    
    PRIMARY KEY (applicant_code)
);

CREATE TABLE intl_trademark_registration (
    add_del_id TEXT,                                 -- 追加削除識別（ほぼ全行「0」）
    intl_reg_num TEXT NOT NULL,                      -- 国際登録番号（連番部分）
    intl_reg_num_update_count_code TEXT,   -- 国際登録番号更新回数記号コード
    intl_reg_num_split_code TEXT,           -- 国際登録番号分割記号コード（A,B,C,D等）
    after_designation_date TEXT,            -- 事後指定年月日（YYYYMMDD）
    intl_reg_date TEXT,                              -- 国際登録年月日（YYYYMMDD）
    jpo_reference_num TEXT,                          -- 庁内整理番号（西暦年＋連番）
    jpo_reference_num_split_code TEXT,               -- 庁内整理番号分割記号コード
    set_registration_date TEXT,                      -- 設定登録年月日（YYYYMMDD）
    right_erasure_id TEXT,                           -- 本権利抹消識別
    right_disappearance_date TEXT,                   -- 本権利消滅年月日（YYYYMMDD）
    close_registration_date TEXT,                    -- 閉鎖登録年月日（YYYYMMDD）
    inspection_prohibition_flag TEXT,                -- 閲覧禁止フラグ
    define_flag TEXT,                       -- 確定フラグ
    update_date TEXT,                                -- 更新年月日（システム操作者）
    batch_update_date TEXT,                          -- バッチ更新年月日
    
    PRIMARY KEY (intl_reg_num, intl_reg_num_update_count_code, intl_reg_num_split_code, after_designation_date, define_flag)
);

CREATE TABLE intl_trademark_progress (
    add_del_id TEXT,                                 -- 追加削除識別（ほぼ全行「0」）
    intl_reg_num TEXT NOT NULL,                      -- 国際登録番号（連番部分）
    intl_reg_num_update_count_code TEXT,   -- 国際登録番号更新回数記号コード
    intl_reg_num_split_code TEXT,           -- 国際登録番号分割記号コード
    after_designation_date TEXT,            -- 事後指定年月日（YYYYMMDD）
    intermediate_code TEXT NOT NULL,                 -- 中間コード（例：IB31400、R150）
    storage_num TEXT NOT NULL,                       -- 格納番号（000001〜の連番）
    intermediate_def_date_1 TEXT,                    -- 中間定義１日付（YYYYMMDD）
    intermediate_def_date_2 TEXT,                    -- 中間定義２日付（YYYYMMDD）
    intermediate_def_date_3 TEXT,                    -- 中間定義３日付（YYYYMMDD）
    intermediate_def_date_4 TEXT,                    -- 中間定義４日付（YYYYMMDD）
    intermediate_def_date_5 TEXT,                    -- 中間定義５日付（YYYYMMDD）
    correspondence_mark TEXT,                        -- 対応マーク
    define_flag TEXT,                       -- 確定フラグ
    status TEXT NOT NULL,                            -- ステータス（4桁）
    update_date TEXT,                                -- 更新年月日（システム操作者）
    batch_update_date TEXT,                          -- バッチ更新年月日
    
    PRIMARY KEY (intl_reg_num, intl_reg_num_update_count_code, intl_reg_num_split_code, after_designation_date, intermediate_code, storage_num, define_flag, status)
);

CREATE TABLE intl_trademark_holders (
    add_del_id TEXT,                                 -- 追加削除識別（ほぼ全行「0」）
    intl_reg_num TEXT NOT NULL,                      -- 国際登録番号（連番部分）
    intl_reg_num_update_count_code TEXT,   -- 国際登録番号更新回数記号コード
    intl_reg_num_split_code TEXT,           -- 国際登録番号分割記号コード
    after_designation_date TEXT,            -- 事後指定年月日（YYYYMMDD）
    temp_principal_reg_id_flag TEXT NOT NULL,        -- 仮・本登録識別フラグ
    display_seq INTEGER NOT NULL,                    -- 表示順序（4桁）
    holder_input_seq_num INTEGER NOT NULL,           -- 名義人入力順序番号（4桁）
    holder_name TEXT,                                -- 名義人名称（最大1024桁）
    holder_address TEXT,                             -- 名義人住所（最大432桁）
    define_flag TEXT,                       -- 確定フラグ
    update_date TEXT,                                -- 更新年月日（システム操作者）
    batch_update_date TEXT,                          -- バッチ更新年月日
    
    PRIMARY KEY (intl_reg_num, intl_reg_num_update_count_code, intl_reg_num_split_code, after_designation_date, temp_principal_reg_id_flag, display_seq, holder_input_seq_num, define_flag)
);

CREATE TABLE intl_trademark_goods_services (
    add_del_id TEXT,                                 -- 追加削除識別（全行「0」）
    intl_reg_num TEXT NOT NULL,                      -- 国際登録番号（連番部分）
    intl_reg_num_update_count_code TEXT,   -- 国際登録番号更新回数記号コード
    intl_reg_num_split_code TEXT,           -- 国際登録番号分割記号コード
    after_designation_date TEXT,            -- 事後指定年月日（YYYYMMDD）
    temp_principal_reg_id_flag TEXT NOT NULL,        -- 仮・本登録識別フラグ（全行「1」）
    display_seq INTEGER NOT NULL,                    -- 表示順序（4桁、ほぼ全て0001）
    seq_num INTEGER NOT NULL,                        -- 順序番号（グループ内の商品・役務順）
    madpro_class TEXT,                               -- 区分（01〜45）
    goods_service_name TEXT,                         -- 商品サービス名（英語、最大8000桁）
    intl_reg_record_date TEXT,                       -- 国際登録記録日（YYYYMMDD）
    define_flag TEXT,                                -- 確定フラグ（全行「1」）
    update_date TEXT,                                -- 更新年月日
    batch_update_date TEXT,                          -- バッチ更新年月日
    
    PRIMARY KEY (intl_reg_num, intl_reg_num_update_count_code, intl_reg_num_split_code, after_designation_date, temp_principal_reg_id_flag, display_seq, seq_num, define_flag)
);

CREATE TABLE intl_trademark_first_indication (
    add_del_id TEXT,                                 -- 追加削除識別（全行「0」）
    intl_reg_num TEXT NOT NULL,                      -- 国際登録番号（連番部分）
    intl_reg_num_update_count_code TEXT,   -- 国際登録番号更新回数記号コード
    intl_reg_num_split_code TEXT,           -- 国際登録番号分割記号コード
    after_designation_date TEXT,            -- 事後指定年月日（YYYYMMDD）
    temp_principal_reg_id_flag TEXT NOT NULL,        -- 仮・本登録識別フラグ（全行「1」）
    display_seq INTEGER NOT NULL,                    -- 表示順序（全行「0001」）
    final_decision_date TEXT,                        -- 査定年月日（YYYYMMDD）
    trial_decision_date TEXT,                        -- 審決年月日（YYYYMMDD）
    priority_app_country_code TEXT,                  -- 優先権出願官庁締約国等コード（CH、EM、US等）
    priority_app_date TEXT,                          -- 優先権出願年月日（YYYYMMDD）
    priority_claim_count TEXT,                       -- 優先権主張件数（000〜006）
    special_trademark_type_flag TEXT,                -- 特殊商標のタイプフラグ
    group_cert_warranty_flag TEXT,                   -- 団体証明保証フラグ
    define_flag TEXT,                                -- 確定フラグ（全行「1」）
    update_date TEXT,                                -- 更新年月日
    batch_update_date TEXT,                          -- バッチ更新年月日
    trademark_detailed_explanation TEXT,             -- 商標の詳細な説明（最大4000桁、全て空欄）
    
    PRIMARY KEY (intl_reg_num, intl_reg_num_split_code, after_designation_date, display_seq)
);

CREATE TABLE trademark_images (
    country_code TEXT,                               -- 国コード（"JP"固定）
    doc_type TEXT,                                   -- 文献種別（"T1"固定）
    doc_num TEXT NOT NULL,                           -- 文献番号（8桁）
    app_num TEXT,                                    -- 出願番号（10桁）
    page_num TEXT NOT NULL,                          -- 頁番号（"0001"から）
    rec_seq_num INTEGER NOT NULL,                    -- レコード順序番号
    year_issue_code TEXT NOT NULL,                   -- 年号コード（"3":昭和,"4":平成等）
    data_creation_date TEXT,                         -- データ作成日（YYYYMMDD）
    all_page_count TEXT,                             -- 全頁数（"0001"～"9999"）
    final_rec_seq_num INTEGER,                       -- 最終レコード順序番号
    fullsize_length TEXT,                            -- 原寸の大きさ_縦（mm単位）
    fullsize_width TEXT,                             -- 原寸の大きさ_横（mm単位）
    compression_format TEXT,                         -- 圧縮方式（"JP":JPEG,"M2":MMR）
    resolution TEXT,                                 -- 解像度（"00":JPEG,"16":MMR）
    line_count_length TEXT,                          -- ライン数_縦（ピクセル数）
    line_count_width TEXT,                           -- ライン数_横（ピクセル数）
    image_data_length TEXT,                          -- イメージデータ長（00001～19740）
    image_data TEXT,                                 -- イメージデータ（Base64エンコード）
    
    PRIMARY KEY (doc_num, page_num, rec_seq_num, year_issue_code)
);

CREATE TABLE bougo_hyosho_articles (
    processing_type TEXT,                          -- 処理種別（削除・修正等を示すコード）
    law_code TEXT NOT NULL,                        -- 四法コード（law_cd → law_code）
    reg_num TEXT NOT NULL,                         -- 登録番号（7桁）
    split_num TEXT NOT NULL,                       -- 分割番号（31桁）
    app_num TEXT NOT NULL,                         -- 出願番号（10桁）
    pe_num TEXT NOT NULL,                          -- ＰＥ番号（3桁）
    defensive_art_upd_date TEXT,                   -- 防護記事部作成更新年月日（sec_art_upd_ymd → defensive_art_upd_date）
    defensive_app_num TEXT,                        -- 防護出願番号（sec_app_num → defensive_app_num）
    defensive_num TEXT,                            -- 防護番号（sec_num → defensive_num）
    defensive_temp_reg_flg TEXT,                   -- 防護仮登録の有無（sec_temp_reg_flg → defensive_temp_reg_flg）
    defensive_conti_prd_expire_date TEXT,          -- 防護存続期間満了年月日（sec_conti_prd_expire_ymd → defensive_conti_prd_expire_date）
    defensive_ersr_flg TEXT,                       -- 防護抹消の有無（sec_ersr_flg → defensive_ersr_flg）
    defensive_apply_law TEXT,                      -- 防護適用法規（sec_apply_law → defensive_apply_law）
    defensive_recovery_num TEXT,                   -- 防護回復番号（sec_recovery_num → defensive_recovery_num）
    defensive_app_date TEXT,                       -- 防護出願年月日（sec_app_year_month_day → defensive_app_date）
    defensive_app_exam_pub_num TEXT,               -- 防護出願公告番号（sec_app_exam_pub_num → defensive_app_exam_pub_num）
    defensive_app_exam_pub_date TEXT,              -- 防護出願公告年月日（sec_app_exam_pub_ymd → defensive_app_exam_pub_date）
    defensive_finl_dcsn_date TEXT,                 -- 防護査定年月日（sec_finl_dcsn_year_month_day → defensive_finl_dcsn_date）
    defensive_trial_dcsn_date TEXT,                -- 防護審決年月日（sec_trial_dcsn_year_month_day → defensive_trial_dcsn_date）
    defensive_reg_date TEXT,                       -- 防護登録年月日（sec_reg_year_month_day → defensive_reg_date）
    defensive_rwrt_app_num TEXT,                   -- 防護書換申請番号（sec_rwrt_app_num → defensive_rwrt_app_num）
    defensive_rwrt_app_date TEXT,                  -- 防護書換申請年月日（sec_rwrt_app_year_month_day → defensive_rwrt_app_date）
    defensive_rwrt_finl_dcsn_date TEXT,            -- 防護書換査定年月日（sec_rwrt_finl_dcsn_ymd → defensive_rwrt_finl_dcsn_date）
    defensive_rwrt_trial_dcsn_date TEXT,           -- 防護書換審決年月日（sec_rwrt_trial_dcsn_ymd → defensive_rwrt_trial_dcsn_date）
    defensive_rwrt_reg_date TEXT,                  -- 防護書換登録年月日（sec_rwrt_reg_year_month_day → defensive_rwrt_reg_date）
    mu_num TEXT NOT NULL,                          -- MU番号（連番 000,001,002...）
    defensive_desig_goods_desig_wrk_cls TEXT,      -- 防護標章指定商品・役務類（sec_desig_goods_desig_wrk_cls → defensive_desig_goods_desig_wrk_cls）
    
    PRIMARY KEY (law_code, reg_num, split_num, app_num, pe_num, mu_num)
);

CREATE TABLE bougo_shohin_mei (
    processing_type TEXT,                          -- 処理種別（削除・修正等を示すコード）
    law_code TEXT NOT NULL,                        -- 四法コード（law_cd → law_code）
    reg_num TEXT NOT NULL,                         -- 登録番号（7桁）
    split_num TEXT NOT NULL,                       -- 分割番号（31桁）
    defensive_num TEXT NOT NULL,                   -- 防護番号（sec_num → defensive_num、統一済み）
    defensive_app_num TEXT NOT NULL,               -- 防護出願番号（sec_app_num → defensive_app_num、12-1と統一）
    defensive_desig_goods_desig_wrk_cls TEXT NOT NULL,  -- 防護指定商品・役務の区分（sec_desig_goods_desig_wrk_cls → defensive_desig_goods_desig_wrk_cls、統一済み）
    master_update_date TEXT,                       -- マスタ更新年月日（mstr_updt_year_month_day → master_update_date、統一済み）
    defensive_desig_gds_desig_wrk_nm_len TEXT,     -- 防護指定商品・役務名レングス（sec_desig_gds_desig_wrk_nm_len → defensive_desig_gds_desig_wrk_nm_len）
    defensive_desig_gds_nm_desig_wrk_nm TEXT,      -- 防護指定商品名・役務名（sec_desig_gds_nm_desig_wrk_nm → defensive_desig_gds_nm_desig_wrk_nm）
    
    PRIMARY KEY (law_code, reg_num, split_num, defensive_num, defensive_app_num, defensive_desig_goods_desig_wrk_cls)
);

CREATE TABLE bougo_koshin_kiji (
    processing_type TEXT,                          -- 処理種別（削除・修正等を示すコード）
    law_code TEXT NOT NULL,                        -- 四法コード（law_cd → law_code）
    reg_num TEXT NOT NULL,                         -- 登録番号（7桁）
    split_num TEXT NOT NULL,                       -- 分割番号（31桁）
    app_num TEXT NOT NULL,                         -- 出願番号（10桁）
    pe_num TEXT NOT NULL,                          -- ＰＥ番号（3桁）
    defensive_updt_art_upd_date TEXT,              -- 防護更新記事部作成更新年月日（sec_updt_art_upd_ymd → defensive_updt_art_upd_date）
    defensive_updt_app_num TEXT,                   -- 防護更新出願番号（sec_updt_app_num → defensive_updt_app_num）
    defensive_updt_num TEXT,                       -- 防護更新防護番号（sec_updt_sec_num → defensive_updt_num）
    defensive_updt_temp_reg_flg TEXT,              -- 防護更新仮登録の有無（sec_updt_temp_reg_flg → defensive_updt_temp_reg_flg）
    defensive_updt_title_chan_flg TEXT,            -- 防護更新名称変更の有無（sec_updt_title_chan_flg → defensive_updt_title_chan_flg）
    defensive_updt_recovery_num TEXT,              -- 防護更新回復番号（sec_updt_recovery_num → defensive_updt_recovery_num）
    defensive_updt_app_date TEXT,                  -- 防護更新出願年月日（sec_updt_app_year_month_day → defensive_updt_app_date）
    defensive_updt_finl_dcsn_date TEXT,            -- 防護更新査定年月日（sec_updt_finl_dcsn_ymd → defensive_updt_finl_dcsn_date）
    defensive_updt_trial_dcsn_date TEXT,           -- 防護更新審決年月日（sec_updt_trial_dcsn_ymd → defensive_updt_trial_dcsn_date）
    defensive_updt_reg_date TEXT,                  -- 防護更新登録年月日（sec_updt_reg_year_month_day → defensive_updt_reg_date）
    mu_num TEXT NOT NULL,                          -- MU番号（3桁、全行「000」）
    
    PRIMARY KEY (law_code, reg_num, split_num, app_num, pe_num, mu_num)
);

CREATE TABLE shohyo_fuka_joho (
    add_del_id TEXT,                    -- 追加削除識別（0:追加、1:削除）
    app_num TEXT,                       -- 出願番号（10桁、正規化済み）※登録ベースのテーブルではNULL可
    split_num TEXT,                     -- 分割番号（ほぼ空欄）
    sub_data_num TEXT,                  -- サブデータ番号（ほぼ空欄）
    right_request TEXT,                 -- 権利不要求（0または1）
    grphc_id TEXT,                      -- 図形識別（0または1）
    color_harftone TEXT,                -- カラーハーフトーン（0または1）
    gdmral_flg TEXT,                    -- 公序良俗フラグ（ほぼ全行「0」）
    duplicate_reg_flg TEXT,             -- 重複登録フラグ（ほぼ全行「0」）
    special_exception_clim_flg TEXT,    -- 特例主張フラグ（ほぼ全行「0」）
    consent_coe_reg_id TEXT,            -- 同意併存登録識別（ほぼ空欄）
    
    PRIMARY KEY (app_num, split_num, sub_data_num)
);

-- インデックス作成
CREATE INDEX idx_trademark_case_info_reg_num ON trademark_case_info(reg_article_reg_num);
CREATE INDEX idx_trademark_case_info_app_date ON trademark_case_info(app_date);
CREATE INDEX idx_trademark_standard_char_content ON trademark_standard_char(standard_char_t);
CREATE INDEX idx_trademark_display_content ON trademark_display(indct_use_t);
CREATE INDEX idx_trademark_search_content ON trademark_search(search_use_t);
CREATE INDEX idx_trademark_pronunciations_content ON trademark_pronunciations(pronunciation);
CREATE INDEX idx_trademark_goods_services_class ON trademark_goods_services(class_num);
CREATE INDEX idx_trademark_goods_services_name ON trademark_goods_services(goods_services_name);
CREATE INDEX idx_trademark_similar_group_codes_code ON trademark_similar_group_codes(similar_group_codes);
CREATE INDEX idx_trademark_vienna_codes_large ON trademark_vienna_codes(large_class);

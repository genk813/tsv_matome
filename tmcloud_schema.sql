-- TMCloud データベーススキーマ
-- 特許庁商標TSVデータ用の統一スキーマ

-- ========================================
-- 基本テーブル
-- ========================================

-- 商標基本情報テーブル
CREATE TABLE IF NOT EXISTS trademark_basic (
    app_num TEXT PRIMARY KEY,          -- 出願番号（正規化済み）
    app_date TEXT,                     -- 出願日
    reg_num TEXT,                      -- 登録番号
    reg_date TEXT,                     -- 登録日
    expiry_date TEXT,                  -- 存続期間満了日
    payment_due_date TEXT,             -- 分納満了日
    status TEXT,                       -- ステータス
    final_disposal TEXT,               -- 最終処分
    final_disposal_date TEXT,          -- 最終処分日
    rejection_date TEXT,               -- 拒絶査定発送日
    pub_date TEXT,                     -- 登録公報発行日
    pub_notice_date TEXT,              -- 公開公報発行日
    trademark_type TEXT,               -- 商標タイプ（標準文字、図形等）
    division_app_num TEXT,             -- 分割出願番号
    public_notice_num TEXT,            -- 公告番号
    protection_num TEXT,               -- 防護番号
    prior_right_date TEXT,             -- 先願権発生日
    app_type TEXT,                     -- 出願種別
    installment_flag TEXT,             -- 分納識別
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========================================
-- 商標内容関連テーブル
-- ========================================

-- 商標テキストテーブル
CREATE TABLE IF NOT EXISTS trademark_texts (
    app_num TEXT,                      -- 出願番号
    text_type TEXT,                    -- テキスト種別（standard, display, search）
    text_content TEXT,                 -- テキスト内容
    trademark_description TEXT,        -- 商標の詳細な説明
    sequence_num INTEGER DEFAULT 0,    -- シーケンス番号（複数行対応）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (app_num, text_type, sequence_num),
    FOREIGN KEY (app_num) REFERENCES trademark_basic(app_num),
    UNIQUE(app_num, text_type, text_content)  -- 重複防止
);

-- 商標画像テーブル
CREATE TABLE IF NOT EXISTS trademark_images (
    app_num TEXT PRIMARY KEY,          -- 出願番号
    image_data TEXT,                   -- Base64エンコード画像データ
    image_format TEXT,                 -- 画像フォーマット（jpeg, png, gif等）
    image_size INTEGER,                -- 画像サイズ（バイト）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (app_num) REFERENCES trademark_basic(app_num)
);

-- 称呼情報テーブル
CREATE TABLE IF NOT EXISTS trademark_pronunciations (
    app_num TEXT,                      -- 出願番号（統一後）
    pronunciation TEXT,                -- 称呼（dsgntから変換）
    sequence_num INTEGER DEFAULT 0,    -- シーケンス番号
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (app_num, sequence_num),
    FOREIGN KEY (app_num) REFERENCES trademark_basic(app_num)
);

-- 商標詳細説明テーブル
CREATE TABLE IF NOT EXISTS trademark_detailed_descriptions (
    app_num TEXT,                      -- 出願番号
    description_type TEXT,             -- 説明種別
    description_text TEXT,             -- 説明文
    sequence_num INTEGER,              -- シーケンス番号
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (app_num, description_type, sequence_num)
);

-- ========================================
-- 商品・役務関連テーブル
-- ========================================

-- 商品・役務情報テーブル
CREATE TABLE IF NOT EXISTS trademark_goods_services (
    app_num TEXT,                      -- 出願番号
    class_num TEXT,                    -- 区分番号
    goods_services_name TEXT,          -- 商品・役務名称
    sequence_num INTEGER DEFAULT 0,    -- シーケンス番号
    length_exceed_flag TEXT,           -- 長さ超過フラグ（複数行データ対応）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (app_num, class_num, sequence_num),
    FOREIGN KEY (app_num) REFERENCES trademark_basic(app_num)
);

-- 類似群コードテーブル
CREATE TABLE IF NOT EXISTS trademark_similar_groups (
    app_num TEXT,                      -- 出願番号
    similar_group_code TEXT,           -- 類似群コード
    sequence_num INTEGER DEFAULT 0,    -- シーケンス番号
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (app_num, similar_group_code),
    FOREIGN KEY (app_num) REFERENCES trademark_basic(app_num)
);

-- ========================================
-- 出願人・権利者関連テーブル
-- ========================================

-- 出願人・代理人情報テーブル
CREATE TABLE IF NOT EXISTS trademark_applicants (
    app_num TEXT,                      -- 出願番号
    applicant_type TEXT,               -- 種別（applicant, agent）
    applicant_code TEXT,               -- 申請人コード
    applicant_name TEXT,               -- 申請人名
    applicant_addr TEXT,               -- 住所
    record_num INTEGER DEFAULT 0,      -- レコード番号
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (app_num, applicant_type, record_num),
    FOREIGN KEY (app_num) REFERENCES trademark_basic(app_num)
);

-- 権利者情報テーブル
CREATE TABLE IF NOT EXISTS trademark_rights_holders (
    reg_num TEXT,                      -- 登録番号
    app_num TEXT,                      -- 出願番号（アクセス改善用）
    holder_code TEXT,                  -- 権利者コード
    holder_name TEXT,                  -- 権利者名
    holder_addr TEXT,                  -- 住所
    record_num INTEGER DEFAULT 0,      -- レコード番号
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (reg_num, record_num),
    FOREIGN KEY (app_num) REFERENCES trademark_basic(app_num)
);

-- 商標代理人情報テーブル
CREATE TABLE IF NOT EXISTS trademark_attorneys (
    reg_num TEXT,                      -- 登録番号
    attorney_code TEXT,                -- 代理人コード
    attorney_name TEXT,                -- 代理人名
    attorney_type TEXT,                -- 代理人種別
    pe_num TEXT,                       -- PE番号
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (reg_num, pe_num)
);

-- 申請人マスタテーブル
CREATE TABLE IF NOT EXISTS applicant_master (
    applicant_code TEXT PRIMARY KEY,   -- 申請人コード
    applicant_name TEXT,               -- 申請人名
    applicant_name_kana TEXT,          -- 申請人名カナ
    applicant_type TEXT,               -- 申請人種別
    country_code TEXT,                 -- 国コード
    prefecture_code TEXT,              -- 県コード
    address TEXT,                      -- 住所
    postcode TEXT,                     -- 郵便番号
    wes_name TEXT,                     -- 欧文名
    wes_addr TEXT,                     -- 欧文住所
    integrated_code TEXT,              -- 統合コード
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========================================
-- 審査・拒絶関連テーブル
-- ========================================

-- 拒絶理由テーブル
CREATE TABLE IF NOT EXISTS trademark_rejections (
    app_num TEXT,                      -- 出願番号
    rejection_code TEXT,               -- 拒絶条文コード
    rejection_date TEXT,               -- 拒絶理由通知日
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (app_num, rejection_code),
    FOREIGN KEY (app_num) REFERENCES trademark_basic(app_num)
);

-- 図形分類テーブル（ウィーンコード）
CREATE TABLE IF NOT EXISTS trademark_vienna_codes (
    app_num TEXT,                      -- 出願番号
    vienna_code TEXT,                  -- ウィーンコード
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (app_num, vienna_code),
    FOREIGN KEY (app_num) REFERENCES trademark_basic(app_num)
);

-- 中間記録テーブル
CREATE TABLE IF NOT EXISTS trademark_progress_records (
    app_num TEXT,                      -- 出願番号
    record_code TEXT,                  -- 中間記録コード
    record_date TEXT,                  -- 記録日
    record_content TEXT,               -- 記録内容
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (app_num, record_code, record_date),
    FOREIGN KEY (app_num) REFERENCES trademark_basic(app_num)
);

-- ========================================
-- 審判・異議関連テーブル
-- ========================================

-- 審判事件テーブル
CREATE TABLE IF NOT EXISTS tribunal_cases (
    tribunal_num TEXT PRIMARY KEY,     -- 審判番号
    app_num TEXT,                      -- 関連出願番号
    reg_num TEXT,                      -- 関連登録番号
    tribunal_type TEXT,                -- 審判種別
    request_date TEXT,                 -- 請求日
    decision_date TEXT,                -- 審決日
    result TEXT,                       -- 結果
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 審決分類テーブル
CREATE TABLE IF NOT EXISTS trademark_trial_decisions (
    app_num TEXT,                      -- 出願番号
    trial_num TEXT,                    -- 審判番号
    decision_class TEXT,               -- 審決分類
    decision_date TEXT,                -- 審決日
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (app_num, trial_num),
    FOREIGN KEY (app_num) REFERENCES trademark_basic(app_num)
);

-- 異議申立テーブル
CREATE TABLE IF NOT EXISTS trademark_oppositions (
    reg_num TEXT,                      -- 登録番号
    opposition_num TEXT,               -- 異議番号
    opposition_date DATE,              -- 異議申立日
    opposition_type TEXT,              -- 異議種別
    applicant_name TEXT,               -- 申立人名
    decision_date DATE,                -- 決定日
    decision_type TEXT,                -- 決定種別
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (reg_num, opposition_num)
);

-- 異議決定テーブル
CREATE TABLE IF NOT EXISTS opposition_decisions (
    reg_num TEXT,                      -- 登録番号
    opposition_num TEXT,               -- 異議番号
    decision_date DATE,                -- 決定日
    decision_type TEXT,                -- 決定種別
    decision_content TEXT,             -- 決定内容
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (reg_num, opposition_num, decision_date)
);

-- 審判受付書類テーブル
CREATE TABLE IF NOT EXISTS trademark_acceptance_documents (
    uktk_syri_bngu TEXT PRIMARY KEY,   -- 受付処理番号
    snpn_bngu TEXT,                    -- 審判番号
    tyukn_cd TEXT,                     -- 中間コード
    syri_ssds_dt TEXT,                 -- 処理作成日
    syri_uktk_dt TEXT,                 -- 処理受付日
    hssu_syri_bngu TEXT,               -- 発送処理番号
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 審判発送書類テーブル
CREATE TABLE IF NOT EXISTS trademark_dispatch_documents (
    case_num TEXT,                     -- 事件番号
    doc_num TEXT,                      -- 書類番号
    doc_name TEXT,                     -- 書類名
    dispatch_date DATE,                -- 発送日
    dispatch_num TEXT,                 -- 発送番号
    page_count INTEGER,                -- ページ数
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (case_num, dispatch_date, doc_num)
);

-- ========================================
-- 更新・管理関連テーブル
-- ========================================

-- 商標更新履歴テーブル
CREATE TABLE IF NOT EXISTS trademark_renewal_history (
    reg_num TEXT,                      -- 登録番号
    renewal_num INTEGER,               -- 更新回数
    renewal_app_date DATE,             -- 更新申請日
    renewal_reg_date DATE,             -- 更新登録日
    expiry_date DATE,                  -- 存続期間満了日
    renewal_type TEXT,                 -- 更新種別
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (reg_num, renewal_num)
);

-- 商標更新記事テーブル
CREATE TABLE IF NOT EXISTS trademark_updates (
    reg_num TEXT,                      -- 登録番号
    update_reg_num TEXT,               -- 更新登録番号
    update_app_date TEXT,              -- 更新申請日
    update_reg_date TEXT,              -- 更新登録日
    update_count INTEGER DEFAULT 0,    -- 更新回数
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (reg_num, update_count)
);

-- 商標管理情報テーブル
CREATE TABLE IF NOT EXISTS trademark_management (
    app_num TEXT,                      -- 出願番号
    reg_num TEXT,                      -- 登録番号
    expiry_date TEXT,                  -- 存続期間満了日
    payment_due_date TEXT,             -- 支払期限日
    status_code TEXT,                  -- ステータスコード
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (app_num)
);

-- 書換申請情報テーブル
CREATE TABLE IF NOT EXISTS trademark_rewrite_applications (
    reg_num TEXT,                      -- 登録番号
    app_num TEXT,                      -- 出願番号
    rewrite_app_num TEXT,              -- 書換申請番号
    update_date TEXT,                  -- 更新日
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (reg_num, app_num)
);

-- 中間記録テーブル（庁内/起案/申請）
CREATE TABLE IF NOT EXISTS trademark_intermediate_records (
    app_num TEXT,                      -- 出願番号
    record_type TEXT,                  -- 記録タイプ（chonai/kian/sinsei）
    record_date TEXT,                  -- 記録日
    record_content TEXT,               -- 記録内容
    document_code TEXT,                -- 書類コード
    detail_1 TEXT,                     -- 詳細1
    detail_2 TEXT,                     -- 詳細2
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (app_num, record_type, record_date, document_code),
    FOREIGN KEY (app_num) REFERENCES trademark_basic(app_num)
);

-- ========================================
-- 国際商標関連テーブル
-- ========================================

-- 国際商標テーブル
CREATE TABLE IF NOT EXISTS international_trademarks (
    intl_reg_num TEXT PRIMARY KEY,     -- 国際登録番号
    app_num TEXT,                      -- 国内出願番号
    reg_num TEXT,                      -- 国内登録番号
    holder_name TEXT,                  -- 権利者名
    origin_country TEXT,               -- 本国
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 国際商標登録テーブル
CREATE TABLE IF NOT EXISTS international_registrations (
    app_num TEXT,                      -- 出願番号
    intl_reg_num TEXT,                 -- 国際登録番号
    intl_reg_date DATE,                -- 国際登録日
    base_reg_num TEXT,                 -- 基礎登録番号
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (app_num, intl_reg_num)
);

-- 国際商標基本情報テーブル
CREATE TABLE IF NOT EXISTS intl_trademark_basic (
    intl_reg_num TEXT PRIMARY KEY,     -- 国際登録番号
    app_date TEXT,                     -- 出願日
    reg_date TEXT,                     -- 登録日
    expiry_date TEXT,                  -- 存続期間満了日
    holder_name TEXT,                  -- 権利者名
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 国際商標進捗情報テーブル
CREATE TABLE IF NOT EXISTS intl_trademark_progress (
    intl_reg_num TEXT,                 -- 国際登録番号
    progress_date DATE,                -- 進捗日
    progress_type TEXT,                -- 進捗種別
    progress_content TEXT,             -- 進捗内容
    country_code TEXT,                 -- 国コード
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (intl_reg_num, progress_date, progress_type)
);

-- 国際商標権利者情報テーブル
CREATE TABLE IF NOT EXISTS intl_trademark_holders (
    intl_reg_num TEXT,                 -- 国際登録番号
    holder_name TEXT,                  -- 権利者名
    holder_address TEXT,               -- 住所
    country_code TEXT,                 -- 国コード
    holder_type TEXT,                  -- 権利者種別
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (intl_reg_num, holder_name)
);

-- 国際商標商品・役務情報テーブル
CREATE TABLE IF NOT EXISTS intl_trademark_goods (
    intl_reg_num TEXT,                 -- 国際登録番号
    class_num TEXT,                    -- 類番号
    goods_services TEXT,               -- 商品・役務
    sequence_num INTEGER,              -- シーケンス番号
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (intl_reg_num, class_num, sequence_num)
);

-- 国際商標最初の表示テーブル
CREATE TABLE IF NOT EXISTS intl_trademark_first_indication (
    intl_reg_num TEXT PRIMARY KEY,     -- 国際登録番号
    final_decision_date TEXT,          -- 最終決定日
    priority_country_code TEXT,        -- 優先権国コード
    priority_date TEXT,                -- 優先権日
    priority_claim_count INTEGER,      -- 優先権主張数
    special_trademark_flag TEXT,       -- 特殊商標フラグ
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========================================
-- その他の情報テーブル
-- ========================================

-- 優先権情報テーブル
CREATE TABLE IF NOT EXISTS trademark_priority (
    app_num TEXT,                      -- 出願番号
    priority_country TEXT,             -- 優先権国
    priority_date TEXT,                -- 優先権日
    priority_num TEXT,                 -- 優先権番号
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (app_num, priority_country, priority_num)
);

-- 商品区分記事テーブル
CREATE TABLE IF NOT EXISTS goods_classification (
    app_num TEXT,                      -- 出願番号
    reg_num TEXT,                      -- 登録番号
    class_num TEXT,                    -- 区分番号
    goods_name TEXT,                   -- 商品名
    sequence_num INTEGER DEFAULT 0,    -- シーケンス番号
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (app_num, class_num, sequence_num)
);

-- 防護標章関連テーブル
CREATE TABLE IF NOT EXISTS trademark_security (
    reg_num TEXT PRIMARY KEY,          -- 登録番号
    security_type TEXT,                -- 防護種別
    security_date TEXT,                -- 防護日
    security_count INTEGER,            -- 防護回数
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 移転受付情報テーブル
CREATE TABLE IF NOT EXISTS trademark_transfers (
    transfer_receipt_num TEXT PRIMARY KEY,  -- 移転受付番号
    reg_num TEXT,                      -- 登録番号
    transfer_date TEXT,                -- 移転日
    transfer_type TEXT,                -- 移転種別
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 商標付加情報テーブル
CREATE TABLE IF NOT EXISTS trademark_additional_info (
    app_num TEXT PRIMARY KEY,          -- 出願番号
    color_claim TEXT,                  -- 色彩主張
    three_d_mark TEXT,                 -- 立体商標
    sound_mark TEXT,                   -- 音商標
    collective_mark TEXT,              -- 団体商標
    geographic_mark TEXT,              -- 地域団体商標
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (app_num) REFERENCES trademark_basic(app_num)
);

-- 公報発行情報テーブル
CREATE TABLE IF NOT EXISTS trademark_gazette (
    app_num TEXT PRIMARY KEY,          -- 出願番号
    gazette_date TEXT,                 -- 公報発行日
    gazette_num TEXT,                  -- 公報番号
    gazette_type TEXT,                 -- 公報種別
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========================================
-- システム管理テーブル
-- ========================================

-- 出願番号と登録番号のマッピングテーブル
CREATE TABLE IF NOT EXISTS app_reg_mapping (
    app_num TEXT PRIMARY KEY,          -- 出願番号
    reg_num TEXT,                      -- 登録番号
    mapping_date TEXT,                 -- マッピング日
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- インポートログテーブル
CREATE TABLE IF NOT EXISTS import_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_name TEXT,                    -- ファイル名
    table_name TEXT,                   -- テーブル名
    records_imported INTEGER,          -- インポート件数
    errors INTEGER,                    -- エラー件数
    encoding_used TEXT,                -- 使用エンコーディング
    import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 週次更新履歴テーブル
CREATE TABLE IF NOT EXISTS update_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    app_num TEXT,                      -- 出願番号
    update_date TEXT,                  -- 更新日
    update_type TEXT,                  -- 更新タイプ（new, update）
    source_file TEXT,                  -- ソースファイル名
    field_updated TEXT,                -- 更新されたフィールド（JSON形式）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (app_num) REFERENCES trademark_basic(app_num)
);

-- ========================================
-- インデックス定義
-- ========================================

-- 基本テーブルのインデックス
CREATE INDEX IF NOT EXISTS idx_trademark_basic_reg_num ON trademark_basic(reg_num);
CREATE INDEX IF NOT EXISTS idx_trademark_basic_app_date ON trademark_basic(app_date);
CREATE INDEX IF NOT EXISTS idx_trademark_basic_status ON trademark_basic(status);

-- 商標内容関連のインデックス
CREATE INDEX IF NOT EXISTS idx_trademark_texts_type ON trademark_texts(text_type);
CREATE INDEX IF NOT EXISTS idx_trademark_texts_content ON trademark_texts(text_content);
CREATE INDEX IF NOT EXISTS idx_trademark_pronunciations_text ON trademark_pronunciations(pronunciation);

-- 商品・役務関連のインデックス
CREATE INDEX IF NOT EXISTS idx_trademark_goods_class ON trademark_goods_services(class_num);
CREATE INDEX IF NOT EXISTS idx_trademark_goods_name ON trademark_goods_services(goods_services_name);
CREATE INDEX IF NOT EXISTS idx_trademark_similar_groups_code ON trademark_similar_groups(similar_group_code);

-- 出願人・権利者関連のインデックス
CREATE INDEX IF NOT EXISTS idx_trademark_applicants_code ON trademark_applicants(applicant_code);
CREATE INDEX IF NOT EXISTS idx_trademark_applicants_name ON trademark_applicants(applicant_name);
CREATE INDEX IF NOT EXISTS idx_trademark_rights_holders_code ON trademark_rights_holders(holder_code);
CREATE INDEX IF NOT EXISTS idx_trademark_rights_holders_name ON trademark_rights_holders(holder_name);
CREATE INDEX IF NOT EXISTS idx_trademark_rights_holders_app_num ON trademark_rights_holders(app_num);
CREATE INDEX IF NOT EXISTS idx_attorney_reg_num ON trademark_attorneys(reg_num);
CREATE INDEX IF NOT EXISTS idx_applicant_master_name ON applicant_master(applicant_name);

-- 審査・拒絶関連のインデックス
CREATE INDEX IF NOT EXISTS idx_trademark_rejections_code ON trademark_rejections(rejection_code);
CREATE INDEX IF NOT EXISTS idx_trademark_vienna_codes_code ON trademark_vienna_codes(vienna_code);
CREATE INDEX IF NOT EXISTS idx_trademark_progress_records_code ON trademark_progress_records(record_code);

-- 審判・異議関連のインデックス
CREATE INDEX IF NOT EXISTS idx_tribunal_cases_app_num ON tribunal_cases(app_num);
CREATE INDEX IF NOT EXISTS idx_tribunal_cases_reg_num ON tribunal_cases(reg_num);
CREATE INDEX IF NOT EXISTS idx_trademark_trial_decisions_num ON trademark_trial_decisions(trial_num);
CREATE INDEX IF NOT EXISTS idx_opposition_reg_num ON trademark_oppositions(reg_num);

-- 更新・管理関連のインデックス
CREATE INDEX IF NOT EXISTS idx_renewal_reg_num ON trademark_renewal_history(reg_num);
CREATE INDEX IF NOT EXISTS idx_updates_reg_num ON trademark_updates(reg_num);

-- 国際商標関連のインデックス
CREATE INDEX IF NOT EXISTS idx_international_trademarks_app_num ON international_trademarks(app_num);
CREATE INDEX IF NOT EXISTS idx_international_trademarks_reg_num ON international_trademarks(reg_num);
CREATE INDEX IF NOT EXISTS idx_intl_reg_num ON international_registrations(intl_reg_num);
CREATE INDEX IF NOT EXISTS idx_intl_progress_reg ON intl_trademark_progress(intl_reg_num);

-- その他のインデックス
CREATE INDEX IF NOT EXISTS idx_gazette_app_num ON trademark_gazette(app_num);
CREATE INDEX IF NOT EXISTS idx_app_reg_mapping_reg_num ON app_reg_mapping(reg_num);
CREATE INDEX IF NOT EXISTS idx_import_log_date ON import_log(import_date);
CREATE INDEX IF NOT EXISTS idx_update_history_app_num ON update_history(app_num);
CREATE INDEX IF NOT EXISTS idx_update_history_date ON update_history(update_date);
CREATE INDEX IF NOT EXISTS idx_update_history_type ON update_history(update_type);

-- Phase 3追加テーブルのインデックス
CREATE INDEX IF NOT EXISTS idx_intermediate_app_num ON trademark_intermediate_records(app_num);
CREATE INDEX IF NOT EXISTS idx_intermediate_type ON trademark_intermediate_records(record_type);
CREATE INDEX IF NOT EXISTS idx_rewrite_reg_num ON trademark_rewrite_applications(reg_num);
CREATE INDEX IF NOT EXISTS idx_priority_app_num ON trademark_priority(app_num);
CREATE INDEX IF NOT EXISTS idx_management_app_num ON trademark_management(app_num);
CREATE INDEX IF NOT EXISTS idx_management_reg_num ON trademark_management(reg_num);
CREATE INDEX IF NOT EXISTS idx_transfers_reg_num ON trademark_transfers(reg_num);
CREATE INDEX IF NOT EXISTS idx_security_reg_num ON trademark_security(reg_num);
CREATE INDEX IF NOT EXISTS idx_goods_class_app_num ON goods_classification(app_num);
CREATE INDEX IF NOT EXISTS idx_goods_class_reg_num ON goods_classification(reg_num);

-- ========================================
-- ビュー定義
-- ========================================

-- 商標統合検索ビュー
CREATE VIEW IF NOT EXISTS v_trademark_search AS
SELECT 
    tb.app_num,
    tb.app_date,
    tb.reg_num,
    tb.reg_date,
    tb.status,
    COALESCE(ts.text_content, td.text_content, tse.text_content) as trademark_text,
    ts.text_content as standard_text,
    td.text_content as display_text,
    tse.text_content as search_text,
    arm.reg_num as mapped_reg_num
FROM 
    trademark_basic tb
    LEFT JOIN trademark_texts ts ON tb.app_num = ts.app_num AND ts.text_type = 'standard'
    LEFT JOIN trademark_texts td ON tb.app_num = td.app_num AND td.text_type = 'display'
    LEFT JOIN trademark_texts tse ON tb.app_num = tse.app_num AND tse.text_type = 'search'
    LEFT JOIN app_reg_mapping arm ON tb.app_num = arm.app_num
WHERE 
    ts.sequence_num = 0 OR ts.sequence_num IS NULL
    AND (td.sequence_num = 0 OR td.sequence_num IS NULL)
    AND (tse.sequence_num = 0 OR tse.sequence_num IS NULL);

-- 商品・役務統合ビュー
CREATE VIEW IF NOT EXISTS v_goods_services_by_app AS
SELECT 
    app_num,
    GROUP_CONCAT(DISTINCT class_num) as class_nums,
    GROUP_CONCAT(goods_services_name, ' / ') as all_goods_services
FROM 
    trademark_goods_services
GROUP BY 
    app_num;

-- 権利者情報統合ビュー
CREATE VIEW IF NOT EXISTS v_rights_holders_by_reg AS
SELECT 
    reg_num,
    GROUP_CONCAT(DISTINCT holder_name) as holder_names,
    COUNT(DISTINCT holder_code) as holder_count
FROM 
    trademark_rights_holders
GROUP BY 
    reg_num;

-- 出願人／権利者統合ビュー（TMSONARスタイル）
CREATE VIEW IF NOT EXISTS v_applicants_rights_holders AS
SELECT 
    tb.app_num,
    tb.reg_num,
    'applicant' as person_type,
    ta.applicant_code as person_code,
    ta.applicant_name as person_name,
    ta.applicant_addr as person_addr,
    am.country_code,
    am.prefecture_code
FROM 
    trademark_basic tb
    INNER JOIN trademark_applicants ta ON tb.app_num = ta.app_num
    LEFT JOIN applicant_master am ON ta.applicant_code = am.applicant_code
WHERE 
    ta.applicant_type = 'applicant'
    
UNION ALL

SELECT 
    tb.app_num,
    tb.reg_num,
    'rights_holder' as person_type,
    trh.holder_code as person_code,
    trh.holder_name as person_name,
    trh.holder_addr as person_addr,
    NULL as country_code,
    NULL as prefecture_code
FROM 
    trademark_basic tb
    INNER JOIN trademark_rights_holders trh ON tb.reg_num = trh.reg_num AND trh.app_num = tb.app_num;
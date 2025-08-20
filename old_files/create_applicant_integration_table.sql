-- 被統合申請人情報管理テーブルの作成（分離して実行）
CREATE TABLE IF NOT EXISTS applicant_integration_mapping (
    appl_cd VARCHAR(9) NOT NULL,
    repeat_num INTEGER NOT NULL,
    under_integ_appl_cd VARCHAR(9) NOT NULL,
    PRIMARY KEY (appl_cd, repeat_num),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- インデックス作成
CREATE INDEX IF NOT EXISTS idx_applicant_integration_under ON applicant_integration_mapping(under_integ_appl_cd);
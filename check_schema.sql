-- テーブル構造確認
.headers on
.mode column

-- trademark_case_infoテーブルの構造
PRAGMA table_info(trademark_case_info);

-- 出願番号2024061720の全カラム確認
SELECT * FROM trademark_case_info WHERE app_num = '2024061720' LIMIT 1;
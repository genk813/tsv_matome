-- 出願番号2024061720を立体商標に修正
UPDATE trademark_case_info
SET special_mark_type = '1',
    dimensional_trademark_flag = '1'
WHERE app_num = '2024061720';

-- 修正後の確認
SELECT app_num, 
       trademark_type,
       dimensional_trademark_flag,
       special_mark_type,
       standard_char_exist
FROM trademark_case_info
WHERE app_num = '2024061720';
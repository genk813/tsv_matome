-- 出願番号2024061720の確認
.headers on
.mode column
.width 15 20 25 20 20

SELECT 
    app_num,
    trademark_type,
    dimensional_trademark_flag,
    special_mark_type,
    standard_char_exist
FROM trademark_case_info
WHERE app_num = '2024061720';

-- 立体商標の例を確認
SELECT '--- 立体商標の例 ---' as info;
SELECT 
    app_num,
    special_mark_type,
    dimensional_trademark_flag
FROM trademark_case_info
WHERE special_mark_type = '1'
LIMIT 3;

-- dimensional_trademark_flagが1の例
SELECT '--- dimensional_trademark_flag=1の例 ---' as info;
SELECT 
    app_num,
    special_mark_type,
    dimensional_trademark_flag
FROM trademark_case_info
WHERE dimensional_trademark_flag = '1'
LIMIT 3;
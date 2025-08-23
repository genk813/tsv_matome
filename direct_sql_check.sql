-- 出願番号2024061720の立体商標判定チェック
.open tmcloud_v2_20250818_081655.db
.headers on
.mode table

SELECT 
    app_num as '出願番号',
    special_mark_type as '特殊マーク種別',
    dimensional_trademark_flag as '立体商標フラグ',
    CASE 
        WHEN special_mark_type = '1' OR dimensional_trademark_flag = '1' 
        THEN '✓ 立体商標'
        ELSE '✗ 非立体商標'
    END as '判定結果'
FROM trademark_case_info
WHERE app_num = '2024061720';

-- もしデータが見つからない場合のデバッグ
.print "=== データ存在確認 ==="
SELECT COUNT(*) as 'データ総数' FROM trademark_case_info;

.print "=== 2024年の出願番号サンプル ==="
SELECT app_num FROM trademark_case_info 
WHERE app_num LIKE '2024%' 
LIMIT 5;
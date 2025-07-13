-- 統合商標検索ビュー作成（重複表示問題修正版）
-- 国内商標と国際商標を統合して類似商標検索を可能にする

-- 既存ビューを削除
DROP VIEW IF EXISTS unified_trademark_search_view;

-- 統合商標検索ビュー作成（重複問題修正）
CREATE VIEW unified_trademark_search_view AS
WITH domestic_trademarks AS (
    SELECT 
        'domestic' as source_type,
        j.normalized_app_num as app_num,
        COALESCE(je.raz_toroku_no, rm.reg_num) as reg_num,
        j.shutugan_bi as app_date,
        j.reg_reg_ymd as reg_date,
        COALESCE(s.standard_char_t, iu.indct_use_t, su.search_use_t) as trademark_text,
        GROUP_CONCAT(DISTINCT td.dsgnt) as pronunciation,  -- 重複除去
        GROUP_CONCAT(DISTINCT gca.goods_classes) as nice_classes,  -- 重複除去
        GROUP_CONCAT(DISTINCT jcs.designated_goods) as goods_services,  -- 重複除去
        GROUP_CONCAT(DISTINCT tknd.smlr_dsgn_group_cd) as similar_groups,  -- 重複除去
        rp.right_person_name as holder_name,
        rp.right_person_addr as holder_addr,
        NULL as holder_country,
        CASE WHEN ts.image_data IS NOT NULL THEN 1 ELSE 0 END as has_image,
        NULL as final_disposition,
        tbi.prior_app_right_occr_dt as prior_right_date,
        tbi.conti_prd_expire_dt as expiry_date
    FROM jiken_c_t j
    LEFT JOIN jiken_c_t_enhanced je ON j.normalized_app_num = je.normalized_app_num
    LEFT JOIN reg_mapping rm ON j.normalized_app_num = rm.app_num
    LEFT JOIN right_person_art_t rp ON rm.reg_num = rp.reg_num
    LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num
    LEFT JOIN indct_use_t_art iu ON j.normalized_app_num = iu.normalized_app_num
    LEFT JOIN search_use_t_art_table su ON j.normalized_app_num = su.normalized_app_num
    LEFT JOIN t_dsgnt_art td ON j.normalized_app_num = td.normalized_app_num
    LEFT JOIN goods_class_art gca ON (j.normalized_app_num = gca.normalized_app_num OR 
                                       (rm.reg_num IS NOT NULL AND gca.reg_num = rm.reg_num))
    LEFT JOIN jiken_c_t_shohin_joho jcs ON j.normalized_app_num = jcs.normalized_app_num
    LEFT JOIN t_knd_info_art_table tknd ON j.normalized_app_num = tknd.normalized_app_num
    LEFT JOIN t_sample ts ON j.normalized_app_num = ts.normalized_app_num
    LEFT JOIN t_basic_item_enhanced tbi ON j.normalized_app_num = tbi.normalized_app_num
    -- 重複除去のための GROUP BY を追加
    GROUP BY j.normalized_app_num, je.raz_toroku_no, rm.reg_num, j.shutugan_bi, j.reg_reg_ymd,
             COALESCE(s.standard_char_t, iu.indct_use_t, su.search_use_t),
             rp.right_person_name, rp.right_person_addr,
             CASE WHEN ts.image_data IS NOT NULL THEN 1 ELSE 0 END,
             tbi.prior_app_right_occr_dt, tbi.conti_prd_expire_dt
),
international_trademarks AS (
    SELECT 
        'international' as source_type,
        ir.app_num,
        ir.intl_reg_num as reg_num,
        ir.app_date,
        ir.intl_reg_date as reg_date,
        it.t_dtl_explntn as trademark_text,
        NULL as pronunciation,
        GROUP_CONCAT(DISTINCT ig.goods_class) as nice_classes,
        GROUP_CONCAT(DISTINCT ig.goods_content) as goods_services,
        NULL as similar_groups,
        COALESCE(ih.holder_name_japanese, ih.holder_name) as holder_name,
        COALESCE(ih.holder_addr_japanese, ih.holder_addr) as holder_addr,
        ih.holder_ctry_cd as holder_country,
        0 as has_image,
        NULL as final_disposition,
        NULL as prior_right_date,
        NULL as expiry_date
    FROM intl_trademark_registration ir
    LEFT JOIN intl_trademark_text it ON ir.intl_reg_num = it.intl_reg_num
    LEFT JOIN intl_trademark_goods_services ig ON ir.intl_reg_num = ig.intl_reg_num
    LEFT JOIN intl_trademark_holder ih ON ir.intl_reg_num = ih.intl_reg_num
    WHERE (ir.define_flg = '1' OR ir.define_flg IS NULL)  -- 確定済み or NULL
    GROUP BY ir.intl_reg_num, ir.app_num, ir.app_date, ir.intl_reg_date,
             it.t_dtl_explntn, ih.holder_name_japanese, ih.holder_name,
             ih.holder_addr_japanese, ih.holder_addr, ih.holder_ctry_cd
)
SELECT 
    source_type,
    app_num,
    reg_num,
    app_date,
    reg_date,
    trademark_text,
    pronunciation,
    nice_classes,
    goods_services,
    similar_groups,
    holder_name,
    holder_addr,
    holder_country,
    has_image,
    final_disposition,
    prior_right_date,
    expiry_date,
    -- 統合用の正規化フィールド
    CASE 
        WHEN source_type = 'domestic' THEN app_num
        ELSE reg_num
    END as unified_id,
    CASE 
        WHEN trademark_text IS NOT NULL AND trademark_text != '' THEN trademark_text
        WHEN pronunciation IS NOT NULL AND pronunciation != '' THEN pronunciation
        ELSE 'テキストなし'
    END as display_text,
    CASE 
        WHEN reg_date IS NOT NULL AND reg_date != '' THEN '登録済'
        ELSE '未登録'
    END as registration_status
FROM domestic_trademarks
WHERE (trademark_text IS NOT NULL AND trademark_text != '')
   OR (pronunciation IS NOT NULL AND pronunciation != '')  -- 称呼があれば含める

UNION ALL

SELECT 
    source_type,
    app_num,
    reg_num,
    app_date,
    reg_date,
    trademark_text,
    pronunciation,
    nice_classes,
    goods_services,
    similar_groups,
    holder_name,
    holder_addr,
    holder_country,
    has_image,
    final_disposition,
    prior_right_date,
    expiry_date,
    CASE 
        WHEN source_type = 'domestic' THEN app_num
        ELSE reg_num
    END as unified_id,
    CASE 
        WHEN trademark_text IS NOT NULL AND trademark_text != '' THEN trademark_text
        WHEN pronunciation IS NOT NULL AND pronunciation != '' THEN pronunciation
        ELSE reg_num  -- 国際商標は登録番号を表示
    END as display_text,
    CASE 
        WHEN reg_date IS NOT NULL AND reg_date != '' THEN '登録済'
        ELSE '未登録'
    END as registration_status
FROM international_trademarks;
-- 国際商標は条件を緩和（登録番号があれば含める）
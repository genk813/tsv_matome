# TMSONARで必要なカラムのマッピング

## TMSONARの検索可能項目（全42項目）

### 《主項目》11項目
1. **商標** → upd_standard_char_t_art.tsv, upd_indct_use_t_art.tsv, upd_search_use_t_art_table.tsv
2. **称呼（発音同一）** → upd_t_dsgnt_art.tsv (dsgnt)
3. **称呼（表記同一）** → upd_t_dsgnt_art.tsv (dsgnt)
4. **類似群コード** → upd_t_knd_info_art_table.tsv (smlr_dsgn_group_cd)
5. **国際分類（類似群コード展開）** → upd_jiken_c_t_shohin_joho.tsv (rui)
6. **法区分＋類** → upd_jiken_c_t.tsv (houkubun) + upd_jiken_c_t_shohin_joho.tsv (rui)
7. **指定商品／役務** → upd_jiken_c_t_shohin_joho.tsv (shohinekimumeisho)
8. **拒絶条文コード** → upd_jiken_c_t_kian_dv.tsv (kyozetsu_riyujobun_code)
9. **ウィーンコード** → upd_t_vienna_class_grphc_term_art.tsv (vienna_code)
10. **審決分類（国内のみ）** → upd_snkt_bnri.tsv (shinketsu_bunrui)
11. **最終処分** → upd_jiken_c_t.tsv (saishushobun)

### 《人名住所》4項目
12. **出願人／権利者** → upd_jiken_c_t_shutugannindairinin.tsv (shutugannindairinin_simei, sikbt='1'), upd_right_person_art_t.tsv (kenrisha_name)
13. **出願人／権利者住所** → upd_jiken_c_t_shutugannindairinin.tsv (shutugannindairinin_jusho), upd_right_person_art_t.tsv (kenrisha_jusho)
14. **国県コード（出願人）** → upd_appl_reg_info.tsv (kuni_cd, ken_cd)
15. **代理人** → upd_jiken_c_t_shutugannindairinin.tsv (shutugannindairinin_simei, sikbt='2'), upd_atty_art_t.tsv

### 《日付》10項目
16. **出願日／国際登録日（事後指定日）** → upd_jiken_c_t.tsv (shutugan_bi), upd_intl_t_org_org_reg_mgt_info.tsv (intl_reg_date)
17. **登録日／国内登録日** → upd_jiken_c_t.tsv (toroku_bi)
18. **拒絶査定発送日** → upd_jiken_c_t.tsv (kyozetu_satei_hasso_bi)
19. **最終処分日** → upd_jiken_c_t.tsv (saishushobun_bi)
20. **存続期間満了日（国内のみ）** → upd_jiken_c_t.tsv (sonzoku_kikan_manryo_bi), upd_mgt_info_t.tsv
21. **分納満了日（国内のみ）** → upd_jiken_c_t.tsv (bunno_manryo_bi)
22. **登録公報発行日（国内のみ）** → upd_jiken_c_t.tsv (toroku_koho_hakko_bi)
23. **公開公報発行日** → upd_jiken_c_t.tsv (kokai_koho_hakko_bi)
24. **新規登録追加日** → システムメタデータ
25. **新規出願追加日** → システムメタデータ
26. **ステータス変更日** → システムメタデータ

### 《番号》4項目
27. **出願番号／マドプロ管理番号** → upd_jiken_c_t.tsv (shutugan_no), upd_intl_t_org_org_reg_mgt_info.tsv
28. **登録番号／国際登録番号** → upd_jiken_c_t.tsv (raz_toroku_no), upd_intl_t_org_org_reg_mgt_info.tsv (intl_reg_num)
29. **審判番号（国内のみ）** → upd_snpn_zkn.tsv (snpn_bngu)
30. **出願番号／登録番号** → upd_jiken_c_t.tsv (shutugan_no, raz_toroku_no)

### 《経過》1項目
31. **中間記録コード** → upd_jiken_c_t_chonai_dv.tsv, upd_jiken_c_t_kian_dv.tsv, upd_jiken_c_t_sinsei_dv.tsv

### 《その他》11項目
32. **商標文字数** → 計算フィールド
33. **称呼音数** → 計算フィールド
34. **情報提供数** → （データ未確認）
35. **閲覧請求数** → （データ未確認）
36. **区分数** → 計算フィールド
37. **出願人／権利者数** → 計算フィールド
38. **称呼数** → 計算フィールド
39. **出願種別** → upd_jiken_c_t.tsv (shutugan_shubetsu)
40. **付加情報** → upd_t_add_info.tsv, upd_t_basic_item_art.tsv
41. **商標タイプ** → upd_jiken_c_t.tsv (hyojun_moji_flg等), upd_t_add_info.tsv
42. **商標の詳細な説明** → upd_jiken_c_t_shousaina_setumei.tsv

## TMSONARの検索結果表示項目

### 商標関連
- **【商標】** → upd_standard_char_t_art.tsv, upd_indct_use_t_art.tsv, upd_search_use_t_art_table.tsv
- **【称呼】** → upd_t_dsgnt_art.tsv (dsgnt)
- **商標画像** → upd_t_sample.tsv (image_data)
- **【商標タイプ】** → upd_jiken_c_t.tsv (hyojun_moji_flg等), upd_t_add_info.tsv
- **【商標の詳細な説明】** → upd_jiken_c_t_shousaina_setumei.tsv

### 番号関連
- **【出願番号】** → upd_jiken_c_t.tsv (shutugan_no)
- **【公告番号】** → upd_t_basic_item_art.tsv (kokoku_no)
- **【防護番号】** → upd_t_basic_item_art.tsv (bogo_no / sec_num)
- **【登録番号】** → upd_jiken_c_t.tsv (raz_toroku_no)
- **【分割番号】** → upd_jiken_c_t.tsv (bunkatsu_gen_shutugan_no)
- **【書換申請番号】** → upd_mrgn_t_rwrt_app_num.tsv
- **【更新出願番号】** → upd_t_updt_art.tsv

### 日付関連
- **出願日** → upd_jiken_c_t.tsv (shutugan_bi)
- **【先願権発生日】** → upd_t_basic_item_art.tsv (prior_app_right_occr_dt)
- **【公開日】** → upd_jiken_c_t.tsv (kokai_koho_hakko_bi)
- **【公報発行日】** → upd_jiken_c_t.tsv (toroku_koho_hakko_bi)
- **【存続期間満了日】** → upd_jiken_c_t.tsv (sonzoku_kikan_manryo_bi), upd_mgt_info_t.tsv
- **【分納満了日】** → upd_jiken_c_t.tsv (bunno_manryo_bi)
- **【拒絶査定発送日】** → upd_jiken_c_t.tsv (kyozetu_satei_hasso_bi)
- **【最終処分日】** → upd_jiken_c_t.tsv (saishushobun_bi)
- **【更新申請日】** → upd_t_updt_art.tsv (koshin_shinsei_bi)
- **【更新登録日】** → upd_t_updt_art.tsv (koshin_toroku_bi)
- **【書換登録日】** → upd_mrgn_t_rwrt_app_num.tsv (kakikae_toroku_bi)

### ステータス関連
- **【法区分】** → upd_jiken_c_t.tsv (houkubun)
- **【分納識別】** → upd_jiken_c_t.tsv (bunno_shikibetsu)
- **【最終処分】** → upd_jiken_c_t.tsv (saishushobun)
- **【出願種別】** → upd_jiken_c_t.tsv (shutugan_shubetsu)

### 権利者・代理人関連
- **【出願人】** → upd_jiken_c_t_shutugannindairinin.tsv (shutugannindairinin_code + shutugannindairinin_simei, sikbt='1')
- **【住所】** → upd_jiken_c_t_shutugannindairinin.tsv (shutugannindairinin_jusho)
- **【代理人】** → upd_jiken_c_t_shutugannindairinin.tsv (sikbt='2'), upd_atty_art_t.tsv

### 商品・役務関連
- **【区分】** → upd_jiken_c_t_shohin_joho.tsv (rui)
- **類似群コード** → upd_t_knd_info_art_table.tsv (smlr_dsgn_group_cd)
- **商品・役務名** → upd_jiken_c_t_shohin_joho.tsv (shohinekimumeisho)

### 経過情報
- **【中間記録情報】** → upd_jiken_c_t_chonai_dv.tsv, upd_jiken_c_t_kian_dv.tsv, upd_jiken_c_t_sinsei_dv.tsv
- **【拒絶理由通知情報】** → upd_jiken_c_t_kian_dv.tsv (kyozetsu_riyujobun_code等)
- **【審判情報】** → upd_snpn_zkn.tsv
- **【異議申立情報】** → upd_ig_mustt.tsv
- **【審判詳細情報】** → upd_snpn_zkn.tsv等
- **【重複情報】** → upd_duplicate_t_doni.tsv

### 図形分類
- **【ウィーン図形分類】** → upd_t_vienna_class_grphc_term_art.tsv (vienna_code)
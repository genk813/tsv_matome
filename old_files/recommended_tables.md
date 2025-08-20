# TMCloud 推奨テーブル構成

## 基本方針
- 実際に存在するTSVファイルのみを使用
- データ量が多く、実用的な情報を含むものを優先
- 商標検索に必須の機能を網羅

## 必須テーブル（15個）

### 1. 商標基本情報
- **jiken_c_t** (16,688件) - 商標の基本情報

### 2. 商標テキスト（4種類）
- **standard_char_t_art** (15,110件) - 標準文字商標
- **indct_use_t_art** (31,692件) - 表示用商標
- **search_use_t_art_table** (40,961件) - 検索用商標
- **t_dsgnt_art** (83,960件) - 称呼

### 3. 商品・分類情報
- **jiken_c_t_shohin_joho** (266,213件) - 商品情報
- **goods_class_art** (30,582件) - 商品区分
- **t_knd_info_art_table** (64,404件) - 類似群コード

### 4. 権利者・出願人情報
- **right_person_art_t** (17,099件) - 権利者
- **jiken_c_t_shutugannindairinin** (37,019件) - 出願人代理人
- **appl_reg_info** (1,612件) - 申請人マスタ

### 5. その他重要情報
- **t_sample** (10,063件) - 商標画像
- **t_vienna_class_grphc_term_art** (100,370件) - Vienna分類
- **mgt_info_t** (16,896件) - 管理情報
- **jiken_c_t_yusenken_joho** (354件) - 優先権情報

## オプションテーブル（必要に応じて追加）

### 国際商標関連
- **intl_t_org_org_reg_mgt_info** (1,431件)
- **intl_t_org_prog_info** (5,739件)
- **intl_t_org_set_dsgn_gds_srvc** (2,280件)

### 代理人関連
- **atty_art_t** (16,966件) - 代理人記事

### その他
- **jiken_c_t_kian_dv** (16,797件) - 起案デバイス
- **jiken_c_t_sinsei_dv** (32,911件) - 申請デバイス

## 不要と判断したテーブル

以下は存在しないか、データが少ないため除外：
- dsgnt_arr_ctgrs_art（TSVなし）
- exhibit_priority_right_article_t（TSVなし）
- int_class_result_art_table（TSVなし）
- jiken_applicant_article_t（TSVなし）
- retrospective_class_article_t（TSVなし）
- rps_class_article_t（TSVなし）
- t_dsgnt_similar_code_art（TSVなし）
- t_knd_dsgn_article_table（TSVなし）
- t_knd_group_article_table（TSVなし）

## 推奨構成
実用的な商標検索システムとして、**15個の必須テーブル**があれば十分機能します。
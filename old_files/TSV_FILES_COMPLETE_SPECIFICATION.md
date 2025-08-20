# TMCloud TSVファイル完全仕様書

## 概要
- 総ファイル数: 82ファイル
- データソース: 日本特許庁商標データ
- エンコーディング: UTF-8
- 区切り文字: タブ（\t）

### コミュニケーションスタイル
- ユーザーとは優しい同級生を意識したタメ口で話す
- 技術的な内容も分かりやすく、親しみやすい口調で説明する
- 「〜だよ」「〜だね」「〜してみるね」などの表現を使う

## カテゴリ別ファイル数
- core_trademark: 9ファイル
- trademark_text: 5ファイル
- classification: 5ファイル
- applicant_agent: 4ファイル
- international: 5ファイル
- priority: 0ファイル
- status_management: 8ファイル
- other: 46ファイル

## 主要キーカラム保有ファイル
- app_numを持つファイル: 22個
- shutugan_noを持つファイル: 10個

## 各TSVファイルの詳細仕様

### 1. del_snpn_zkn.tsv
**カテゴリ**: other
**カラム数**: 15
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_201_審判事件ファイル.csv
**データ状況**: 実質1行のみ（審判番号のみ）、14カラムが空欄
**推奨**: スキップ（削除対象リストのみ）
**インポート対象**: ❌
**主要キーカラム**: snpn_bngu

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| skbt_flg | 識別フラグ | フラグ、全行で空 |
| snpn_bngu | 審判番号 | 主キー、唯一データあり |
| sytgn_bngu | 出願番号 | 全行で空 |
| ynpu_kbn | 四法区分 | 全行で空 |
| turk_bngu | 登録番号 | 全行で空 |
| bnkt_bngu | 分割番号 | 全行で空 |
| riz_bngu | 類似番号 | 全行で空 |
| bug_bngu | 防護番号 | 全行で空 |
| snkyu_sybt | 審級種別 | 全行で空 |
| snpn_sybt | 審判種別 | 全行で空 |
| snpn_sikyu_dt | 審判請求日 | 日付型、全行で空 |
| sytgn_bngu_kbn | 出願番号区分 | 全行で空 |
| snpn_zkn_sisyu_sybn_cd | 審判事件最終処分コード | コード、全行で空 |
| sisyu_sybn_kkti_dt | 最終処分確定日 | 日付型、全行で空 |
| kusn_ntz_bat | 更新日時 | 全行で空 |

### 2. del_t_basic_item_art.tsv
**カテゴリ**: other
**カラム数**: 30
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_154_商標基本項目記事ファイル.csv
**データ状況**: 実質2行のみ、27カラムが空欄
**推奨**: スキップ（削除対象リストのみ）
**インポート対象**: ❌
**主要キーカラム**: mgt_num

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| add_del_id | 追加削除識別 | 両行とも「1」 |
| mgt_num | 管理番号 | 主キー、両行とも「0」 |
| rec_status_id | レコード状態識別 | 全行で空 |
| app_num | 出願番号 | データあり |
| reg_num | 登録番号 | 全行で空 |
| split_num | 分割番号 | 全行で空 |
| sec_num | 防護番号 | 全行で空 |
| app_typ_sec | 出願種別防護 | 全行で空 |
| app_typ_split | 出願種別分割 | 全行で空 |
| app_typ_complement_rjct | 出願種別補却 | 全行で空 |
| app_typ_chan | 出願種別変更 | 全行で空 |
| app_typ_priorty | 出願種別優先 | 全行で空 |
| app_typ_group | 出願種別団体 | 全行で空 |
| app_typ_area_group | 出願種別地域団体 | 全行で空 |
| app_dt | 出願日 | 日付型、全行で空 |
| prior_app_right_occr_dt | 先願権発生日 | 日付型、全行で空 |
| rjct_finl_dcsn_dsptch_dt | 拒絶査定発送日 | 日付型、全行で空 |
| final_dspst_cd | 最終処分コード | コード、全行で空 |
| final_dspst_dt | 最終処分日 | 日付型、全行で空 |
| rwrt_app_num | 書換申請番号 | 全行で空 |
| old_law | 旧法類 | 全行で空 |
| ver_num | 版コード | 全行で空 |
| intl_reg_num | 国際登録番号 | 全行で空 |
| intl_reg_split_num | 国際登録分割番号 | 全行で空 |
| intl_reg_dt | 国際登録日 | 日付型、全行で空 |
| rec_latest_updt_dt | レコード最新更新日 | 日付型、全行で空 |
| conti_prd_expire_dt | 存続期間満了日 | 日付型、全行で空 |
| instllmnt_expr_dt_aft_des_dt | 分納満了日／事後指定日 | 日付型、全行で空 |
| installments_id | 分納識別 | 全行で空 |
| set_reg_dt | 設定登録日 | 日付型、全行で空 |

### 3. upd_aki_uktk_syri_syri_dt_ar.tsv
**カテゴリ**: status_management
**カラム数**: 27
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_202_受付書類ファイル.csv
**データ状況**: 実データあり（100行以上）、審判関連の受付書類データ
**推奨**: 必要（審判の進行状況追跡）
**インポート対象**: ○
**主要キーカラム**: uktk_syri_bngu

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| skbt_flg | 識別フラグ | 全行「0」 |
| uktk_syri_bngu | 受付書類番号 | 主キー、11桁 |
| snpn_bngu | 審判番号 | 年＋連番形式 |
| tyukn_cd | 中間コード | A51,A821,A523等 |
| syri_ssds_dt | 書類差出日 | 日付型、データあり |
| syri_uktk_dt | 書類受付日 | 日付型、データあり |
| sri_kykr_kbn | 指令・却理区分 | 全行「1」 |
| husk_sybn_stat | 方式処分ステータス | 全行「1」 |
| hssu_syri_bngu | 発送書類番号 | 一部のみデータ |
| sir_bngu | 整理番号 | 全行で空 |
| syri_sybt_cd | 書類種別コード | 全行「1」 |
| syri_bnri_cd | 書類分類コード | A151,A1821等 |
| yuku_flg | 有効フラグ | 全行「0」 |
| tiou_mk | 対応マーク | 全行で空 |
| etrn_kns_flg | 閲覧禁止フラグ | 全行「0」 |
| hnku_tisyu_sytgnnn_dirnn_cd | 変更対象出願人・代理人コード | 全行で空 |
| yusnkn_tisytkk_cd | 優先権提出国コード | 全行で空 |
| syri_ztti_rrk_bngu | 書類実体履歴番号 | 全行「0」 |
| misisy_ver | 明細書バージョン | 全行で空 |
| mkug_syri_um | 無効後書類有無 | 全行で空 |
| syri_fomt_sybt | 書類フォーマット種別 | 全行で空 |
| tksk_bngu | 蓄積番号 | 全行で空 |
| dna_hirthyu_um | DNA配列表有無 | 全行で空 |
| yuyksy_tnp_syri_sikyu_hni_um | 要約書、添付書類、請求の範囲の有無 | 全行で空 |
| tnp_syri_pagesu | 添付書類頁数 | 全行「0」 |
| syri_siz | 書類サイズ | 全行「0」 |
| kusn_ntz_bat | 更新日時 | 全行同じ日時 |

### 4. upd_appl_reg_info.tsv
**カテゴリ**: applicant_agent
**カラム数**: 10
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_055_申請人登録情報ファイル.csv
**データ状況**: 実データ豊富（国内外の申請人マスタデータ）
**推奨**: 必須（申請人名表示に必要）
**インポート対象**: ○
**主要キーカラム**: appl_cd

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| data_id_cd | データ識別コード | 全行「520010」 |
| appl_cd | 申請人コード | 主キー、9桁 |
| appl_name | 申請人氏名 | 日本語/英語/中国語等 |
| appl_cana_name | 申請人カナ氏名 | 日本の申請人のみ |
| appl_postcode | 申請人郵便番号 | 日本の住所のみ |
| appl_addr | 申請人住所 | 国内外の住所 |
| wes_join_name | 欧文併記氏名 | 一部データあり |
| wes_join_addr | 欧文併記住所 | 多くは「（省略）」 |
| integ_appl_cd | 統合申請人コード | ほとんど空 |
| dbl_reg_integ_mgt_srl_num | 二重登録統合管理通番 | 数値型、ほぼ「0」 |

### 5. upd_atty_art_t.tsv
**カテゴリ**: applicant_agent
**カラム数**: 12
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_125_代理人記事ファイル(商標).csv
**データ状況**: 実データ豊富（登録番号ベースの代理人情報）
**推奨**: 必須（登録商標の代理人表示に必要）
**インポート対象**: ○
**主要キーカラム**: law_cd, reg_num, split_num, app_num, rec_num, pe_num

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| processing_type | 処理種別 | 全行「0」 |
| law_cd | 四法コード | 主キー、全行「4」（商標） |
| reg_num | 登録番号 | 主キー、7桁 |
| split_num | 分割番号 | 主キー、全行31桁の0 |
| app_num | 出願番号 | 主キー、全行「0000000000」 |
| rec_num | レコード番号 | 主キー、代理人情報の版数（現在は全て00） |
| pe_num | PE番号 | 主キー、同一商標内の代理人順序（000が筆頭代理人） |
| atty_art_upd_ymd | 代理人記事部作成更新年月日 | 日付型、YYYYMMDD |
| atty_appl_id | 代理人申請人ID | 9桁の代理人ID |
| atty_typ | 代理人種別 | 全行「1」 |
| atty_name_len | 代理人氏名レングス | 氏名の長さ |
| atty_name | 代理人氏名 | 弁理士名・事務所名 |

### 6. upd_design_state_gvrnmnt_mstr_mk.tsv
**カテゴリ**: international
**カラム数**: 29
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_168_指定国官庁マスタ_マークファイル.csv
**データ状況**: 実データあり（国際商標の図形・色彩・記述情報）

**データ内容の詳細**:
- **標準文字宣言フラグ**: 「1」なら文字のみの商標、「0」なら図形を含む商標
- **色彩主張**: 商標で権利を主張する色（例: "navy blue and white"→「紺色及び白」）
- **標章記述**: 商標の構成要素の説明（例: "CLA inside a circle"→「円の中のCLA」）
- **ウィーン分類**: 図形要素の国際分類コード
  - 07xx: 建築物・構造物
  - 26xx: 幾何学的図形（2601:円、2605:三角形など）
  - 27xx: 文字・数字
  - 29xx: 色彩
- **ディスクレーマー**: 商標の一部について独占権を放棄する宣言（例: "MAKEUP"や"DIGITAL ENGINEERING"の文字部分）
- **任意標章記述**: 追加の詳細説明（例: 文字の傾きや特殊な形状の説明）
**推奨**: インポート（国際商標の詳細情報）
**インポート対象**: ○
**主要キーカラム**: jpo_rfr_num, jpo_rfr_num_split_sign_cd, history_num, define_flg
| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| jpo_rfr_num | 庁内整理番号 | 主キー、年＋連番形式（例：2019000456） |
| jpo_rfr_num_split_sign_cd | 庁内整理番号分割記号コード | 主キー、商標が分割処理される場合の記号（例：A、B）。ほとんど空欄 |
| history_num | 履歴番号 | 主キー、更新履歴の番号。全て「0000」（初版または履歴管理なし） |
| standard_char_declarat_flg | 標準文字宣言フラグ | 0/1の値 |
| color_clim_detail | 色彩主張内容 | 英語の色彩説明（例："navy blue and white"） |
| color_clim_detail_japanese | 色彩主張内容の和訳 | 日本語の色彩説明（例：「紺色及び白」） |
| emblem_transliterat_detail | 標章音訳内容 | 商標の音訳（発音）情報、一部データあり |
| three_dmns_emblem_flg | 立体標章フラグ | 全行「0」 |
| sound_t_flg | 音商標フラグ | 全行「0」 |
| group_cert_warranty_flg | 団体証明保証フラグ | 全行「0」 |
| emblem_doc_detail | 標章記述内容 | 英語の標章説明（例："CLA inside a circle"） |
| emblem_doc_detail_japanese | 標章記述内容の和訳 | 日本語の標章説明（例：「円の中のCLA」） |
| vienna_class | ウィーン分類 | 図形要素の分類コード（例：2601=円、2705=文字） |
| exam_art_03_prgrph_02_flg | 審査３条２項有無フラグ | 全行「0」 |
| exam_color_proviso_apply_flg | 審査色彩の但し書適用フラグ | 全行「0」 |
| exam_art_09_prgrph_01_flg | 審査９条１項有無フラグ | 全行「0」 |
| acclrtd_exam_class | 早期審査区分 | 全行「0」 |
| define_flg | 確定フラグ | 主キー、データ確定状態（1=確定済み）。全て「1」 |
| updt_year_month_day | 更新年月日 | 日付型、YYYYMMDD |
| batch_updt_year_month_day | バッチ更新年月日 | バッチプログラムによる更新年月日 |
| special_t_typ | 特殊商標のタイプ | 全行空 |
| t_dtl_explntn | 商標の詳細な説明 | 全行空 |
| t_dtl_explntn_japanese | 商標の詳細な説明の和訳 | 全行空 |
| dtl_explntn_doc_submt_dt | 詳細な説明の書類提出日 | 全行空 |
| color_chk_box | 色彩のチェックボックス | 全行空 |
| disclaimer | ディスクレーマー | 英語の権利放棄部分（例："No claim to MAKEUP"） |
| opt_emblem_doc_detail | 任意標章記述内容 | 英語の追加説明 |
| opt_emblem_doc_detail_jp | 任意標章記述内容の和訳 | 日本語の追加説明 |

### 7. upd_design_state_gvrnmnt_mstr_pri.tsv
**カテゴリ**: international
**カラム数**: 12
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_167_指定国官庁マスタ_優先権ファイル.csv
**データ状況**: 2357行、国際商標の優先権主張情報
**推奨**: 必要（国際商標の優先権情報）
**インポート対象**: ○
**主要キーカラム**: jpo_rfr_num, jpo_rfr_num_split_sign_cd, history_num, pri_clim_id, define_flg

| カラム名 | 日本語説明 | 備考 |
|---------|------------|------|
| jpo_rfr_num | 庁内整理番号 | 主キー、年＋連番 |
| jpo_rfr_num_split_sign_cd | 庁内整理番号分割記号コード | 主キー、一部「A」 |
| history_num | 履歴番号 | 主キー、全行「0000」 |
| pri_clim_id | 優先権主張識別番号 | 主キー、数値型（1,2,3...） |
| pri_app_gvrn_cntrcntry_cd | 優先権出願官庁締約国等コード | 2文字国コード（FR,CH,EM,US,CA,DE等） |
| pri_app_num | 優先権出願番号 | 最初の出願番号 |
| pri_app_year_month_day | 優先権出願年月日 | 日付型、YYYYMMDD |
| define_flg | 確定フラグ | 主キー、全行「1」 |
| updt_year_month_day | 更新年月日 | システム操作者による更新年月日 |

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| add_del_id | 追加削除識別 | 全行「0」 |
| jpo_rfr_num | 庁内整理番号 | 主キー、年＋連番 |
| jpo_rfr_num_split_sign_cd | 庁内整理番号分割記号コード | 主キー、一部「A」 |
| history_num | 履歴番号 | 主キー、全行「0000」 |
| pri_clim_id | 優先権主張識別番号 | 主キー、数値型（1,2,3...） |
| pri_finding_flg | 優先権認定フラグ | 全行「0」 |
| pri_app_gvrn_cntrcntry_cd | 優先権出願官庁締約国等コード | 2文字国コード（FR,CH,EM,US,CA,DE等） |
| pri_app_num | 優先権出願番号 | 最初の出願番号 |
| pri_app_year_month_day | 優先権出願年月日 | 日付型、YYYYMMDD |
| define_flg | 確定フラグ | 主キー、全行「1」 |
| updt_year_month_day | 更新年月日 | システム操作者による更新年月日 |
| batch_updt_year_month_day | バッチ更新年月日 | バッチプログラムによる更新年月日 |

### 8. upd_duplicate_t_doni.tsv
**カテゴリ**: registration
**カラム数**: 8
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_118_重複商標番号記事ファイル.csv
**データ状況**: 52行、重複商標番号の情報
**推奨**: スキップ（データ量少なく特殊ケース）
**インポート対象**: ❌
**主要キーカラム**: law_cd, reg_num, split_num, app_num, mu_num

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| processing_type | 処理種別 | 全行「0」 |
| law_cd | 四法コード | 主キー、全行「4」（商標法） |
| reg_num | 登録番号 | 主キー、7桁数字 |
| split_num | 分割番号 | 主キー、31桁（ほとんど0埋め） |
| app_num | 出願番号 | 主キー、10桁数字 |
| dpl_t_doni_upd_ymd | 重複商標番号記事部作成更新年月日 | YYYYMMDD形式 |
| mu_num | ＭＵ番号 | 主キー、重複商標の連番（000,001,002...） |
| duplicate_t_reg_split_num | 重複商標登録分割番号 | 登録番号＋分割番号（17桁） |

### 9. upd_goods_class_art.tsv
**カテゴリ**: classification
**カラム数**: 8
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_117_商品区分記事ファイル.csv
**データ状況**: 30,583行、商品・役務区分情報
**推奨**: 必須（商標の区分検索）
**インポート対象**: ○
**主要キーカラム**: law_cd, reg_num, split_num, app_num, mu_num

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| processing_type | 処理種別 | 全行「0」 |
| law_cd | 四法コード | 主キー、全行「4」（商標法） |
| reg_num | 登録番号 | 主キー、7桁数字 |
| split_num | 分割番号 | 主キー、31桁（ほとんど0埋め） |
| app_num | 出願番号 | 主キー、10桁数字 |
| goods_cls_art_upd_ymd | 商品区分記事部作成更新年月日 | YYYYMMDD形式 |
| mu_num | ＭＵ番号 | 主キー、区分の連番（000,001,002...） |
| desig_goods_or_desig_wrk_class | 指定商品又は指定役務の区分 | 2桁数字（01～45類） |

### 10. upd_gugkn.tsv
**カテゴリ**: tribunal
**カラム数**: 5
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_224_合議官ファイル.csv
**データ状況**: 6,010行、審判合議官情報
**推奨**: スキップ（商標検索には不要）
**インポート対象**: ❌
**主要キーカラム**: snpn_bngu, krkes_bngu

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| skbt_flg | 識別フラグ | 全行「0」 |
| snpn_bngu | 審判番号 | 主キー、10桁数字 |
| krkes_bngu | 繰返番号 | 主キー、合議官の順番（1,2,3...） |
| gugkn_cd | 合議官コード | 4桁の審判官ID |
| kusn_ntz_bat | 更新日時 | YYYYMMDDhhmmss形式 |

### 11. upd_h_tkky_bnkn_suh.tsv
**カテゴリ**: other
**カラム数**: 4
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_206_非特許文献送付ファイル.csv
**データ状況**: 151行、非特許文献の送付管理データ
**推奨**: スキップ（商標検索システムには不要）
**インポート対象**: ❌
**主要キーカラム**: hssu_syri_bngu

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| skbt_flg | 識別フラグ | 全行「0」固定 |
| hssu_syri_bngu | 発送書類番号 | 主キー、11桁の書類番号（07で始まる） |
| suh_tisyu_hssu_syri_bngu | 送付対象発送書類番号 | 関連する発送書類番号、1対多の関係 |
| kusn_ntz_bat | 更新日時 | YYYYMMDDhhmmss形式、時刻は全て000000 |

### 12. upd_h_tkky_snku_bnkn.tsv
**カテゴリ**: other
**カラム数**: 5
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_244_非特許参考文献ファイル.csv
**データ状況**: 126行（ヘッダ含む）、審判事件の非特許参考文献データ
**推奨**: スキップ（商標検索システムには不要、審判専用データ）
**インポート対象**: ❌
**主要キーカラム**: snpn_bngu, krkes_bngu

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| skbt_flg | 識別フラグ | 全行「0」固定 |
| snpn_bngu | 審判番号 | 主キー、10桁（年＋連番形式） |
| krkes_bngu | 繰返番号 | 主キー、参考文献の順序（1,2,3...最大9） |
| h_tkky_snku_bnknmi | 非特許参考文献名 | 論文誌、特許公報、書籍等の引用文献情報 |
| kusn_ntz_bat | 更新日時 | YYYYMMDDhhmmss形式、時刻は全て000000 |

### 13. upd_higu_snpn_zkn.tsv
**カテゴリ**: other
**カラム数**: 6
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_223_併合審判事件ファイル.csv
**データ状況**: 9行（ヘッダ含む）、併合審判事件の関連データ
**推奨**: スキップ（商標検索システムには不要、審判専用データ）
**インポート対象**: ❌
**主要キーカラム**: snpn_bngu, krkes_bngu

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| skbt_flg | 識別フラグ | 全行「0」固定 |
| snpn_bngu | 審判番号 | 主キー、10桁（2024800082等） |
| krkes_bngu | 繰返番号 | 主キー、併合関係の順序（1,2） |
| knrn_snpn_bngu | 関連審判番号 | 併合される審判番号 |
| higu_kij_flg | 併合解除フラグ | 全行「1」（併合解除済み？） |
| kusn_ntz_bat | 更新日時 | YYYYMMDDhhmmss形式、時刻は全て000000 |

### 14. upd_hnkt_bnri.tsv
**カテゴリ**: other
**カラム数**: 14
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_231_判決分類ファイル.csv
**データ状況**: 45行（ヘッダ含む）、審判事件の判決分類データ
**推奨**: スキップ（商標検索システムには不要、裁判・審判専用データ）
**インポート対象**: ❌
**主要キーカラム**: sibnsy_cd, zkn_krk_hgu_cd, zkn_bngu, ssyu_kbn, krkes_bngu

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| skbt_flg | 識別フラグ | 全行「0」固定 |
| sibnsy_cd | 裁判所コード | 主キー、5桁（31200=知財高裁？） |
| zkn_krk_hgu_cd | 事件記録符号コード | 主キー、3桁（001） |
| zkn_bngu | 事件番号 | 主キー、9桁（例：202410105） |
| ssyu_kbn | 訴訟区分 | 主キー、1桁（1,3） |
| krkes_bngu | 繰返番号 | 主キー、判決内容の順序（1～7） |
| ynpu_kbn | 四法区分 | 1=特許、4=商標 |
| snkyu_sybt | 審級種別 | 3,4（上訴審の種類） |
| snpn_sybt | 審判種別 | 3桁のコード（113,123,80等） |
| hnz_zku_cd | 判示事項コード | 3桁のコード（121,841等） |
| hnkt_bnri_ktrn_cd | 判決分類結論コード | 技術分野コード（G06F,H04N等） |
| hj_bnri_skbt | 補助分類識別 | ほとんど空欄 |
| syum_skbt | 訟務識別 | ほとんど空欄 |
| kusn_ntz_bat | 更新日時 | YYYYMMDDhhmmss形式 |

### 15. upd_hssu_syri.tsv
**カテゴリ**: status_management
**カラム数**: 17
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_203_発送書類ファイル.csv
**データ状況**: 15,350行、審判事件の発送書類管理データ
**推奨**: 必須（JPlatPatへのリンク構築に必要）
**主要キーカラム**: hssu_syri_bngu
**インポート対象**: ○

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| skbt_flg | 識別フラグ | 全行「0」固定 |
| hssu_syri_bngu | 発送書類番号 | 主キー、11桁の書類番号 |
| snpn_bngu | 審判番号 | 10桁（例：2018800031） |
| tyukn_cd | 中間コード | 書類種別コード（C20,C22,C03等） |
| gnsyri_bngu | 原書類番号 | 関連書類番号、多くは空欄 |
| syri_hssu_dt | 書類発送日 | YYYYMMDD形式 |
| atsk_sybt | 宛先種別 | 1(66%)、2(22%)、4(9%)、9(2%)、3(少数)。推測：1=請求人、2=被請求人 |
| ig_tuzsy_bngu | 異議当事者番号 | 異議申立の場合の当事者番号（001等）、通常は空欄 |
| snk_snsi_bngu | 参加申請番号 | 参加申請がある場合の番号、ほぼ空欄 |
| uktk_syri_bngu | 受付書類番号 | 関連する受付書類番号（11桁） |
| kan_dt | 起案日 | YYYYMMDD形式、発送日の数日前 |
| yuku_flg | 有効フラグ | 全行「0」（おそらく0=有効、1=無効） |
| tiou_mk | 対応マーク | 98%空欄、A(1.8%)、B,C,D(少数)。意味不明 |
| etrn_kns_flg | 閲覧禁止フラグ | 0=閲覧可、1=閲覧禁止 |
| syri_ztti_rrk_bngu | 書類実体履歴番号 | 数値型、多くは0または1 |
| syri_fomt_sybt | 書類フォーマット種別 | ほとんど空欄 |
| kusn_ntz_bat | 更新日時 | YYYYMMDDhhmmss形式 |

### 16. upd_ig_ktti.tsv
**カテゴリ**: status_management
**カラム数**: 7
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_219_異議決定ファイル.csv
**データ状況**: 55行、商標登録への異議申立決定データ
**推奨**: 必要（異議申立の決定情報）
**主要キーカラム**: snpn_bngu, mustt_bngu, ig_ktti_bngu（複合主キー）
**インポート対象**: ○

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| skbt_flg | 識別フラグ | 1桁（半角文字列）、全て「0」 |
| snpn_bngu | 審判番号 | 10桁（半角文字列）、主キー、例：2024700611 |
| mustt_bngu | 申立番号 | 3桁（半角文字列）、主キー、連番（001〜003等） |
| ig_ktti_bngu | 異議決定番号 | 2桁（半角文字列）、主キー、全て「01」 |
| hssu_syri_bngu | 発送書類番号 | 11桁（半角文字列）、例：07124114752 |
| ig_ktti_kkti_stat | 異議決定確定ステータス | 2桁（半角文字列）、「01」または空白 |
| kusn_ntz_bat | 更新日時 | 14桁（半角文字列）、YYYYMMDDHHMMSS形式 |

### 17. upd_ig_ktti_bnri.tsv
**カテゴリ**: status_management
**カラム数**: 13
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_220_異議決定分類ファイル.csv
**データ状況**: 129行、異議決定の分類情報（特許・商標両方含む）
**推奨**: スキップ（18番の異議申立ファイルで基本情報は網羅可能）
**インポート対象**: ❌
**主要キーカラム**: snpn_bngu, mustt_bngu, ig_ktti_bngu, krkes_bngu（複合主キー）

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| skbt_flg | 識別フラグ | 1桁（半角文字列）、0=有効、1=削除 |
| snpn_bngu | 審判番号 | 10桁（半角文字列）、主キー、例：2024700611 |
| mustt_bngu | 申立番号 | 3桁（半角文字列）、主キー、例：001 |
| ig_ktti_bngu | 異議決定番号 | 2桁（半角文字列）、主キー、例：01 |
| krkes_bngu | 繰返番号 | 4桁（数値型）、主キー、連番（1,2,3...） |
| ynpu_kbn | 四法区分 | 1桁（半角文字列）、1=特許、4=商標 |
| tkyu_huk_skbt | 適用法規識別 | 1桁（半角文字列）、ほぼ空欄 |
| snkyu_sybt | 審級種別 | 1桁（半角文字列）、1=第一審、4=その他 |
| snpn_sybt | 審判種別 | 3桁（半角文字列）、651,652等のコード |
| hnz_zku_cd | 判示事項コード | 3桁（半角文字列）、113,121,537等 |
| ig_ktti_bnri_ktrn_cd | 異議決定分類結論コード | 3桁（半角文字列）、Y,ZC,ZDA,ZAA等 |
| hj_bnri_skbt | 補助分類識別 | 13桁（半角文字列）、技術分類(G06Q等)または商標分類(W07等) |
| kusn_ntz_bat | 更新日時 | 14桁（半角文字列）、YYYYMMDDHHMMSS形式 |

### 18. upd_ig_mustt.tsv
**カテゴリ**: status_management
**カラム数**: 7
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_218_異議申立ファイル.csv
**データ状況**: 344行、商標登録への異議申立データ
**推奨**: 必要（異議申立情報の管理）
**主要キーカラム**: snpn_bngu, mustt_bngu（複合主キー）
**インポート対象**: ○

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| skbt_flg | 識別フラグ | 1桁（半角文字列）、全て「0」 |
| snpn_bngu | 審判番号 | 10桁（半角文字列）、主キー、例：2024700611 |
| mustt_bngu | 申立番号 | 3桁（半角文字列）、主キー、連番（001〜004等） |
| ig_mustt_dt | 異議申立日 | 8桁（半角文字列）、YYYYMMDD形式 |
| ig_mustt_sisyu_sybn_cd | 異議申立最終処分コード | 2桁（半角文字列）、06,07,08等、多くは空欄 |
| sisyu_sybn_kkti_dt | 最終処分確定日 | 8桁（半角文字列）、YYYYMMDD形式、多くは空欄 |
| kusn_ntz_bat | 更新日時 | 14桁（半角文字列）、YYYYMMDDHHMMSS形式 |

### 19. upd_indct_use_t_art.tsv
**カテゴリ**: trademark_text
**カラム数**: 5
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_156_表示用商標記事ファイル.csv
**データ状況**: 31,692行、商標の表示用テキストデータ
**推奨**: 必要（商標の表示文字情報）
**主要キーカラム**: app_num, split_num, sub_data_num（複合主キー）
**インポート対象**: ○

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| add_del_id | 追加削除識別 | 1桁（半角文字列）、全て「0」 |
| app_num | 出願番号 | 10桁（半角文字列）、主キー |
| split_num | 分割番号 | 31桁（半角文字列）、主キー、ほぼ空欄 |
| sub_data_num | サブデータ番号 | 9桁（半角文字列）、主キー、初期値（NULL）固定 |
| indct_use_t | 表示用商標 | 256桁（全半角文字列）、商標テキスト |

### 20. upd_intl_t_org_org_reg_mgt_info.tsv
**カテゴリ**: international
**カラム数**: 16
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_177_国際商標登録原簿マスタ_原簿管理情報ファイル.csv
**データ状況**: 1,431行、国際商標登録の管理情報（国際登録番号、事後指定、設定登録など）
**推奨**: 参考情報として記載（国際商標を扱う場合は重要）
**インポート対象**: ○
**主要キーカラム**: intl_reg_num, intl_reg_num_updt_cnt_sign_cd, intl_reg_num_split_sign_cd, aft_desig_year_month_day

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| add_del_id | 追加削除識別 | フラグ、ほぼ全行で「0」 |
| intl_reg_num | 国際登録番号 | 主キー、国際登録番号の「連番」 |
| intl_reg_num_updt_cnt_sign_cd | 国際登録番号更新回数記号コード | 主キー |
| intl_reg_num_split_sign_cd | 国際登録番号分割記号コード | 主キー、A,B,C,D等 |
| aft_desig_year_month_day | 事後指定年月日 | 主キー、YYYYMMDD形式 |
| intl_reg_year_month_day | 国際登録年月日 | YYYYMMDD形式 |
| jpo_rfr_num | 庁内整理番号 | 庁内整理番号の「西暦年＋連番」 |
| jpo_rfr_num_split_sign_cd | 庁内整理番号分割記号コード |  |
| set_reg_year_month_day | 設定登録年月日 | YYYYMMDD形式 |
| right_ersr_id | 本権利抹消識別 |  |
| right_disppr_year_month_day | 本権利消滅年月日 | YYYYMMDD形式 |
| close_reg_year_month_day | 閉鎖登録年月日 | YYYYMMDD形式 |
| inspct_prhbt_flg | 閲覧禁止フラグ | フラグ |
| define_flg | 確定フラグ | 主キー、フラグ |
| updt_year_month_day | 更新年月日 | システム操作者による更新年月日 |
| batch_updt_year_month_day | バッチ更新年月日 | バッチプログラムによる更新年月日 |

### 21. upd_intl_t_org_prog_info.tsv
**カテゴリ**: international
**カラム数**: 17
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_178_国際商標登録原簿マスタ_経過情報ファイル.csv
**データ状況**: 2,869行、国際商標登録の経過情報（中間コード、ステータスなど）
**推奨**: 参考情報として記載（国際商標の経過管理に必要）
**インポート対象**: ○
**主要キーカラム**: intl_reg_num, intl_reg_num_updt_cnt_sign_cd, intl_reg_num_split_sign_cd, aft_desig_year_month_day, intrmd_cd, string_num

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| add_del_id | 追加削除識別 | フラグ、ほぼ全行で「0」 |
| intl_reg_num | 国際登録番号 | 主キー、国際登録番号の「連番」 |
| intl_reg_num_updt_cnt_sign_cd | 国際登録番号更新回数記号コード | 主キー |
| intl_reg_num_split_sign_cd | 国際登録番号分割記号コード | 主キー |
| aft_desig_year_month_day | 事後指定年月日 | 主キー、YYYYMMDD形式 |
| intrmd_cd | 中間コード | 主キー、7桁コード（例：IB31400、R150） |
| string_num | 格納番号 | 主キー、000001〜の連番 |
| intrmd_dfn_1_dt | 中間定義１日付 | YYYYMMDD形式 |
| intrmd_dfn_2_dt | 中間定義２日付 | YYYYMMDD形式 |
| intrmd_dfn_3_dt | 中間定義３日付 | YYYYMMDD形式 |
| intrmd_dfn_4_dt | 中間定義４日付 | YYYYMMDD形式 |
| intrmd_dfn_5_dt | 中間定義５日付 | YYYYMMDD形式 |
| crrspnd_mk | 対応マーク |  |
| define_flg | 確定フラグ | 主キー、フラグ |
| stts | ステータス | 主キー、4桁 |
| updt_year_month_day | 更新年月日 | システム操作者による更新年月日 |
| batch_updt_year_month_day | バッチ更新年月日 | バッチプログラムによる更新年月日 |

### 22. upd_intl_t_org_set_crr_nm_addr.tsv
**カテゴリ**: international
**カラム数**: 13
**CSV仕槕書**: （別添3.3）ファイル仕槕書_1.13版_181_国際商標登録原簿マスタ_設定時名義人氏名・住所ファイル.csv
**データ状況**: 746行、国際商標登録の設定時名義人情報（名称、住所）
**推奨**: 必要（国際商標の名義人情報）
**インポート対象**: ○
**主要キーカラム**: intl_reg_num, intl_reg_num_updt_cnt_sign_cd, intl_reg_num_split_sign_cd, aft_desig_year_month_day, temp_principal_reg_id_flg, indct_seq, crrcter_input_seq_num

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| add_del_id | 追加削除識別 | フラグ、ほぼ全行で「0」 |
| intl_reg_num | 国際登録番号 | 主キー、国際登録番号の「連番」 |
| intl_reg_num_updt_cnt_sign_cd | 国際登録番号更新回数記号コード | 主キー |
| intl_reg_num_split_sign_cd | 国際登録番号分割記号コード | 主キー |
| aft_desig_year_month_day | 事後指定年月日 | 主キー、YYYYMMDD形式 |
| temp_principal_reg_id_flg | 仮・本登録識別フラグ | 主キー、フラグ |
| indct_seq | 表示順序 | 主キー、4桁 |
| crrcter_input_seq_num | 名義人入力順序番号 | 主キー、数値型4桁 |
| crrcter_name | 名義人名称 | 全半角文字列、最大1024桁 |
| crrcter_addr | 名義人住所 | 全半角文字列、最大432桁 |
| define_flg | 確定フラグ | 主キー、フラグ |
| updt_year_month_day | 更新年月日 | システム操作者による更新年月日 |
| batch_updt_year_month_day | バッチ更新年月日 | バッチプログラムによる更新年月日 |

### 23. upd_intl_t_org_set_dsgn_gds_srvc.tsv
**カテゴリ**: international
**カラム数**: 14
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_180_国際商標登録原簿マスタ_設定時指定国商品・サービスファイル.csv
**データ状況**: 2,280行、国際商標の設定時指定商品・役務情報（区分、商品名）
**推奨**: 参考情報として記載（国際商標の商品・役務情報として重要）
**インポート対象**: ○
**主要キーカラム**: intl_reg_num, intl_reg_num_updt_cnt_sign_cd, intl_reg_num_split_sign_cd, aft_desig_year_month_day, temp_principal_reg_id_flg, indct_seq, seq_num

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| add_del_id | 追加削除識別 | フラグ、全行で「0」 |
| intl_reg_num | 国際登録番号 | 主キー、国際登録番号の「連番」 |
| intl_reg_num_updt_cnt_sign_cd | 国際登録番号更新回数記号コード | 主キー |
| intl_reg_num_split_sign_cd | 国際登録番号分割記号コード | 主キー |
| aft_desig_year_month_day | 事後指定年月日 | 主キー、YYYYMMDD形式 |
| temp_principal_reg_id_flg | 仮・本登録識別フラグ | 主キー、フラグ、全行で「1」 |
| indct_seq | 表示順序 | 主キー、4桁、グループ単位の表示順序（ほぼ全て0001） |
| seq_num | 順序番号 | 主キー、数値型4桁、グループ内での個別商品・役務の順番 |
| madopro_class | 区分 | 2桁、商品・役務の分類（01〜45） |
| goods_service_name | 商品サービス名 | 全半角文字列、最大8000桁、英語表記 |
| intl_reg_rec_dt | 国際登録記録日 | YYYYMMDD形式 |
| define_flg | 確定フラグ | フラグ、全行で「1」 |
| updt_year_month_day | 更新年月日 | システム操作者による更新年月日 |
| batch_updt_year_month_day | バッチ更新年月日 | バッチプログラムによる更新年月日 |

### 24. upd_intl_t_org_set_frst_indct.tsv
**カテゴリ**: international
**カラム数**: 18
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_179_国際商標登録原簿マスタ_設定時第一表示部ファイル.csv
**データ状況**: 1,339行、国際商標の設定時第一表示部情報（査定日、優先権など）
**推奨**: 参考情報として記載（国際商標の基本情報として参考になる）
**インポート対象**: ○
**主要キーカラム**: intl_reg_num, intl_reg_num_updt_cnt_sign_cd, intl_reg_num_split_sign_cd, aft_desig_year_month_day, temp_principal_reg_id_flg, indct_seq

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| add_del_id | 追加削除識別 | フラグ、全行で「0」 |
| intl_reg_num | 国際登録番号 | 主キー、国際登録番号の「連番」 |
| intl_reg_num_updt_cnt_sign_cd | 国際登録番号更新回数記号コード | 主キー |
| intl_reg_num_split_sign_cd | 国際登録番号分割記号コード | 主キー |
| aft_desig_year_month_day | 事後指定年月日 | 主キー、YYYYMMDD形式 |
| temp_principal_reg_id_flg | 仮・本登録識別フラグ | 主キー、フラグ、全行で「1」 |
| indct_seq | 表示順序 | 主キー、4桁、全行で「0001」 |
| finl_dcsn_year_month_day | 査定年月日 | YYYYMMDD形式 |
| trial_dcsn_year_month_day | 審決年月日 | YYYYMMDD形式、ほぼ空欄 |
| pri_app_gvrn_cntrcntry_cd | 優先権出願官庁締約国等コード | 2桁国コード（CH、EM、US等） |
| pri_app_year_month_day | 優先権出願年月日 | YYYYMMDD形式 |
| pri_clim_cnt | 優先権主張件数 | 3桁、000〜006 |
| special_t_typ_flg | 特殊商標のタイプフラグ | フラグ、ほぼ「0」（5件のみ「1」） |
| group_cert_warranty_flg | 団体証明保証フラグ | フラグ、ほぼ「0」（1件のみ「1」） |
| define_flg | 確定フラグ | フラグ、全行で「1」 |
| updt_year_month_day | 更新年月日 | システム操作者による更新年月日 |
| batch_updt_year_month_day | バッチ更新年月日 | バッチプログラムによる更新年月日 |
| t_dtl_explntn | 商標の詳細な説明 | 全半角文字列、最大4000桁、全て空欄 |

### 25. upd_jiken_c_t.tsv
**カテゴリ**: core_trademark
**カラム数**: 49
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_042_事件フォルダ_商標ファイル.csv
**データ状況**: 16,688行、商標出願の基本情報（出願日、最終処分、登録番号など）
**推奨**: 必須（商標検索システムの中核となる基本情報）
**インポート対象**: ○
**主要キーカラム**: yonpo_code, shutugan_no

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| masterkosin_nitiji | マスタ更新日時 | YYYYMMDDHHmmss形式 |
| yonpo_code | 四法コード | 主キー、「4」（商標）固定 |
| shutugan_no | 出願番号 | 主キー、10桁 |
| shutugan_bi | 出願日 | YYYYMMDD形式 |
| shutugan_shubetu1 | 出願種別１ | 01（通常出願）が99.5% |
| shutugan_shubetu2 | 出願種別２ |  |
| shutugan_shubetu3 | 出願種別３ |  |
| shutugan_shubetu4 | 出願種別４ |  |
| shutugan_shubetu5 | 出願種別５ |  |
| seiri_no | 整理番号 |  |
| saishushobun_shubetu | 最終処分種別 | A01（登録査定）が27%、空欄が70% |
| saishushobun_bi | 最終処分日 | YYYYMMDD形式 |
| raz_toroku_no | 登録記事登録番号 | 登録された案件のみ（4,557件/16,688件） |
| raz_bunkatu_no | 登録記事分割番号 | 31桁 |
| bogo_no | 防護番号 | 3桁、防護標章の番号 |
| toroku_bi | 登録日 | YYYYMMDD形式 |
| raz_sotugo_su | 登録記事総通号数 | 6桁、公報の通し番号 |
| raz_nenkantugo_su | 登録記事年間通号数 | 6桁、年内の通し番号 |
| raz_kohohakko_bi | 登録記事公報発行日 | YYYYMMDD形式 |
| tantokan_code | 担当官コード | 4桁、審査担当者コード |
| pcz_kokaikohohakko_bi | 公開公報記事公開公報発行日 | YYYYMMDD形式 |
| kubun_su | 区分数 | 3桁、商品・役務の区分数 |
| torokusateijikubun_su | 登録査定時区分数 | 3桁 |
| hyojunmoji_umu | 標準文字有無 | 1:標準文字商標 |
| rittaishohyo_umu | 特殊商標識別 | 1:立体商標等の特殊商標 |
| hyoshosikisai_umu | 標章色彩有無 | 1:色彩付き |
| shohyoho3jo2ko_flag | 商標法３条２項フラグ | 使用による識別力取得 |
| shohyoho5jo4ko_flag | 色彩の但し書フラグ | 商標法5条4項適用 |
| genshutugan_shubetu | 原出願種別 | 分割・変更の元出願 |
| genshutuganyonpo_code | 原出願四法コード | 1桁 |
| genshutugan_no | 原出願番号 | 10桁 |
| sokyu_bi | 遡及日 | YYYYMMDD形式 |
| obz_shutugan_no | 防護原登録記事出願番号 | 防護標章の基礎出願 |
| obz_toroku_no | 防護原登録記事登録番号 | 防護標章の基礎登録 |
| obz_bunkatu_no | 防護原登録記事分割番号 | 31桁 |
| kosintoroku_no | 更新登録番号 | 7桁、商標権の更新 |
| pez_bunkatu_no | 更新登録記事分割番号 | 31桁 |
| pez_bogo_no | 更新登録記事防護番号 | 3桁 |
| kakikaetoroku_no | 書換登録番号 | 7桁、旧法からの書換 |
| ktz_bunkatu_no | 書換登録記事分割番号 | 31桁 |
| ktz_bogo_no | 書換登録記事防護番号 | 3桁 |
| krz_kojoryozokuihan_flag | 公序良俗違反フラグ | 1:公序良俗違反あり |
| sokisinsa_mark | 早期審査マーク | 1:早期審査対象 |
| tekiyohoki_kubun | 適用法規区分 | 1桁、適用される法律の区分 |
| sinsa_shubetu | 審査種別 | 2桁 |
| sosho_code | 訴訟コード | 1桁 |
| satei_shubetu | 査定種別 | 1桁 |
| igiken_su | 異議件数 | 2桁、異議申立の件数 |
| igiyuko_su | 異議有効数 | 2桁、有効な異議の数 |

### 26. upd_jiken_c_t_chonai_dv.tsv
**カテゴリ**: core_trademark
**カラム数**: 13
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_054_事件フォルダ_商標_庁内中間記録ファイル.csv
**データ状況**: 1,944行、商標出願の庁内中間記録（手続き書類、処理状況）
**推奨**: 参考情報として記載（審査経過の詳細が必要な場合）
**インポート対象**: ❌
**主要キーカラム**: yonpo_code, shutugan_no, folderbetusakusejnj_no

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| yonpo_code | 四法コード | 主キー、「4」（商標）固定 |
| shutugan_no | 出願番号 | 主キー、10桁 |
| folderbetusakusejnj_no | フォルダ別作成順序番号 | 主キー、4桁の連番 |
| sakusei_bi | 作成日 | YYYYMMDD形式 |
| chukanshorui_code | 中間書類コード | 7桁、A971005が最多（56%） |
| taio_mark | 対応マーク | 2桁、ほぼ空欄 |
| chonaishoruisakusei_bi | 庁内書類作成日 | YYYYMMDD形式 |
| gyohuku_no | 行服番号 | 9桁、行政不服審査関連 |
| shusso_no | 出訴番号 | 7桁、訴訟関連 |
| shorui_no | 書類番号 | 11桁 |
| shorui_shubetu | 書類種別 | 1桁 |
| teiseitaishoshorui_no | 訂正対象書類番号 | 11桁、訂正書類の元番号 |
| version_no | バージョン番号 | 4桁 |

### 27. upd_jiken_c_t_kian_dv.tsv
**カテゴリ**: core_trademark
**カラム数**: 14
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_053_事件フォルダ_商標_起案中間記録ファイル.csv
**データ状況**: 16,797行、商標審査の起案記録（拒絶理由通知、登録査定など）
**推奨**: 推奨（審査経過の把握に重要）
**インポート対象**: ○
**主要キーカラム**: yonpo_code, shutugan_no, folderbetusakusejnj_no

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| yonpo_code | 四法コード | 主キー、「4」（商標）固定 |
| shutugan_no | 出願番号 | 主キー、10桁 |
| folderbetusakusejnj_no | フォルダ別作成順序番号 | 主キー、4桁の連番 |
| sakusei_bi | 作成日 | YYYYMMDD形式 |
| chukanshorui_code | 中間書類コード | 7桁、A01（登録査定）46%、A131（拒絶理由）33% |
| taio_mark | 対応マーク | 2桁、ほぼ空欄 |
| kian_bi | 起案日 | YYYYMMDD形式、審査官が起案した日 |
| hasso_bi | 発送日 | YYYYMMDD形式、書類を発送した日 |
| aaz_igi_no | 異議番号 | 2桁、異議申立関連 |
| shorui_no | 書類番号 | 11桁 |
| kyozeturiyujobun_code | 拒絶理由条文コード | 2桁、41（第4条1項）が最多 |
| taioshorui_no | 対応書類番号 | 11桁、対応する書類の番号 |
| shorui_shubetu | 書類種別 | 1桁 |
| version_no | バージョン番号 | 4桁 |

### 28. upd_jiken_c_t_kohohako_joho.tsv
**カテゴリ**: core_trademark
**カラム数**: 10
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_043_事件フォルダ_商標_公報発行情報ファイル.csv
**データ状況**: 2333行、商標公報発行情報（発行日、通号数等）
**推奨**: インポート（公報発行日や通号数の参照に有用）
**インポート対象**: ○
**主要キーカラム**: yonpo_code, shutugan_no, jaz_junjo_no

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| yonpo_code | 四法コード | 全行「4」（商標） |
| shutugan_no | 出願番号 | 主キー、10桁 |
| jaz_sotugo_su | 公報発行情報記事総通号数 | 6桁、例：000194 |
| jaz_nenkantugo_su | 公報発行情報記事年間通号数 | 6桁、例：030049 |
| jaz_bumonbetutugo_su | 部門別通号数 | ほとんど空欄 |
| jaz_bumonbetunenkantugo_su | 部門別年間通号数 | ほとんど空欄 |
| jaz_kohohakko_bi | 公報発行情報記事公報発行日 | YYYYMMDD形式 |
| jaz_seigo_sikibetu | 正誤識別 | 全行「00」 |
| jaz_koho_sikibetu | 公報発行情報記事公報識別 | 「4A010」等 |
| jaz_junjo_no | 公報発行情報記事順序番号 | 主キー、全行「1」 |

### 29. upd_jiken_c_t_old.tsv
**カテゴリ**: core_trademark
**カラム数**: 12
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_194_事件フォルダ_商標凍結ファイル.csv
**データ状況**: 78行、データはほぼ空（出願番号のみ）
**推奨**: スキップ（ほとんどのカラムが空欄、凍結ファイル）
**インポート対象**: ❌
**主要キーカラム**: yonpo_code, shutugan_no

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| yonpo_code | 四法コード | 全行「4」（商標） |
| shutugan_no | 出願番号 | 主キー、10桁 |
| kokoku_no | 公告番号 | 全行で空 |
| kokoku_bi | 公告日 | 日付型、全行で空 |
| paz_sotugo_su | 総通号数 | 全行で空 |
| paz_nenkantugo_su | 年間通号数 | 全行で空 |
| oaz_sotugo_su | 補正記事総通号数 | 全行で空 |
| oaz_nenkantugo_su | 補正記事年間通号数 | 全行で空 |
| oaz_bumonbetutugo_su | 補正記事部門別通号数 | 全行で空 |
| oaz_bumonbetunenkantugo_su | 補正記事部門別年間通号数 | 全行で空 |
| oaz_kohohakko_bi | 補正記事公報発行日 | 日付型、全行で空 |
| oaz_seigo_sikibetu | 補正記事正誤識別 | 全行で空 |

### 30. upd_jiken_c_t_shohin_joho.tsv
**カテゴリ**: classification
**カラム数**: 6
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_048_事件フォルダ_商標_商品情報ファイル.csv
**データ状況**: 33,386行、指定商品・役務の詳細情報
**推奨**: 必須（商品・役務の表示に必要）
**インポート対象**: ○
**主要キーカラム**: yonpo_code, shutugan_no, abz_junjo_no

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| yonpo_code | 四法コード | 全行「4」（商標） |
| shutugan_no | 出願番号 | 主キー、10桁 |
| rui | 類 | 2桁、区分（01-45） |
| lengthchoka_flag | レングス超過フラグ | 全行「0」 |
| shohinekimumeisho | 商品役務名称 | 最大5500文字、商品・役務の詳細 |
| abz_junjo_no | 商品情報記事順序番号 | 主キー、全行「1」 |

### 31. upd_jiken_c_t_shousaina_setumei.tsv
**カテゴリ**: core_trademark
**カラム数**: 6
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_049_事件フォルダ_商標_商標の詳細な説明情報ファイル.csv
**データ状況**: 18行、立体商標等の詳細説明
**推奨**: インポート（特殊商標の説明に有用）
**インポート対象**: ○
**主要キーカラム**: yonpo_code, shutugan_no, dtz_rireki_no

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| yonpo_code | 四法コード | 全行「4」（商標） |
| shutugan_no | 出願番号 | 主キー、10桁 |
| dtz_rireki_no | 商標の詳細な説明記事履歴番号 | 主キー、1-2の値 |
| dtz_sakusei_bi | 商標の詳細な説明記事作成日 | YYYYMMDD形式 |
| lengthchoka_flag | レングス超過フラグ | 全行「0」 |
| shohyonoshousaina_setumei | 商標の詳細な説明 | 立体商標の形状説明等、最大2000文字 |

### 32. upd_jiken_c_t_shutugannindairinin.tsv
**カテゴリ**: applicant_agent
**カラム数**: 15
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_047_事件フォルダ_商標_出願人代理人情報ファイル.csv
**データ状況**: 37,020行、出願人・代理人の情報（コードのみ、住所・氏名は「（省略）」）
**推奨**: 必須（出願人・代理人情報の表示に必要）
**インポート対象**: ○
**主要キーカラム**: yonpo_code, shutugan_no, gez_junjo_no

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| yonpo_code | 四法コード | 全行「4」（商標） |
| shutugan_no | 出願番号 | 主キー、10桁 |
| shutugannindairinin_sikbt | 出願人代理人識別 | 1=出願人、2=代理人 |
| shutugannindairinin_code | 出願人代理人コード | 9桁のコード |
| gez_henko_no | 出願人代理人記事変更番号 | ほとんど空欄 |
| gez_kohokan_kubun | 出願人代理人記事個法官区分 | ほとんど空欄 |
| gez_kokken_code | 出願人代理人記事国県コード | ほとんど空欄 |
| daihyoshutugannin_sikibetu | 代表出願人識別 | 0=通常、1=代表 |
| jokishutugannin_nanmei | 上記出願人何名 | 00,01等の数値 |
| dairininhoka_nanmei | 代理人外何名 | 00,01等の数値 |
| dairinin_shubetu | 代理人種別 | 1=弁理士等 |
| dairininsikaku_shubetu | 代理人資格種別 | ほとんど空欄 |
| shutugannindairinin_jusho | 出願人代理人住所 | 全行「（省略）」 |
| shutugannindairinin_simei | 出願人代理人氏名 | 全行空欄 |
| gez_junjo_no | 出願人代理人記事順序番号 | 主キー、連番 |

### 33. upd_jiken_c_t_sinsei_dv.tsv
**カテゴリ**: status_management
**カラム数**: 16
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_052_事件フォルダ_商標_申請中間記録ファイル.csv
**データ状況**: 32,912行、申請書類の中間記録情報
**推奨**: インポート（審査経過の把握に有用）
**インポート対象**: ○
**主要キーカラム**: yonpo_code, shutugan_no, folderbetusakusejnj_no

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| yonpo_code | 四法コード | 全行「4」（商標） |
| shutugan_no | 出願番号 | 主キー、10桁 |
| folderbetusakusejnj_no | フォルダ別作成順序番号 | 主キー、4桁連番 |
| sakusei_bi | 作成日 | YYYYMMDD形式 |
| chukanshorui_code | 中間書類コード | A63等のコード |
| taio_mark | 対応マーク | ほとんど空欄 |
| sasidasi_bi | 差出日 | YYYYMMDD形式 |
| uketuke_bi | 受付日 | YYYYMMDD形式 |
| aaz_igi_no | 異議番号 | ほとんど空欄 |
| shorui_no | 書類番号 | 11桁の番号 |
| hosikikan_mark | 方式完マーク | 0/1の値 |
| sireikan_flag | 指令完フラグ | ほとんど空欄 |
| taioshorui_no | 対応書類番号 | ほとんど空欄 |
| shorui_shubetu | 書類種別 | 1,8等の数値 |
| version_no | バージョン番号 | 0001,0002等 |
| eturankinsi_flag | 閲覧禁止フラグ | 全行「0」 |

### 34. upd_jiken_c_t_yusenken_joho.tsv
**カテゴリ**: priority
**カラム数**: 6
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_044_事件フォルダ_商標_優先権情報ファイル.csv
**データ状況**: 355行、優先権主張の情報
**推奨**: インポート（優先権情報の表示に有用）
**インポート対象**: ○
**主要キーカラム**: yonpo_code, shutugan_no, bmz_junjo_no

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| yonpo_code | 四法コード | 全行「4」（商標） |
| shutugan_no | 出願番号 | 主キー、10桁 |
| yusenkenshutugan_no | 優先権出願番号 | 最大20桁、外国の出願番号 |
| yusenkenshucho_bi | 優先権主張日 | YYYYMMDD形式 |
| yusenkenkuni_code | 優先権国コード | JM（ジャマイカ）、NZ（ニュージーランド）等 |
| bmz_junjo_no | 優先権記事順序番号 | 主キー、全行「1」 |

### 35. upd_knktk.tsv
**カテゴリ**: other
**カラム数**: 6
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_241_菌寄託ファイル.csv
**データ状況**: 2行のみ、菌寄託情報（審判関連）
**推奨**: スキップ（データ量極小、審判関連）
**インポート対象**: ❌
**主要キーカラム**: snpn_bngu, krkes_bngu

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| skbt_flg | 識別フラグ | 全行「0」 |
| snpn_bngu | 審判番号 | 主キー、10桁 |
| krkes_bngu | 繰返番号 | 主キー、「1」 |
| jtk_kkn_cd | 受託機関コード | ATCC等 |
| jtk_bngu | 受託番号 | PTA-10698等 |
| kusn_ntz_bat | 更新日時 | YYYYMMDDhhmmss形式 |

### 36. upd_knpu_kukk.tsv
**カテゴリ**: other
**カラム数**: 5
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_212_官報公告ファイル.csv
**データ状況**: 8行のみ、官報公告情報（審判関連）
**推奨**: スキップ（データ量極小、審判関連）
**インポート対象**: ❌
**主要キーカラム**: tyuni_syri_bngu

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| skbt_flg | 識別フラグ | 全行「0」 |
| tyuni_syri_bngu | 庁内書類番号 | 主キー、11桁 |
| hssu_syri_bngu | 発送書類番号 | 11桁 |
| knpu_kukk_sybn_dt | 官報公告処分日 | YYYYMMDD形式 |
| kusn_ntz_bat | 更新日時 | YYYYMMDDhhmmss形式 |

### 37. upd_kusi_ktti.tsv
**カテゴリ**: other
**カラム数**: 4
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_205_更正決定ファイル.csv
**データ状況**: 2行のみ、更正決定情報（審判関連）
**推奨**: スキップ（データ量極小、審判関連）
**インポート対象**: ❌
**主要キーカラム**: hssu_syri_bngu

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| skbt_flg | 識別フラグ | 全行「0」 |
| hssu_syri_bngu | 発送書類番号 | 主キー、11桁 |
| kusi_tisyu_hssu_syri_bngu | 更正対象発送書類番号 | 11桁 |
| kusn_ntz_bat | 更新日時 | YYYYMMDDhhmmss形式 |

### 38. upd_madpro_snpn_zkn_kyu.tsv
**カテゴリ**: international
**カラム数**: 7
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_245_マドプロ審判事件固有ファイル.csv
**データ状況**: 25行、マドリッドプロトコル審判事件情報
**推奨**: スキップ（審判関連、データ量少）
**インポート対象**: ○
**主要キーカラム**: snpn_bngu

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| skbt_flg | 識別フラグ | 全行「0」 |
| snpn_bngu | 審判番号 | 主キー、10桁 |
| tyuni_sir_bngu | 庁内整理番号 | 10桁 |
| bnkt_kgu_cd | 分割記号コード | ほとんど空欄 |
| kksi_trk_bg_ks_ks_kg_cd | 国際登録番号更新回数記号コード | ほとんど空欄 |
| kksi_turk_bngu | 国際登録番号 | 7桁 |
| kusn_ntz_bat | 更新日時 | YYYYMMDDhhmmss形式 |

### 39. upd_mgt_info_t.tsv
**カテゴリ**: status_management
**カラム数**: 40
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_115_管理情報ファイル(商標).csv
**データ状況**: 16,899行、登録商標の管理情報
**推奨**: 必須（登録商標の詳細情報）
**インポート対象**: ○
**主要キーカラム**: law_cd, reg_num, split_num, app_num

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| processing_type | 処理種別 | 全行「0」 |
| law_cd | 四法コード | 全行「4」（商標） |
| reg_num | 登録番号 | 主キー、7桁（0073914等） |
| split_num | 分割番号 | 主キー、31桁の0 |
| mstr_updt_year_month_day | マスタ更新年月日 | YYYYMMDD形式（20250604等） |
| tscript_inspct_prhbt_flg | 謄本閲覧禁止の有無 | ほとんど空欄 |
| conti_prd_expire_ymd | 存続期間満了年月日 | YYYYMMDD形式（20350816等） |
| next_pen_pymnt_tm_lmt_ymd | 次期年金納付期限年月日 | 存続期間満了日と同じ |
| last_pymnt_yearly | 最終納付年分 | 「10」（10年分）が多い |
| share_rate | 持分の割合 | 「0000000000」（単独所有） |
| pblc_prvt_trnsfr_reg_ymd | 官民移転登録年月日 | 「00000000」（該当なし） |
| right_ersr_id | 本権利抹消識別 | 「00」（抹消なし） |
| right_disppr_year_month_day | 本権利消滅年月日 | 「00000000」（消滅なし） |
| close_orgnl_reg_trnsfr_rec_flg | 閉鎖原簿移記の有無 | ほとんど空欄 |
| close_reg_year_month_day | 閉鎖登録年月日 | 「00000000」（閉鎖なし） |
| gvrnmnt_relation_id_flg | 官庁関係識別の有無 | ほとんど空欄 |
| pen_suppl_flg | 年金補充の有無 | ほとんど空欄 |
| apply_law | 適用法規 | 「2」「3」等（旧法・新法区分） |
| group_t_flg | 団体商標の有無 | ほとんど空欄 |
| special_t_id | 特殊商標識別 | ほとんど空欄 |
| standard_char_t_flg | 標準文字商標の有無 | ほとんど空欄 |
| area_group_t_flg | 地域団体商標の有無 | ほとんど空欄 |
| trust_reg_flg | 信託登録の有無 | ほとんど空欄 |
| app_num | 出願番号 | 主キー、10桁（古い登録は短い） |
| recvry_num | 回復番号 | 「0000000000」または古い番号 |
| app_year_month_day | 出願年月日 | YYYYMMDD形式 |
| app_exam_pub_num | 出願公告番号 | 10桁または短い番号 |
| app_exam_pub_year_month_day | 出願公告年月日 | YYYYMMDD形式 |
| finl_dcsn_year_month_day | 査定年月日 | YYYYMMDD形式 |
| trial_dcsn_year_month_day | 審決年月日 | 「00000000」が多い |
| set_reg_year_month_day | 設定登録年月日 | YYYYMMDD形式 |
| t_rwrt_app_num | 商標書換申請番号 | 「2003549865」等（一部のみ） |
| t_rwrt_app_year_month_day | 商標書換申請年月日 | YYYYMMDD形式（書換あり時） |
| t_rwrt_finl_dcsn_ymd | 商標書換査定年月日 | YYYYMMDD形式（書換あり時） |
| t_rwrt_trial_dcsn_ymd | 商標書換審決年月日 | 「00000000」が多い |
| t_rwrt_reg_year_month_day | 商標書換登録年月日 | YYYYMMDD形式（書換あり時） |
| invent_title_etc_len | 発明の名称（等）レングス | 「0000000000」（商標では未使用） |
| pri_cntry_name_cd | 優先権国名コード | ほとんど空欄 |
| pri_clim_year_month_day | 優先権主張年月日 | 「00000000」が多い |
| pri_clim_cnt | 優先権主張件数 | 「000」が多い |

### 40. upd_mrgn_t_rwrt_app_num.tsv
**カテゴリ**: other
**カラム数**: 8
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_116_欄外商標書換申請番号ファイル.csv
**データ状況**: 2,996行、商標書換申請情報
**推奨**: スキップ（商標書換制度は廃止済み）
**インポート対象**: ○
**主要キーカラム**: law_cd, reg_num, split_num, app_num, mu_num

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| processing_type | 処理種別 | 全行「0」 |
| law_cd | 四法コード | 全行「4」（商標） |
| reg_num | 登録番号 | 主キー、7桁 |
| split_num | 分割番号 | 主キー、31桁の0 |
| app_num | 出願番号 | 主キー、10桁 |
| mrgn_info_upd_ymd | 欄外情報部作成更新年月日 | YYYYMMDD形式 |
| mu_num | ＭＵ番号 | 主キー、全行「000」 |
| mrgn_t_rwrt_app_num | 欄外商標書換申請番号 | 全行「0000000000」 |

### 41. upd_mustt_kkr_sikyuku.tsv
**カテゴリ**: other
**カラム数**: 6
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_221_申立に係る請求項ファイル.csv
**データ状況**: 2,505行、異議申立の請求項情報
**推奨**: スキップ（審判関連、商標検索には不要）
**インポート対象**: ○
**主要キーカラム**: snpn_bngu, mustt_bngu, krkes_bngu

**データ内容の詳細**:
- **申立番号（mustt_bngu）**: 同じ審判事件で複数の申立がある場合の番号（001、002など）
- **繰返番号（krkes_bngu）と請求項番号（sikyuku_bngu）**: 
  - 多くの場合は同じ値（SAME: 2,039件）
  - 異なる場合もある（DIFFERENT: 466件）
  - 異議申立の対象となった指定商品・役務の区分を細かく管理
- **請求項番号**: 商標の場合、指定商品・役務の区分（第1類〜第45類）に対応すると推測

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| skbt_flg | 識別フラグ | 全行「0」 |
| snpn_bngu | 審判番号 | 主キー、10桁 |
| mustt_bngu | 申立番号 | 主キー、3桁（001、002など） |
| krkes_bngu | 繰返番号 | 主キー、1-34の値 |
| sikyuku_bngu | 請求項番号 | 1-34の値、指定商品・役務区分に対応 |
| kusn_ntz_bat | 更新日時 | YYYYMMDDhhmmss形式 |

### 42. upd_mustt_kkr_sti_syuhn_ekmmi.tsv
**カテゴリ**: other
**カラム数**: 6
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_238_申立に係る指定商品・役務名ファイル.csv
**データ状況**: 34行、異議申立対象の商品・役務情報
**推奨**: スキップ（審判関連、データ量少）
**インポート対象**: ○
**主要キーカラム**: snpn_bngu, mustt_bngu, mustt_tisyu_syuhn_kbn

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| skbt_flg | 識別フラグ | 全行「0」 |
| snpn_bngu | 審判番号 | 主キー、10桁 |
| mustt_bngu | 申立番号 | 主キー、3桁（001） |
| mustt_tisyu_syuhn_kbn | 申立対象商品区分 | 主キー、2桁（03,12,33,35等） |
| mustt_tisyu_sti_syuhn_ekmmi | 申立対象指定商品・役務名 | 「全指定商品」「全指定役務」等 |
| kusn_ntz_bat | 更新日時 | YYYYMMDDhhmmss形式 |

### 43. upd_prog_info_div_t.tsv
**カテゴリ**: status_management
**カラム数**: 13
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_126_経過情報部ファイル(商標).csv
**データ状況**: 223,694行、登録商標の経過情報
**推奨**: インポート（登録後の手続き経過情報として有用）
**インポート対象**: ○
**主要キーカラム**: law_cd, reg_num, split_num, app_num, rec_num, pe_num

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| processing_type | 処理種別 | 全行「0」 |
| law_cd | 四法コード | 全行「4」（商標） |
| reg_num | 登録番号 | 主キー、7桁 |
| split_num | 分割番号 | 主キー、31桁の0 |
| app_num | 出願番号 | 主キー、ほとんど「0000000000」 |
| rec_num | レコード番号 | 主キー、00等 |
| pe_num | ＰＥ番号 | 主キー、3桁連番 |
| prog_info_upd_ymd | 経過情報部作成更新年月日 | YYYYMMDD形式 |
| reg_intrmd_cd | 登録中間コード | R350等のコード |
| crrspnd_mk | 対応マーク | 21,22等の数値 |
| rcpt_pymnt_dsptch_ymd | 受付又は納付又は発送年月日 | YYYYMMDD形式 |
| prog_info_div_app_num | 経過情報部出願番号 | ほとんど「0000000000」 |
| rcpt_num_common_use | 受付番号（共用） | 11桁の受付番号 |

### 44. upd_right_goods_name.tsv
**カテゴリ**: classification
**カラム数**: 10
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_127_本権商品名ファイル.csv
**データ状況**: 30,581行、登録商標の指定商品・役務情報
**推奨**: 必須（登録商標の商品・役務表示に必要）
**インポート対象**: ○
**主要キーカラム**: law_cd, reg_num, split_num, app_num, desig_goods_or_desig_wrk_class, rec_num

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| processing_type | 処理種別 | 全行「0」 |
| law_cd | 四法コード | 全行「4」（商標） |
| reg_num | 登録番号 | 主キー、7桁 |
| split_num | 分割番号 | 主キー、31桁の0 |
| app_num | 出願番号 | 主キー、「0000000000」が多い |
| desig_goods_or_desig_wrk_class | 指定商品又は指定役務の区分 | 主キー、2桁（01-45） |
| mstr_updt_year_month_day | マスタ更新年月日 | 「00000000」または更新日 |
| desg_gds_desg_wrk_name_len | 指定商品又は指定役務名レングス | 10桁、文字数 |
| desg_gds_name_desg_wrk_name | 指定商品名又は指定役務名 | 最大12000文字、詳細な商品・役務名 |
| rec_num | レコード番号 | 主キー、「00」固定 |

### 45. upd_right_person_art_t.tsv
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_124_権利者記事ファイル(商標).csv
**データ状況**: 17,099行、登録商標の権利者情報
**インポート推奨**: YES
**インポート対象**: ○
**カテゴリ**: applicant_agent
**カラム数**: 13
**主要キーカラム**: law_cd, reg_num, split_num, app_num, rec_num, pe_num

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| processing_type | 処理種別 | 削除・修正等を示すコード |
| law_cd | 四法コード | 主キー、商標は「4」 |
| reg_num | 登録番号 | 主キー、7桁の登録番号 |
| split_num | 分割番号 | 主キー、通常「0000000000000000000000000000000」 |
| app_num | 出願番号 | 主キー、10桁の出願番号 |
| rec_num | レコード番号 | 主キー、「00」固定 |
| pe_num | ＰＥ番号 | 主キー、「000」固定 |
| right_psn_art_upd_ymd | 権利者記事部作成更新年月日 | YYYYMMDD形式の更新日 |
| right_person_appl_id | 権利者申請人ＩＤ | 9桁の申請人識別番号 |
| right_person_addr_len | 権利者住所レングス | 住所のバイト数 |
| right_person_addr | 権利者住所 | 最大1000文字の住所情報 |
| right_person_name_len | 権利者氏名レングス | 氏名のバイト数 |
| right_person_name | 権利者氏名 | 最大1000文字の権利者名 |

### 46. upd_search_use_t_art_table.tsv
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_158_検索用商標記事ファイル.csv
**データ状況**: 40,961行、検索用商標文字列データ
**インポート推奨**: YES
**インポート対象**: ○
**カテゴリ**: trademark_text
**カラム数**: 6
**主要キーカラム**: app_num, split_num, sub_data_num, search_use_t_seq

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| add_del_id | 追加削除識別 | 0:追加、1:削除 |
| app_num | 出願番号 | 主キー、10桁の出願番号 |
| split_num | 分割番号 | 主キー、31桁の分割番号 |
| sub_data_num | サブデータ番号 | 主キー、初期値（NULL）固定 |
| search_use_t_seq | 検索用商標順序 | 主キー、同一出願内の連番 |
| search_use_t | 検索用商標 | 最大256文字の検索用商標文字列 |

### 47. upd_sec_art.tsv
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_122_防護記事ファイル.csv
**データ状況**: 769行、防護標章の登録情報
**インポート推奨**: YES
**インポート対象**: ○
**カテゴリ**: other
**カラム数**: 27
**主要キーカラム**: law_cd, reg_num, split_num, app_num, pe_num, mu_num

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| processing_type | 処理種別 | 削除・修正等を示すコード |
| law_cd | 四法コード | 主キー、商標は「4」 |
| reg_num | 登録番号 | 主キー、7桁の登録番号 |
| split_num | 分割番号 | 主キー、31桁の分割番号 |
| app_num | 出願番号 | 主キー、10桁の出願番号 |
| pe_num | ＰＥ番号 | 主キー、3桁のＰＥ番号 |
| sec_art_upd_ymd | 防護記事部作成更新年月日 | YYYYMMDD形式の更新日 |
| sec_app_num | 防護出願番号 | 10桁の防護出願番号 |
| sec_num | 防護番号 | 3桁の防護番号 |
| sec_temp_reg_flg | 防護仮登録の有無 | 仮登録フラグ |
| sec_conti_prd_expire_ymd | 防護存続期間満了年月日 | YYYYMMDD形式の満了日 |
| sec_ersr_flg | 防護抹消の有無 | 抹消フラグ |
| sec_apply_law | 防護適用法規 | 1桁の法規コード |
| sec_recovery_num | 防護回復番号 | 10桁の回復番号 |
| sec_app_year_month_day | 防護出願年月日 | YYYYMMDD形式の出願日 |
| sec_app_exam_pub_num | 防護出願公告番号 | 10桁の公告番号 |
| sec_app_exam_pub_ymd | 防護出願公告年月日 | YYYYMMDD形式の公告日 |
| sec_finl_dcsn_year_month_day | 防護査定年月日 | YYYYMMDD形式の査定日 |
| sec_trial_dcsn_year_month_day | 防護審決年月日 | YYYYMMDD形式の審決日 |
| sec_reg_year_month_day | 防護登録年月日 | YYYYMMDD形式の登録日 |
| sec_rwrt_app_num | 防護書換申請番号 | 10桁の書換申請番号 |
| sec_rwrt_app_year_month_day | 防護書換申請年月日 | YYYYMMDD形式の申請日 |
| sec_rwrt_finl_dcsn_ymd | 防護書換査定年月日 | YYYYMMDD形式の査定日 |
| sec_rwrt_trial_dcsn_ymd | 防護書換審決年月日 | YYYYMMDD形式の審決日 |
| sec_rwrt_reg_year_month_day | 防護書換登録年月日 | YYYYMMDD形式の登録日 |
| mu_num | ＭＵ番号 | 主キー、3桁のＭＵ番号 |
| sec_desig_goods_desig_wrk_cls | 防護指定商品又は指定役務の区分 | 2桁の商品・役務区分 |

### 48. upd_sec_goods_name.tsv
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_128_防護商品名ファイル.csv
**データ状況**: 1,472行、防護標章の指定商品・役務情報
**インポート推奨**: YES
**インポート対象**: ○
**カテゴリ**: classification
**カラム数**: 10
**主要キーカラム**: law_cd, reg_num, split_num, sec_num, sec_app_num, sec_desig_goods_desig_wrk_cls

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| processing_type | 処理種別 | 削除・修正等を示すコード |
| law_cd | 四法コード | 主キー、商標は「4」 |
| reg_num | 登録番号 | 主キー、7桁の登録番号 |
| split_num | 分割番号 | 主キー、31桁の分割番号 |
| sec_num | 防護番号 | 主キー、3桁の防護番号 |
| sec_app_num | 防護出願番号 | 主キー、10桁の防護出願番号 |
| sec_desig_goods_desig_wrk_cls | 防護指定商品又は指定役務の区分 | 主キー、2桁の商品・役務区分 |
| mstr_updt_year_month_day | マスタ更新年月日 | YYYYMMDD形式の更新日 |
| sec_desig_gds_desig_wrk_nm_len | 防護指定商品又は指定役務名レングス | 10桁、文字数 |
| sec_desig_gds_nm_desig_wrk_nm | 防護指定商品名又は指定役務名 | 最大12000文字、詳細な商品・役務名 |

### 49. upd_sec_updt_art.tsv
**カテゴリ**: other
**カラム数**: 17
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_123_防護更新記事ファイル.csv
**データ状況**: 1,911行、防護標章の更新登録に関する記事情報
**推奨**: スキップ（防護標章の更新記事は特殊な情報）
**インポート対象**: ○
**主要キーカラム**: law_cd, reg_num, split_num, app_num, pe_num, mu_num

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| processing_type | 処理種別 | 全行で"0" |
| law_cd | 四法コード | 全行で"4"（商標） |
| reg_num | 登録番号 | 7桁の数値 |
| split_num | 分割番号 | 31桁、ほぼ全行で"0"埋め |
| app_num | 出願番号 | 10桁の出願番号 |
| pe_num | ＰＥ番号 | 3桁、連番 |
| sec_updt_art_upd_ymd | 防護更新記事部作成更新年月日 | YYYYMMDD形式 |
| sec_updt_app_num | 防護更新出願番号 | 防護更新の出願番号 |
| sec_updt_sec_num | 防護更新防護番号 | 3桁の防護番号 |
| sec_updt_temp_reg_flg | 防護更新仮登録の有無 | ほぼ空欄 |
| sec_updt_title_chan_flg | 防護更新名称変更の有無 | ほぼ空欄 |
| sec_updt_recovery_num | 防護更新回復番号 | ほぼ"0000000000" |
| sec_updt_app_year_month_day | 防護更新出願年月日 | YYYYMMDD形式 |
| sec_updt_finl_dcsn_ymd | 防護更新査定年月日 | YYYYMMDD形式 |
| sec_updt_trial_dcsn_ymd | 防護更新審決年月日 | ほぼ"00000000" |
| sec_updt_reg_year_month_day | 防護更新登録年月日 | YYYYMMDD形式 |
| mu_num | ＭＵ番号 | 3桁、全行で"000" |

### 50. upd_sisu.tsv
**カテゴリ**: other
**カラム数**: 5
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_211_再送ファイル.csv
**データ状況**: 53行、書類の再送に関する情報
**推奨**: スキップ（書類再送の管理情報のみ）
**インポート対象**: ❌
**主要キーカラム**: tyuni_syri_bngu

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| skbt_flg | 識別フラグ | 全行で"0" |
| tyuni_syri_bngu | 庁内書類番号 | 11桁の書類番号 |
| hssu_syri_bngu | 発送書類番号 | 11桁の書類番号 |
| sisu_dt | 再送日 | YYYYMMDD形式、再送日付 |
| kusn_ntz_bat | 更新日時 | YYYYMMDDHHMMSS形式のタイムスタンプ |

### 51. upd_smi_tut.tsv
**カテゴリ**: other
**カラム数**: 5
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_204_氏名通知ファイル.csv
**データ状況**: 4,302行、審判における氏名通知に関する情報
**推奨**: スキップ（審判手続きの氏名通知管理）
**インポート対象**: ❌
**主要キーカラム**: hssu_syri_bngu

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| skbt_flg | 識別フラグ | 全行で"0" |
| hssu_syri_bngu | 発送書類番号 | 11桁の書類番号 |
| snpn_bngu | 審判番号 | 10桁の審判番号 |
| gugti_rrk_rrk_bngu | 合議体（履歴）履歴番号 | ほぼ全行で"1" |
| kusn_ntz_bat | 更新日時 | YYYYMMDDHHMMSS形式のタイムスタンプ |

### 52. upd_sngi_ssyu.tsv
**カテゴリ**: other
**カラム数**: 11
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_239_侵害訴訟ファイル.csv
**データ状況**: 1行のみ、侵害訴訟に関する情報（文字化けあり）
**推奨**: スキップ（データが1行のみで文字化けもあり）
**インポート対象**: ❌
**主要キーカラム**: sibnsy_cd, zkn_krk_hgu_cd, zkn_bngu

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| skbt_flg | 識別フラグ | "0" |
| sibnsy_cd | 裁判所コード | 5桁のコード |
| zkn_krk_hgu_cd | 事件記録符号コード | 3桁のコード |
| zkn_bngu | 事件番号 | 9桁の番号 |
| hyuzyu_sngi_ssyu_zkn_bngu_gngu | 表示用侵害訴訟事件番号_元号 | 文字化けあり |
| hyuzyu_sngi_ssyu_zkn_bngu_nnsu | 表示用侵害訴訟事件番号_年数 | 年数 |
| hyuzyu_sngi_ssyu_zkn_bngu_tubn | 表示用侵害訴訟事件番号_通番 | 通番 |
| sibnsy_sbtu | 裁判所支部等 | 文字化けあり |
| syukyk_dt | 終局日 | YYYYMMDD形式 |
| syukyk_zyu_cd | 終局事由コード | 2桁のコード |
| kusn_ntz_bat | 更新日時 | YYYYMMDDHHMMSS形式 |

### 53. upd_sngi_turk_bngu.tsv
**カテゴリ**: other
**カラム数**: 10
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_240_侵害登録番号ファイル.csv
**データ状況**: 132行、侵害訴訟に関連する登録番号情報
**推奨**: スキップ（侵害訴訟関連の特殊情報）
**インポート対象**: ❌
**主要キーカラム**: sibnsy_cd, zkn_krk_hgu_cd, zkn_bngu, krkes_bngu

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| skbt_flg | 識別フラグ | 全行で"0" |
| sibnsy_cd | 裁判所コード | 5桁のコード |
| zkn_krk_hgu_cd | 事件記録符号コード | 3桁のコード |
| zkn_bngu | 事件番号 | 9桁の番号 |
| krkes_bngu | 繰返番号 | 連番（1から開始） |
| ynpu_kbn | 四法区分 | 全行で"1"（特許） |
| turk_bngu | 登録番号 | 7桁の登録番号 |
| bnkt_bngu | 分割番号 | ほぼ空欄 |
| riz_bngu | 類似番号 | ほぼ空欄 |
| kusn_ntz_bat | 更新日時 | YYYYMMDDHHMMSS形式 |

### 54. upd_snk_ktti.tsv
**カテゴリ**: other
**カラム数**: 5
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_226_参加決定ファイル.csv
**データ状況**: 10行、審判手続きへの参加決定に関する情報
**推奨**: スキップ（審判手続きの参加決定情報のみ）
**インポート対象**: ❌
**主要キーカラム**: snpn_bngu, snk_snsi_bngu

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| skbt_flg | 識別フラグ | 全行で"0" |
| snpn_bngu | 審判番号 | 10桁の審判番号 |
| snk_snsi_bngu | 参加申請番号 | 3桁、全行で"001" |
| hssu_syri_bngu | 発送書類番号 | 11桁の書類番号 |
| kusn_ntz_bat | 更新日時 | YYYYMMDDHHMMSS形式 |

### 55. upd_snk_ktti_bnri.tsv
**カテゴリ**: other
**カラム数**: 12
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_227_参加決定分類ファイル.csv
**データ状況**: 10行、参加決定の分類情報
**推奨**: スキップ（審判手続きの参加決定分類）
**インポート対象**: ❌
**主要キーカラム**: snpn_bngu, snk_snsi_bngu, krkes_bngu

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| skbt_flg | 識別フラグ | 全行で"0" |
| snpn_bngu | 審判番号 | 10桁の審判番号 |
| snk_snsi_bngu | 参加申請番号 | 3桁、全行で"001" |
| krkes_bngu | 繰返番号 | 全行で"1" |
| ynpu_kbn | 四法区分 | 全行で"1"（特許） |
| tkyu_huk_skbt | 適用法規識別 | ほぼ空欄 |
| snkyu_sybt | 審級種別 | 全行で"1" |
| snpn_sybt | 審判種別 | 2-3桁のコード |
| hnz_zku_cd | 判示事項コード | 3桁のコード |
| snk_ktti_bnri_ktrn_cd | 参加決定分類結論コード | "Y"など |
| hj_bnri_skbt | 補助分類識別 | 分類コード |
| kusn_ntz_bat | 更新日時 | YYYYMMDDHHMMSS形式 |

### 56. upd_snk_snsi.tsv
**カテゴリ**: other
**カラム数**: 7
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_225_参加申請ファイル.csv
**データ状況**: 10行、審判手続きへの参加申請情報
**推奨**: スキップ（審判手続きの参加申請情報）
**インポート対象**: ❌
**主要キーカラム**: snpn_bngu, snk_snsi_bngu

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| skbt_flg | 識別フラグ | 全行で"0" |
| snpn_bngu | 審判番号 | 10桁の審判番号 |
| snk_snsi_bngu | 参加申請番号 | 3桁、全行で"001" |
| snsi_dt | 申請日 | YYYYMMDD形式 |
| tiyu_skbt | 態様識別 | 1桁のコード（1,2,3） |
| sisyu_sybn_stat | 最終処分ステータス | 2桁のコード（01,04） |
| kusn_ntz_bat | 更新日時 | YYYYMMDDHHMMSS形式 |

### 57. upd_snksi_sust_rigi.tsv
**カテゴリ**: other
**カラム数**: 6
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_242_新規性喪失例外ファイル.csv
**データ状況**: 6行、新規性喪失例外に関する情報（文字化けあり）
**推奨**: スキップ（特許の新規性喪失例外情報）
**インポート対象**: ❌
**主要キーカラム**: snpn_bngu, krkes_bngu

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| skbt_flg | 識別フラグ | 全行で"0" |
| snpn_bngu | 審判番号 | 10桁の審判番号 |
| krkes_bngu | 繰返番号 | 全行で"1" |
| jubn_cd | 条文コード | 1または2 |
| niyu | 内容 | 新規性喪失例外の内容（文字化け） |
| kusn_ntz_bat | 更新日時 | YYYYMMDDHHMMSS形式 |

### 58. upd_snkt.tsv
**カテゴリ**: other
**カラム数**: 6
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_232_審決ファイル.csv
**データ状況**: 462行、審判の審決に関する情報
**推奨**: スキップ（審判の審決情報）
**インポート対象**: ❌
**主要キーカラム**: snpn_bngu, snkt_bngu

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| skbt_flg | 識別フラグ | 全行で"0" |
| snpn_bngu | 審判番号 | 10桁の審判番号 |
| snkt_bngu | 審決番号 | 2桁、ほぼ全行で"01" |
| hssu_syri_bngu | 発送書類番号 | 11桁の書類番号 |
| snkttu_kkti_stat | 審決等確定ステータス | 1桁（1,2または空欄） |
| kusn_ntz_bat | 更新日時 | YYYYMMDDHHMMSS形式 |

### 59. upd_snkt_bnri.tsv
**カテゴリ**: other
**カラム数**: 12
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_233_審決分類ファイル.csv
**データ状況**: 897行、審決の分類情報
**推奨**: スキップ（審判の審決分類情報）
**インポート対象**: ○
**主要キーカラム**: snpn_bngu, snkt_bngu, krkes_bngu

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| skbt_flg | 識別フラグ | 全行で"0" |
| snpn_bngu | 審判番号 | 10桁の審判番号 |
| snkt_bngu | 審決番号 | 2桁、ほぼ全行で"01" |
| krkes_bngu | 繰返番号 | 連番 |
| ynpu_kbn | 四法区分 | 全行で"1"（特許） |
| tkyu_huk_skbt | 適用法規識別 | ほぼ空欄 |
| snkyu_sybt | 審級種別 | 全行で"1" |
| snpn_sybt | 審判種別 | 3桁のコード |
| hnz_zku_cd | 判示事項コード | 3桁のコード |
| snkt_bnri_ktrn_cd | 審決分類結論コード | "Y"や分類コード |
| hj_bnri_skbt | 補助分類識別 | 分類コードまたは空欄 |
| kusn_ntz_bat | 更新日時 | YYYYMMDDHHMMSS形式 |

### 60. upd_snpn_sk_kkr_st_sh_ekmmi.tsv
**カテゴリ**: other
**カラム数**: 5
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_237_審判請求に係る指定商品・役務名ファイル.csv
**データ状況**: 181行、審判請求の対象となる商品・役務情報
**推奨**: スキップ（審判請求の商品・役務情報）
**インポート対象**: ○
**主要キーカラム**: snpn_bngu, sikyu_tisyu_syuhn_kbn

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| skbt_flg | 識別フラグ | 全行で"0" |
| snpn_bngu | 審判番号 | 10桁の審判番号 |
| sikyu_tisyu_syuhn_kbn | 請求対象商品区分 | 2桁の商品区分 |
| sikyu_tisyu_sti_syuhn_ekmmi | 請求対象指定商品・役務名 | 商品・役務名（多くは空欄、一部文字化け） |
| kusn_ntz_bat | 更新日時 | YYYYMMDDHHMMSS形式 |

### 61. upd_snpn_tuzsy.tsv
**カテゴリ**: other
**カラム数**: 9
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_234_審判当事者ファイル.csv
**データ状況**: 11,966行、審判事件の当事者情報
**推奨**: スキップ（審判手続きの当事者情報）
**インポート対象**: ○
**主要キーカラム**: snpn_bngu, tuzsy_sybt, krkes_bngu

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| skbt_flg | 識別フラグ | 全行で"0" |
| snpn_bngu | 審判番号 | 10桁の審判番号 |
| tuzsy_sybt | 当事者種別 | 1-2桁のコード（1,2,4,11,21等） |
| krkes_bngu | 繰返番号 | 連番 |
| ig_tuzsy_bngu | 異議当事者番号 | 3桁、多くは"000"または空欄 |
| snk_snsi_bngu | 参加申請番号 | ほぼ空欄 |
| snsinn_cd | 申請人コード | 9桁のコード（代理人情報含む） |
| dirnn_sybt | 代理人種別 | 1桁（1または空欄） |
| kusn_ntz_bat | 更新日時 | YYYYMMDDHHMMSS形式 |

### 62. upd_snpn_tzs_ssn_cd_ys_juhu.tsv
**カテゴリ**: other
**カラム数**: 10
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_235_審判当事者・申請人コード優先情報ファイル.csv
**データ状況**: 1,576行、審判当事者の住所・氏名情報（文字化けあり）
**推奨**: スキップ（審判当事者の個人情報）
**インポート対象**: ○
**主要キーカラム**: snpn_bngu, tuzsy_sybt, krkes_bngu

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| skbt_flg | 識別フラグ | 全行で"0" |
| snpn_bngu | 審判番号 | 10桁の審判番号 |
| tuzsy_sybt | 当事者種別 | 1-2桁のコード |
| krkes_bngu | 繰返番号 | 連番 |
| jusy | 住所 | 住所情報（文字化け） |
| smi | 氏名 | 氏名情報（文字化け） |
| khukn_kbn | 個法官区分 | 1桁（1,2または空欄） |
| kkkn_cd | 国県コード | 2桁のコード（27等） |
| dirnn_skk_sybt | 代理人資格種別 | 1桁（1,2または空欄） |
| kusn_ntz_bat | 更新日時 | YYYYMMDDHHMMSS形式 |

### 63. upd_snpn_zkn.tsv
**カテゴリ**: other
**カラム数**: 15
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_201_審判事件ファイル.csv
**データ状況**: 3,119行、審判事件の基本情報
**推奨**: スキップ（審判事件情報）
**インポート対象**: ○
**主要キーカラム**: snpn_bngu

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| skbt_flg | 識別フラグ | 全行で"0" |
| snpn_bngu | 審判番号 | 10桁の審判番号 |
| sytgn_bngu | 出願番号 | 10桁の出願番号 |
| ynpu_kbn | 四法区分 | 1桁（1:特許、4:商標） |
| turk_bngu | 登録番号 | 7桁の登録番号（多くは空欄） |
| bnkt_bngu | 分割番号 | ほぼ空欄 |
| riz_bngu | 類似番号 | ほぼ空欄 |
| bug_bngu | 防護番号 | ほぼ空欄 |
| snkyu_sybt | 審級種別 | 全行で"1" |
| snpn_sybt | 審判種別 | 3桁のコード（41,80,113等） |
| snpn_sikyu_dt | 審判請求日 | YYYYMMDD形式 |
| sytgn_bngu_kbn | 出願番号区分 | 1桁（1,2） |
| snpn_zkn_sisyu_sybn_cd | 審判事件最終処分コード | 2桁のコード（01,02,07等） |
| sisyu_sybn_kkti_dt | 最終処分確定日 | YYYYMMDD形式（多くは空欄） |
| kusn_ntz_bat | 更新日時 | YYYYMMDDHHMMSS形式 |

### 64. upd_standard_char_t_art.tsv
**カテゴリ**: trademark_text
**カラム数**: 5
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_157_標準文字商標記事ファイル.csv
**データ状況**: 15,110行、標準文字商標の更新情報
**推奨**: インポート（商標文字情報の更新）
**インポート対象**: ○
**主要キーカラム**: app_num, split_num, sub_data_num

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| add_del_id | 追加削除識別 | 全行で"0"（追加） |
| app_num | 出願番号 | 10桁の出願番号 |
| split_num | 分割番号 | ほぼ空欄 |
| sub_data_num | サブデータ番号 | ほぼ空欄 |
| standard_char_t | 標準文字商標 | 商標テキスト（最大127文字） |

### 65. upd_suk_snr_juhu.tsv
**カテゴリ**: other
**カラム数**: 4
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_236_早期審理情報ファイル.csv
**データ状況**: 17行、審判の早期審理選定情報
**推奨**: スキップ（審判の早期審理情報）
**インポート対象**: ❌
**主要キーカラム**: snpn_bngu

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| skbt_flg | 識別フラグ | 全行で"0" |
| snpn_bngu | 審判番号 | 10桁の審判番号 |
| suk_snr_snti_stat | 早期審理選定ステータス | 全行で"2" |
| kusn_ntz_bat | 更新日時 | YYYYMMDDHHMMSS形式 |

### 66. upd_sutt.tsv
**カテゴリ**: other
**カラム数**: 5
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_213_送達ファイル.csv
**データ状況**: 1,038行、書類の送達情報
**推奨**: スキップ（書類送達の管理情報）
**インポート対象**: ❌
**主要キーカラム**: tyuni_syri_bngu

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| skbt_flg | 識別フラグ | 全行で"0" |
| tyuni_syri_bngu | 庁内書類番号 | 11桁の書類番号 |
| hssu_syri_bngu | 発送書類番号 | 11桁の書類番号 |
| sutt_dt | 送達日 | YYYYMMDD形式 |
| kusn_ntz_bat | 更新日時 | YYYYMMDDHHMMSS形式 |

### 67. upd_syss_jukk_juhu.tsv
**カテゴリ**: other
**カラム数**: 13
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_230_出訴・上告情報ファイル.csv
**データ状況**: 46行、審決に対する出訴・上告情報
**推奨**: スキップ（審判の出訴・上告情報）
**インポート対象**: ❌
**主要キーカラム**: sibnsy_cd, zkn_krk_hgu_cd, zkn_bngu, krkes_bngu

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| skbt_flg | 識別フラグ | 全行で"0" |
| sibnsy_cd | 裁判所コード | 5桁のコード |
| zkn_krk_hgu_cd | 事件記録符号コード | 3桁のコード |
| zkn_bngu | 事件番号 | 9桁の番号 |
| krkes_bngu | 繰返番号 | 連番 |
| syss_jukk_zkn_bngu | 出訴・上告事件番号 | 9桁（一部空欄） |
| syss_jukk_zkn_krk_hgu_cd | 出訴・上告事件記録符号コード | 3桁（一部空欄） |
| hyuzyu_zkn_bngu_gngu | 表示用事件番号_元号 | 元号（文字化け） |
| hyuzyu_zkn_bngu_nnsu | 表示用事件番号_年数 | 年数 |
| hyuzyu_zkn_bngu_bngu | 表示用事件番号_番号 | 番号 |
| syss_jukk_dt | 出訴・上告日 | YYYYMMDD形式（一部空欄） |
| tiou_krkes_bngu | 対応繰返番号 | 番号（多くは0） |
| kusn_ntz_bat | 更新日時 | YYYYMMDDHHMMSS形式 |

### 68. upd_syss_tisyu_snkttu.tsv
**カテゴリ**: other
**カラム数**: 8
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_229_出訴対象審決等ファイル.csv
**データ状況**: 27行、出訴対象となった審決等の情報
**推奨**: スキップ（審判の出訴対象情報）
**インポート対象**: ❌
**主要キーカラム**: sibnsy_cd, zkn_krk_hgu_cd, zkn_bngu, krkes_bngu

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| skbt_flg | 識別フラグ | 全行で"0" |
| sibnsy_cd | 裁判所コード | 5桁のコード |
| zkn_krk_hgu_cd | 事件記録符号コード | 3桁のコード |
| zkn_bngu | 事件番号 | 9桁の番号 |
| krkes_bngu | 繰返番号 | 全行で"1" |
| snpn_bngu | 審判番号 | 10桁の審判番号 |
| hssu_syri_bngu | 発送書類番号 | 11桁の書類番号 |
| kusn_ntz_bat | 更新日時 | YYYYMMDDHHMMSS形式 |

### 69. upd_t_add_info.tsv
**カテゴリ**: other
**カラム数**: 11
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_155_商標付加情報記事ファイル.csv
**データ状況**: 33,418行、商標の付加情報
**推奨**: インポート（商標の付加属性情報）
**インポート対象**: ○
**主要キーカラム**: app_num, split_num, sub_data_num

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| add_del_id | 追加削除識別 | 全行で"0"（追加） |
| app_num | 出願番号 | 10桁の出願番号 |
| split_num | 分割番号 | ほぼ空欄 |
| sub_data_num | サブデータ番号 | ほぼ空欄 |
| right_request | 権利不要求 | 0または1のフラグ |
| grphc_id | 図形識別 | 0または1のフラグ |
| color_harftone | カラーハーフトーン | 0または1のフラグ |
| gdmral_flg | 公序良俗フラグ | ほぼ全行で"0" |
| duplicate_reg_flg | 重複登録フラグ | ほぼ全行で"0" |
| special_exception_clim_flg | 特例主張フラグ | ほぼ全行で"0" |
| consent_coe_reg_id | 同意併存登録識別 | ほぼ空欄 |

### 70. upd_t_basic_item_art.tsv
**カテゴリ**: core_trademark
**カラム数**: 30
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_154_商標基本項目記事ファイル.csv
**データ状況**: 33,418行、商標の基本情報（出願日、登録日、最終処分等）
**推奨**: インポート（商標の基本管理情報）
**インポート対象**: ○
**主要キーカラム**: mgt_num

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| add_del_id | 追加削除識別 | 全行で"0"（追加） |
| mgt_num | 管理番号 | 主キー、7桁の数値 |
| rec_status_id | レコード状態識別 | "1"または"2" |
| app_num | 出願番号 | 10桁の出願番号 |
| reg_num | 登録番号 | 7桁、未登録は"0000000" |
| split_num | 分割番号 | ほぼ空欄 |
| sec_num | 防護番号 | "000"固定 |
| app_typ_sec | 出願種別防護 | "0"固定 |
| app_typ_split | 出願種別分割 | "0"固定 |
| app_typ_complement_rjct | 出願種別補却 | "0"固定 |
| app_typ_chan | 出願種別変更 | "0"固定 |
| app_typ_priorty | 出願種別優先 | "0"固定 |
| app_typ_group | 出願種別団体 | "0"固定 |
| app_typ_area_group | 出願種別地域団体 | "0"固定 |
| app_dt | 出願日 | YYYYMMDD形式 |
| prior_app_right_occr_dt | 先願権発生日 | YYYYMMDD形式 |
| rjct_finl_dcsn_dsptch_dt | 拒絶査定発送日 | "00000000"が多い |
| final_dspst_cd | 最終処分コード | 空欄が多い |
| final_dspst_dt | 最終処分日 | "00000000"が多い |
| rwrt_app_num | 書換申請番号 | "0000000000"固定 |
| old_law | 旧法類 | 空欄が多い |
| ver_num | 版コード | "C1"固定 |
| intl_reg_num | 国際登録番号 | "0000000"固定 |
| intl_reg_split_num | 国際登録分割番号 | 空欄 |
| intl_reg_dt | 国際登録日 | "00000000"固定 |
| rec_latest_updt_dt | レコード最新更新日 | YYYYMMDD形式 |
| conti_prd_expire_dt | 存続期間満了日 | YYYYMMDD形式、登録商標のみ |
| instllmnt_expr_dt_aft_des_dt | 分納満了日／事後指定日 | "00000000"が多い |
| installments_id | 分納識別 | "0"固定 |
| set_reg_dt | 設定登録日 | YYYYMMDD形式、登録商標のみ |

### 71. upd_t_dsgnt_art.tsv
**カテゴリ**: trademark_text
**カラム数**: 6
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_159_商標称呼記事ファイル.csv
**データ状況**: 83,960行、商標の称呼（カタカナ表記）、複数称呼あり
**推奨**: インポート（商標の称呼検索に必須）
**インポート対象**: ○
**主要キーカラム**: app_num, split_num, sub_data_num, dsgnt_seq

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| add_del_id | 追加削除識別 | 全行で"0"（追加） |
| app_num | 出願番号 | 10桁の出願番号 |
| split_num | 分割番号 | 空欄 |
| sub_data_num | サブデータ番号 | 空欄 |
| dsgnt_seq | 称呼順序 | 1～複数（最大3以上） |
| dsgnt | 称呼 | カタカナ表記の称呼 |

### 72. upd_t_first_indct_div.tsv
**カテゴリ**: other
**カラム数**: 10
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_129_商標第一表示部ファイル.csv
**データ状況**: 16,891行、商標登録原簿の第一表示部情報
**推奨**: インポート（登録商標の原簿管理情報）
**インポート対象**: ○
**主要キーカラム**: law_cd, reg_num, split_num, history_num

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| processing_type | 処理種別 | 全行で"0" |
| law_cd | 四法コード | "4"（商標）固定 |
| reg_num | 登録番号 | 7桁の登録番号 |
| split_num | 分割番号 | 31桁、ほぼ"0"埋め |
| history_num | 履歴番号 | "0"固定 |
| mstr_updt_year_month_day | マスタ更新年月日 | YYYYMMDD形式 |
| cancel_and_disposal_id | 取消及び廃棄識別 | 空欄 |
| intl_reg_num | 国際登録番号 | 空欄 |
| intl_reg_year_month_day | 国際登録年月日 | "00000000"固定 |
| aft_desig_year_month_day | 事後指定年月日 | "00000000"固定 |

### 73. upd_t_knd_info_art_table.tsv
**カテゴリ**: classification
**カラム数**: 6
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_160_商標類情報記事ファイル.csv
**データ状況**: 64,404行、商標の類と類似群コード情報
**推奨**: インポート（類似群コード検索に必須）
**インポート対象**: ○
**主要キーカラム**: app_num, split_num, sub_data_num, knd

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| add_del_id | 追加削除識別 | 全行で"0"（追加） |
| app_num | 出願番号 | 10桁の出願番号 |
| split_num | 分割番号 | 空欄 |
| sub_data_num | サブデータ番号 | 空欄 |
| knd | 類 | 01～45の商品・役務区分 |
| smlr_dsgn_group_cd | 類似群コード | 複数の類似群コードを連結 |

### 74. upd_t_sample.tsv
**カテゴリ**: image_data
**カラム数**: 18
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_187_商標見本ファイル.csv
**データ状況**: 10,063行、商標画像データ（Base64エンコード）
**推奨**: インポート（商標画像表示に必須）
**インポート対象**: ○
**主要キーカラム**: doc_num, page_num, rec_seq_num, year_issu_cd

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| cntry_cd | 国コード | "JP"固定（日本） |
| doc_typ | 文献種別 | "T1"固定（商標） |
| doc_num | 文献番号 | 8桁の文献番号 |
| app_num | 出願番号 | 10桁の出願番号 |
| page_num | 頁番号 | "0001"から始まる |
| rec_seq_num | レコード順序番号 | 分割レコードの順序 |
| year_issu_cd | 年号コード | "3"（昭和）,"4"（平成）等 |
| data_crt_dt | データ作成日(西暦) | YYYYMMDD形式 |
| all_page_cnt | 全頁数 | "0001"～"9999" |
| final_rec_seq_num | 最終レコード順序番号 | レコード分割数 |
| fullsize_length | 原寸の大きさ_縦 | mm単位（001～999） |
| fullsize_width | 原寸の大きさ_横 | mm単位（001～999） |
| comp_frmlchk | 圧縮方式 | "JP"（JPEG）または"M2"（MMR） |
| resolution | 解像度 | "00"（JPEG）または"16"（MMR） |
| linecnt_length | ライン数_縦 | 縦のピクセル数 |
| linecnt_width | ライン数_横 | 横のピクセル数 |
| image_data_len | イメージデータ長 | 00001～19740 |
| image_data | イメージデータ | Base64エンコードされた画像 |

### 75. upd_t_updt_art.tsv
**カテゴリ**: other
**カラム数**: 16
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_121_商標更新記事ファイル.csv
**データ状況**: 16,262行、商標権更新の履歴情報
**推奨**: インポート（商標権更新管理に必要）
**インポート対象**: ○
**主要キーカラム**: law_cd, reg_num, split_num, app_num, pe_num, mu_num

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| processing_type | 処理種別 | 全行で"0" |
| law_cd | 四法コード | "4"（商標）固定 |
| reg_num | 登録番号 | 7桁の登録番号 |
| split_num | 分割番号 | 31桁、ほぼ"0"埋め |
| app_num | 出願番号 | 10桁、古いものは"0000000000" |
| pe_num | PE番号 | 3桁、"000"～"007"等 |
| t_updt_art_upd_ymd | 商標更新記事部作成更新年月日 | YYYYMMDD形式 |
| t_updt_app_num | 商標更新出願番号 | 10桁、更新申請番号 |
| t_updt_temp_reg_flg | 商標更新仮登録の有無 | 空欄が多い |
| t_updt_title_chan_flg | 商標更新名称変更の有無 | 空欄が多い |
| t_updt_recovery_num | 商標更新回復番号 | "0000000000"が多い |
| t_updt_app_ymd_app_ymd | 商標更新出願年月日又は申請年月日 | YYYYMMDD形式 |
| t_updt_finl_dcsn_ymd | 商標更新査定年月日 | YYYYMMDD形式 |
| t_updt_trial_dcsn_ymd | 商標更新審決年月日 | "00000000"が多い |
| t_updt_reg_year_month_day | 商標更新登録年月日 | YYYYMMDD形式 |
| mu_num | MU番号 | "000"固定 |

### 76. upd_t_vienna_class_grphc_term_art.tsv
**カテゴリ**: classification
**カラム数**: 8
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_161_ウィーン分類図形ターム記事ファイル.csv
**データ状況**: 100,370行、図形商標のウィーン分類コード
**推奨**: インポート（図形商標検索に必要）
**インポート対象**: ○
**主要キーカラム**: app_num, split_num, sub_data_num, grphc_term_large_class, grphc_term_mid_class, grphc_term_small_class, grphc_term_complement_sub_cls

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| add_del_id | 追加削除識別 | 全行で"0"（追加） |
| app_num | 出願番号 | 10桁の出願番号 |
| split_num | 分割番号 | 空欄 |
| sub_data_num | サブデータ番号 | 空欄 |
| grphc_term_large_class | 図形ターム大分類 | 01～29の2桁 |
| grphc_term_mid_class | 図形ターム中分類 | 01～99の2桁 |
| grphc_term_small_class | 図形ターム小分類 | 01～99の2桁 |
| grphc_term_complement_sub_cls | 図形ターム細分類 | 00～99の2桁 |

### 77. upd_tkky_snku_bnkn.tsv
**カテゴリ**: other
**カラム数**: 5
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_243_特許参考文献ファイル.csv
**データ状況**: 1,044行、審判での特許参考文献情報
**推奨**: スキップ（審判事件の参考文献、商標検索には不要）
**インポート対象**: ×

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| skbt_flg | 識別フラグ | 全行で"0" |
| snpn_bngu | 審判番号 | 審判番号 |
| krkes_bngu | 繰返番号 | 1から始まる連番 |
| tkky_snku_bnknmi | 特許参考文献名 | 特許番号等の文献名 |
| kusn_ntz_bat | 更新通知バッチ | YYYYMMDD形式+"000000" |

### 78. upd_trnsfr_rcpt_info_t.tsv
**カテゴリ**: other
**カラム数**: 8
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_119_移転受付情報ファイル(商標).csv
**データ状況**: 25,078行、商標権の移転受付情報
**推奨**: インポート（商標権移転履歴の管理）
**インポート対象**: ○
**主要キーカラム**: law_cd, reg_num, split_num, app_num, mu_num

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| processing_type | 処理種別 | 全行で"0" |
| law_cd | 四法コード | "4"（商標）固定 |
| reg_num | 登録番号 | 7桁の登録番号 |
| split_num | 分割番号 | 31桁、ほぼ"0"埋め |
| app_num | 出願番号 | 10桁の出願番号 |
| mrgn_info_upd_ymd | 欄外情報部作成更新年月日 | YYYYMMDD形式 |
| mu_num | MU番号 | "000"固定 |
| trnsfr_rcpt_info | 移転受付情報 | 受付番号＋日付＋移転名称 |

### 79. upd_tyuni_syri.tsv
**カテゴリ**: status_management
**カラム数**: 17
**CSV仕様書**: 特定できず（実データから推測）
**データ状況**: 6,570行、審判事件の庁内中間書類情報
**推奨**: スキップ（審判事件の庁内書類、商標検索には不要）
**インポート対象**: ×

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| skbt_flg | 識別フラグ | 全行で"0" |
| tyuni_syri_bngu | 庁内書類番号 | 11桁の番号 |
| snpn_bngu | 審判番号 | 10桁の審判番号 |
| tyukn_cd | 中間コード | "C91"～"C95"等 |
| kan_dt | 完了日 | 空欄が多い |
| tyukn_krk_hyuzjn_kjn_dt | 中間記録表示基準日 | YYYYMMDD形式 |
| atsk_sybt | 宛先種別 | 空欄または"4" |
| ig_tuzsy_bngu | 意見通知書番号 | 空欄または"001"等 |
| snk_snsi_bngu | 審査審査番号 | 空欄 |
| tyuni_syri_sksi_dt | 中間書類作成日 | YYYYMMDD形式 |
| yuku_flg | 有効フラグ | 空欄 |
| tiou_mk | 対応マーク | 空欄 |
| etrn_kns_flg | 電子化フラグ | 空欄 |
| syri_fomt_sybt | 書類フォーマット種別 | 空欄 |
| tyuni_syri_img_pagesu | 中間書類画像ページ数 | 空欄 |
| syri_siz | 書類サイズ | 空欄 |
| kusn_ntz_bat | 更新通知バッチ | YYYYMMDD形式+"000000" |

### 80. upd_uktk_syri.tsv
**カテゴリ**: status_management
**カラム数**: 27
**CSV仕様書**: 特定できず（実データから推測）
**データ状況**: 5,425行、審判事件の受付書類情報
**推奨**: スキップ（審判事件の受付書類、商標検索には不要）
**インポート対象**: ×

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| skbt_flg | 識別フラグ | 全行で"0" |
| uktk_syri_bngu | 受付書類番号 | 11桁の番号 |
| snpn_bngu | 審判番号 | 10桁の審判番号 |
| tyukn_cd | 中間コード | "A51","C60"等 |
| syri_ssds_dt | 書類送信日 | 空欄 |
| syri_uktk_dt | 書類受付日 | YYYYMMDD形式 |
| sri_kykr_kbn | 書類局区分 | "1"固定 |
| husk_sybn_stat | 発送書番ステータス | "1"固定 |
| hssu_syri_bngu | 発送書類番号 | 空欄 |
| sir_bngu | 書類番号 | 空欄 |
| syri_sybt_cd | 書類種別コード | "T100"等 |
| syri_bnri_cd | 書類分類コード | "17"等 |
| yuku_flg | 有効フラグ | 空欄 |
| tiou_mk | 対応マーク | 空欄 |
| etrn_kns_flg | 電子化フラグ | "1"が多い |
| hnku_tisyu_sytgnnn_dirnn_cd | 判定対象出願番号方向コード | 空欄 |
| yusnkn_tisytkk_cd | 優先権対象特許コード | 空欄 |
| syri_ztti_rrk_bngu | 書類全体履歴番号 | 空欄 |
| misisy_ver | ミシシーバージョン | "V2"等 |
| mkug_syri_um | 枚数書類数 | 数値 |
| syri_fomt_sybt | 書類フォーマット種別 | "S-HTML"等 |
| tksk_bngu | 特許番号 | 空欄 |
| dna_hirthyu_um | DNA配列数 | 空欄 |
| yuyksy_tnp_syri_sikyu_hni_um | 優先審査転送書類至急範囲数 | 空欄 |
| tnp_syri_pagesu | 転送書類ページ数 | 空欄 |
| syri_siz | 書類サイズ | 数値（バイト） |
| kusn_ntz_bat | 更新通知バッチ | YYYYMMDD形式+"000000" |

### 81. upd_under_integ_appl_info_mgt.tsv
**カテゴリ**: applicant_agent
**カラム数**: 3
**CSV仕様書**: （別添3.3）ファイル仕様書_1.13版_056_申請人登録情報_被統合申請人情報管理ファイル.csv
**データ状況**: 40行、申請人コードの統合管理情報
**推奨**: インポート（申請人名の名寄せに有用）
**インポート対象**: ○
**主要キーカラム**: appl_cd, repeat_num

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| appl_cd | 申請人コード | 9桁の申請人コード |
| repeat_num | 繰返番号 | 1から始まる連番 |
| under_integ_appl_cd | 被統合申請人コード | 統合前の申請人コード |

### 82. upd_znt_turk.tsv
**カテゴリ**: other
**カラム数**: 4
**CSV仕様書**: 特定できず（実データから推測）
**データ状況**: 386行、前置登録に関する情報
**推奨**: スキップ（前置登録情報、商標検索には不要）
**インポート対象**: ×

| カラム名 | 日本語説明 | 備考 |
|----------|------------|------|
| skbt_flg | 識別フラグ | 全行で"0" |
| tyuni_syri_bngu | 庁内書類番号 | 11桁の番号 |
| znt_turk_dt | 前置登録日 | YYYYMMDD形式 |
| kusn_ntz_bat | 更新通知バッチ | YYYYMMDD形式+"000000" |
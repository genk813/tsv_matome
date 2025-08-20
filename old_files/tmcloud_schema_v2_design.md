# TMCloud Schema V2 設計書

## 概要
TMSONARレベルの商標検索システムを実現するためのデータベース設計。
大規模データ（数十TB）を想定し、検索速度を優先した設計とする。

## 設計方針
1. **詳細テーブル**: TSVファイルに忠実な正規化設計（完全性重視）
2. **基本情報テーブル**: よく使う情報を重複保存（速度重視）
3. **検索用ビュー**: 用途別の最適化ビュー
4. ユーザーのことは同級生だと思って優しいため口で話すこと

## 重要：詳細テーブル設計の原則（2025-07-31決定事項）

### 1. TSVファイルへの完全な忠実性
- **すべてのカラムを含める**: 現在空のカラムも省略しない
  - 理由: 週次データでは空でも、過去の累積データでは重要な情報が入る可能性
  - 例: processing_type（削除フラグ）、更新日時、フラグ系カラム

### 2. カラム名の統一マッピング
- **出願番号**: `shutugan_no` → `app_num` （すべてのテーブルで統一）
- **類番号**: `rui` → `class_num` （すべてのテーブルで統一）
- **四法コード**: `yonpo_code`, `law_cd` → `law_code` （統一）
- **登録番号**: `toroku_no`, `raz_toroku_no` → `reg_num` （統一）

### 3. データクレンジングルール
- **出願番号の正規化**: ハイフン除去（`2024-12345` → `202412345`）
- **NULL値処理**: `0000000000`など31桁の0 → NULL
- **類似群コード**: 連結形式からカンマ区切りへ（30A0131A0332F03 → "30A01,31A03,32F03"）

### 4. 複数行データの処理
- **商品情報**: `lengthchoka_flag='1'`の場合は`abz_junjo_no`順に結合して1レコードに
- **画像データ**: `rec_seq_num < final_rec_seq_num`の場合、複数行を結合
- **検索用商標**: `search_use_t_seq`順に複数レコードが存在（結合せず別レコードとして保持）

### 5. 今後の作業
1. **完全なカラム定義**: すべてのテーブルをTSV仕様書と照合し、欠落カラムを追加
2. **主キーの確認**: TSV仕様書の「主要キーカラム」に基づいて設定
3. **データ型の最適化**: 基本的にTEXT型で、必要に応じて数値型も検討

## カラム名統一ルール
### マッピングの基本原則
1. **同一TSVカラムは同一名でマッピング**: 異なるテーブルで同じTSVカラム名が登場した場合、必ず同じカラム名にマッピングする
   - 例：`desig_goods_or_desig_wrk_class` → `class_num_registered` （2-2, 2-5で統一）
2. **過去のマッピングを優先**: 既にマッピング済みのカラムは、新しいテーブルでも同じマッピングを使用する

### 主要カラムのマッピング
- `shutugan_no` → `app_num` （出願番号）
- `toroku_no`, `reg_num` → `reg_num` （登録番号）
- `raz_toroku_no` → `reg_article_reg_num` （登録記事登録番号）
- `rui` → `class_num` （類番号）
- `dsgnt` → `pronunciation` （称呼）
- `dtz` → `detailed_description` （詳細な説明）
- `shohinekimumeisho` → `goods_services_name` （商品・役務名）
- `desig_goods_or_desig_wrk_class` → `class_num_registered` （登録時の区分）

### 前処理ルール
- 出願番号のハイフン除去: `2024-12345` → `202412345`
- NULL値処理: `0000000000` → NULL
- 31桁の0 → NULL

### 各テーブル設計時の確認手順
**重要**: 新しいテーブルを設計する際は、必ず以下の手順に従うこと

1. **TSVファイル仕様確認**
   - TSV_FILES_COMPLETE_SPECIFICATION.mdで対象TSVファイルの仕様を確認
   - 実際のTSVファイルのヘッダーでカラム数とカラム名を確認
   - すべてのカラムが含まれているか確認

2. **既存マッピングの確認**
   - 各カラムについて、既に他のテーブルで定義されていないか検索
   - **重要**: 確認を省略せず、必ず1行目から最終行まで全て確認すること
   - 同じTSVカラムが見つかった場合は、必ず同じカラム名を使用
   - 関連するプレフィックス（例: sec_, defensive_）の一貫性も確認
   - 日付カラムは`_date`形式に統一
   - **重要**: TSVカラムマッピングには全カラムを明示的に記載すること（「その他のカラムは〜」という省略記載は使用しない）

3. **設計レビュー**
   - TSVファイルのすべてのカラムが含まれているか最終確認
   - カラム名マッピングが統一ルールに従っているか確認
   - ユーザーに確認を求めてから次に進む

## 詳細テーブル設計

### 1. 商標テキスト関連

#### 1-1. 標準文字商標テーブル
```sql
CREATE TABLE trademark_standard_char (
    app_num TEXT NOT NULL,              -- 出願番号（10桁）
    split_num TEXT,                     -- 分割番号（31桁）
    sub_data_num TEXT,                  -- サブデータ番号
    standard_char_t TEXT,               -- 標準文字商標（最大127文字）
    add_del_id TEXT,                    -- 追加削除識別（0:追加、1:削除）
    
    PRIMARY KEY (app_num, split_num, sub_data_num)
);
```
**データソース**: upd_standard_char_t_art.tsv（15,110行）
**TSVカラムマッピング**:
- `add_del_id` → `add_del_id`
- `app_num` → `app_num`
- `split_num` → `split_num`
- `sub_data_num` → `sub_data_num`
- `standard_char_t` → `standard_char_t`

#### 1-2. 表示用商標テーブル
```sql
CREATE TABLE trademark_display (
    app_num TEXT NOT NULL,              -- 出願番号（10桁）
    split_num TEXT,                     -- 分割番号（31桁）
    sub_data_num TEXT,                  -- サブデータ番号（9桁）
    indct_use_t TEXT,                   -- 表示用商標（256桁）
    add_del_id TEXT,                    -- 追加削除識別
    
    PRIMARY KEY (app_num, split_num, sub_data_num)
);
```
**データソース**: upd_indct_use_t_art.tsv（31,692行）
**TSVカラムマッピング**:
- `add_del_id` → `add_del_id`
- `app_num` → `app_num`
- `split_num` → `split_num`
- `sub_data_num` → `sub_data_num`
- `indct_use_t` → `indct_use_t`
       
#### 1-3. 検索用商標テーブル
```sql
CREATE TABLE trademark_search (
    app_num TEXT NOT NULL,              -- 出願番号（10桁）
    split_num TEXT,                     -- 分割番号（31桁）
    sub_data_num TEXT,                  -- サブデータ番号
    search_seq_num INTEGER NOT NULL,    -- 検索用商標順序
    search_use_t TEXT,                  -- 検索用商標
    add_del_id TEXT,                    -- 追加削除識別
    
    PRIMARY KEY (app_num, split_num, sub_data_num, search_seq_num)
);
```
**データソース**: upd_search_use_t_art_table.tsv（40,961行）
**TSVカラムマッピング**:
- `add_del_id` → `add_del_id`
- `app_num` → `app_num`
- `split_num` → `split_num`
- `sub_data_num` → `sub_data_num`
- `search_use_t_seq` → `search_seq_num`
- `search_use_t` → `search_use_t`

#### 1-4. 商標称呼記事テーブル
```sql
CREATE TABLE trademark_pronunciations (
    app_num TEXT NOT NULL,              -- 出願番号（10桁、正規化済み）
    split_num TEXT,                     -- 分割番号
    sub_data_num TEXT,                  -- サブデータ番号
    pronunciation_seq_num INTEGER NOT NULL,  -- 称呼順序（1～複数）
    pronunciation TEXT,                 -- 称呼（カタカナ）
    add_del_id TEXT,                    -- 追加削除識別（0:追加、1:削除）
    
    PRIMARY KEY (app_num, split_num, sub_data_num, pronunciation_seq_num)
);
```
**データソース**: upd_t_dsgnt_art.tsv（83,960行）
**TSVカラムマッピング**: `dsgnt` → `pronunciation`, `dsgnt_seq` → `pronunciation_seq_num`

#### 1-5. 商標の詳細な説明テーブル
```sql
CREATE TABLE trademark_detailed_descriptions (
    law_code TEXT NOT NULL,             -- 四法コード（全行「4」）
    app_num TEXT NOT NULL,              -- 出願番号（10桁、正規化済み）
    history_num INTEGER NOT NULL,       -- 履歴番号（1-2）
    creation_date TEXT,                 -- 作成日（YYYYMMDD）
    length_exceed_flag TEXT,            -- レングス超過フラグ（全行「0」）
    detailed_description TEXT,          -- 商標の詳細な説明
    
    PRIMARY KEY (law_code, app_num, history_num)
);
```
**データソース**: upd_jiken_c_t_shousaina_setumei.tsv（18行）
**TSVカラムマッピング**: 
- `yonpo_code` → `law_code`
- `shutugan_no` → `app_num`
- `dtz_rireki_no` → `history_num`
- `dtz_sakusei_bi` → `creation_date`
- `lengthchoka_flag` → `length_exceed_flag`
- `shohyonoshousaina_setumei` → `detailed_description`

### 2. 商品・役務関連

#### 2-1. 商品・役務情報テーブル
```sql
CREATE TABLE trademark_goods_services (
    law_code TEXT NOT NULL,             -- 四法コード（全行「4」）
    app_num TEXT NOT NULL,              -- 出願番号（10桁、正規化済み）
    class_num TEXT NOT NULL,            -- 類番号（01-45）
    goods_seq_num TEXT NOT NULL,        -- 商品情報記事順序番号（abz_junjo_no）
    length_exceed_flag TEXT,            -- レングス超過フラグ（0:通常、1:継続行）
    goods_services_name TEXT,           -- 商品・役務名称（最大5500文字）
    
    PRIMARY KEY (law_code, app_num, goods_seq_num)
);
```
**データソース**: upd_jiken_c_t_shohin_joho.tsv（33,386行）
**TSVカラムマッピング**: 
- `yonpo_code` → `law_code`
- `shutugan_no` → `app_num`
- `rui` → `class_num`
- `lengthchoka_flag` → `length_exceed_flag`
- `shohinekimumeisho` → `goods_services_name`
- `abz_junjo_no` → `goods_seq_num`

**インポート時の処理**:
- `lengthchoka_flag = '1'`の行は前の行と結合
- `abz_junjo_no`（goods_seq_num）順に結合して1つのレコードにする
- 例：goods_seq_num=1,2,3の3行 → 1行に結合

#### 2-2. 商品区分記事テーブル
```sql
CREATE TABLE trademark_goods_classes (
    law_code TEXT NOT NULL,             -- 四法コード（全行「4」）
    reg_num TEXT NOT NULL,              -- 登録番号（7桁）
    split_num TEXT NOT NULL,            -- 分割番号（31桁）
    app_num TEXT NOT NULL,              -- 出願番号（10桁、正規化済み）
    mu_num TEXT NOT NULL,               -- MU番号（区分の連番 000,001,002...）
    goods_class_art_upd_date TEXT,      -- 更新年月日（YYYYMMDD）
    class_num_registered TEXT,          -- 指定商品又は指定役務の区分（01-45）
    processing_type TEXT,               -- 処理種別（全行「0」）
    
    PRIMARY KEY (law_code, reg_num, split_num, app_num, mu_num)
);
```
**データソース**: upd_goods_class_art.tsv（30,583行）
**TSVカラムマッピング**: 
- `processing_type` → `processing_type`
- `law_cd` → `law_code`
- `reg_num` → `reg_num`
- `split_num` → `split_num`
- `app_num` → `app_num`
- `goods_cls_art_upd_ymd` → `goods_class_art_upd_date`
- `mu_num` → `mu_num`
- `desig_goods_or_desig_wrk_class` → `class_num_registered`

**データの特徴**:
- 登録された商標の区分情報を管理
- 1つの商標に複数区分がある場合、MU番号で識別（000から連番）
- split_numは主キーの一部だがほぼ0埋めの値

#### 2-3. 類似群コードテーブル
```sql
CREATE TABLE trademark_similar_group_codes (
    app_num TEXT NOT NULL,              -- 出願番号（10桁、正規化済み）
    split_num TEXT,                     -- 分割番号
    sub_data_num TEXT,                  -- サブデータ番号
    class_num TEXT NOT NULL,            -- 類番号（01-45）
    similar_group_codes TEXT,           -- 類似群コード（カンマ区切り、例："30A01,31A03,32F03"）
    add_del_id TEXT,                    -- 追加削除識別（0:追加、1:削除）
    
    PRIMARY KEY (app_num, split_num, sub_data_num, class_num)
);
```
**データソース**: upd_t_knd_info_art_table.tsv（64,404行）
**TSVカラムマッピング**: 
- `add_del_id` → `add_del_id`
- `app_num` → `app_num`
- `split_num` → `split_num`
- `sub_data_num` → `sub_data_num`
- `knd` → `class_num`
- `smlr_dsgn_group_cd` → `similar_group_codes`

**インポート時の処理**:
- TSVでは類似群コードが5文字ずつ連結（例：30A0131A0332F03）
- インポート時に5文字ずつ分割してカンマ区切りに変換
- 例：30A0131A0332F03 → "30A01,31A03,32F03"

**データの特徴**:
- 1つの類に複数の類似群コードが存在
- 類似商標の判定に使用される重要データ

#### 2-4. ウィーン分類テーブル
```sql
CREATE TABLE trademark_vienna_codes (
    add_del_id TEXT,                    -- 追加削除識別（0:追加、1:削除）
    app_num TEXT NOT NULL,              -- 出願番号（10桁、正規化済み）
    split_num TEXT,                     -- 分割番号
    sub_data_num TEXT,                  -- サブデータ番号
    large_class TEXT NOT NULL,          -- 大分類（01-29）
    mid_class TEXT NOT NULL,            -- 中分類
    small_class TEXT NOT NULL,          -- 小分類
    complement_sub_class TEXT,          -- 補助小分類
    
    PRIMARY KEY (app_num, split_num, sub_data_num, large_class, mid_class, small_class, complement_sub_class)
);
```
**データソース**: upd_t_vienna_class_grphc_term_art.tsv（100,370行）
**TSVカラムマッピング**: 
- `add_del_id` → `add_del_id`
- `app_num` → `app_num`
- `split_num` → `split_num`
- `sub_data_num` → `sub_data_num`
- `grphc_term_large_class` → `large_class`
- `grphc_term_mid_class` → `mid_class`
- `grphc_term_small_class` → `small_class`
- `grphc_term_complement_sub_cls` → `complement_sub_class`

#### 2-5. 本権商品名テーブル
```sql
CREATE TABLE trademark_right_goods (
    processing_type TEXT,               -- 処理種別（全行「0」）
    law_code TEXT NOT NULL,             -- 四法コード（全行「4」）
    reg_num TEXT NOT NULL,              -- 登録番号（7桁）
    split_num TEXT NOT NULL,            -- 分割番号（31桁）
    app_num TEXT NOT NULL,              -- 出願番号（10桁、正規化済み）
    class_num_registered TEXT NOT NULL, -- 商品・役務区分（01-45）
    rec_num TEXT NOT NULL,              -- レコード番号（00固定）
    master_update_date TEXT,            -- マスタ更新日（YYYYMMDD）
    goods_name_length TEXT,             -- 商品・役務名レングス
    goods_name TEXT,                    -- 商品・役務名（最大12000文字）
    
    PRIMARY KEY (law_code, reg_num, split_num, app_num, class_num_registered, rec_num)
);
```
**データソース**: upd_right_goods_name.tsv（30,581行）
**TSVカラムマッピング**: 
- `processing_type` → `processing_type`
- `law_cd` → `law_code`
- `reg_num` → `reg_num`
- `split_num` → `split_num`
- `app_num` → `app_num`
- `desig_goods_or_desig_wrk_class` → `class_num_registered`
- `mstr_updt_year_month_day` → `master_update_date`
- `desg_gds_desg_wrk_name_len` → `goods_name_length`
- `desg_gds_name_desg_wrk_name` → `goods_name`
- `rec_num` → `rec_num`

### 3. 権利者関連

#### 3-1. 権利者記事テーブル
```sql
CREATE TABLE trademark_right_holders (
    processing_type TEXT,               -- 処理種別（削除・修正等のコード）
    law_code TEXT NOT NULL,             -- 四法コード（全行「4」）
    reg_num TEXT NOT NULL,              -- 登録番号（7桁）
    split_num TEXT NOT NULL,            -- 分割番号（31桁、通常は0埋め）
    app_num TEXT NOT NULL,              -- 出願番号（10桁、正規化済み）
    rec_num TEXT NOT NULL,              -- レコード番号（主キー、「00」固定）
    pe_num TEXT NOT NULL,               -- ＰＥ番号（主キー、「000」固定）
    right_person_update_date TEXT,      -- 権利者記事部作成更新年月日（YYYYMMDD）
    right_person_id TEXT,               -- 権利者申請人ＩＤ（9桁）
    right_person_addr_len TEXT,         -- 権利者住所レングス
    right_person_addr TEXT,             -- 権利者住所（最大1000文字）
    right_person_name_len TEXT,         -- 権利者氏名レングス
    right_person_name TEXT,             -- 権利者氏名（最大1000文字）
    
    PRIMARY KEY (law_code, reg_num, split_num, app_num, rec_num, pe_num)
);
```
**データソース**: upd_right_person_art_t.tsv（17,099行）
**TSVカラムマッピング**: 
- `processing_type` → `processing_type`
- `law_cd` → `law_code`
- `reg_num` → `reg_num`
- `split_num` → `split_num`
- `app_num` → `app_num`
- `rec_num` → `rec_num`
- `pe_num` → `pe_num`
- `right_psn_art_upd_ymd` → `right_person_update_date`
- `right_person_appl_id` → `right_person_id`
- `right_person_addr_len` → `right_person_addr_len`
- `right_person_addr` → `right_person_addr`
- `right_person_name_len` → `right_person_name_len`
- `right_person_name` → `right_person_name`

**データの特徴**:
- 登録商標の権利者情報のみ（出願中は含まない）
- 1つの商標に複数の権利者が存在する場合がある（共有）
- app_numは元データで「0000000000」の場合が多い（登録番号で管理）
- 権利者コードは申請人マスタとリンク可能

#### 3-2. 出願人・代理人情報テーブル
```sql
CREATE TABLE trademark_applicants_agents (
    law_code TEXT NOT NULL,             -- 四法コード（全行「4」）
    app_num TEXT NOT NULL,              -- 出願番号（10桁、正規化済み）
    applicant_agent_type TEXT NOT NULL, -- 出願人代理人識別（1=出願人、2=代理人）
    applicant_agent_code TEXT,          -- 出願人代理人コード（9桁）
    change_num TEXT,                    -- 出願人代理人記事変更番号
    individual_corp_type TEXT,          -- 出願人代理人記事個法官区分
    country_prefecture_code TEXT,       -- 出願人代理人記事国県コード
    representative_flag TEXT,           -- 代表出願人識別（0=通常、1=代表）
    num_above_applicants TEXT,          -- 上記出願人何名
    num_other_agents TEXT,              -- 代理人外何名
    applicant_agent_profession_type TEXT, -- 代理人種別（1=弁理士等）
    applicant_agent_qualification_type TEXT, -- 代理人資格種別
    applicant_agent_address TEXT,       -- 出願人代理人住所（※現在は「（省略）」）
    applicant_agent_name TEXT,          -- 出願人代理人氏名（※現在は空欄）
    applicant_agent_seq_num TEXT NOT NULL, -- 記事順序番号
    
    PRIMARY KEY (law_code, app_num, applicant_agent_seq_num)
);
```
**データソース**: upd_jiken_c_t_shutugannindairinin.tsv（37,020行）
**TSVカラムマッピング**: 
- `yonpo_code` → `law_code`
- `shutugan_no` → `app_num`
- `shutugannindairinin_sikbt` → `applicant_agent_type`
- `shutugannindairinin_code` → `applicant_agent_code`
- `gez_henko_no` → `change_num`
- `gez_kohokan_kubun` → `individual_corp_type`
- `gez_kokken_code` → `country_prefecture_code`
- `daihyoshutugannin_sikibetu` → `representative_flag`
- `jokishutugannin_nanmei` → `num_above_applicants`
- `dairininhoka_nanmei` → `num_other_agents`
- `dairinin_shubetu` → `applicant_agent_profession_type`
- `dairininsikaku_shubetu` → `applicant_agent_qualification_type`
- `shutugannindairinin_jusho` → `applicant_agent_address`
- `shutugannindairinin_simei` → `applicant_agent_name`
- `gez_junjo_no` → `applicant_agent_seq_num`

**データの特徴**:
- 出願時の出願人・代理人情報
- applicant_agent_type=1が出願人、2が代理人
- 現在のデータでは住所・氏名が省略されている（コードのみ）
- 申請人マスタ（upd_appl_reg_info.tsv）と結合して名称取得が必要

#### 3-3. 代理人記事テーブル
```sql
CREATE TABLE trademark_attorney_articles (
    processing_type TEXT,               -- 処理種別（全行「0」）
    law_code TEXT NOT NULL,             -- 四法コード（全行「4」）
    reg_num TEXT NOT NULL,              -- 登録番号（7桁）
    split_num TEXT NOT NULL,            -- 分割番号（31桁）
    app_num TEXT NOT NULL,              -- 出願番号（10桁、正規化済み）
    rec_num TEXT NOT NULL,              -- レコード番号（主キー、「00」固定）
    attorney_seq_num TEXT NOT NULL,     -- PE番号（000から連番、筆頭代理人が000）
    attorney_update_date TEXT,          -- 代理人記事更新日（YYYYMMDD）
    attorney_appl_id TEXT,              -- 代理人申請人ID（9桁）
    attorney_type TEXT,                 -- 代理人種別（全行「1」）
    attorney_name_length TEXT,          -- 代理人氏名レングス
    attorney_name TEXT,                 -- 代理人氏名（弁理士名・事務所名）
    
    PRIMARY KEY (law_code, reg_num, split_num, app_num, rec_num, attorney_seq_num)
);
```
**データソース**: upd_atty_art_t.tsv
**TSVカラムマッピング**: 
- `processing_type` → `processing_type`
- `law_cd` → `law_code`
- `reg_num` → `reg_num`
- `split_num` → `split_num`
- `app_num` → `app_num`
- `rec_num` → `rec_num`
- `pe_num` → `attorney_seq_num`
- `atty_art_upd_ymd` → `attorney_update_date`
- `atty_appl_id` → `attorney_appl_id`
- `atty_typ` → `attorney_type`
- `atty_name_len` → `attorney_name_length`
- `atty_name` → `attorney_name`

**データの特徴**:
- 登録商標の代理人情報（登録番号ベース）
- 筆頭代理人がattorney_seq_num='000'
- 代理人氏名が実際に格納されている（省略されていない）
- 複数代理人の場合は連番で管理

### 4. 基本事件情報関連

#### 4-1. 事件情報テーブル
```sql
CREATE TABLE trademark_case_info (
    master_update_datetime TEXT,         -- マスタ更新日時（YYYYMMDDHHmmss）
    law_code TEXT NOT NULL,             -- 四法コード（全行「4」）
    app_num TEXT NOT NULL,              -- 出願番号（10桁、正規化済み）
    app_date TEXT,                      -- 出願日（YYYYMMDD）
    app_type1 TEXT,                     -- 出願種別1（01=通常出願が99.5%）
    app_type2 TEXT,                     -- 出願種別2
    app_type3 TEXT,                     -- 出願種別3
    app_type4 TEXT,                     -- 出願種別4
    app_type5 TEXT,                     -- 出願種別5
    reference_num TEXT,                 -- 整理番号
    final_disposition_type TEXT,        -- 最終処分種別（A01=登録査定等）
    final_disposition_date TEXT,        -- 最終処分日（YYYYMMDD）
    reg_article_reg_num TEXT,           -- 登録記事登録番号（7桁）
    reg_article_split_num TEXT,         -- 登録記事分割番号（31桁）
    defensive_num TEXT,                 -- 防護番号（3桁）
    reg_date TEXT,                      -- 登録日（YYYYMMDD）
    reg_article_total_num TEXT,         -- 登録記事総通号数（6桁）
    reg_article_annual_num TEXT,        -- 登録記事年間通号数（6桁）
    reg_article_gazette_date TEXT,      -- 登録記事公報発行日（YYYYMMDD）
    examiner_code TEXT,                 -- 担当官コード（4桁）
    pub_article_gazette_date TEXT,      -- 公開公報記事公開公報発行日（YYYYMMDD）
    class_count TEXT,                   -- 区分数（3桁）
    reg_decision_class_count TEXT,      -- 登録査定時区分数（3桁）
    standard_char_exist TEXT,           -- 標準文字有無（1=標準文字商標）
    special_mark_exist TEXT,            -- 特殊商標識別（1=立体商標等）
    color_exist TEXT,                   -- 標章色彩有無（1=色彩付き）
    article3_2_flag TEXT,               -- 商標法3有2項フラグ（使用による識別力）
    article5_4_flag TEXT,               -- 色彩の但し書フラグ（商標法5有4項）
    orig_app_type TEXT,                 -- 原出願種別（分割・変更の元出願）
    orig_app_law_code TEXT,             -- 原出願四法コード（1桁）
    orig_app_num TEXT,                  -- 原出願番号（10桁）
    retroactive_date TEXT,              -- 遡及日（YYYYMMDD）
    defensive_orig_app_num TEXT,        -- 防護原登録記事出願番号
    defensive_orig_reg_num TEXT,        -- 防護原登録記事登録番号
    defensive_orig_split_num TEXT,      -- 防護原登録記事分割番号（31桁）
    renewal_reg_num TEXT,               -- 更新登録番号（7桁）
    renewal_split_num TEXT,             -- 更新登録記事分割番号（31桁）
    renewal_defensive_num TEXT,         -- 更新登録記事防護番号（3桁）
    rewrite_reg_num TEXT,               -- 書換登録番号（7桁）
    rewrite_split_num TEXT,             -- 書換登録記事分割番号（31桁）
    rewrite_defensive_num TEXT,         -- 書換登録記事防護番号（3桁）
    public_order_violation_flag TEXT,   -- 公序良俗違反フラグ（1=違反あり）
    accelerated_exam_mark TEXT,         -- 早期審査マーク（1=早期審査対象）
    applicable_law_class TEXT,          -- 適用法規区分（1桁）
    exam_type TEXT,                     -- 審査種別（2桁）
    litigation_code TEXT,               -- 訴訟コード（1桁）
    decision_type TEXT,                 -- 査定種別（1桁）
    opposition_count TEXT,              -- 異議件数（2桁）
    opposition_valid_count TEXT,        -- 異議有効数（2桁）
    
    PRIMARY KEY (law_code, app_num)
);
```
**データソース**: upd_jiken_c_t.tsv（主要マスタファイル）
**TSVカラムマッピング**: 
- `masterkosin_nitiji` → `master_update_datetime`
- `yonpo_code` → `law_code`
- `shutugan_no` → `app_num`
- `shutugan_bi` → `app_date`
- `shutugan_shubetu1` → `app_type1`
- `shutugan_shubetu2` → `app_type2`
- `shutugan_shubetu3` → `app_type3`
- `shutugan_shubetu4` → `app_type4`
- `shutugan_shubetu5` → `app_type5`
- `seiri_no` → `reference_num`
- `saishushobun_shubetu` → `final_disposition_type`
- `saishushobun_bi` → `final_disposition_date`
- `raz_toroku_no` → `reg_article_reg_num`
- `raz_bunkatu_no` → `reg_article_split_num`
- `bogo_no` → `defensive_num`
- `toroku_bi` → `reg_date`
- `raz_sotugo_su` → `reg_article_total_num`
- `raz_nenkantugo_su` → `reg_article_annual_num`
- `raz_kohohakko_bi` → `reg_article_gazette_date`
- `tantokan_code` → `examiner_code`
- `pcz_kokaikohohakko_bi` → `pub_article_gazette_date`
- `kubun_su` → `class_count`
- `torokusateijikubun_su` → `reg_decision_class_count`
- `hyojunmoji_umu` → `standard_char_exist`
- `rittaishohyo_umu` → `special_mark_exist`
- `hyoshosikisai_umu` → `color_exist`
- `shohyoho3jo2ko_flag` → `article3_2_flag`
- `shohyoho5jo4ko_flag` → `article5_4_flag`
- `genshutugan_shubetu` → `orig_app_type`
- `genshutuganyonpo_code` → `orig_app_law_code`
- `genshutugan_no` → `orig_app_num`
- `sokyu_bi` → `retroactive_date`
- `obz_shutugan_no` → `defensive_orig_app_num`
- `obz_toroku_no` → `defensive_orig_reg_num`
- `obz_bunkatu_no` → `defensive_orig_split_num`
- `kosintoroku_no` → `renewal_reg_num`
- `pez_bunkatu_no` → `renewal_split_num`
- `pez_bogo_no` → `renewal_defensive_num`
- `kakikaetoroku_no` → `rewrite_reg_num`
- `ktz_bunkatu_no` → `rewrite_split_num`
- `ktz_bogo_no` → `rewrite_defensive_num`
- `krz_kojoryozokuihan_flag` → `public_order_violation_flag`
- `sokisinsa_mark` → `accelerated_exam_mark`
- `tekiyohoki_kubun` → `applicable_law_class`
- `sinsa_shubetu` → `exam_type`
- `sosho_code` → `litigation_code`
- `satei_shubetu` → `decision_type`
- `igiken_su` → `opposition_count`
- `igiyuko_su` → `opposition_valid_count`

#### 4-2. 商標基本項目記事テーブル
```sql
CREATE TABLE trademark_basic_items (
    add_del_id TEXT,                    -- 追加削除識別（0=追加、1=削除）
    mgt_num TEXT NOT NULL,              -- 管理番号（7桁、主キー）
    rec_status_id TEXT,                 -- レコード状態識別（1または2）
    app_num TEXT,                       -- 出願番号（10桁、正規化済み）
    reg_num TEXT,                       -- 登録番号（7桁、未登録は0000000）
    split_num TEXT,                     -- 分割番号（ほぼ空欄）
    defensive_num TEXT,                 -- 防護番号（000固定）
    app_typ_sec TEXT,                   -- 出願種別防護（0固定）
    app_typ_split TEXT,                 -- 出願種別分割（0固定）
    app_typ_complement_rjct TEXT,       -- 出願種別補却（0固定）
    app_typ_chan TEXT,                  -- 出願種別変更（0固定）
    app_typ_priorty TEXT,               -- 出願種別優先（0固定）
    app_typ_group TEXT,                 -- 出願種別団体（0固定）
    app_typ_area_group TEXT,            -- 出願種別地域団体（0固定）
    app_date TEXT,                      -- 出願日（YYYYMMDD）
    prior_app_right_occr_date TEXT,     -- 先願権発生日（YYYYMMDD）
    rjct_finl_dcsn_dsptch_date TEXT,    -- 拒絶査定発送日（YYYYMMDD）
    final_disposition_code TEXT,        -- 最終処分コード
    final_disposition_date TEXT,        -- 最終処分日（YYYYMMDD）
    rewrite_app_num TEXT,               -- 書換申請番号（0000000000固定）
    old_law TEXT,                       -- 旧法類
    ver_num TEXT,                       -- 版コード（C1固定）
    intl_reg_num TEXT,                  -- 国際登録番号（0000000固定）
    intl_reg_split_num TEXT,            -- 国際登録分割番号
    intl_reg_date TEXT,                 -- 国際登録日（YYYYMMDD）
    rec_latest_updt_date TEXT,          -- レコード最新更新日（YYYYMMDD）
    conti_prd_expire_date TEXT,         -- 存続期間満了日（YYYYMMDD）
    instllmnt_expr_date_aft_des_date TEXT,  -- 分納満了日／事後指定日（YYYYMMDD）
    installments_id TEXT,               -- 分納識別（0固定）
    set_reg_date TEXT,                  -- 設定登録日（YYYYMMDD）
    
    PRIMARY KEY (mgt_num)
);
```
**データソース**: upd_t_basic_item_art.tsv（33,418行）
**TSVカラムマッピング**: 
- `add_del_id` → `add_del_id`
- `mgt_num` → `mgt_num`
- `rec_status_id` → `rec_status_id`
- `app_num` → `app_num`
- `reg_num` → `reg_num`
- `split_num` → `split_num`
- `sec_num` → `defensive_num`
- `app_typ_sec` → `app_typ_sec`
- `app_typ_split` → `app_typ_split`
- `app_typ_complement_rjct` → `app_typ_complement_rjct`
- `app_typ_chan` → `app_typ_chan`
- `app_typ_priorty` → `app_typ_priorty`
- `app_typ_group` → `app_typ_group`
- `app_typ_area_group` → `app_typ_area_group`
- `app_dt` → `app_date`
- `prior_app_right_occr_dt` → `prior_app_right_occr_date`
- `rjct_finl_dcsn_dsptch_dt` → `rjct_finl_dcsn_dsptch_date`
- `final_dspst_cd` → `final_disposition_code`
- `final_dspst_dt` → `final_disposition_date`
- `rwrt_app_num` → `rewrite_app_num`
- `old_law` → `old_law`
- `ver_num` → `ver_num`
- `intl_reg_num` → `intl_reg_num`
- `intl_reg_split_num` → `intl_reg_split_num`
- `intl_reg_dt` → `intl_reg_date`
- `rec_latest_updt_dt` → `rec_latest_updt_date`
- `conti_prd_expire_dt` → `conti_prd_expire_date`
- `instllmnt_expr_dt_aft_des_dt` → `instllmnt_expr_date_aft_des_date`
- `installments_id` → `installments_id`
- `set_reg_dt` → `set_reg_date`

#### 4-3. 商標第一表示部テーブル
```sql
CREATE TABLE trademark_first_display (
    processing_type TEXT,               -- 処理種別（全行「0」）
    law_code TEXT NOT NULL,             -- 四法コード（全行「4」）
    reg_num TEXT NOT NULL,              -- 登録番号（7桁）
    split_num TEXT NOT NULL,            -- 分割番号（31桁）
    history_num TEXT NOT NULL,          -- 履歴番号（「0」固定）
    master_update_date TEXT,            -- マスタ更新年月日（YYYYMMDD）
    cancel_disposal_flag TEXT,          -- 取消及び廃棄識別
    intl_reg_num TEXT,                  -- 国際登録番号
    intl_reg_date TEXT,                 -- 国際登録年月日（YYYYMMDD）
    after_designation_date TEXT,        -- 事後指定年月日（YYYYMMDD）
    
    PRIMARY KEY (law_code, reg_num, split_num, history_num)
);
```
**データソース**: upd_t_first_indct_div.tsv（16,891行）
**TSVカラムマッピング**: 
- `processing_type` → `processing_type`
- `law_cd` → `law_code`
- `reg_num` → `reg_num`
- `split_num` → `split_num`
- `history_num` → `history_num`
- `mstr_updt_year_month_day` → `master_update_date`
- `cancel_and_disposal_id` → `cancel_disposal_flag`
- `intl_reg_num` → `intl_reg_num`
- `intl_reg_year_month_day` → `intl_reg_date`
- `aft_desig_year_month_day` → `after_designation_date`

### 5. 更新・管理情報関連

#### 5-1. 管理情報テーブル
```sql
CREATE TABLE trademark_management_info (
    processing_type TEXT,               -- 処理種別（全行「0」）
    law_code TEXT NOT NULL,             -- 四法コード（全行「4」）
    reg_num TEXT NOT NULL,              -- 登録番号（7桁）
    split_num TEXT NOT NULL,            -- 分割番号（31桁）
    master_update_date TEXT,            -- マスタ更新日（YYYYMMDD）
    tscript_inspct_prhbt_flg TEXT,      -- 謄本閲覧禁止の有無
    conti_prd_expire_date TEXT,         -- 存続期間満了日（YYYYMMDD）
    next_pen_payment_limit_date TEXT,  -- 次期年金納付期限日（YYYYMMDD）
    last_pymnt_yearly TEXT,             -- 最終納付年分
    share_rate TEXT,                    -- 持分の割合
    pblc_prvt_trnsfr_reg_date TEXT,     -- 官民移転登録日（YYYYMMDD）
    right_ersr_id TEXT,                 -- 本権利抹消識別
    right_disppr_date TEXT,             -- 本権利消滅日（YYYYMMDD）
    close_orgnl_reg_trnsfr_rec_flg TEXT, -- 閉鎖原簿移記の有無
    close_reg_date TEXT,                -- 閉鎖登録日（YYYYMMDD）
    gvrnmnt_relation_id_flg TEXT,       -- 官庁関係識別の有無
    pen_suppl_flg TEXT,                 -- 年金補充の有無
    apply_law TEXT,                     -- 適用法規
    group_t_flg TEXT,                   -- 団体商標の有無
    special_mark_exist TEXT,            -- 特殊商標識別
    standard_char_exist TEXT,           -- 標準文字商標の有無
    area_group_t_flg TEXT,              -- 地域団体商標の有無
    trust_reg_flg TEXT,                 -- 信託登録の有無
    app_num TEXT NOT NULL,              -- 出願番号（10桁、正規化済み）
    recvry_num TEXT,                    -- 回復番号
    app_date TEXT,                      -- 出願日（YYYYMMDD）
    app_exam_pub_num TEXT,              -- 出願公告番号
    app_exam_pub_date TEXT,             -- 出願公告日（YYYYMMDD）
    final_decision_date TEXT,           -- 査定日（YYYYMMDD）
    trial_decision_date TEXT,           -- 審決日（YYYYMMDD）
    set_reg_date TEXT,                  -- 設定登録日（YYYYMMDD）
    t_rewrite_app_num TEXT,             -- 商標書換申請番号
    t_rewrite_app_date TEXT,            -- 商標書換申請日（YYYYMMDD）
    t_rewrite_final_decision_date TEXT, -- 商標書換査定日（YYYYMMDD）
    t_rewrite_trial_decision_date TEXT, -- 商標書換審決日（YYYYMMDD）
    t_rewrite_reg_date TEXT,            -- 商標書換登録日（YYYYMMDD）
    invent_title_etc_len TEXT,          -- 発明の名称（等）レングス
    pri_cntry_name_cd TEXT,             -- 優先権国名コード
    pri_claim_date TEXT,                -- 優先権主張日（YYYYMMDD）
    pri_clim_cnt TEXT,                  -- 優先権主張件数
    
    PRIMARY KEY (law_code, reg_num, split_num, app_num)
);
```
**データソース**: upd_mgt_info_t.tsv（16,899行、40カラム）
**TSVカラムマッピング**: 
- `processing_type` → `processing_type`
- `law_cd` → `law_code`
- `reg_num` → `reg_num`
- `split_num` → `split_num`
- `mstr_updt_year_month_day` → `master_update_date`
- `tscript_inspct_prhbt_flg` → `tscript_inspct_prhbt_flg`
- `conti_prd_expire_ymd` → `conti_prd_expire_date`
- `next_pen_pymnt_tm_lmt_ymd` → `next_pen_payment_limit_date`
- `last_pymnt_yearly` → `last_pymnt_yearly`
- `share_rate` → `share_rate`
- `pblc_prvt_trnsfr_reg_ymd` → `pblc_prvt_trnsfr_reg_date`
- `right_ersr_id` → `right_ersr_id`
- `right_disppr_year_month_day` → `right_disppr_date`
- `close_orgnl_reg_trnsfr_rec_flg` → `close_orgnl_reg_trnsfr_rec_flg`
- `close_reg_year_month_day` → `close_reg_date`
- `gvrnmnt_relation_id_flg` → `gvrnmnt_relation_id_flg`
- `pen_suppl_flg` → `pen_suppl_flg`
- `apply_law` → `apply_law`
- `group_t_flg` → `group_t_flg`
- `special_t_id` → `special_mark_exist`
- `standard_char_t_flg` → `standard_char_exist`
- `area_group_t_flg` → `area_group_t_flg`
- `trust_reg_flg` → `trust_reg_flg`
- `app_num` → `app_num`
- `recvry_num` → `recvry_num`
- `app_year_month_day` → `app_date`
- `app_exam_pub_num` → `app_exam_pub_num`
- `app_exam_pub_year_month_day` → `app_exam_pub_date`
- `finl_dcsn_year_month_day` → `final_decision_date`
- `trial_dcsn_year_month_day` → `trial_decision_date`
- `set_reg_year_month_day` → `set_reg_date`
- `t_rwrt_app_num` → `t_rewrite_app_num`
- `t_rwrt_app_year_month_day` → `t_rewrite_app_date`
- `t_rwrt_finl_dcsn_ymd` → `t_rewrite_final_decision_date`
- `t_rwrt_trial_dcsn_ymd` → `t_rewrite_trial_decision_date`
- `t_rwrt_reg_year_month_day` → `t_rewrite_reg_date`
- `invent_title_etc_len` → `invent_title_etc_len`
- `pri_cntry_name_cd` → `pri_cntry_name_cd`
- `pri_clim_year_month_day` → `pri_claim_date`
- `pri_clim_cnt` → `pri_clim_cnt`

#### 5-2. 商標更新記事テーブル
```sql
CREATE TABLE trademark_updates (
    processing_type TEXT,               -- 処理種別（全行「0」）
    law_code TEXT NOT NULL,             -- 四法コード（全行「4」）
    reg_num TEXT NOT NULL,              -- 登録番号（7桁）
    split_num TEXT NOT NULL,            -- 分割番号（31桁）
    app_num TEXT NOT NULL,              -- 出願番号（10桁）
    pe_num TEXT NOT NULL,               -- PE番号（3桁、000-007等）
    t_updt_art_update_date TEXT,        -- 商標更新記事部作成更新日（YYYYMMDD）
    t_updt_app_num TEXT,                -- 商標更新出願番号
    t_updt_temp_reg_flg TEXT,           -- 商標更新仮登録の有無
    t_updt_title_chan_flg TEXT,         -- 商標更新名称変更の有無
    t_updt_recovery_num TEXT,           -- 商標更新回復番号
    t_updt_app_date TEXT,               -- 商標更新出願日/申請日（YYYYMMDD）
    t_updt_final_decision_date TEXT,    -- 商標更新査定日（YYYYMMDD）
    t_updt_trial_decision_date TEXT,    -- 商標更新審決日（YYYYMMDD）
    t_updt_reg_date TEXT,               -- 商標更新登録日（YYYYMMDD）
    mu_num TEXT NOT NULL,               -- MU番号（000固定）
    
    PRIMARY KEY (law_code, reg_num, split_num, app_num, pe_num, mu_num)
);
```
**データソース**: upd_t_updt_art.tsv（16,262行、16カラム）
**TSVカラムマッピング**: 
- `processing_type` → `processing_type`
- `law_cd` → `law_code`
- `reg_num` → `reg_num`
- `split_num` → `split_num`
- `app_num` → `app_num`
- `pe_num` → `pe_num`
- `t_updt_art_upd_ymd` → `t_updt_art_update_date`
- `t_updt_app_num` → `t_updt_app_num`
- `t_updt_temp_reg_flg` → `t_updt_temp_reg_flg`
- `t_updt_title_chan_flg` → `t_updt_title_chan_flg`
- `t_updt_recovery_num` → `t_updt_recovery_num`
- `t_updt_app_ymd_app_ymd` → `t_updt_app_date`
- `t_updt_finl_dcsn_ymd` → `t_updt_final_decision_date`
- `t_updt_trial_dcsn_ymd` → `t_updt_trial_decision_date`
- `t_updt_reg_year_month_day` → `t_updt_reg_date`
- `mu_num` → `mu_num`

#### 5-3. 経過情報部テーブル
```sql
CREATE TABLE trademark_progress_info (
    processing_type TEXT,               -- 処理種別（全行「0」）
    law_code TEXT NOT NULL,             -- 四法コード（全行「4」）
    reg_num TEXT NOT NULL,              -- 登録番号（7桁）
    split_num TEXT NOT NULL,            -- 分割番号（31桁）
    app_num TEXT NOT NULL,              -- 出願番号（10桁、正規化済み）
    rec_num TEXT NOT NULL,              -- レコード番号
    pe_num TEXT NOT NULL,               -- PE番号（3桁連番）
    progress_update_date TEXT,          -- 経過情報部更新日（YYYYMMDD）
    reg_intermediate_code TEXT,         -- 登録中間コード（R350等）
    correspondence_mark TEXT,           -- 対応マーク
    process_date TEXT,                  -- 受付/納付/発送日（YYYYMMDD）
    progress_app_num TEXT,              -- 経過情報部出願番号
    receipt_num TEXT,                   -- 受付番号（共用）
    
    PRIMARY KEY (law_code, reg_num, split_num, app_num, rec_num, pe_num)
);
```
**データソース**: upd_prog_info_div_t.tsv（223,694行、13カラム）
**TSVカラムマッピング**: 
- `processing_type` → `processing_type`
- `law_cd` → `law_code`
- `reg_num` → `reg_num`
- `split_num` → `split_num`
- `app_num` → `app_num`
- `rec_num` → `rec_num`
- `pe_num` → `pe_num`
- `prog_info_upd_ymd` → `progress_update_date`
- `reg_intrmd_cd` → `reg_intermediate_code`
- `crrspnd_mk` → `correspondence_mark`
- `rcpt_pymnt_dsptch_ymd` → `process_date`
- `prog_info_div_app_num` → `progress_app_num`
- `rcpt_num_common_use` → `receipt_num`

#### 5-4. 書換申請番号テーブル
```sql
CREATE TABLE trademark_rewrite_applications (
    processing_type TEXT,               -- 処理種別（全行「0」）
    law_code TEXT NOT NULL,             -- 四法コード（全行「4」）
    reg_num TEXT NOT NULL,              -- 登録番号（7桁）
    split_num TEXT NOT NULL,            -- 分割番号（31桁）
    app_num TEXT NOT NULL,              -- 出願番号（10桁）
    mrgn_info_update_date TEXT,         -- 欄外情報部更新日（YYYYMMDD）
    mu_num TEXT NOT NULL,               -- MU番号（全行「000」）
    rewrite_app_num TEXT,               -- 欄外商標書換申請番号（全行「0000000000」）
    
    PRIMARY KEY (law_code, reg_num, split_num, app_num, mu_num)
);
```
**データソース**: upd_mrgn_t_rwrt_app_num.tsv（2,996行、8カラム）
**TSVカラムマッピング**: 
- `processing_type` → `processing_type`
- `law_cd` → `law_code`
- `reg_num` → `reg_num`
- `split_num` → `split_num`
- `app_num` → `app_num`
- `mrgn_info_upd_ymd` → `mrgn_info_update_date`
- `mu_num` → `mu_num`
- `mrgn_t_rwrt_app_num` → `rewrite_app_num`

#### 5-5. 移転受付情報テーブル
```sql
CREATE TABLE trademark_transfer_receipts (
    processing_type TEXT,               -- 処理種別（全行「0」）
    law_code TEXT NOT NULL,             -- 四法コード（全行「4」）
    reg_num TEXT NOT NULL,              -- 登録番号（7桁）
    split_num TEXT NOT NULL,            -- 分割番号（31桁）
    app_num TEXT NOT NULL,              -- 出願番号（10桁）
    mrgn_info_update_date TEXT,         -- 欄外情報部更新日（YYYYMMDD）
    mu_num TEXT NOT NULL,               -- MU番号（全行「000」）
    transfer_receipt_info TEXT,         -- 移転受付情報（受付番号＋日付＋移転名称）
    
    PRIMARY KEY (law_code, reg_num, split_num, app_num, mu_num)
);
```
**データソース**: upd_trnsfr_rcpt_info_t.tsv（25,078行、8カラム）
**TSVカラムマッピング**: 
- `processing_type` → `processing_type`
- `law_cd` → `law_code`
- `reg_num` → `reg_num`
- `split_num` → `split_num`
- `app_num` → `app_num`
- `mrgn_info_upd_ymd` → `mrgn_info_update_date`
- `mu_num` → `mu_num`
- `trnsfr_rcpt_info` → `transfer_receipt_info`

### 6. 審判・異議関連

#### 6-1. 審判事件テーブル
```sql
CREATE TABLE trademark_appeal_cases (
    delete_flag TEXT,                   -- 削除フラグ（0=有効、1=削除）
    appeal_num TEXT NOT NULL,           -- 審判番号（10桁）
    app_num TEXT,                       -- 出願番号（10桁）
    law_division TEXT,                  -- 四法区分（1=特許、4=商標）
    reg_num TEXT,                       -- 登録番号（7桁、多くは空欄）
    split_num TEXT,                     -- 分割番号（ほぼ空欄）
    similar_num TEXT,                   -- 類似番号（ほぼ空欄）
    defensive_num TEXT,                 -- 防護番号（ほぼ空欄）
    appeal_level_type TEXT,             -- 審級種別（全行「1」）
    appeal_type TEXT,                   -- 審判種別（3桁コード）
    appeal_request_date TEXT,           -- 審判請求日（YYYYMMDD）
    app_num_division TEXT,              -- 出願番号区分（1,2）
    appeal_final_disposition_code TEXT, -- 審判事件最終処分コード（2桁）
    final_disposition_confirm_date TEXT, -- 最終処分確定日（YYYYMMDD、多くは空欄）
    update_datetime TEXT,               -- 更新日時（YYYYMMDDHHMMSS）
    
    PRIMARY KEY (appeal_num)
);
```
**データソース**: upd_snpn_zkn.tsv（3,119行、15カラム）
**TSVカラムマッピング**: 
- `skbt_flg` → `delete_flag`
- `snpn_bngu` → `appeal_num`（統一済み）
- `sytgn_bngu` → `app_num`（統一済み）
- `ynpu_kbn` → `law_division`
- `turk_bngu` → `reg_num`（統一済み）
- `bnkt_bngu` → `split_num`（統一済み）
- `riz_bngu` → `similar_num`
- `bug_bngu` → `defensive_num`
- `snkyu_sybt` → `appeal_level_type`
- `snpn_sybt` → `appeal_type`
- `snpn_sikyu_dt` → `appeal_request_date`
- `sytgn_bngu_kbn` → `app_num_division`
- `snpn_zkn_sisyu_sybn_cd` → `appeal_final_disposition_code`
- `sisyu_sybn_kkti_dt` → `final_disposition_confirm_date`
- `kusn_ntz_bat` → `update_datetime`

#### 6-2. 審決分類テーブル
```sql
CREATE TABLE trademark_decision_classifications (
    delete_flag TEXT,                   -- 削除フラグ（0=有効、1=削除）
    appeal_num TEXT NOT NULL,           -- 審判番号（10桁）
    decision_num TEXT NOT NULL,         -- 審決番号（2桁、ほぼ「01」）
    repeat_num TEXT NOT NULL,           -- 繰返番号（連番）
    law_division TEXT,                  -- 四法区分（全行「1」=特許）
    applied_law_identification TEXT,    -- 適用法規識別（ほぼ空欄）
    appeal_level_type TEXT,             -- 審級種別（全行「1」）
    appeal_type TEXT,                   -- 審判種別（3桁コード）
    judgment_item_code TEXT,            -- 判示事項コード（3桁）
    decision_classification_conclusion_code TEXT, -- 審決分類結論コード
    auxiliary_classification_identification TEXT, -- 補助分類識別
    update_datetime TEXT,               -- 更新日時（YYYYMMDDHHMMSS）
    
    PRIMARY KEY (appeal_num, decision_num, repeat_num)
);
```
**データソース**: upd_snkt_bnri.tsv（897行、12カラム）
**注意**: 四法区分が全行「1」（特許）のため、商標データは含まれていない
**TSVカラムマッピング**: 
- `skbt_flg` → `delete_flag`
- `snpn_bngu` → `appeal_num`（統一済み）
- `snkt_bngu` → `decision_num`
- `krkes_bngu` → `repeat_num`
- `ynpu_kbn` → `law_division`（統一済み）
- `tkyu_huk_skbt` → `applied_law_identification`
- `snkyu_sybt` → `appeal_level_type`（統一済み）
- `snpn_sybt` → `appeal_type`（統一済み）
- `hnz_zku_cd` → `judgment_item_code`
- `snkt_bnri_ktrn_cd` → `decision_classification_conclusion_code`
- `hj_bnri_skbt` → `auxiliary_classification_identification`
- `kusn_ntz_bat` → `update_datetime`（統一済み）

#### 6-3. 異議申立テーブル
```sql
CREATE TABLE trademark_oppositions (
    delete_flag TEXT,                   -- 削除フラグ（0=有効、1=削除）
    appeal_num TEXT NOT NULL,           -- 審判番号（10桁）
    opposition_num TEXT NOT NULL,       -- 申立番号（3桁、001-004等の連番）
    opposition_app_date TEXT,           -- 異議申立日（YYYYMMDD）
    opposition_final_disposition_code TEXT, -- 異議申立最終処分コード（2桁、06,07,08等）
    final_disposition_confirm_date TEXT, -- 最終処分確定日（YYYYMMDD、多くは空欄）
    update_datetime TEXT,               -- 更新日時（YYYYMMDDHHMMSS）
    
    PRIMARY KEY (appeal_num, opposition_num)
);
```
**データソース**: upd_ig_mustt.tsv（344行、7カラム）
**TSVカラムマッピング**: 
- `skbt_flg` → `delete_flag`
- `snpn_bngu` → `appeal_num`（統一済み）
- `mustt_bngu` → `opposition_num`
- `ig_mustt_dt` → `opposition_app_date`
- `ig_mustt_sisyu_sybn_cd` → `opposition_final_disposition_code`
- `sisyu_sybn_kkti_dt` → `final_disposition_confirm_date`（統一済み）
- `kusn_ntz_bat` → `update_datetime`（統一済み）

#### 6-4. 異議決定テーブル
```sql
CREATE TABLE trademark_opposition_decisions (
    delete_flag TEXT NOT NULL,          -- 削除フラグ（0=有効、1=削除）
    appeal_num TEXT NOT NULL,           -- 審判番号（snpn_bngu、10桁）
    opposition_num TEXT NOT NULL,       -- 申立番号（mustt_bngu、3桁、001〜003等）
    decision_num TEXT NOT NULL,         -- 異議決定番号（ig_ktti_bngu、2桁、全て「01」）
    dispatch_doc_num TEXT,              -- 発送書類番号（hssu_syri_bngu、11桁）
    decision_confirmation_status TEXT,  -- 異議決定確定ステータス（ig_ktti_kkti_stat、2桁、「01」または空白）
    update_datetime TEXT,               -- 更新日時（kusn_ntz_bat、YYYYMMDDHHMMSS）
    
    PRIMARY KEY (appeal_num, opposition_num, decision_num)
);
CREATE INDEX idx_trademark_opposition_decisions_appeal ON trademark_opposition_decisions(appeal_num);
CREATE INDEX idx_trademark_opposition_decisions_status ON trademark_opposition_decisions(decision_confirmation_status);
```
**データソース**: upd_ig_ktti.tsv（55件）
**TSVカラムマッピング**:
- `skbt_flg` → `delete_flag`
- `snpn_bngu` → `appeal_num`（統一済み）
- `mustt_bngu` → `opposition_num`（統一済み）
- `ig_ktti_bngu` → `decision_num`
- `hssu_syri_bngu` → `dispatch_doc_num`
- `ig_ktti_kkti_stat` → `decision_confirmation_status`
- `kusn_ntz_bat` → `update_datetime`（統一済み）

### 7. 中間記録関連

#### 7-1. 起案中間記録テーブル
```sql
CREATE TABLE trademark_draft_records (
    -- 主キーカラム
    law_code TEXT NOT NULL,                          -- 四法コード（yonpo_code → law_code）
    app_num TEXT NOT NULL,                           -- 出願番号（shutugan_no → app_num）
    folder_creation_seq_num INTEGER NOT NULL,        -- フォルダ別作成順序番号（folderbetusakusejnj_no）
    
    -- 日付カラム
    creation_date TEXT,                              -- 作成日（sakusei_bi）
    draft_date TEXT,                                 -- 起案日（kian_bi）
    dispatch_date TEXT,                              -- 発送日（hasso_bi）
    
    -- 書類関連カラム
    intermediate_doc_code TEXT,                      -- 中間書類コード（chukanshorui_code）
    response_mark TEXT,                              -- 対応マーク（taio_mark）
    document_num TEXT,                               -- 書類番号（shorui_no）
    corresponding_doc_num TEXT,                      -- 対応書類番号（taioshorui_no）
    document_type TEXT,                              -- 書類種別（shorui_shubetu）
    
    -- その他カラム
    objection_num TEXT,                              -- 異議番号（aaz_igi_no）
    rejection_reason_code TEXT,                      -- 拒絶理由条文コード（kyozeturiyujobun_code）
    version_num TEXT,                                -- バージョン番号（version_no）
    
    PRIMARY KEY (law_code, app_num, folder_creation_seq_num)
);
```
**データソース**: upd_jiken_c_t_kian_dv.tsv（16,797件）
**TSVカラムマッピング（全14カラム）**: 
- `yonpo_code` → `law_code`
- `shutugan_no` → `app_num`
- `folderbetusakusejnj_no` → `folder_creation_seq_num`
- `sakusei_bi` → `creation_date`
- `chukanshorui_code` → `intermediate_doc_code`
- `taio_mark` → `response_mark`
- `kian_bi` → `draft_date`
- `hasso_bi` → `dispatch_date`
- `aaz_igi_no` → `objection_num`
- `shorui_no` → `document_num`
- `kyozeturiyujobun_code` → `rejection_reason_code`
- `taioshorui_no` → `corresponding_doc_num`
- `shorui_shubetu` → `document_type`
- `version_no` → `version_num`

#### 7-2. 申請中間記録テーブル
```sql
CREATE TABLE trademark_application_records (
    law_code TEXT NOT NULL,                          -- 四法コード（全行「4」）
    app_num TEXT NOT NULL,                           -- 出願番号（10桁、正規化済み）
    folder_creation_seq_num INTEGER NOT NULL,        -- フォルダ別作成順序番号（4桁連番）
    creation_date TEXT,                              -- 作成日（YYYYMMDD）
    intermediate_doc_code TEXT,                      -- 中間書類コード（例：A63）
    correspondence_mark TEXT,                        -- 対応マーク
    dispatch_date TEXT,                              -- 差出日（YYYYMMDD）
    receipt_date TEXT,                               -- 受付日（YYYYMMDD）
    opposition_num TEXT,                             -- 異議番号
    doc_num TEXT,                                    -- 書類番号（11桁）
    procedure_complete_mark TEXT,                    -- 方式完マーク（0/1）
    order_complete_flag TEXT,                        -- 指令完フラグ
    corresponding_doc_num TEXT,                      -- 対応書類番号
    doc_type TEXT,                                   -- 書類種別（1,8等）
    version_num TEXT,                                -- バージョン番号（0001,0002等）
    viewing_restriction_flag TEXT,                   -- 閲覧禁止フラグ（全行「0」）
    
    PRIMARY KEY (law_code, app_num, folder_creation_seq_num)
);
```
**データソース**: upd_jiken_c_t_sinsei_dv.tsv（32,911件）
**TSVカラムマッピング**:
- `yonpo_code` → `law_code`
- `shutugan_no` → `app_num`
- `folderbetusakusejnj_no` → `folder_creation_seq_num`
- `sakusei_bi` → `creation_date`
- `chukanshorui_code` → `intermediate_doc_code`
- `taio_mark` → `correspondence_mark`
- `sasidasi_bi` → `dispatch_date`
- `uketuke_bi` → `receipt_date`
- `aaz_igi_no` → `opposition_num`
- `shorui_no` → `doc_num`
- `hosikikan_mark` → `procedure_complete_mark`
- `sireikan_flag` → `order_complete_flag`
- `taioshorui_no` → `corresponding_doc_num`
- `shorui_shubetu` → `doc_type`
- `version_no` → `version_num`
- `eturankinsi_flag` → `viewing_restriction_flag`

**データの特徴**:
- 申請書類の中間記録情報（審査経過の詳細）
- 1つの出願に複数の中間記録が存在
- 書類コード（A63等）により処理内容を識別
- 異議番号、対応書類番号はほとんど空欄

### 8. 優先権・公報関連

#### 8-1. 優先権情報テーブル
```sql
CREATE TABLE trademark_priority_claims (
    law_code TEXT NOT NULL,                    -- 四法コード（全行「4」）
    app_num TEXT NOT NULL,                     -- 出願番号（10桁、正規化済み）
    priority_seq_num INTEGER NOT NULL,         -- 優先権記事順序番号（現在は全行1）
    priority_app_num TEXT,                     -- 優先権出願番号（最大20桁）
    priority_date TEXT,                        -- 優先権主張日（YYYYMMDD）
    priority_country_code TEXT,                -- 優先権国コード（例：JM、NZ）
    
    PRIMARY KEY (law_code, app_num, priority_seq_num)
);
```
**データソース**: upd_jiken_c_t_yusenken_joho.tsv（355行）
**TSVカラムマッピング**:
- `yonpo_code` → `law_code`
- `shutugan_no` → `app_num`
- `bmz_junjo_no` → `priority_seq_num`
- `yusenkenshutugan_no` → `priority_app_num`
- `yusenkenshucho_bi` → `priority_date`
- `yusenkenkuni_code` → `priority_country_code`

**データの特徴**:
- 優先権主張の情報（パリ条約による）
- 1つの出願に複数の優先権主張が可能（現在は全て1件のみ）
- 外国の出願番号を含む（最大20桁）
- 主要な優先権国：JM（ジャマイカ）、NZ（ニュージーランド）等

#### 8-2. 公報発行情報テーブル
```sql
CREATE TABLE trademark_gazette_publications (
    law_code TEXT NOT NULL,                          -- 四法コード（全行「4」）
    app_num TEXT NOT NULL,                           -- 出願番号（10桁、正規化済み）
    gazette_seq_num INTEGER NOT NULL,                -- 公報発行情報記事順序番号（全行「1」）
    total_serial_num TEXT,                           -- 公報発行情報記事総通号数（6桁）
    annual_serial_num TEXT,                          -- 公報発行情報記事年間通号数（6桁）
    dept_serial_num TEXT,                            -- 部門別通号数
    dept_annual_serial_num TEXT,                     -- 部門別年間通号数
    gazette_publication_date TEXT,                   -- 公報発行情報記事公報発行日（YYYYMMDD）
    correction_type TEXT,                            -- 正誤識別（全行「00」）
    gazette_type TEXT,                               -- 公報発行情報記事公報識別（例：4A010）
    
    PRIMARY KEY (law_code, app_num, gazette_seq_num)
);
```
**データソース**: upd_jiken_c_t_kohohako_joho.tsv（2,333行）
**TSVカラムマッピング**:
- `yonpo_code` → `law_code`
- `shutugan_no` → `app_num`
- `jaz_junjo_no` → `gazette_seq_num`
- `jaz_sotugo_su` → `total_serial_num`
- `jaz_nenkantugo_su` → `annual_serial_num`
- `jaz_bumonbetutugo_su` → `dept_serial_num`
- `jaz_bumonbetunenkantugo_su` → `dept_annual_serial_num`
- `jaz_kohohakko_bi` → `gazette_publication_date`
- `jaz_seigo_sikibetu` → `correction_type`
- `jaz_koho_sikibetu` → `gazette_type`

**データの特徴**:
- 商標公報発行情報（発行日、通号数等）
- 公報種別コード（4A010等）により公報の種類を識別
- 部門別通号数はほとんど空欄
- 正誤識別は全て「00」（正常）

### 9. 申請人マスタ関連

#### 9-1. 申請人登録情報テーブル
```sql
CREATE TABLE applicant_registration_info (
    data_id_code TEXT,                               -- データ識別コード（全行「520010」）
    applicant_code TEXT NOT NULL,                    -- 申請人コード（9桁）
    applicant_name TEXT,                             -- 申請人氏名（日本語/英語/中国語等）
    applicant_kana_name TEXT,                        -- 申請人カナ氏名（日本の申請人のみ）
    applicant_postal_code TEXT,                      -- 申請人郵便番号（日本の住所のみ）
    applicant_address TEXT,                          -- 申請人住所（国内外の住所）
    roman_name TEXT,                                 -- ローマ字氏名
    roman_address TEXT,                              -- ローマ字住所（多くは「（省略）」）
    integrated_applicant_code TEXT,                  -- 統合申請人コード
    double_reg_integration_num INTEGER,              -- 二重登録統合管理通番（ほぼ0）
    
    PRIMARY KEY (applicant_code)
);
```
**データソース**: upd_appl_reg_info.tsv（1,612件）
**TSVカラムマッピング**:
- `data_id_cd` → `data_id_code`
- `appl_cd` → `applicant_code`
- `appl_name` → `applicant_name`
- `appl_cana_name` → `applicant_kana_name`
- `appl_postcode` → `applicant_postal_code`
- `appl_addr` → `applicant_address`
- `wes_join_name` → `roman_name`
- `wes_join_addr` → `roman_address`
- `integ_appl_cd` → `integrated_applicant_code`
- `dbl_reg_integ_mgt_srl_num` → `double_reg_integration_num`

**データの特徴**:
- 国内外の申請人マスタデータ
- 申請人名は日本語/英語/中国語等の多言語対応
- カナ氏名と郵便番号は日本の申請人のみ
- ローマ字住所は多くが「（省略）」
- 統合申請人コードはほとんど空欄（申請人統合時に使用）

### 10. 国際商標関連

#### 10-1. 国際商標登録管理情報テーブル
```sql
CREATE TABLE intl_trademark_registration (
    add_del_id TEXT,                                 -- 追加削除識別（ほぼ全行「0」）
    intl_reg_num TEXT NOT NULL,                      -- 国際登録番号（連番部分）
    intl_reg_num_update_count_code TEXT NOT NULL,   -- 国際登録番号更新回数記号コード
    intl_reg_num_split_code TEXT NOT NULL,           -- 国際登録番号分割記号コード（A,B,C,D等）
    after_designation_date TEXT NOT NULL,            -- 事後指定年月日（YYYYMMDD）
    intl_reg_date TEXT,                              -- 国際登録年月日（YYYYMMDD）
    jpo_reference_num TEXT,                          -- 庁内整理番号（西暦年＋連番）
    jpo_reference_num_split_code TEXT,               -- 庁内整理番号分割記号コード
    set_registration_date TEXT,                      -- 設定登録年月日（YYYYMMDD）
    right_erasure_id TEXT,                           -- 本権利抹消識別
    right_disappearance_date TEXT,                   -- 本権利消滅年月日（YYYYMMDD）
    close_registration_date TEXT,                    -- 閉鎖登録年月日（YYYYMMDD）
    inspection_prohibition_flag TEXT,                -- 閲覧禁止フラグ
    define_flag TEXT NOT NULL,                       -- 確定フラグ
    update_date TEXT,                                -- 更新年月日（システム操作者）
    batch_update_date TEXT,                          -- バッチ更新年月日
    
    PRIMARY KEY (intl_reg_num, intl_reg_num_update_count_code, intl_reg_num_split_code, after_designation_date, define_flag)
);
```
**データソース**: upd_intl_t_org_org_reg_mgt_info.tsv（1,431行）
**TSVカラムマッピング**:
- `add_del_id` → `add_del_id`
- `intl_reg_num` → `intl_reg_num`
- `intl_reg_num_updt_cnt_sign_cd` → `intl_reg_num_update_count_code`
- `intl_reg_num_split_sign_cd` → `intl_reg_num_split_code`
- `aft_desig_year_month_day` → `after_designation_date`
- `intl_reg_year_month_day` → `intl_reg_date`
- `jpo_rfr_num` → `jpo_reference_num`
- `jpo_rfr_num_split_sign_cd` → `jpo_reference_num_split_code`
- `set_reg_year_month_day` → `set_registration_date`
- `right_ersr_id` → `right_erasure_id`
- `right_disppr_year_month_day` → `right_disappearance_date`
- `close_reg_year_month_day` → `close_registration_date`
- `inspct_prhbt_flg` → `inspection_prohibition_flag`
- `define_flg` → `define_flag`
- `updt_year_month_day` → `update_date`
- `batch_updt_year_month_day` → `batch_update_date`

**データの特徴**:
- 国際商標登録の管理情報（マドプロ出願）
- 事後指定により複数のレコードが存在可能
- 分割記号（A,B,C,D等）で派生案件を管理
- 設定登録、権利消滅、閉鎖などのライフサイクル管理

#### 10-2. 国際商標経過情報テーブル
```sql
CREATE TABLE intl_trademark_progress (
    add_del_id TEXT,                                 -- 追加削除識別（ほぼ全行「0」）
    intl_reg_num TEXT NOT NULL,                      -- 国際登録番号（連番部分）
    intl_reg_num_update_count_code TEXT NOT NULL,   -- 国際登録番号更新回数記号コード
    intl_reg_num_split_code TEXT NOT NULL,           -- 国際登録番号分割記号コード
    after_designation_date TEXT NOT NULL,            -- 事後指定年月日（YYYYMMDD）
    intermediate_code TEXT NOT NULL,                 -- 中間コード（例：IB31400、R150）
    storage_num TEXT NOT NULL,                       -- 格納番号（000001〜の連番）
    intermediate_def_date_1 TEXT,                    -- 中間定義１日付（YYYYMMDD）
    intermediate_def_date_2 TEXT,                    -- 中間定義２日付（YYYYMMDD）
    intermediate_def_date_3 TEXT,                    -- 中間定義３日付（YYYYMMDD）
    intermediate_def_date_4 TEXT,                    -- 中間定義４日付（YYYYMMDD）
    intermediate_def_date_5 TEXT,                    -- 中間定義５日付（YYYYMMDD）
    correspondence_mark TEXT,                        -- 対応マーク
    define_flag TEXT NOT NULL,                       -- 確定フラグ
    status TEXT NOT NULL,                            -- ステータス（4桁）
    update_date TEXT,                                -- 更新年月日（システム操作者）
    batch_update_date TEXT,                          -- バッチ更新年月日
    
    PRIMARY KEY (intl_reg_num, intl_reg_num_update_count_code, intl_reg_num_split_code, after_designation_date, intermediate_code, storage_num, define_flag, status)
);
```
**データソース**: upd_intl_t_org_prog_info.tsv（2,869行）
**TSVカラムマッピング**:
- `add_del_id` → `add_del_id`
- `intl_reg_num` → `intl_reg_num`
- `intl_reg_num_updt_cnt_sign_cd` → `intl_reg_num_update_count_code`
- `intl_reg_num_split_sign_cd` → `intl_reg_num_split_code`
- `aft_desig_year_month_day` → `after_designation_date`
- `intrmd_cd` → `intermediate_code`
- `string_num` → `storage_num`
- `intrmd_dfn_1_dt` → `intermediate_def_date_1`
- `intrmd_dfn_2_dt` → `intermediate_def_date_2`
- `intrmd_dfn_3_dt` → `intermediate_def_date_3`
- `intrmd_dfn_4_dt` → `intermediate_def_date_4`
- `intrmd_dfn_5_dt` → `intermediate_def_date_5`
- `crrspnd_mk` → `correspondence_mark`
- `define_flg` → `define_flag`
- `stts` → `status`
- `updt_year_month_day` → `update_date`
- `batch_updt_year_month_day` → `batch_update_date`

**データの特徴**:
- 国際商標登録の経過情報（審査・登録の進行状況）
- 中間コード（IB31400等）により処理内容を識別
- 複数の中間定義日付により時系列管理
- ステータス（4桁）で現在の状態を表示

#### 10-3. 国際商標名義人テーブル
```sql
CREATE TABLE intl_trademark_holders (
    add_del_id TEXT,                                 -- 追加削除識別（ほぼ全行「0」）
    intl_reg_num TEXT NOT NULL,                      -- 国際登録番号（連番部分）
    intl_reg_num_update_count_code TEXT NOT NULL,   -- 国際登録番号更新回数記号コード
    intl_reg_num_split_code TEXT NOT NULL,           -- 国際登録番号分割記号コード
    after_designation_date TEXT NOT NULL,            -- 事後指定年月日（YYYYMMDD）
    temp_principal_reg_id_flag TEXT NOT NULL,        -- 仮・本登録識別フラグ
    display_seq INTEGER NOT NULL,                    -- 表示順序（4桁）
    holder_input_seq_num INTEGER NOT NULL,           -- 名義人入力順序番号（4桁）
    holder_name TEXT,                                -- 名義人名称（最大1024桁）
    holder_address TEXT,                             -- 名義人住所（最大432桁）
    define_flag TEXT NOT NULL,                       -- 確定フラグ
    update_date TEXT,                                -- 更新年月日（システム操作者）
    batch_update_date TEXT,                          -- バッチ更新年月日
    
    PRIMARY KEY (intl_reg_num, intl_reg_num_update_count_code, intl_reg_num_split_code, after_designation_date, temp_principal_reg_id_flag, display_seq, holder_input_seq_num, define_flag)
);
```
**データソース**: upd_intl_t_org_set_crr_nm_addr.tsv（746行）
**TSVカラムマッピング**:
- `add_del_id` → `add_del_id`
- `intl_reg_num` → `intl_reg_num`
- `intl_reg_num_updt_cnt_sign_cd` → `intl_reg_num_update_count_code`
- `intl_reg_num_split_sign_cd` → `intl_reg_num_split_code`
- `aft_desig_year_month_day` → `after_designation_date`
- `temp_principal_reg_id_flg` → `temp_principal_reg_id_flag`
- `indct_seq` → `display_seq`
- `crrcter_input_seq_num` → `holder_input_seq_num`
- `crrcter_name` → `holder_name`
- `crrcter_addr` → `holder_address`
- `define_flg` → `define_flag`
- `updt_year_month_day` → `update_date`
- `batch_updt_year_month_day` → `batch_update_date`

**データの特徴**:
- 国際商標登録の設定時名義人情報
- 1つの国際登録に複数の名義人が存在可能
- 仮登録・本登録の識別フラグで状態管理
- 表示順序と入力順序番号で並び順を管理

#### 10-4. 国際商標商品・役務テーブル
```sql
CREATE TABLE intl_trademark_goods_services (
    add_del_id TEXT,                                 -- 追加削除識別（全行「0」）
    intl_reg_num TEXT NOT NULL,                      -- 国際登録番号（連番部分）
    intl_reg_num_update_count_code TEXT NOT NULL,   -- 国際登録番号更新回数記号コード
    intl_reg_num_split_code TEXT NOT NULL,           -- 国際登録番号分割記号コード
    after_designation_date TEXT NOT NULL,            -- 事後指定年月日（YYYYMMDD）
    temp_principal_reg_id_flag TEXT NOT NULL,        -- 仮・本登録識別フラグ（全行「1」）
    display_seq INTEGER NOT NULL,                    -- 表示順序（4桁、ほぼ全て0001）
    seq_num INTEGER NOT NULL,                        -- 順序番号（グループ内の商品・役務順）
    madpro_class TEXT,                               -- 区分（01〜45）
    goods_service_name TEXT,                         -- 商品サービス名（英語、最大8000桁）
    intl_reg_record_date TEXT,                       -- 国際登録記録日（YYYYMMDD）
    define_flag TEXT,                                -- 確定フラグ（全行「1」）
    update_date TEXT,                                -- 更新年月日
    batch_update_date TEXT,                          -- バッチ更新年月日
    
    PRIMARY KEY (intl_reg_num, intl_reg_num_update_count_code, intl_reg_num_split_code, after_designation_date, temp_principal_reg_id_flag, display_seq, seq_num)
);
```
**データソース**: upd_intl_t_org_set_dsgn_gds_srvc.tsv（2,280行）
**TSVカラムマッピング**:
- `add_del_id` → `add_del_id`
- `intl_reg_num` → `intl_reg_num`
- `intl_reg_num_updt_cnt_sign_cd` → `intl_reg_num_update_count_code`
- `intl_reg_num_split_sign_cd` → `intl_reg_num_split_code`
- `aft_desig_year_month_day` → `after_designation_date`
- `temp_principal_reg_id_flg` → `temp_principal_reg_id_flag`
- `indct_seq` → `display_seq`
- `seq_num` → `seq_num`
- `madopro_class` → `madpro_class`
- `goods_service_name` → `goods_service_name`
- `intl_reg_rec_dt` → `intl_reg_record_date`
- `define_flg` → `define_flag`
- `updt_year_month_day` → `update_date`
- `batch_updt_year_month_day` → `batch_update_date`

**データの特徴**:
- 国際商標の設定時指定商品・役務情報
- 区分（01〜45）ごとに商品・役務を英語で記載
- 表示順序とシーケンス番号で並び順を管理
- 国際登録記録日により時系列管理

#### 10-5. 国際商標第一表示部テーブル
```sql
CREATE TABLE intl_trademark_first_indication (
    add_del_id TEXT,                                 -- 追加削除識別（全行「0」）
    intl_reg_num TEXT NOT NULL,                      -- 国際登録番号（連番部分）
    intl_reg_num_update_count_code TEXT NOT NULL,   -- 国際登録番号更新回数記号コード
    intl_reg_num_split_code TEXT NOT NULL,           -- 国際登録番号分割記号コード
    after_designation_date TEXT NOT NULL,            -- 事後指定年月日（YYYYMMDD）
    temp_principal_reg_id_flag TEXT NOT NULL,        -- 仮・本登録識別フラグ（全行「1」）
    display_seq INTEGER NOT NULL,                    -- 表示順序（全行「0001」）
    final_decision_date TEXT,                        -- 査定年月日（YYYYMMDD）
    trial_decision_date TEXT,                        -- 審決年月日（YYYYMMDD）
    priority_app_country_code TEXT,                  -- 優先権出願官庁締約国等コード（CH、EM、US等）
    priority_app_date TEXT,                          -- 優先権出願年月日（YYYYMMDD）
    priority_claim_count TEXT,                       -- 優先権主張件数（000〜006）
    special_trademark_type_flag TEXT,                -- 特殊商標のタイプフラグ
    group_cert_warranty_flag TEXT,                   -- 団体証明保証フラグ
    define_flag TEXT,                                -- 確定フラグ（全行「1」）
    update_date TEXT,                                -- 更新年月日
    batch_update_date TEXT,                          -- バッチ更新年月日
    trademark_detailed_explanation TEXT,             -- 商標の詳細な説明（最大4000桁、全て空欄）
    
    PRIMARY KEY (intl_reg_num, intl_reg_num_update_count_code, intl_reg_num_split_code, after_designation_date, temp_principal_reg_id_flag, display_seq)
);
```
**データソース**: upd_intl_t_org_set_frst_indct.tsv（1,339行）
**TSVカラムマッピング**:
- `add_del_id` → `add_del_id`
- `intl_reg_num` → `intl_reg_num`
- `intl_reg_num_updt_cnt_sign_cd` → `intl_reg_num_update_count_code`
- `intl_reg_num_split_sign_cd` → `intl_reg_num_split_code`
- `aft_desig_year_month_day` → `after_designation_date`
- `temp_principal_reg_id_flg` → `temp_principal_reg_id_flag`
- `indct_seq` → `display_seq`
- `finl_dcsn_year_month_day` → `final_decision_date`
- `trial_dcsn_year_month_day` → `trial_decision_date`
- `pri_app_gvrn_cntrcntry_cd` → `priority_app_country_code`
- `pri_app_year_month_day` → `priority_app_date`
- `pri_clim_cnt` → `priority_claim_count`
- `special_t_typ_flg` → `special_trademark_type_flag`
- `group_cert_warranty_flg` → `group_cert_warranty_flag`
- `define_flg` → `define_flag`
- `updt_year_month_day` → `update_date`
- `batch_updt_year_month_day` → `batch_update_date`
- `t_dtl_explntn` → `trademark_detailed_explanation`

**データの特徴**:
- 国際商標の設定時第一表示部情報
- 査定日、審決日、優先権情報を含む
- 特殊商標（5件）、団体証明保証（1件）のフラグ管理
- 商標の詳細な説明欄は現在全て空欄

### 11. 画像データ関連

#### 11-1. 商標画像テーブル
```sql
CREATE TABLE trademark_images (
    country_code TEXT,                               -- 国コード（"JP"固定）
    doc_type TEXT,                                   -- 文献種別（"T1"固定）
    doc_num TEXT NOT NULL,                           -- 文献番号（8桁）
    app_num TEXT,                                    -- 出願番号（10桁）
    page_num TEXT NOT NULL,                          -- 頁番号（"0001"から）
    rec_seq_num INTEGER NOT NULL,                    -- レコード順序番号
    year_issue_code TEXT NOT NULL,                   -- 年号コード（"3":昭和,"4":平成等）
    data_creation_date TEXT,                         -- データ作成日（YYYYMMDD）
    all_page_count TEXT,                             -- 全頁数（"0001"～"9999"）
    final_rec_seq_num INTEGER,                       -- 最終レコード順序番号
    fullsize_length TEXT,                            -- 原寸の大きさ_縦（mm単位）
    fullsize_width TEXT,                             -- 原寸の大きさ_横（mm単位）
    compression_format TEXT,                         -- 圧縮方式（"JP":JPEG,"M2":MMR）
    resolution TEXT,                                 -- 解像度（"00":JPEG,"16":MMR）
    line_count_length TEXT,                          -- ライン数_縦（ピクセル数）
    line_count_width TEXT,                           -- ライン数_横（ピクセル数）
    image_data_length TEXT,                          -- イメージデータ長（00001～19740）
    image_data TEXT,                                 -- イメージデータ（Base64エンコード）
    
    PRIMARY KEY (doc_num, page_num, rec_seq_num, year_issue_code)
);
```
**データソース**: upd_t_sample.tsv（10,063行）
**TSVカラムマッピング**:
- `cntry_cd` → `country_code`
- `doc_typ` → `doc_type`
- `doc_num` → `doc_num`
- `app_num` → `app_num`
- `page_num` → `page_num`
- `rec_seq_num` → `rec_seq_num`
- `year_issu_cd` → `year_issue_code`
- `data_crt_dt` → `data_creation_date`
- `all_page_cnt` → `all_page_count`
- `final_rec_seq_num` → `final_rec_seq_num`
- `fullsize_length` → `fullsize_length`
- `fullsize_width` → `fullsize_width`
- `comp_frmlchk` → `compression_format`
- `resolution` → `resolution`
- `linecnt_length` → `line_count_length`
- `linecnt_width` → `line_count_width`
- `image_data_len` → `image_data_length`
- `image_data` → `image_data`

**インポート時の処理**:
- rec_seq_num < final_rec_seq_numの場合、複数行のimage_dataを結合
- 「//」で始まるBase64データを処理
- 標準文字商標の場合は画像なしの可能性

**データの特徴**:
- 商標画像データ（Base64エンコード）
- 1つの画像が複数レコードに分割される場合あり
- JPEG（"JP"）またはMMR（"M2"）形式で圧縮
- 画像サイズと解像度情報を含む

### 12. 防護標章関連

#### 12-1. 防護標章記事テーブル（bougo_hyosho_articles）
```sql
CREATE TABLE bougo_hyosho_articles (
    processing_type TEXT,                          -- 処理種別（削除・修正等を示すコード）
    law_code TEXT NOT NULL,                        -- 四法コード（law_cd → law_code）
    reg_num TEXT NOT NULL,                         -- 登録番号（7桁）
    split_num TEXT NOT NULL,                       -- 分割番号（31桁）
    app_num TEXT NOT NULL,                         -- 出願番号（10桁）
    pe_num TEXT NOT NULL,                          -- ＰＥ番号（3桁）
    defensive_art_upd_date TEXT,                   -- 防護記事部作成更新年月日（sec_art_upd_ymd → defensive_art_upd_date）
    defensive_app_num TEXT,                        -- 防護出願番号（sec_app_num → defensive_app_num）
    defensive_num TEXT,                            -- 防護番号（sec_num → defensive_num）
    defensive_temp_reg_flg TEXT,                   -- 防護仮登録の有無（sec_temp_reg_flg → defensive_temp_reg_flg）
    defensive_conti_prd_expire_date TEXT,          -- 防護存続期間満了年月日（sec_conti_prd_expire_ymd → defensive_conti_prd_expire_date）
    defensive_ersr_flg TEXT,                       -- 防護抹消の有無（sec_ersr_flg → defensive_ersr_flg）
    defensive_apply_law TEXT,                      -- 防護適用法規（sec_apply_law → defensive_apply_law）
    defensive_recovery_num TEXT,                   -- 防護回復番号（sec_recovery_num → defensive_recovery_num）
    defensive_app_date TEXT,                       -- 防護出願年月日（sec_app_year_month_day → defensive_app_date）
    defensive_app_exam_pub_num TEXT,               -- 防護出願公告番号（sec_app_exam_pub_num → defensive_app_exam_pub_num）
    defensive_app_exam_pub_date TEXT,              -- 防護出願公告年月日（sec_app_exam_pub_ymd → defensive_app_exam_pub_date）
    defensive_finl_dcsn_date TEXT,                 -- 防護査定年月日（sec_finl_dcsn_year_month_day → defensive_finl_dcsn_date）
    defensive_trial_dcsn_date TEXT,                -- 防護審決年月日（sec_trial_dcsn_year_month_day → defensive_trial_dcsn_date）
    defensive_reg_date TEXT,                       -- 防護登録年月日（sec_reg_year_month_day → defensive_reg_date）
    defensive_rwrt_app_num TEXT,                   -- 防護書換申請番号（sec_rwrt_app_num → defensive_rwrt_app_num）
    defensive_rwrt_app_date TEXT,                  -- 防護書換申請年月日（sec_rwrt_app_year_month_day → defensive_rwrt_app_date）
    defensive_rwrt_finl_dcsn_date TEXT,            -- 防護書換査定年月日（sec_rwrt_finl_dcsn_ymd → defensive_rwrt_finl_dcsn_date）
    defensive_rwrt_trial_dcsn_date TEXT,           -- 防護書換審決年月日（sec_rwrt_trial_dcsn_ymd → defensive_rwrt_trial_dcsn_date）
    defensive_rwrt_reg_date TEXT,                  -- 防護書換登録年月日（sec_rwrt_reg_year_month_day → defensive_rwrt_reg_date）
    mu_num TEXT NOT NULL,                          -- MU番号（連番 000,001,002...）
    defensive_desig_goods_desig_wrk_cls TEXT,      -- 防護標章指定商品・役務類（sec_desig_goods_desig_wrk_cls → defensive_desig_goods_desig_wrk_cls）
    
    PRIMARY KEY (law_code, reg_num, split_num, app_num, pe_num, mu_num)
);
```
**データソース**: upd_sec_art.tsv（769行）

**TSVカラムマッピング**:
- `processing_type` → `processing_type`
- `law_cd` → `law_code`（統一済み）
- `reg_num` → `reg_num`
- `split_num` → `split_num`
- `app_num` → `app_num`
- `pe_num` → `pe_num`
- `sec_art_upd_ymd` → `defensive_art_upd_date`
- `sec_app_num` → `defensive_app_num`
- `sec_num` → `defensive_num`（統一済み）
- `sec_temp_reg_flg` → `defensive_temp_reg_flg`
- `sec_conti_prd_expire_ymd` → `defensive_conti_prd_expire_date`
- `sec_ersr_flg` → `defensive_ersr_flg`
- `sec_apply_law` → `defensive_apply_law`
- `sec_recovery_num` → `defensive_recovery_num`
- `sec_app_year_month_day` → `defensive_app_date`
- `sec_app_exam_pub_num` → `defensive_app_exam_pub_num`
- `sec_app_exam_pub_ymd` → `defensive_app_exam_pub_date`
- `sec_finl_dcsn_year_month_day` → `defensive_finl_dcsn_date`
- `sec_trial_dcsn_year_month_day` → `defensive_trial_dcsn_date`
- `sec_reg_year_month_day` → `defensive_reg_date`
- `sec_rwrt_app_num` → `defensive_rwrt_app_num`
- `sec_rwrt_app_year_month_day` → `defensive_rwrt_app_date`
- `sec_rwrt_finl_dcsn_ymd` → `defensive_rwrt_finl_dcsn_date`
- `sec_rwrt_trial_dcsn_ymd` → `defensive_rwrt_trial_dcsn_date`
- `sec_rwrt_reg_year_month_day` → `defensive_rwrt_reg_date`
- `mu_num` → `mu_num`（統一済み）
- `sec_desig_goods_desig_wrk_cls` → `defensive_desig_goods_desig_wrk_cls`

**インポート時の処理**:
- mu_numの値により、同一防護標章で複数の商品・役務類を持つ場合がある
- 防護標章は基礎登録番号（本権）に対して設定される
- 書換（rwrt）関連のカラムは旧法対応のため含まれる

**データの特徴**:
- 防護標章の登録・更新・抹消情報を管理
- 1つの防護標章に対して複数の商品・役務類が指定可能（mu_numで識別）
- 存続期間満了日により有効性を判断
- 書換申請は旧法時代の制度（現在は使用されない可能性が高い）

#### 12-2. 防護商品名テーブル（bougo_shohin_mei）
```sql
CREATE TABLE bougo_shohin_mei (
    processing_type TEXT,                          -- 処理種別（削除・修正等を示すコード）
    law_code TEXT NOT NULL,                        -- 四法コード（law_cd → law_code）
    reg_num TEXT NOT NULL,                         -- 登録番号（7桁）
    split_num TEXT NOT NULL,                       -- 分割番号（31桁）
    defensive_num TEXT NOT NULL,                   -- 防護番号（sec_num → defensive_num、統一済み）
    defensive_app_num TEXT NOT NULL,               -- 防護出願番号（sec_app_num → defensive_app_num、12-1と統一）
    defensive_desig_goods_desig_wrk_cls TEXT NOT NULL,  -- 防護指定商品・役務の区分（sec_desig_goods_desig_wrk_cls → defensive_desig_goods_desig_wrk_cls、統一済み）
    master_update_date TEXT,                       -- マスタ更新年月日（mstr_updt_year_month_day → master_update_date、統一済み）
    defensive_desig_gds_desig_wrk_nm_len TEXT,     -- 防護指定商品・役務名レングス（sec_desig_gds_desig_wrk_nm_len → defensive_desig_gds_desig_wrk_nm_len）
    defensive_desig_gds_nm_desig_wrk_nm TEXT,      -- 防護指定商品名・役務名（sec_desig_gds_nm_desig_wrk_nm → defensive_desig_gds_nm_desig_wrk_nm）
    
    PRIMARY KEY (law_code, reg_num, split_num, defensive_num, defensive_app_num, defensive_desig_goods_desig_wrk_cls)
);
```
**データソース**: upd_sec_goods_name.tsv（1,472行）

**TSVカラムマッピング**:
- `processing_type` → `processing_type`
- `law_cd` → `law_code`（統一済み）
- `reg_num` → `reg_num`
- `split_num` → `split_num`
- `sec_num` → `defensive_num`（統一済み）
- `sec_app_num` → `defensive_app_num`（12-1と統一）
- `sec_desig_goods_desig_wrk_cls` → `defensive_desig_goods_desig_wrk_cls`（統一済み）
- `mstr_updt_year_month_day` → `master_update_date`（統一済み）
- `sec_desig_gds_desig_wrk_nm_len` → `defensive_desig_gds_desig_wrk_nm_len`
- `sec_desig_gds_nm_desig_wrk_nm` → `defensive_desig_gds_nm_desig_wrk_nm`

**インポート時の処理**:
- 商品・役務名は最大12000文字
- レングス（文字数）カラムは10桁の数値文字列
- 1つの防護標章に対して複数の商品・役務区分が存在

**データの特徴**:
- 防護標章に指定された商品・役務の詳細情報
- 類番号（区分）ごとに商品・役務名を管理
- 防護番号と防護出願番号の組み合わせで防護標章を特定

#### 12-3. 防護更新記事テーブル（bougo_koshin_kiji）
```sql
CREATE TABLE bougo_koshin_kiji (
    processing_type TEXT,                          -- 処理種別（削除・修正等を示すコード）
    law_code TEXT NOT NULL,                        -- 四法コード（law_cd → law_code）
    reg_num TEXT NOT NULL,                         -- 登録番号（7桁）
    split_num TEXT NOT NULL,                       -- 分割番号（31桁）
    app_num TEXT NOT NULL,                         -- 出願番号（10桁）
    pe_num TEXT NOT NULL,                          -- ＰＥ番号（3桁）
    defensive_updt_art_upd_date TEXT,              -- 防護更新記事部作成更新年月日（sec_updt_art_upd_ymd → defensive_updt_art_upd_date）
    defensive_updt_app_num TEXT,                   -- 防護更新出願番号（sec_updt_app_num → defensive_updt_app_num）
    defensive_updt_num TEXT,                       -- 防護更新防護番号（sec_updt_sec_num → defensive_updt_num）
    defensive_updt_temp_reg_flg TEXT,              -- 防護更新仮登録の有無（sec_updt_temp_reg_flg → defensive_updt_temp_reg_flg）
    defensive_updt_title_chan_flg TEXT,            -- 防護更新名称変更の有無（sec_updt_title_chan_flg → defensive_updt_title_chan_flg）
    defensive_updt_recovery_num TEXT,              -- 防護更新回復番号（sec_updt_recovery_num → defensive_updt_recovery_num）
    defensive_updt_app_date TEXT,                  -- 防護更新出願年月日（sec_updt_app_year_month_day → defensive_updt_app_date）
    defensive_updt_finl_dcsn_date TEXT,            -- 防護更新査定年月日（sec_updt_finl_dcsn_ymd → defensive_updt_finl_dcsn_date）
    defensive_updt_trial_dcsn_date TEXT,           -- 防護更新審決年月日（sec_updt_trial_dcsn_ymd → defensive_updt_trial_dcsn_date）
    defensive_updt_reg_date TEXT,                  -- 防護更新登録年月日（sec_updt_reg_year_month_day → defensive_updt_reg_date）
    mu_num TEXT NOT NULL,                          -- MU番号（3桁、全行「000」）
    
    PRIMARY KEY (law_code, reg_num, split_num, app_num, pe_num, mu_num)
);
```
**データソース**: upd_sec_updt_art.tsv（1,911行）

**TSVカラムマッピング**:
- `processing_type` → `processing_type`
- `law_cd` → `law_code`（統一済み）
- `reg_num` → `reg_num`
- `split_num` → `split_num`
- `app_num` → `app_num`
- `pe_num` → `pe_num`
- `sec_updt_art_upd_ymd` → `defensive_updt_art_upd_date`
- `sec_updt_app_num` → `defensive_updt_app_num`
- `sec_updt_sec_num` → `defensive_updt_num`
- `sec_updt_temp_reg_flg` → `defensive_updt_temp_reg_flg`
- `sec_updt_title_chan_flg` → `defensive_updt_title_chan_flg`
- `sec_updt_recovery_num` → `defensive_updt_recovery_num`
- `sec_updt_app_year_month_day` → `defensive_updt_app_date`
- `sec_updt_finl_dcsn_ymd` → `defensive_updt_finl_dcsn_date`
- `sec_updt_trial_dcsn_ymd` → `defensive_updt_trial_dcsn_date`
- `sec_updt_reg_year_month_day` → `defensive_updt_reg_date`
- `mu_num` → `mu_num`（統一済み）

**インポート時の処理**:
- pe_numの値により、同一防護標章で複数の更新記録を持つ
- 審決年月日は多くの場合「00000000」（未発生）
- 仮登録フラグ、名称変更フラグはほぼ空欄

**データの特徴**:
- 防護標章の更新登録に関する履歴情報
- 1つの防護標章に対して複数回の更新が可能（pe_numで識別）
- 更新出願から査定、登録までの日付を管理
- 存続期間満了に伴う更新手続きの記録

### 13. その他の情報

#### 13-1. 商標付加情報テーブル（shohyo_fuka_joho）
```sql
CREATE TABLE shohyo_fuka_joho (
    add_del_id TEXT,                    -- 追加削除識別（0:追加、1:削除）
    app_num TEXT NOT NULL,              -- 出願番号（10桁、正規化済み）
    split_num TEXT,                     -- 分割番号（ほぼ空欄）
    sub_data_num TEXT,                  -- サブデータ番号（ほぼ空欄）
    right_request TEXT,                 -- 権利不要求（0または1）
    grphc_id TEXT,                      -- 図形識別（0または1）
    color_harftone TEXT,                -- カラーハーフトーン（0または1）
    gdmral_flg TEXT,                    -- 公序良俗フラグ（ほぼ全行「0」）
    duplicate_reg_flg TEXT,             -- 重複登録フラグ（ほぼ全行「0」）
    special_exception_clim_flg TEXT,    -- 特例主張フラグ（ほぼ全行「0」）
    consent_coe_reg_id TEXT,            -- 同意併存登録識別（ほぼ空欄）
    
    PRIMARY KEY (app_num, split_num, sub_data_num)
);
```
**データソース**: upd_t_add_info.tsv（33,418行）

**TSVカラムマッピング**:
- `add_del_id` → `add_del_id`（統一済み）
- `app_num` → `app_num`
- `split_num` → `split_num`
- `sub_data_num` → `sub_data_num`（統一済み）
- `right_request` → `right_request`
- `grphc_id` → `grphc_id`
- `color_harftone` → `color_harftone`
- `gdmral_flg` → `gdmral_flg`
- `duplicate_reg_flg` → `duplicate_reg_flg`
- `special_exception_clim_flg` → `special_exception_clim_flg`
- `consent_coe_reg_id` → `consent_coe_reg_id`

**インポート時の処理**:
- 各フラグは0または1の値
- split_num、sub_data_numはほとんどの場合空欄
- 同意併存登録識別は特殊なケースのみ値が入る

**データの特徴**:
- 商標出願の特殊な属性情報を管理
- 権利不要求：商標の一部に対して権利を主張しない場合
- 図形識別：図形商標であることを示す
- カラーハーフトーン：色彩の使用を示す
- 公序良俗フラグ：公序良俗に反する可能性がある場合
- 重複登録フラグ：既存の登録と重複する場合
- 特例主張フラグ：特別な法的主張がある場合
- 同意併存登録：他の権利者との合意に基づく併存登録

## 基本情報テーブル設計
（不要と判断 - 2025-07-31）
理由：既に詳細テーブルが網羅的に設計されており、必要に応じて検索用ビューでJOINすれば十分なため。

## 検索用ビュー設計
（詳細テーブル完成後に必要に応じて設計）

## 2025-07-31 作業完了記録

### 実施内容
1. **全テーブルのTSVカラムマッピング確認完了**
   - セクション2-1から13-1まで全テーブルを確認
   - 70行目ルール（全カラム明示的記載）の遵守を確認
   - 「その他のカラムは〜」のような省略記法はすべて排除済み

2. **TSVカラムの重複確認完了**
   - 共通カラムの統一マッピング確認
     - `skbt_flg` → `delete_flag`（全テーブル統一）
     - `kusn_ntz_bat` → `update_datetime`（全テーブル統一）
     - `app_num` → `app_num`（統一済み）
     - `reg_num` → `reg_num`（統一済み）
     - その他多数の共通カラムも統一済み

3. **次のステップ**
   - インポートスクリプトの作成準備完了
   
  
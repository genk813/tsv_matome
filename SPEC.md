# SPEC.md — 仕様（設計・マッピング・検索要件）

---

## スキーマ設計（設計書）

### 出典: `tmcloud_schema_v2_design.md`

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
   
  

---

## スキーマ設計チェック

### 出典: `tmcloud_schema_v2_design_check.md`

# tmcloud_schema_v2_design.md 設計漏れチェック結果

## 1. インポート対象でないのに設計に含まれているもの

### 1-1. 中間記録関連（TSV仕様書に「インポート対象」の記載なし）
- **upd_jiken_c_t_chonai_dv.tsv**（庁内中間記録）- 1,944行
  - TSV仕様書では「参考情報として記載」とあり、インポート対象の明記なし
- **upd_jiken_c_t_kian_dv.tsv**（起案中間記録）- 16,797行
  - インポート対象: ○
- **upd_jiken_c_t_sinsei_dv.tsv**（申請中間記録）- 32,911行
  - インポート対象: ○

### 1-2. 審判関連（インポート対象だが優先度低）
- **upd_snpn_zkn.tsv**（審判事件）- 18,451件
- **upd_snkt_bnri.tsv**（審決分類）
- これらは設計に含まれているが、TMSONARの商標検索機能としては優先度低

## 2. TSV_FILES_COMPLETE_SPECIFICATION.mdでインポート対象「○」となっているが、設計に含まれていないファイル

### 1. 重要な漏れ

#### 1-1. 商標画像データ
- **ファイル**: upd_t_sample.tsv
- **説明**: 商標見本ファイル（Base64エンコード画像）
- **レコード数**: 10,063行
- **重要度**: 必須（商標画像表示に必要）

#### 1-2. 商標第一表示部
- **ファイル**: upd_t_first_indct_div.tsv
- **説明**: 商標登録原簿の第一表示部情報
- **レコード数**: 16,891行
- **重要度**: 重要（登録商標の原簿管理情報）

#### 1-3. 本権商品名
- **ファイル**: upd_right_goods_name.tsv
- **説明**: 登録商標の指定商品・役務情報
- **レコード数**: 30,581行
- **重要度**: 必須（登録商標の商品・役務表示）

#### 1-4. 経過情報部
- **ファイル**: upd_prog_info_div_t.tsv
- **説明**: 登録商標の経過情報
- **レコード数**: 223,694行
- **重要度**: 重要（登録後の手続き経過情報）

#### 1-5. 被統合申請人情報
- **ファイル**: upd_under_integ_appl_info_mgt.tsv
- **説明**: 申請人コードの統合管理情報
- **レコード数**: 40行
- **重要度**: 有用（申請人名の名寄せ）

#### 1-6. 欄外商標書換申請番号
- **ファイル**: upd_mrgn_t_rwrt_app_num.tsv
- **説明**: 商標書換申請情報
- **レコード数**: 2,996行
- **重要度**: 参考（書換制度は廃止済みだが、設計には含まれている）

### 2. 審判関連（TMSONARでは必要だが、優先度は低い）

#### 2-1. 受付書類
- **ファイル**: upd_aki_uktk_syri_syri_dt_ar.tsv
- **説明**: 審判関連の受付書類データ
- **レコード数**: 100行以上

#### 2-2. 発送書類
- **ファイル**: upd_hssu_syri.tsv
- **説明**: 審判事件の発送書類管理データ
- **レコード数**: 15,350行

#### 2-3. 審判当事者関連
- **ファイル**: upd_snpn_tuzsy.tsv, upd_snpn_tzs_ssn_cd_ys_juhu.tsv
- **説明**: 審判当事者情報

#### 2-4. その他審判関連
- upd_mustt_kkr_sikyuku.tsv（申立に係る請求項）
- upd_mustt_kkr_sti_syuhn_ekmmi.tsv（申立に係る指定商品・役務名）
- upd_snksi_sust_rigi.tsv（審判請求に係る指定商品・役務名）

### 3. 設計に含まれているが、TSVファイル名の確認が必要なもの

#### 3-1. 庁内中間記録
- 設計: upd_jiken_c_t_chonai_dv.tsv（1,944件）
- TSV仕様書には「upd_jiken_c_t_chonai_dv.tsv」が見当たらない
- 「upd_tyuni_syri.tsv」（庁内書類）が対応する可能性

## 結論

TMSONARレベルの検索に必要な主要項目は概ねカバーされていますが、以下の重要な漏れがあります：

1. **商標画像データ**（upd_t_sample.tsv）- 必須
2. **商標第一表示部**（upd_t_first_indct_div.tsv）- 重要
3. **本権商品名**（upd_right_goods_name.tsv）- 必須
4. **経過情報部**（upd_prog_info_div_t.tsv）- 重要

これらを追加すれば、TMSONARレベルの検索機能を完全に実現できます。

---

## TSV 完全仕様

### 出典: `TSV_FILES_COMPLETE_SPECIFICATION.md`

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

---

## インポート・マッピング仕様

### 出典: `DATABASE_IMPORT_MAPPING.md`

# TMCloud Database Import Mapping Documentation

このドキュメントは、TMCloudプロジェクトにおけるTSVファイルからデータベーステーブルへのマッピングを詳細に記載したものです。

## 目次

1. [概要](#概要)
2. [データベース構造](#データベース構造)
3. [TSVファイルとデータベーステーブルのマッピング](#tsvファイルとデータベーステーブルのマッピング)
4. [カラムマッピング](#カラムマッピング)
5. [データ型と変換](#データ型と変換)
6. [インポート統計](#インポート統計)
7. [特記事項](#特記事項)

## 概要

TMCloudプロジェクトは、日本国特許庁（JPO）のTSVファイルから商標データをSQLiteデータベースにインポートします。

### 主要コンポーネント

- **データベース**: SQLite database (`tmcloud.db`)
- **TSVソースディレクトリ**: `/home/ygenk/TMCloud/tsv_data/tsv/`
- **メインインポートスクリプト**:
  - `tmcloud_import_unified.py` - 統合インポートスクリプト（Phase 1 + Phase 2）
  - `tmcloud_cli_search.py` - CLI検索ツール（V2）
  - `tmcloud_schema.sql` - データベーススキーマ定義

### データベーススキーマ

データベーススキーマは`tmcloud_schema.sql`で定義されており、以下のカテゴリーに分類される17テーブルで構成されています：

## データベース構造

### 主要テーブル一覧

#### 1. 商標基本情報

- `trademark_basic` - 商標基本情報（出願・登録・日付等）
- `trademark_texts` - 商標テキスト（標準文字・表示・検索用）
- `trademark_images` - 商標画像（Base64エンコード）
- `trademark_pronunciations` - 商標の称呼

#### 2. 商品・役務情報

- `trademark_goods_services` - 指定商品・指定役務
- `trademark_similar_groups` - 類似群コード
- `goods_classification` - 商品分類マスタ（未使用）

#### 3. 権利関係者情報

- `trademark_applicants` - 出願人・代理人情報
- `trademark_rights_holders` - 権利者情報
- `applicant_master` - 出願人マスタ（未使用）

#### 4. 審査・拒絶情報

- `trademark_rejections` - 拒絶理由情報
- `trademark_vienna_codes` - ウィーン図形分類
- `trademark_trial_decisions` - 審決分類
- `trademark_intermediate_records` - 中間記録（庁内・起案・申請）

#### 5. その他の管理情報

- `trademark_rewrite_applications` - 書換申請情報
- `app_reg_mapping` - 出願番号・登録番号マッピング
- `import_log` - インポートログ
- `update_history` - 更新履歴（未使用）

## TSVファイルとデータベーステーブルのマッピング

### Phase 1 - 基本データ（tmcloud_import_unified.pyでインポート）

| TSVファイル | データベーステーブル | 説明 | レコード数 |
|------------|-------------------|------|----------|
| `upd_jiken_c_t.tsv` | `trademark_basic` | 商標基本情報 | 16,688 |
| `upd_standard_char_t_art.tsv` | `trademark_texts` (type='standard') | 標準文字商標 | 385 |
| `upd_indct_use_t_art.tsv` | `trademark_texts` (type='display') | 表示用商標 | 3,127 |
| `upd_search_use_t_art_table.tsv` | `trademark_texts` (type='search') | 検索用商標 | 983 |
| `upd_jiken_c_t_shohin_joho.tsv` | `trademark_goods_services` | 指定商品・役務 | 33,385 |
| `upd_t_sample.tsv` | `trademark_images` | 商標画像 | 1,612 |
| `upd_jiken_c_t_shutugannindairinin.tsv` | `trademark_applicants` | 出願人・代理人 | 28,742 |
| `upd_right_person_art_t.tsv` | `trademark_rights_holders` | 権利者情報 | 16,884 |
| `upd_t_knd_info_art_table.tsv` | `trademark_similar_groups` | 類似群コード | 63,970 |
| `upd_t_dsgnt_art.tsv` | `trademark_pronunciations` | 称呼 | 31,678 |
| `upd_jiken_c_t_kian_dv.tsv` | `trademark_rejections` | 拒絶理由 | 5,451 |
| `upd_t_vienna_class_grphc_term_art.tsv` | `trademark_vienna_codes` | ウィーン図形分類 | 100,320 |

### Phase 2 - 追加データ（tmcloud_import_unified.pyでインポート）

| TSVファイル | データベーステーブル | 説明 | レコード数 |
|------------|-------------------|------|----------|
| `upd_t_basic_item_art.tsv` | `trademark_basic` (UPDATE) | 公告番号・防護番号等の更新 | 16,642 |
| `upd_mrgn_t_rwrt_app_num.tsv` | `trademark_rewrite_applications` | 書換申請情報 | 2,995 |
| `upd_jiken_c_t_chonai_dv.tsv` | `trademark_intermediate_records` | 庁内中間記録 | 1,944 |
| `upd_jiken_c_t_kian_dv.tsv` | `trademark_intermediate_records` | 起案中間記録 | 16,797 |
| `upd_jiken_c_t_sinsei_dv.tsv` | `trademark_intermediate_records` | 申請中間記録 | 32,911 |
| `upd_snkt_bnri.tsv` | `trademark_trial_decisions` | 審決分類 | 0 |

### 未インポートのTSVファイル

以下のTSVファイルは現在インポートされていません：
- 国際商標関連のTSVファイル（intl_*.tsv）
- 審判関連のTSVファイル（snpn_*.tsv）
- その他の補助的なTSVファイル

## カラムマッピング

### 主要なカラム名の統一

#### 出願番号の統一
- TSVファイルでの名称:
  - `shutugan_no` (upd_jiken_c_t.tsv, upd_jiken_c_t_shohin_joho.tsv等)
  - `app_num` (upd_standard_char_t_art.tsv等)
- データベースでの統一名: `app_num`
- 変換: ハイフン除去 `2023-123456` → `2023123456`

#### 類番号の統一
- TSVファイルでの名称: `rui`
- データベースでの統一名: `class_num`

#### 日付フィールド
- 形式: YYYYMMDD (8桁)
- NULL値: '00000000' → NULL
- 主な日付フィールド:
  - `app_date` (出願日)
  - `reg_date` (登録日)
  - `rejection_date` (拒絶日)
  - `final_disposal_date` (最終処分日)

### テーブル別主キー構造

| テーブル | 主キー |
|---------|--------|
| `trademark_basic` | `app_num` |
| `trademark_texts` | `(app_num, text_type, sequence_num)` |
| `trademark_goods_services` | `(app_num, class_num, sequence_num)` |
| `trademark_applicants` | `(app_num, applicant_type, applicant_code)` |
| `trademark_rejections` | `(app_num, rejection_code, rejection_date)` |
| `trademark_vienna_codes` | `(app_num, vienna_code)` |

## データ型と変換

### エンコーディング処理

複数のエンコーディングを試行し、最適なものを自動選択：
```python
encodings = ['utf-8', 'cp932', 'shift_jis', 'euc-jp', 'iso-2022-jp']
```

### 特殊な変換処理

1. **画像データ（trademark_images）**
   - 複数行にまたがるBase64データを結合
   - `rec_seq_num < final_rec_seq_num`で継続行を判定
   - `//`で始まるBase64エンコードデータ

2. **商品・役務テキスト**
   - `lengthchoka_flag='1'`の場合、複数行を結合
   - `abz_junjo_no`で順序管理
   - 最大長: 約5500文字

3. **出願人・代理人の区別**
   - `shutugannindairinin_sikbt`:
     - '1' → 'applicant' (出願人)
     - '2' → 'agent' (代理人)

4. **中間記録の種別**
   - '庁内中間記録' → 'office'
   - '起案中間記録' → 'draft'
   - '申請中間記録' → 'application'

## インポート統計

### 2025-07-28時点のインポート実績

| テーブル | レコード数 | 備考 |
|---------|-----------|------|
| trademark_basic | 16,688 | 商標基本情報 |
| trademark_texts | 4,422 | 標準文字・表示・検索用テキスト |
| trademark_goods_services | 33,385 | 指定商品・役務 |
| trademark_images | 1,612 | 商標画像（Base64） |
| trademark_applicants | 28,742 | 出願人・代理人（重複除去済み） |
| trademark_rights_holders | 16,884 | 権利者 |
| trademark_similar_groups | 63,970 | 類似群コード |
| trademark_pronunciations | 31,678 | 称呼（重複除去済み） |
| trademark_rejections | 5,451 | 拒絶理由 |
| trademark_vienna_codes | 100,320 | ウィーン図形分類 |
| trademark_intermediate_records | 51,652 | 中間記録（3種類合計） |
| trademark_rewrite_applications | 2,995 | 書換申請 |
| app_reg_mapping | 4,557 | 出願番号・登録番号マッピング |
| **合計** | **362,356** | |

### インポート性能

- バッチサイズ: 1,000レコード
- テストモード: 各ファイル最大1,000レコード
- 総インポート時間: 約12秒（テストモード）

## 特記事項

### 1. TSV仕様書

重要な参照文書: `/home/ygenk/TMCloud/TSV_COLUMN_SPECIFICATIONS.md`
- 82個のTSVファイルの完全な仕様
- 正確なカラム定義とデータ型
- 既知の問題（`rui`列の欠落等）への対処法

### 2. カラム名の不統一問題

元のTSVファイルでは出願番号のカラム名が統一されていない：
- `shutugan_no`: 13ファイルで使用
- `app_num`: 他のファイルで使用
→ データベースでは`app_num`に統一

### 3. インデックス戦略

主要インデックス（tmcloud_schema.sqlで定義）：
```sql
CREATE INDEX idx_basic_app_num ON trademark_basic(app_num);
CREATE INDEX idx_basic_reg_num ON trademark_basic(reg_num);
CREATE INDEX idx_texts_app_num ON trademark_texts(app_num);
CREATE INDEX idx_goods_app_class ON trademark_goods_services(app_num, class_num);
CREATE INDEX idx_rejections_app ON trademark_rejections(app_num);
CREATE INDEX idx_vienna_app ON trademark_vienna_codes(app_num);
```

### 4. データの完全性

- 出願番号のハイフン除去により一貫性を保証
- 複数行データの結合処理により欠損を防止
- エンコーディング自動検出により文字化けを回避

## インポート処理フロー

1. **データベース初期化**
   ```bash
   # スキーマ作成
   sqlite3 tmcloud.db < tmcloud_schema.sql
   ```

2. **統合インポート実行**
   ```bash
   # テストモード（各ファイル1000件まで）
   python3 tmcloud_import_unified.py --test
   
   # 本番モード（全データ）
   python3 tmcloud_import_unified.py
   ```

3. **検証**
   ```bash
   # CLI検索ツールで動作確認
   python3 tmcloud_cli_search.py --mark-text "ソニー"
   ```

## 今後の拡張予定

### 実装済み機能
- ✅ 基本的な商標情報のインポート
- ✅ 拒絶理由・ウィーン分類の対応
- ✅ 中間記録のインポート
- ✅ CLI検索ツール（V2）

### 未実装機能
- ❌ Web UI（Flask）
- ❌ 国際商標データのインポート
- ❌ 審判データの完全な対応
- ❌ 週次自動更新システム

---

*最終更新: 2025-07-28*
*データ仕様は日本国特許庁のCSV仕様書に基づく*

---

## TMSONAR 必須カラム

### 出典: `TMSONAR_REQUIRED_COLUMNS.md`

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

---

## TMSONAR カバレッジチェック

### 出典: `TMSONAR_COVERAGE_CHECK.md`

# TMCloud vs TMSONAR 機能比較

## TMSONARの主要検索項目と実装状況

### 1. 基本検索項目 ✅ 実装済み
- ✅ 出願番号検索
- ✅ 登録番号検索
- ✅ 商標（文字）検索
- ✅ 称呼（読み方）検索
- ✅ 出願人・権利者検索
- ✅ 区分（類）検索
- ✅ 指定商品・役務検索

### 2. 日付検索 ✅ 実装済み
- ✅ 出願日検索（範囲指定可）
- ✅ 登録日検索
- ✅ 公開日検索
- ✅ 登録公告日検索

### 3. ステータス検索 ✅ 実装済み
- ✅ 最終処分（査定）
- ✅ 権利状態（存続/消滅）
- ✅ 存続期間満了日

### 4. 拒絶理由検索 ✅ 実装済み
- ✅ 拒絶理由条文（第3条、第4条など）
- ✅ 拒絶理由通知日
- ✅ 拒絶査定日

### 5. 図形商標検索 ✅ 実装済み
- ✅ ウィーン図形分類コード検索
- ✅ 図形商標の有無
- ✅ 画像データの保存・表示

### 6. 類似群コード検索 ✅ 実装済み
- ✅ 類似群コードによる検索
- ✅ 複数類似群コードの表示

### 7. 中間記録検索 ✅ 実装済み
- ✅ 庁内中間記録
- ✅ 起案中間記録
- ✅ 申請中間記録

### 8. その他の検索項目 ⚠️ 一部実装
- ✅ 書換申請情報
- ✅ 公告番号（データは0件）
- ✅ 防護標章番号（データは0件）
- ✅ 出願種別
- ❌ 国際商標（マドプロ）検索
- ❌ 更新情報
- ❌ 異議申立情報
- ❌ 審判情報（データ準備済み、0件）
- ❌ 優先権情報
- ❌ 分割・変更情報

## 実装率サマリー

### カテゴリー別実装状況
| カテゴリー | 実装済み | 未実装 | 実装率 |
|---------|---------|--------|--------|
| 基本検索 | 7 | 0 | 100% |
| 日付検索 | 4 | 0 | 100% |
| ステータス | 3 | 0 | 100% |
| 拒絶理由 | 3 | 0 | 100% |
| 図形商標 | 3 | 0 | 100% |
| 類似群 | 2 | 0 | 100% |
| 中間記録 | 3 | 0 | 100% |
| その他 | 4 | 6 | 40% |
| **合計** | **29** | **6** | **82.9%** |


# SPEC.md — 検索機能 追記ドラフト

> ※本ドラフトは **HTML（全文検索画面・検索結果）由来の項目をそのまま列挙**。解釈・提案なし。

---

## 検索項目（プルダウン／入力欄）

* 商標（ID: 101）
* 称呼（表記同一）（ID: 103）
* 国際分類（類似群コード展開）（ID: 104）
* 法区分＋類（ID: 105）
* 類似群コード（ID: 106）
* 指定商品／役務（ID: 107）
* 拒絶条文コード（ID: 108）
* 審決分類（国内のみ）（ID: 109）
* ウィーンコード（ID: 112）
* 称呼（発音同一）（ID: 123）
* 最終処分（ID: 130）
* 出願人／権利者（ID: 102）
* 出願人／権利者住所（ID: 134）
* 国県コード（出願人）（ID: 129）
* 代理人（ID: 124）
* 出願日／国際登録日（事後指定日）（ID: 110）
* 登録日／国内登録日（ID: 111）
* 新規出願追加日（ID: 113）
* 存続期間満了日（国内のみ）（ID: 114）
* ステータス変更日（ID: 115）
* 最終処分日（ID: 116）
* 拒絶査定発送日（ID: 117）
* 分納満了日（国内のみ）（ID: 121）
* 登録公報発行日（国内のみ）（ID: 122）
* 新規登録追加日（ID: 142）
* 公開公報発行日（ID: 143）
* 出願番号／マドプロ管理番号（ID: 118）
* 登録番号／国際登録番号（ID: 119）
* 審判番号（国内のみ）（ID: 120）
* 出願番号／登録番号（ID: 141）
* 中間記録コード（ID: 131）
* 商標タイプ（ID: 125）
* 商標の詳細な説明（ID: 126）
* 出願種別（ID: 127）
* 付加情報（ID: 128）
* 商標文字数（ID: 132）
* 称呼音数（ID: 133）
* 情報提供数（ID: 135）
* 閲覧請求数（ID: 136）
* 区分数（ID: 137）
* 出願人／権利者数（ID: 138）
* 称呼数（ID: 139）

---

## ヘッダー条件（上部フィルタ）

* ラジオ①：全て／登録済／未登録
* ラジオ②：全て／国内／マドプロ
* チェック：権利存続／失効5年／失効10年／失効全て／出願却下を除く

---

## 検索方法（演算・一致条件・範囲指定）

* 一致条件：完全一致／部分一致／前方一致／後方一致／正規表現
* 論理演算：AND／OR／NOT（括弧によるグルーピング可）
* 範囲指定：日付レンジ（開始日～終了日）

---

## メモ

* 由来：`全文検索画面.txt`・`検索結果.txt`
* 反映方針：そのまま列挙（順不同／重複整理済み）

## 現在のTMCloudデータベースの内容

```
商標基本情報: 16,688件
商標テキスト: 4,422件
指定商品・役務: 33,385件
商標画像: 1,612件
出願人・代理人: 28,742件
権利者: 16,884件
類似群コード: 63,970件
称呼: 31,678件
拒絶理由: 5,451件
ウィーン図形分類: 100,320件
中間記録: 51,652件
書換申請: 2,995件
```

## 結論

**TMSONARの主要な検索機能の82.9%が実装済みです。**

実装済みの機能：
- ✅ 文字商標検索（標準文字、表示用、検索用）
- ✅ 称呼検索
- ✅ 出願人・権利者検索
- ✅ 商品・役務検索
- ✅ 類似群コード検索
- ✅ 拒絶理由検索（条文別）
- ✅ ウィーン図形分類検索
- ✅ 中間記録検索
- ✅ 日付範囲検索

未実装の機能：
- ❌ 国際商標（マドプロ）関連
- ❌ 更新履歴
- ❌ 異議申立
- ❌ 審判情報（TSVファイルにデータなし）
- ❌ 優先権
- ❌ 分割・変更

TMSONARの基本的な商標検索機能はほぼ網羅されており、実用的な商標検索システムとして機能します。

---

## 検索実装ステータス

### 出典: `SEARCH_IMPLEMENTATION_STATUS.md`

# TMCloud 検索機能実装状況
*最終更新: 2025-08-08*

## 📊 現在の実装状況

### ✅ 完了済み機能

#### 1. 商標名検索（FTS5）
- **ファイル**: `tmcloud_search_v2.py`
- **機能**:
  - FTS5による高速部分一致検索
  - NFKC正規化
  - 1-3文字対応のハイブリッド検索（unigram/bigram/trigram）
  - メモリ効率的な処理（10M件対応）

#### 2. 称呼検索（TMSONAR完全準拠）
- **ファイル**: `tmcloud_search_v5_complete.py`
- **機能**:
  - 称呼（発音同一）の5段階処理
    - 発音同一（ヲ＝オ、ヂ＝ジ等）
    - 微差音統一（ヴァ＝バ等）
    - 長音・促音処理
    - 拗音大文字化
    - 段階的処理（ティーエル→テル）
  - 複数キーワード検索（スペース/カンマ区切り）
  - 全指定機能（？で全件検索）
  - 部分一致検索（ワイルドカード対応）

#### 3. 最適化版（高速化）
- **ファイル**: `tmcloud_search_v4_optimized.py`
- **機能**:
  - pronunciation_norm列による事前正規化
  - インデックス最適化
  - IN句上限対策（400件制限）
  - LIKE検索の安全化

### 📁 ファイル構成
```
TMCloud/
├── 検索機能/
│   ├── tmcloud_search_v2.py           # 商標名検索（FTS5）
│   ├── tmcloud_search_v3_phonetic.py  # 称呼検索（基本版）
│   ├── tmcloud_search_v3_phonetic_complete.py  # 称呼検索（拡張版）
│   ├── tmcloud_search_v4_optimized.py # 最適化版
│   └── tmcloud_search_v5_complete.py  # TMSONAR完全準拠版 ★推奨
├── データベース/
│   ├── tmcloud_v2_20250807_213449.db  # メインDB（FTS5構築済み）
│   └── tmcloud_weekly_update.py       # 週次更新スクリプト
└── ドキュメント/
    ├── SEARCH_DEVELOPMENT_LOG.md      # 開発履歴
    ├── TMSONAR_VERIFICATION_REPORT.md # TMSONAR準拠検証
    └── SEARCH_IMPLEMENTATION_STATUS.md # 本ドキュメント
```

## 🎯 次にやるべきこと

### Phase 1: 統合と整理（優先度：高）
1. **統合検索システムの構築**
   ```python
   # tmcloud_search_integrated.py
   - 商標名検索（v2）
   - 称呼検索（v5）
   - 番号検索
   - 日付検索
   を統合した単一インターフェース
   ```

2. **データベース最適化**
   ```bash
   # pronunciation_norm列の確認と最適化
   python3 tmcloud_search_v4_optimized.py --rebuild
   # FTS5インデックスの確認
   python3 tmcloud_search_v2.py --rebuild
   ```

### Phase 2: 書誌検索の実装（優先度：高）
1. **登録番号/出願番号検索**
   - 完全一致/前方一致/後方一致
   - 分割番号・防護番号対応

2. **日付範囲検索**
   - 出願日、登録日、公開日等
   - 期間指定（FROM-TO）

3. **ステータス検索**
   - 法区分＋類
   - 最終処分
   - 権利状態（有効/失効）

### Phase 3: 商品・役務検索（優先度：中）
1. **類似群コード検索**
   - 前方一致対応（例：11?）
   - 複数指定

2. **指定商品/役務検索**
   - 全文検索
   - 区分指定との組み合わせ

3. **国際分類検索**
   - 類似群コード展開

### Phase 4: Web UI開発（優先度：中）
1. **Flask/FastAPIによるWeb API**
   ```python
   # tmcloud_web_api.py
   - RESTful API設計
   - 検索エンドポイント
   - 結果のJSON返却
   ```

2. **フロントエンド**
   ```html
   <!-- tmcloud_search_ui.html -->
   - 検索フォーム
   - 結果一覧表示
   - 詳細表示
   - CSV/Excelエクスポート
   ```

### Phase 5: 運用環境整備（優先度：低）
1. **自動更新システム**
   - cronジョブ設定
   - エラー通知
   - ログローテーション

2. **バックアップ戦略**
   - 定期バックアップスクリプト
   - リストア手順書

3. **パフォーマンス監視**
   - 検索速度計測
   - インデックス最適化スケジュール

## 💡 推奨される次のステップ

### 今すぐやるべきこと（1-2日）
```bash
# 1. 最適化版のセットアップを完了
python3 tmcloud_search_v4_optimized.py tmcloud_v2_20250807_213449.db --rebuild

# 2. 統合検索システムの作成開始
# tmcloud_search_integrated.pyを作成し、v2とv5の機能を統合
```

### 今週中にやるべきこと（3-5日）
- 書誌検索の基本機能実装（番号・日付検索）
- Web APIの基本設計

### 今月中にやるべきこと（2-3週間）
- Web UIの完成
- 全検索機能の統合
- 運用マニュアルの作成

## 📝 注意事項

1. **データベースの週次更新を忘れずに**
   ```bash
   python3 tmcloud_weekly_update.py 20250723 --db tmcloud_v2_20250807_213449.db
   ```

2. **検索インデックスの定期的な再構築**
   - FTS5インデックス：週1回推奨
   - pronunciation_norm：週次更新後に実行

3. **バックアップの重要性**
   - データベース更新前には必ずバックアップ
   - 検索システム変更前にもバックアップ

## 🔗 関連ドキュメント
- [TMSONAR_REQUIRED_COLUMNS.md](TMSONAR_REQUIRED_COLUMNS.md) - 必要カラムマッピング
- [tmcloud_schema_v2_design.md](tmcloud_schema_v2_design.md) - DB設計書
- [WEEKLY_UPDATE_HISTORY.md](WEEKLY_UPDATE_HISTORY.md) - 週次更新履歴

---

## テーブル検証手順

### 出典: `TABLE_VERIFICATION_PROCEDURE.md`

# テーブル検証手順書

## 基本原則
**特許庁CSV仕様書が唯一の真実**
- 推測・憶測は一切禁止
- 仕様書が見つからない場合は、諦めずに徹底的に探す
- カラム名は仕様書の物理名と完全一致させる

## 検証手順

### 1. 特許庁CSV仕様書の特定
1. テーブルに対応するTSVファイル名を確認
2. `/home/ygenk/TMCloud/old_files/csvs/`内で対応する仕様書を検索
   - ファイル名で検索
   - 物理ファイル名で検索
   - カラム名で検索
3. **見つからない場合は諦めるな！**必ず存在する

### 2. 仕様書の読み取り
1. ファイル名（物理名）を確認
2. 主キー（○印のついたカラム）を確認
3. 全カラムの物理名を確認
4. データ型と桁数を確認

### 3. スクリプトの検証
#### 週次更新スクリプト（tmcloud_weekly_update_v17.py）
- key_columnsが主キーと一致しているか
- column_mappingが全カラムを網羅しているか
- TSVファイルのカラム名（左）→DBカラム名（右）のマッピングが正しいか

#### インポートスクリプト（tmcloud_import_v2.py）
- 同様に全カラムが正しくマッピングされているか確認

#### SQLスキーマ（tmcloud_schema_v2.sql）
- PRIMARY KEYが仕様書と一致しているか
- カラム定義が正しいか

## これまでの体たらく記録

### テーブル11: trademark_right_goods
- **失態**: CSV仕様書を探さずに諦めて「見つからない」と報告
- **実際**: 127_本権商品名ファイル.csv が存在していた
- **教訓**: 諦めるな。必ず仕様書は存在する

### 誤ったカラムマッピングの例
1. **trademark_case_info**: 49カラム中21カラムが欠落していた
2. **trademark_applicants_agents**: 存在しないカラム（shutugannindairinin_kojinhoujin）をマッピング
3. **日本語ローマ字の誤字**: sikbt→sikibetu、shurui→shubetu など

### 推測による誤り
- pe_num、mu_num などを勝手に主キーに含めていた
- カラム名を推測で決めていた（例: tokkyo_toroku_no）

## 作業記録フォーマット
```
## テーブルX: テーブル名

### 特許庁CSV仕様書（ファイル番号_ファイル名.csv）
ファイル名: xxx.tsv
主キー: カラム1 + カラム2 + ...

全Xカラム:
1. 物理名 - 論理名 ○主キー
2. ...

### 検証結果
- 週次更新スクリプト: X個のカラムが欠落/誤り
- インポートスクリプト: X個のカラムが欠落/誤り
- SQLスキーマ: 問題なし/問題あり

### 修正内容
（具体的な修正内容を記載）
```

## 作業履歴

### 2025-08-07 全40テーブル検証完了

#### 実施内容
1. 全40テーブルについて、特許庁CSV仕様書との整合性を検証
2. 週次更新スクリプト、インポートスクリプト、SQLスキーマの3ファイルを比較検証
3. 大量のカラムマッピング誤りと PRIMARY KEY 定義の不整合を修正

#### 主な修正箇所
- テーブル1-4: カラム名修正（dt → date など）
- テーブル13-15: 大量のカラムマッピング修正（40カラム以上）
- テーブル29-30: 全カラム名の修正が必要だった
- テーブル32-36: 国際商標関連で PRIMARY KEY 定義が不完全
- テーブル35: madpro_class → madopro_class の誤字修正
- テーブル37: インポートスクリプトのカラム名修正（sytgn_bngu → app_num）
- テーブル38-39: 防護標章関連で大量のカラムマッピング修正

#### 体たらく記録（追加）
- テーブル35で madpro_class の誤字を見逃しそうになった
- PRIMARY KEY の定義で多くのカラムが欠落していたことを発見
- 防護標章関連テーブルで、CSV仕様と全く異なるカラム名を使用していた

#### 結果
- 全40テーブルの検証・修正完了
- 特許庁CSV仕様書との完全な整合性を確保

---

## README（補助情報）

### 出典: `README.md`

# TMCloud - 商標検索システム

TMSONAR互換の商標検索システム。日本特許庁の商標TSVデータを処理・検索可能。

## システム概要

- **データベース**: SQLite（tmcloud.db）
- **スキーマ**: TMSONAR互換の46テーブル構造
- **インポート機能**: 82種類のTSVファイルに対応
- **検索機能**: 出願番号、商標テキスト、商品・役務、類似群コード等

## 現在の状態（2025年7月29日）

### データ状況
- 商標基本情報: 16,688件（週次更新データ）
- 商標テキスト: 8,981件（カバレッジ18.7%）
- 出願人名充足率: 0.4%（申請人マスタ不足）
- ウィーン分類: 100,320件
- 類似群コード: 63,970件

### 課題
現在のTSVファイルは**週次更新データ**のため、全体の3.7%しか含まれていません。
完全なデータベース構築には累積データの入手が必要です。

## ファイル構成

### コアファイル
- `tmcloud_schema.sql` - データベーススキーマ定義
- `tmcloud_import_unified.py` - 統合インポートスクリプト
- `tmcloud_cli_search.py` - CLIベース検索ツール
- `tmcloud_search_improved.py` - 改良版検索（重複除去対応）
- `tmcloud_verify.py` - データ検証ツール
- `check_applicants.py` - 出願人データ確認ツール

### ドキュメント
- `TSV_FILES_COMPLETE_SPECIFICATION.md` - TSVファイル完全仕様
- `TMSONAR_REQUIRED_COLUMNS.md` - TMSONAR必須カラム定義
- `DATABASE_IMPORT_MAPPING.md` - カラムマッピング詳細
- `IMPORT_REPORT_20250729.md` - インポート実施報告
- `final_import_summary_20250729.md` - 最終インポート総括

### ディレクトリ
- `tsv_data/tsv/` - TSVデータファイル（82ファイル）
- `analysis_reports/` - 分析レポート
- `old_files/` - 過去バージョンのファイル

## 使用方法

### データベース初期化
```bash
sqlite3 tmcloud.db < tmcloud_schema.sql
```

### データインポート
```bash
python3 tmcloud_import_unified.py
```

### 商標検索
```bash
# 商標テキスト検索
python3 tmcloud_cli_search.py --mark-text "商標名"

# 出願番号検索
python3 tmcloud_cli_search.py --app-num "2024123456"

# 商品・役務検索
python3 tmcloud_cli_search.py --goods-classes "09,42"
```

### データ検証
```bash
python3 tmcloud_verify.py
python3 check_applicants.py
```

## 今後の対応

1. **累積データの入手**
   - 特許庁から全件データをダウンロード
   - 450,000件以上の商標データが必要

2. **申請人マスタの完備**
   - 現在1,612件→50万件規模が必要

3. **Phase 3実装**
   - 国際商標対応
   - 更新・異議申立情報
   - 優先権情報

## 技術仕様

- Python 3.x + SQLite3
- エンコーディング自動検出（UTF-8, CP932, Shift-JIS対応）
- カラム名正規化（shutugan_no→app_num等）
- 複数行データ処理対応
- TMSONAR互換率: 構造83.3%（データ充実で90%以上可能）

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
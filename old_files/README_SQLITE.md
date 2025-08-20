# TMCloud SQLite版インポートスクリプト

## 概要
TMCloud TSVデータをSQLiteデータベースにインポートする統合スクリプトです。
PostgreSQL版と同等の機能をSQLiteで実現しています。

## 主な機能
- 28テーブルの自動作成とデータインポート
- 出願番号の正規化（ハイフン自動除去）
- 複数行データの自動結合
- JSONフォーマットでの複数レコード保存
- インポート履歴の自動記録
- エラーハンドリングとトランザクション管理

## 使用方法

### 基本的な使い方
```bash
python3 import_tmcloud_data_sqlite.py <TSVディレクトリ>
```

### テストデータでの実行例
```bash
python3 import_tmcloud_data_sqlite.py test_tsv
```

### データベースの確認
```bash
# 詳細な内容確認
python3 check_database_detailed.py

# データベース構造のサマリー
python3 database_summary.py

# 簡易確認
python3 check_database.py
```

## テーブル一覧（28テーブル）

### 基本情報（2テーブル）
- `mgt_info_t` - 管理情報
- `jiken_c_t` - 事件基本情報

### 商標テキスト（3テーブル）
- `standard_char_t_art` - 標準文字商標
- `indct_use_t_art` - 指定商品・役務
- `search_use_t_art_table` - 検索用商標

### 商品・サービス（3テーブル）
- `jiken_c_t_shohin_joho` - 商品・役務情報（複数行結合対応）
- `goods_class_art` - 商品分類
- `t_knd_info_art_table` - 類似群コード

### 権利者・代理人（3テーブル）
- `right_person_art_t` - 権利者情報（JSON形式）
- `jiken_c_t_shutugannindairinin` - 出願人・代理人
- `atty_art_t` - 代理人詳細

### 画像・称呼（2テーブル）
- `t_sample` - 商標画像（Base64、複数行結合対応）
- `t_dsgnt_art` - 称呼情報

### 審査・手続き（5テーブル）
- `jiken_c_t_hanketsu` - 判決情報
- `jiken_c_t_kian_dv` - 起案情報（JSON形式）
- `jiken_c_t_sinsei_dv` - 申請情報（JSON形式）
- `prog_info_div_t` - 進捗情報（JSON形式）
- `jiken_c_t_yusenken_joho` - 優先権情報

### その他情報（3テーブル）
- `jiken_c_t_kohohako_joho` - 公報発行情報
- `jiken_c_t_shousaina_setumei` - 詳細な説明
- `jiken_c_t_tokubyoki_joho` - 特別記載情報

### 登録情報（7テーブル）
- `torokujoho_shutuganninkohan` - 出願人交替情報
- `torokujoho_ganyugokei` - 外国語系情報
- `torokujoho_nonalfabet` - 非アルファベット情報
- `torokujoho_dosound` - 音商標情報
- `torokujoho_gochuimark` - 誤注意商標
- `torokujoho_chichomark` - 地著商標
- `torokujoho_colormark` - 色彩商標

## 特殊処理

### 1. 出願番号の正規化
```python
# 2023-123456 → 2023123456
app_num = self.normalize_app_num(row.get('shutugan_no'))
```

### 2. 複数行データの結合
- `jiken_c_t_shohin_joho`: `abz_junjo_no`で順序管理
- `t_sample`: `rec_seq_num`で順序管理

### 3. JSON形式での保存
- `right_person_art_t`: 複数の権利者情報
- `prog_info_div_t`: 複数の進捗情報
- `jiken_c_t_kian_dv`: 複数の起案情報
- `jiken_c_t_sinsei_dv`: 複数の申請情報

## エラー処理
- 各テーブルごとにトランザクション管理
- エラー時は自動ロールバック
- インポート履歴にエラー情報を記録
- 詳細なログファイル出力

## ログファイル
`import_tmcloud_YYYYMMDD_HHMMSS.log` 形式で自動生成

## 注意事項
- TSVファイルはUTF-8エンコーディングである必要があります
- 出願番号が'0000000000'のレコードは自動的にスキップされます
- SQLiteの制限により、真のJSONB型は使用できません（TEXT型で保存）
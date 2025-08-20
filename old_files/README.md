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
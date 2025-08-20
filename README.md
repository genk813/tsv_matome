# TMCloud - 日本商標データベース検索システム

## 概要
TMCloudは、日本特許庁の商標データを検索・管理するためのPythonベースのシステムです。
SQLiteデータベースに格納された商標情報を高速に検索し、Web UIやCLIから利用できます。

## 主要機能
- 商標名検索（完全一致・部分一致・前方一致）
- 称呼（読み方）検索
- 出願番号・登録番号検索
- 出願人・代理人検索
- 商品・役務検索
- 類似群コード検索
- 複合条件検索（AND/OR）
- 中間記録の表示（審査・審判・登録）
- 商標画像の表示

## ファイル構成

### コアモジュール
- `tmcloud` - CLIツール（実行可能シェルスクリプト）
- `tmcloud_search_integrated.py` - 統合検索エンジン（全検索機能）
- `tmcloud_simple_web.py` - Flask Webサーバー
- `tmcloud_import_v2.py` - 初期データインポート
- `tmcloud_weekly_update.py` - 週次差分更新

### 設定・仕様
- `CLAUDE.md` - 開発ガイドライン
- `SPEC.md` - 詳細仕様書
- `SPEC_TMSONAR.md` - TMSONAR互換仕様
- `HISTORY.md` - 開発履歴・変更記録
- `USAGE.md` - 使用方法

### ディレクトリ
- `tests/` - テストスクリプト
- `utils/` - ユーティリティツール
- `old_versions/` - 旧バージョンアーカイブ
- `old_files/` - 参考資料・仕様書
- `backups/` - データベースバックアップ
- `analysis_reports/` - 分析レポート
- `scripts/` - 補助スクリプト
- `tsv_data/` - TSVデータファイル（.gitignore）

## データベース
- `tmcloud_v2_*.db` - SQLiteデータベース（約1.4GB）
- 40テーブル、約80万件の商標データ
- 全文検索インデックス（FTS5）対応

## 使用方法

### CLI検索
```bash
# 商標名検索
./tmcloud "コカコーラ"

# 称呼検索
./tmcloud "コカコーラ" --type phonetic

# 出願番号検索
./tmcloud "2023123456" --type app_num

# 複合条件検索
./tmcloud --complex
```

### Web UI
```bash
# サーバー起動
python3 tmcloud_simple_web.py

# ブラウザで http://localhost:5000 を開く
```

### 週次更新
```bash
# TSVファイルからの差分更新
python3 tmcloud_weekly_update.py 20250716 --db tmcloud_v2.db
```

## 必要環境
- Python 3.8以上
- SQLite3
- Flask（Web UI用）

## インストール
```bash
# 依存パッケージのインストール
pip install flask

# データベースの初期化（TSVファイルが必要）
python3 tmcloud_import_v2.py
```

## 中間記録コード
3,416個の中間記録コードを正式仕様書から実装：
- C0840（審査中間コード）: 441項目
- C0850（審判中間コード）: 425項目
- C0860（登録中間コード）: 1,978項目
- C1280（マドプロ出願）: 116項目
- C1380（マドプロ原簿）: 456項目

## ライセンス
内部利用のみ

## 更新履歴
最新の更新内容はHISTORY.mdを参照してください。

---
最終更新: 2025-08-14
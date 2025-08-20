# 週次データ更新ガイド

## 概要
特許庁から提供される週次TSVデータを既存のデータベースに効率的に追加・更新するためのガイドです。

## 更新手順

### 1. 新しいTSVデータの取得
```bash
# 特許庁からデータをダウンロード
# 例: JPWRT_YYYYMMDD.zip を展開
mkdir -p weekly_data/YYYYMMDD
cd weekly_data/YYYYMMDD
unzip JPWRT_YYYYMMDD.zip
```

### 2. 週次更新の実行
```bash
# 基本的な更新
python3 weekly_data_updater.py weekly_data/YYYYMMDD/tsv

# データ検証付きの更新
python3 weekly_data_updater.py weekly_data/YYYYMMDD/tsv --validate
```

### 3. 更新結果の確認
```bash
# 更新後の統計確認
python3 analyze_trademark_display.py

# アプリケーションの動作確認
python3 app_dynamic_join_claude_optimized.py
```

## ベストプラクティス

### データ管理
1. **バックアップ**: 更新前に自動でバックアップを作成
2. **段階的更新**: 小さなバッチで更新してエラーを早期発見
3. **検証**: 更新後は必ずデータ整合性をチェック

### ディレクトリ構造
```
tsv_matome/
├── output.db                    # メインデータベース
├── backups/                     # 自動バックアップ
│   ├── output_backup_20250710_120000.db
│   └── output_backup_20250710_140000.db
├── weekly_data/                 # 週次データ
│   ├── 20250710/
│   │   └── tsv/
│   │       ├── upd_jiken_c_t.tsv
│   │       ├── upd_standard_char_t_art.tsv
│   │       └── ...
│   └── 20250717/
│       └── tsv/
└── weekly_data_updater.py      # 更新スクリプト
```

### 更新頻度
- **推奨**: 毎週金曜日の夜間（特許庁の更新後）
- **最小**: 月1回
- **最大**: 毎日（必要に応じて）

## 更新対象テーブル

### 主要テーブル
| テーブル名 | 更新方法 | 説明 |
|-----------|---------|------|
| jiken_c_t | UPSERT | メインの事件情報 |
| standard_char_t_art | UPSERT | 標準文字商標 |
| goods_class_art | REPLACE | 商品・役務区分 |
| jiken_c_t_shohin_joho | REPLACE | 指定商品・役務情報 |
| t_knd_info_art_table | REPLACE | 類似群コード |
| t_dsgnt_art | REPLACE | 称呼情報 |
| t_sample | REPLACE | サンプル・画像データ |

### 特別処理が必要
- `right_person_art_t`: 権利者情報（reg_numベース）
- `reg_mapping`: 登録マッピング（手動実装が必要）

## エラー処理

### 一般的なエラー
1. **ファイルが見つからない**
   ```
   解決: TSVファイルのパスとファイル名を確認
   ```

2. **データ形式エラー**
   ```
   解決: TSVファイルの文字エンコーディングを確認（UTF-8）
   ```

3. **データベースロック**
   ```
   解決: アプリケーションを停止してから更新実行
   ```

### バックアップからの復旧
```bash
# 更新に失敗した場合
cp backups/output_backup_YYYYMMDD_HHMMSS.db output.db

# データベースの整合性確認
python3 analyze_trademark_display.py
```

## 運用スケジュール例

### 毎週金曜日の運用
```bash
#!/bin/bash
# weekly_update.sh

# 1. アプリケーション停止
pkill -f app_dynamic_join_claude_optimized.py

# 2. 新しいデータの取得（手動またはAPI）
echo "新しいTSVデータを weekly_data/$(date +%Y%m%d)/ に配置してください"

# 3. データ更新
python3 weekly_data_updater.py weekly_data/$(date +%Y%m%d)/tsv --validate

# 4. アプリケーション再起動
nohup python3 app_dynamic_join_claude_optimized.py > app.log 2>&1 &

echo "週次更新完了"
```

## 監視とメンテナンス

### 定期チェック項目
1. **データベースサイズ**: 異常な増加がないか
2. **バックアップ**: 最新のバックアップが存在するか
3. **データ品質**: 商標表示率の変化
4. **アプリケーション**: 検索機能の動作確認

### 月次メンテナンス
```bash
# 古いバックアップの整理
find backups/ -name "output_backup_*.db" -mtime +30 -delete

# データベースの最適化
python3 -c "
import sqlite3
conn = sqlite3.connect('output.db')
conn.execute('VACUUM')
conn.close()
print('データベース最適化完了')
"

# 統計情報の更新
python3 analyze_trademark_display.py > monthly_stats.txt
```

## 高度な使用法

### 差分更新
```bash
# 特定のテーブルのみ更新
python3 weekly_data_updater.py weekly_data/20250710/tsv --table jiken_c_t

# 複数テーブルの選択更新
python3 weekly_data_updater.py weekly_data/20250710/tsv --tables jiken_c_t,standard_char_t_art
```

### カスタム更新
```python
# custom_update.py
from weekly_data_updater import WeeklyDataUpdater

updater = WeeklyDataUpdater("output.db")
updater.update_jiken_c_t("path/to/upd_jiken_c_t.tsv")
```

## トラブルシューティング

### よくある問題

1. **メモリ不足**
   ```
   解決: バッチサイズを小さくする
   ```

2. **更新時間が長い**
   ```
   解決: インデックスを一時的に削除してから更新
   ```

3. **データの重複**
   ```
   解決: REPLACE文を使用してデータを置換
   ```

### ログ確認
```bash
# 更新ログの確認
python3 weekly_data_updater.py weekly_data/20250710/tsv 2>&1 | tee update.log

# エラーログの抽出
grep -i error update.log
```

## 連絡先
- システム管理者: [管理者メール]
- 技術サポート: [サポートメール]
- 緊急時: [緊急連絡先]

---

最終更新: 2025年7月10日  
バージョン: 1.0
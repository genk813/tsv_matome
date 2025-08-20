# TMCloud 表形式検索システム 完全版 使い方ガイド

## 概要
TMCloud 表形式検索システム完全版は、インポートされたすべてのデータを活用して、商標情報を網羅的に表示するHTMLレポート生成ツールです。

## 表示される情報

### 基本情報
- **出願番号**: ハイフン付きフォーマット（例: 2024-123456）
- **出願日**: YYYY/MM/DD形式
- **登録状態**: 登録済み／審査中／拒絶／処理中
- **登録日**: 登録済みの場合に表示

### 商標情報
- **商標テキスト**: 優先順位で表示
  1. 標準文字商標（standard_char_t_art）
  2. 表音文字商標（indct_use_t_art）
  3. 検索用商標（search_use_t_art_table）
  4. データがない場合は「（標準文字商標）」または「（図形商標）」

### 分類情報
- **商品・役務区分**: バッジ形式で表示（第9類、第35類など）
- **類似群コード**: カンマ区切りで表示（例: 11C01,09G55）
- **商品・役務名**: 指定商品・役務の説明

### 関係者情報
- **出願人**: 出願人数を表示（例: 出願人2名）
- **代理人**: 代理人がいる場合は併記（例: 出願人2名 (代理人1名)）

## 使用方法

### 1. 日付範囲検索
```bash
# 2024年第1四半期の商標を検索
python3 tmcloud_search_table_complete.py --date-start 2024-01-01 --date-end 2024-03-31 --limit 50 --output 2024Q1_results.html

# 2024年全体の商標を検索（最大100件）
python3 tmcloud_search_table_complete.py --date-start 2024-01-01 --date-end 2024-12-31 --output 2024_all.html

# 特定月の商標を検索
python3 tmcloud_search_table_complete.py --date-start 2024-03-01 --date-end 2024-03-31 --limit 200 --output 2024_march.html
```

### 2. 商品分類検索
```bash
# 第9類（電気機械器具・ソフトウェア）
python3 tmcloud_search_table_complete.py --goods-class 09 --limit 50 --output class09_software.html

# 第35類（広告・事業管理）
python3 tmcloud_search_table_complete.py --goods-class 35 --limit 100 --output class35_business.html

# 第3類（化粧品）
python3 tmcloud_search_table_complete.py --goods-class 03 --output class03_cosmetics.html
```

## コマンドオプション

| オプション | 説明 | 例 |
|-----------|------|-----|
| `--date-start` | 検索開始日（YYYY-MM-DD） | `--date-start 2024-01-01` |
| `--date-end` | 検索終了日（YYYY-MM-DD） | `--date-end 2024-12-31` |
| `--goods-class` | 商品分類コード（2桁） | `--goods-class 09` |
| `--limit` | 表示件数上限（デフォルト: 100） | `--limit 50` |
| `--output` | 出力ファイル名 | `--output results.html` |

## HTMLの特徴

### デザイン
- **モダングラデーション**: 美しいグラデーション背景
- **ホバーエフェクト**: マウスオーバーで行が強調表示
- **ステータス表示**: 登録状態を色分けで表示
  - 緑: 登録済み
  - オレンジ: 審査中
  - 赤: 拒絶
- **レスポンシブデザイン**: PC・タブレット・スマートフォン対応

### 情報の見やすさ
- **区分バッジ**: 商品分類が一目でわかるバッジ表示
- **省略表示**: 長いテキストは適切に省略（...）
- **類似群コード**: 最初の3つを表示、それ以上は件数表示
- **印刷対応**: 印刷時も見やすいレイアウト

## データ品質について

### 利用可能なデータ（2025年7月時点）
- ✅ **基本情報**: 出願番号、出願日、登録日など（100%）
- ✅ **商標テキスト**: 標準文字、表音文字、検索用商標（90%以上）
- ✅ **商品分類**: 区分、指定商品・役務（100%）
- ✅ **類似群コード**: 64,366件のデータ
- ✅ **出願人数**: 各出願の出願人数情報

### 制限事項
- ❌ **商標画像**: 現在は表示されません
- ❌ **権利者名**: 個人情報保護のため非公開
- ❌ **出願人名**: 個人情報保護のため非公開
- ❌ **正確な登録番号**: 登録番号の詳細は取得できません

## トラブルシューティング

### 商標テキストが表示されない場合
- 図形商標の可能性があります
- 「（図形商標）」と表示されます

### 出願人情報が「-」の場合
- 出願人情報が登録されていない古いデータの可能性があります
- 2000年以前のデータは情報が限定的です

### 類似群コードが多すぎる場合
- 最初の3つのコードのみ表示されます
- 残りは「(+N)」形式で件数表示されます

## 実行例

### 最新のIT関連商標を探す
```bash
# 2024年の第9類（ソフトウェア）商標
python3 tmcloud_search_table_complete.py --goods-class 09 --limit 100 --output IT_trademarks_2024.html
```

### 特定期間の全商標を確認
```bash
# 2024年3月の全商標（最大200件）
python3 tmcloud_search_table_complete.py --date-start 2024-03-01 --date-end 2024-03-31 --limit 200 --output march_2024_all.html
```

### 化粧品関連の商標調査
```bash
# 第3類（化粧品）の最新50件
python3 tmcloud_search_table_complete.py --goods-class 03 --limit 50 --output cosmetics_latest.html
```

## ファイル一覧
- `tmcloud_search_table_complete.py`: 完全版検索スクリプト
- `tmcloud_tsv.db`: SQLiteデータベース（商標データ）
- 生成されるHTMLファイル: 指定した出力ファイル名

## 更新履歴
- 2025-07-21: 完全版リリース
  - 商標テキスト表示機能を追加
  - 類似群コード表示機能を追加
  - 出願人数表示機能を追加
  - ステータス表示を改善
# TMCloud 使用方法

## 🚀 クイックスタート

### 方法1: CLI（コマンドライン）
```bash
# 基本的な使い方
./tmcloud "プル"

# 詳細オプション
./tmcloud "アップル" --type trademark --limit 20

# JSON出力
./tmcloud "2025049545" --type app_num --json

# 称呼検索
./tmcloud "プルーム" --type phonetic
```

### 方法2: Web UI（ブラウザ）
```bash
# Webサーバー起動
python3 tmcloud_simple_web.py

# ブラウザで開く
# http://localhost:5000
```

### 方法3: Python API
```python
from tmcloud_search_integrated import TMCloudIntegratedSearch

searcher = TMCloudIntegratedSearch('tmcloud_v2_20250810_restored.db')
results = searcher.search_trademark_name('プル', limit=10)

for result in results:
    info = result['basic_info']
    print(f"{info['app_num']}: {info['trademark_name']}")
```

## 📊 実行例

### CLI実行例
```bash
$ ./tmcloud "プル" --limit 3

検索結果: 3件
================================================================================

[1] トリプルエンジン戦略
  出願番号: 2025051892
  登録番号: None
  出願日: 20250513
  区分: 41
  称呼: トリプルエンジンセンリャク, トリプルエンジン
  商品・役務:
    区分41: 技芸・スポーツ又は知識の教授，インターネットを利用した知識の教授...

[2] プルオク
  出願番号: 2025049995
  登録番号: None
  出願日: 20250508
  区分: 28
  称呼: プルオク
  商品・役務:
    区分28: フラシ天おもちゃ，おもちゃの乗物，ジグソーパズル...

[3] アップルペーパー
  出願番号: 2025049545
  登録番号: None
  出願日: 20250421
  区分: 16
  称呼: アップルペーパー, アップル
  商品・役務:
    区分16: 事務用又は家庭用ののり及び接着剤，封ろう，印刷用インテル...
```

### Web UI
1. `python3 tmcloud_simple_web.py` を実行
2. ブラウザで `http://localhost:5000` を開く
3. 検索フォームにキーワードを入力
4. 結果がブラウザに表示される

## 🔧 オプション

### CLI オプション
| オプション | 説明 | 例 |
|-----------|------|-----|
| `-t, --type` | 検索タイプ | `trademark`, `phonetic`, `app_num`, `applicant` |
| `-l, --limit` | 最大表示件数 | `--limit 20` |
| `--db` | データベースファイル | `--db mydb.db` |
| `--json` | JSON形式で出力 | `--json` |

### Web API エンドポイント
| エンドポイント | メソッド | 説明 |
|---------------|---------|------|
| `/` | GET | 検索画面 |
| `/search` | POST | 検索API（JSON） |

## 📁 ファイル構成
```
TMCloud/
├── tmcloud                     # CLI実行ファイル
├── tmcloud_simple_web.py       # Web UIサーバー
├── tmcloud_search_integrated.py # 検索エンジン本体
└── tmcloud_v2_*.db            # データベース
```

## 🔄 将来の拡張

### Phase 1（現在）
- CLI検索 ✅
- 簡易Web UI ✅
- JSON出力 ✅

### Phase 2（計画中）
- 認証機能
- 検索履歴
- お気に入り機能
- エクスポート機能

### Phase 3（将来）
- フル機能Web UI（React/Vue）
- REST API完全対応
- マルチユーザー対応
- クラウドデプロイ

## 💡 Tips

### データベース更新後
```bash
# 週次更新実行後、DBパスを更新
./tmcloud "検索語" --db tmcloud_v2_新しい日付.db
```

### 大量検索結果のエクスポート
```bash
./tmcloud "検索語" --limit 1000 --json > results.json
```

### パイプライン処理
```bash
./tmcloud "プル" --json | jq '.[] | .basic_info.app_num'
```

## 🐛 トラブルシューティング

### ポート5000が使用中
```bash
# 別のポートを使用
python3 tmcloud_simple_web.py --port 8080
```

### データベースエラー
```bash
# データベースパスを確認
ls -la *.db
# 正しいパスを指定
./tmcloud "検索語" --db 正しいパス.db
```

---
*詳細は SPEC_TMSONAR.md を参照*
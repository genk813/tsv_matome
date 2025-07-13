# 自走商標検索システム

WSL上で動作する自律的な商標検索・改善システム。商標検索、自動テスト、パフォーマンス改善を自動で実行します。

## 🎯 システム概要

- **CLI商標検索ツール**: Flaskアプリと同等の検索機能をコマンドラインで実行
- **自動テストシステム**: 様々な検索シナリオを自動実行し品質を評価
- **自己改善システム**: 問題を自動検出してデータベース最適化を実行
- **統合ランチャー**: 全機能を簡単に実行できる統合インターフェース

## 🚀 クイックスタート

### 基本的な使い方

```bash
# システム状況確認
python3 autonomous_system_launcher.py status

# 商標検索実行
python3 autonomous_system_launcher.py search --mark-text "ソニー" --limit 10

# 自動テスト実行
python3 autonomous_system_launcher.py test

# 自己改善実行（単発）
python3 autonomous_system_launcher.py improve

# 全機能デモ
python3 autonomous_system_launcher.py demo
```

### 高度な使い方

```bash
# 継続的改善（3サイクル、30秒間隔）
python3 autonomous_system_launcher.py improve --continuous --cycles 3 --interval 30

# 複合検索
python3 autonomous_system_launcher.py search --mark-text "コンピュータ" --goods-classes "9" --limit 20
```

## 📁 システム構成

### コアファイル

- `cli_trademark_search.py` - CLI商標検索ツール（Flaskアプリと同等機能）
- `autonomous_test_system.py` - 自動テストシステム
- `self_improving_system.py` - 自己改善システム
- `autonomous_system_launcher.py` - 統合ランチャー
- `search_results_html_generator.py` - HTML検索結果生成ツール

### データファイル

- `output.db` - SQLite商標データベース（415,300レコード）
- `improvement_history.json` - 改善履歴ファイル
- `test_results/` - テスト結果ディレクトリ
- `search_results/html/` - HTML検索結果ディレクトリ

## 🔍 CLI商標検索ツール

### 基本検索

```bash
# 出願番号検索
python3 cli_trademark_search.py --app-num "2024012345"

# 商標文字検索
python3 cli_trademark_search.py --mark-text "ソニー"

# 商品区分検索
python3 cli_trademark_search.py --goods-classes "9"

# 指定商品検索
python3 cli_trademark_search.py --designated-goods "コンピュータ"
```

### 複合検索

```bash
# 商標文字 + 商品区分
python3 cli_trademark_search.py --mark-text "ソニー" --goods-classes "9"

# 複数条件での絞り込み
python3 cli_trademark_search.py --mark-text "テレビ" --goods-classes "9" --limit 50
```

### 出力形式

```bash
# テキスト形式（デフォルト）
python3 cli_trademark_search.py --mark-text "ソニー" --format text

# JSON形式
python3 cli_trademark_search.py --mark-text "ソニー" --format json

# HTML形式（綺麗なレポート）
python3 search_results_html_generator.py --mark-text "ソニー" --limit 20
python3 autonomous_system_launcher.py search --mark-text "ソニー" --html --output "sony_report.html"
```

## 🧪 自動テストシステム

システムを自動的にテストして品質を評価します。

### 実行

```bash
python3 autonomous_test_system.py
```

### テストシナリオ

1. **基本検索テスト**
   - 出願番号検索
   - 商標文字検索  
   - 商品区分検索

2. **複合検索テスト**
   - 複数条件での検索

3. **エラーケーステスト**
   - 存在しない出願番号
   - 空文字検索

4. **パフォーマンステスト**
   - 連続検索での実行時間測定

### 評価項目

- **実行時間**: 検索の応答性能
- **データ品質**: 結果の完全性と正確性
- **エラー率**: システムの安定性
- **成功率**: 全体的な信頼性

## ⚡ 自己改善システム

自動的にシステムの問題を検出し、改善を実装します。

### 単発改善

```bash
python3 self_improving_system.py single
```

### 継続的改善

```bash
# 3サイクル、30秒間隔
python3 self_improving_system.py continuous 3 30
```

### 改善機能

1. **パフォーマンス最適化**
   - データベースインデックス追加
   - クエリ最適化
   - VACUUM実行

2. **データ品質向上**
   - 重複データ削除
   - データ正規化
   - 不正値修正

3. **自動評価**
   - 改善前後の性能比較
   - 改善効果の定量評価
   - 履歴管理

### 評価指標

```python
{
    'performance': {
        'max_acceptable_time': 5.0,      # 最大許容実行時間
        'target_success_rate': 95.0,     # 目標成功率
    },
    'data_quality': {
        'min_mark_text_coverage': 90.0,  # 商標文字表示率
        'min_valid_app_nums': 95.0,      # 有効出願番号率
    },
    'system_stability': {
        'max_error_rate': 5.0,           # 最大エラー率
        'min_uptime': 99.0,              # 最小稼働時間
    }
}
```

## 📊 結果ファイル

### テスト結果

```json
{
  "timestamp": "2025-07-12T08:09:07.123456",
  "test_scenarios": 5,
  "successful_tests": 5,
  "failed_tests": 0,
  "success_rate": 100.0,
  "performance_metrics": {
    "average_time": 0.03,
    "max_time": 0.04,
    "min_time": 0.03
  },
  "improvement_suggestions": [
    "実行時間が遅いテスト: 1件 - クエリ最適化が必要"
  ]
}
```

### 改善履歴

```json
{
  "sessions": [...],
  "total_improvements": 5,
  "best_performance": {
    "success_rate": 100.0,
    "execution_time": 44.34
  }
}
```

## 🔧 トラブルシューティング

### よくある問題

1. **データベースファイルが見つからない**
   ```bash
   # 解決方法：データベースパスを指定
   python3 cli_trademark_search.py --db /path/to/output.db --mark-text "ソニー"
   ```

2. **検索結果が0件**
   ```bash
   # 解決方法：検索条件を確認
   python3 cli_trademark_search.py --mark-text "ソニー" --limit 50
   ```

3. **実行時間が長い**
   ```bash
   # 解決方法：自動改善を実行
   python3 self_improving_system.py single
   ```

### ログ確認

- テスト結果: `test_results/test_results_YYYYMMDD_HHMMSS.json`
- 改善履歴: `improvement_history.json`
- エラーログ: 標準エラー出力

## 🎯 使用ケース

### 1. 日常的な商標検索

```bash
# 新商品名の商標調査
python3 autonomous_system_launcher.py search --mark-text "新商品名" --goods-classes "35"

# 競合他社の商標調査
python3 autonomous_system_launcher.py search --mark-text "競合社名" --limit 100
```

### 2. システムメンテナンス

```bash
# 週次システムチェック
python3 autonomous_system_launcher.py test

# 月次パフォーマンス改善
python3 autonomous_system_launcher.py improve --continuous --cycles 5
```

### 3. 開発・デバッグ

```bash
# 新機能のテスト
python3 autonomous_test_system.py

# パフォーマンス分析
python3 self_improving_system.py single
```

## 🚀 今後の発展

### Flask/Web化

現在のCLIシステムをベースに、Webインターフェースを構築予定：

1. **API化**: CLI機能をREST APIとして公開
2. **Web UI**: Flaskベースのユーザーインターフェース
3. **リアルタイム改善**: Webアクセスログを使った自動改善

### 機能拡張

- **機械学習**: 検索精度向上のためのMLモデル統合
- **分散処理**: 大量データ処理のための並列化
- **API連携**: 外部商標データベースとの連携

## 📝 ライセンス

MIT License

## 👨‍💻 作成者

Claude Code (Anthropic) + User Collaboration

---

**注意**: このシステムは日本の商標データベース（特許庁TSVファイル）を使用しています。商用利用の際は適切なライセンス確認を行ってください。
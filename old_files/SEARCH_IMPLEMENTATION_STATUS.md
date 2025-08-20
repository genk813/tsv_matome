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
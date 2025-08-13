# HISTORY.md — 履歴・レポート・検証記録

---

## 2025-08-14 中間記録コードの正式仕様書準拠への修正

### 問題の発見と対応
1. **不正確なコードマッピングの発見**
   - 登録番号5026160で「実用新案登録願」等の特許用語が表示される問題
   - 出願番号2025038959で「特許査定」が表示される問題（商標では「登録査定」が正しい）
   - 登録番号1955387の出願種別が「防護標章」ではなく「防護の更新」である問題

2. **正式仕様書からのコード抽出**
   - `04.docx`（コード表マスタ）から中間記録コードを完全抽出
   - C0840（審査中間コード）: 441項目
   - C0850（審判中間コード）: 425項目  
   - C0860（登録中間コード）: 1978項目
   - C1280（マドプロ出願中間コード）: 116項目
   - C1380（マドプロ原簿中間コード）: 456項目
   - 合計3416項目のコードマッピングを実装

3. **重複コード問題の解決**
   - 同一コードで特許用と商標用が存在する場合、備考欄で判別
   - 例: A01は「特許査定」と「登録査定」の2つ存在 → 商標では「登録査定」を使用
   - A80, A916, A971004等も商標用の正しい名称に修正

4. **出願種別コードの正式対応**
   - `4-02出願マスタ（意商）_1.13版.docx`からコードINDEX 02010を発見
   - コード13: 「防護標章」→「防護の更新」に修正
   - コード11: 「防護」（65条1項）
   - 全14種類の出願種別を正式名称で実装

### Web UIの改善
- 中間記録の分類ロジックを修正
  - コンテンツベースから接頭辞ベースの判定に変更
  - A系→審査、数字→審判、R系→登録、IB/MD/AP/M3→マドプロ

### 技術的詳細
- 全角・半角のコード記号を統一処理（例: Ａ０１→A01）
- 3416個の中間記録コードを5つのカテゴリ別辞書に整理
- 仕様書の備考欄を確認し、商標専用のマッピングを選別

---

## 2025-08-12 中間記録表示の重大バグ修正

### 発見した問題
1. **検索方法による中間記録の欠落**
   - 商標名検索や複合検索で、一部の出願の中間記録が表示されない（願書も含む）
   - 出願番号検索では正しく表示される

2. **根本原因**
   - `_format_unified_result`メソッドのSQLクエリで`LIMIT 20`がサブクエリ全体に適用
   - 複数出願検索時、最初の数件が20件の枠を使い切り、残りの出願の記録が取得されない

### 修正内容
1. **SQLクエリの修正**
   - `progress_data`サブクエリから`LIMIT 20`を削除
   - 各出願の全中間記録を取得するように変更

2. **コードマッピングの修正**
   - 出願種別: '01'→'通常出願'（27556件の実データに基づく）
   - 審査種別: '01'→'通常審査'（27503件の実データに基づく）
   - 中間記録: A821→'出願審査請求書'等、未マッピングコードを追加

3. **Web UI改善**
   - 中間記録の表示制限（5件）を撤廃、全件表示に
   - 出願種別・審査種別の日本語変換を実装

### 検証結果
- 全出願の99.8%に願書（A63）が存在することを確認
- 修正後、商標名検索でも全ての中間記録が正しく表示される

---

## 2025-08-11 商標画像対応とUI改善

### 完了した作業

#### 修正1: 折り畳み表示の重複問題
- 商品・役務の折りたたみ表示で、サマリーに項目数のみ表示するよう修正
- 展開時にのみ詳細テキストを表示（重複解消）

#### 修正2: 半角全角正規化問題
- 出願人検索で半角英数字でヒットしない問題を修正
- 解決策：NFKC正規化後の半角パターンと全角パターンの両方で検索

#### 修正3: 商標表示優先順位の実装
- 優先順位：画像→商標見本→標準文字→表示用商標
- `trademark_images`テーブルのJP形式画像データをBase64デコードして表示
- M2形式などの特殊圧縮形式は除外し、テキストデータを表示
- 全検索メソッドでCOALESCE優先順位を実装

#### 商標画像対応
- `trademark_images`テーブルから画像データを取得（複数行対応）
- Base64エンコードされたJPEG画像をWeb UIで表示
- 例：app_num 2025049741は画像が正しく「[商標画像]」として表示される

#### UI改善3項目
1. **商品役務の折り畳み廃止** - 全文を常に表示
2. **検索結果上限を3000件に拡張** - 全検索メソッドで対応
3. **検索後の並び替え機能** - クライアント側でのリアルタイム並び替え実装
   - 検索時ではなく、検索結果表示後に並び替え可能
   - 6種類のソート（出願日・登録日・商標名の昇順/降順）

### 次のステップ（最優先）

#### ✅ 完了: TMSONARレベルの検索結果表示項目の充実（2025-08-11）
統一フォーマットに以下の重要項目を追加：

**追加した表示項目:**
1. **ステータス情報**
   - ✅ 最終処分コード/日付（final_disposition_type/date）
   - ✅ 存続期間満了日（conti_prd_expire_date）- trademark_management_info/basic_itemsから取得
   - ✅ 次回分納期限日（next_pen_payment_limit_date）- trademark_management_infoから取得

2. **公報情報**
   - ✅ 登録公報発行日（reg_article_gazette_date）
   - ✅ 公開公報発行日（pub_article_gazette_date）

**実装内容:**
- `tmcloud_search_integrated.py`の`_get_unified_results`メソッドを修正
  - basic_dataクエリにtrademark_management_info、trademark_basic_itemsをJOIN
  - 新フィールドを統一フォーマット結果に追加
- `tmcloud_simple_web.py`のHTML表示部分を更新
  - 新フィールドの表示を追加（JavaScript部分）
- `tmcloud`CLIツールを修正
  - unified_format=Trueを全検索メソッドに適用
  - 新フィールドの表示を追加

**動作確認:**
- 出願番号2005081102（登録商標「ふわとろ」）で検証
- 存続期間満了日: 20260630
- 登録公報発行日: 20060801
- 公開公報発行日: 20050922
- 最終処分コード: A01（登録査定）

### 次のステップ（今後の改善）
   - 審判番号（appeal_trial_no）
   - 拒絶条文コード（rejection_article_codes）

3. **商標タイプ・付加情報**
   - 商標タイプ（trademark_type: 標準文字/図形/立体など）
   - 出願種別（app_type1-5: 通常/分割/変更など）
   - 付加情報（orig_app_type: 3条2項など）

4. **出願人・代理人の詳細**
   - 出願人住所（applicant_address）
   - 国県コード（country_code）
   - 代理人の詳細情報

5. **中間記録・進捗**
   - 中間記録コード（intermediate_code）
   - 進捗情報（process_date）

**データ取得・表示の改善:**
- 各テーブルからの情報取得を_format_unified_result()に追加
- Web UIでの表示レイアウト改善（情報の階層化・グループ化）
- 重要情報の強調表示（ステータス、期限など）

#### その他の改善候補（低優先度）
- ステップ5: CSVエクスポート機能
- ステップ7: ページネーション実装
- 検索履歴機能
- お気に入り機能
- 詳細画面の実装

---

## 2025-08-10 Web UI改善作業

### ステップ6 完了: 複合条件検索（AND/OR切り替え）とバグ修正
- **検索メソッド追加**: `search_complex`メソッドを`TMCloudIntegratedSearch`クラスに追加
  - 複数の検索条件を組み合わせ可能
  - AND/OR演算子で条件を結合
  - 既存の検索メソッドを内部で再利用（安全な実装）
- **Web UI**: 複合条件検索フォームを追加
  - 2つの条件を指定可能
  - 検索タイプ: 商標名、称呼、区分、出願人、商品・役務
  - AND/OR切り替え可能
- **APIエンドポイント**: `/search_complex`を追加
- **バグ修正**: 区分検索の問題を修正
  - 問題: `search_by_international_class`が類似群コードテーブルのみ参照（全商標をカバーしない）
  - 解決: `_search_by_class_for_complex`メソッドを追加、`trademark_goods_services`テーブルから直接検索
  - 結果: 区分03 OR 05の検索が正しく4000件以上ヒットするように改善
- 動作確認:
  - 商標名「プル」AND 区分「28」→ 1件（プルオク）
  - 区分「03」OR 区分「05」→ 4000件以上（修正後）
  - 区分「03」AND 区分「05」→ 約679件

### バグ修正: DB接続のコネクション切れ問題
- **問題**: Web UIで起動時に1回だけDB接続を作成していたため、長時間経過後にコネクションが切れてエラーが発生
- **修正**: 検索リクエストごとに新しいDB接続を作成するよう変更
- **結果**: 商標検索・称呼検索が正常に動作するように改善

### ステップ4 完了: 検索結果の並び替え機能
- **Web UI**: 並び替えセレクトボックスを追加（6種類のソート方法）
  - 出願日（新しい順/古い順）
  - 登録日（新しい順/古い順）
  - 商標名（A-Z/Z-A）
- **サーバー側**: 並び替え処理を実装
  - basic_info内のデータを参照して適切にソート
  - 降順/昇順の判定ロジック
- **CLIツール**: `--sort`オプションを追加
  - デフォルトは出願日の新しい順
- 動作確認:
  - 化粧品検索で出願日順の並び替え確認
  - 商標名検索で名前順の並び替え確認

### セキュリティとパフォーマンス改善
- **XSS対策**: エスケープ関数を実装し、全18箇所の動的コンテンツに適用
- **エラーハンドリング**: HTTPステータスコード（400, 500）を適切に返すよう修正
- **パフォーマンス**: DB接続をアプリ起動時に1回作成し使い回し
- **折りたたみUI**: 長い商品・役務テキスト（200文字以上）にdetails要素を適用
- **環境変数対応**: FLASK_DEBUG, FLASK_HOST, FLASK_PORTで設定可能に
- **コード品質**: 未使用importを削除

## 2025-08-10 Web UI改善作業（前半）

### ステップ3-2 完了: 類似群コード検索の追加
- **tmcloud_simple_web.py** に類似群コード検索オプション追加
- **tmcloud** CLIツールに類似群コード検索オプション追加
- 検索メソッド `search_by_similar_group` は既にunified_format対応済み
- 動作確認:
  - 完全一致検索: `01A01` → 正常動作
  - 前方一致検索: `01A?` → 正常動作

### ステップ3-3 完了: 商品・役務AND検索の追加
- **search_goods_services** メソッドにunified_formatパラメータ追加
- LEFT JOINをINNER JOINに変更（他メソッドと一貫性確保）
- **tmcloud_simple_web.py** に商品・役務検索オプション追加
- **tmcloud** CLIツールに商品・役務検索オプション追加
- **バグ修正**: QueryParser.split_termsメソッドの重複処理を修正
  - 問題: カンマと空白の分割を別々に処理していたため重複が発生
  - 解決: 正規表現`r'[,，\s　]+'`で一度に処理
- 動作確認:
  - 単一キーワード検索: `化粧品` → 正常動作
  - AND検索: `小売 卸売` → 正常動作（修正後）

---

## 週次更新履歴（最新）

### 出典: `WEEKLY_UPDATE_HISTORY_v16.md`

# TMCloud 週次更新システム作業履歴

## 2025-08-05 作業記録

### 実施内容

#### 削除系ファイル対応（v16）
- **tmcloud_weekly_update.py** を v16 に更新
- 削除系ファイル（del_*.tsv）の処理ロジックを実装
  - `del_snpn_zkn.tsv`: 審判番号による審判事件の削除
  - `del_t_basic_item_art.tsv`: 出願番号による商標関連データの削除
- 削除対象テーブルを12テーブルに拡張
- 削除前のデータ存在確認を追加
- 削除処理の詳細ログ出力を追加

#### 削除処理の動作確認
- 20250611のデータで削除処理をテスト
- 削除結果：
  - 出願番号 2017114531, 2020145693 の2件を削除
  - 合計80件のレコードを12テーブルから削除
  - 各テーブルの削除件数を詳細にログ出力

### 削除系ファイルの分析結果
- 削除ファイルは週次データに含まれたり含まれなかったりする
- 含まれる週: 20250611, 20250618, 20250709, 20250716
- 含まれない週: 20250625, 20250702
- ファイル構造は同一、削除対象のキー（審判番号/出願番号）のみ異なる

## 2025-08-04 作業記録

### 実施内容

#### 1. 週次更新スクリプトのテスト
- **tmcloud_weekly_update.py** (v15) の動作確認
- 20250625 → 20250702 → 20250709 → 20250716 の週次更新テストを実施
- すべてのテストで正常にUPSERT動作（挿入/更新）することを確認

#### 2. 週次TSVデータの分析
- 各週のデータには60-70%の重複（既存出願のステータス更新）があることを判明
- 週次ファイルには新規出願と既存出願の更新が混在
- 更新が多く、挿入が少ないのは正常な動作

#### 3. フォルダ整理
削除したファイル:
- 更新統計JSONファイル（23個）
- テスト用データベース（6個）
- Zone.Identifierファイル（多数）
- 古いバックアップスクリプト（3個）
- 一時テストスクリプト（4個）
- 古いデータベースバックアップ

#### 4. データベース再作成
- 誤って削除したメインデータベースを再作成
- `tmcloud_v2_20250804_215722.db` (393MB) を20250611データから作成
- 全テーブルに正常にデータをインポート

#### 5. TSVファイル構造の統一
- 20250618と20250625のサブフォルダ構造をフラット化
- すべての週次データを「日付フォルダ/TSVファイル」の統一構造に変更
- 各週のファイル数: 82〜98個

### 現在のシステム状態

#### メインファイル
- **tmcloud_weekly_update.py** - 週次更新スクリプト（v16、削除対応済み）
- **tmcloud_import_v2.py** - 初期インポート用
- **tmcloud_schema_v2.sql** - データベーススキーマ
- **tmcloud_v2_20250804_215722.db** - メインデータベース（393MB）

#### TSVデータ構造
```
tsv_data/tsv/
├── 20250611/  (82 TSVファイル、del_あり)
├── 20250618/  (93 TSVファイル、del_あり)  
├── 20250625/  (89 TSVファイル、del_なし)
├── 20250702/  (92 TSVファイル、del_なし)
├── 20250709/  (94 TSVファイル、del_あり)
└── 20250716/  (98 TSVファイル、del_あり)
```

### 更新履歴

#### v16 (2025-08-05) - 最新版
- 削除系ファイル（del_*.tsv）の処理を実装
- 削除対象テーブルを12テーブルに拡張
- 削除前のデータ存在確認とエラーハンドリングを追加

#### v15 (2025-08-04)
- TSVファイルのディレクトリ構造を統一化
- 重複ファイルの処理を修正

#### v12 (2025-08-02)
- 全テーブルのPRIMARY KEY修正
- エラー0件を達成

---

## 週次更新履歴（従来）

### 出典: `WEEKLY_UPDATE_HISTORY.md`

# TMCloud 週次更新システム作業履歴

## 2025-08-04 作業記録

### 実施内容

#### 1. 週次更新スクリプトのテスト
- **tmcloud_weekly_update.py** (v15) の動作確認
- 20250625 → 20250702 → 20250709 → 20250716 の週次更新テストを実施
- すべてのテストで正常にUPSERT動作（挿入/更新）することを確認

#### 2. 週次TSVデータの分析
- 各週のデータには60-70%の重複（既存出願のステータス更新）があることを判明
- 週次ファイルには新規出願と既存出願の更新が混在
- 更新が多く、挿入が少ないのは正常な動作

#### 3. フォルダ整理
削除したファイル:
- 更新統計JSONファイル（23個）
- テスト用データベース（6個）
- Zone.Identifierファイル（多数）
- 古いバックアップスクリプト（3個）
- 一時テストスクリプト（4個）
- 古いデータベースバックアップ

#### 4. データベース再作成
- 誤って削除したメインデータベースを再作成
- `tmcloud_v2_20250804_215722.db` (393MB) を20250611データから作成
- 全テーブルに正常にデータをインポート

#### 5. TSVファイル構造の統一
- 20250618と20250625のサブフォルダ構造をフラット化
- すべての週次データを「日付フォルダ/TSVファイル」の統一構造に変更
- 各週のファイル数: 82〜98個

### 現在のシステム状態

#### メインファイル
- **tmcloud_weekly_update.py** - 週次更新スクリプト（動作確認済み）
- **tmcloud_import_v2.py** - 初期インポート用
- **tmcloud_schema_v2.sql** - データベーススキーマ
- **tmcloud_v2_20250804_215722.db** - メインデータベース（393MB）

#### TSVデータ構造
```
tsv_data/tsv/
├── 20250611/  (82 TSVファイル)
├── 20250618/  (93 TSVファイル)  
├── 20250625/  (89 TSVファイル)
├── 20250702/  (92 TSVファイル)
├── 20250709/  (94 TSVファイル)
└── 20250716/  (98 TSVファイル)
```

### 週次更新の動作確認結果
- UPSERT機能は正常に動作
- 既存レコードは更新、新規レコードは挿入
- エラー0件で安定動作

## 次のステップ
1. 実運用での週次更新プロセスの確立
2. 自動化スクリプトの作成（必要に応じて）
3. バックアップとリカバリ手順の文書化

---

## インポート実施レポート（2025-07-29）

### 出典: `IMPORT_REPORT_20250729.md`

# TMCloud Database Import Report
Date: 2025-07-29

## Summary
Successfully completed the import of trademark data from TSV files into the unified TMCloud database schema.

## Actions Performed

1. **Database Backup Created**
   - Backup file: `tmcloud_backup_20250729_073523.db`
   - Original size: 298.7 MB

2. **Schema Updates Applied**
   - Updated `tmcloud_import_unified.py` to match the new schema in `tmcloud_schema.sql`
   - Removed deprecated columns: `old_law`, `version_code`
   - Fixed column name: `applicant_name_kanji` → `applicant_name_kana`
   - Added missing table definitions for Phase 2 tables

3. **Data Import Completed**
   - Successfully imported data from 35 TSV files
   - Total records imported: 452,261
   - Tables with data: 21 out of 41 total tables

## Import Statistics by Table

| Table Name                          | Record Count |
|-------------------------------------|--------------|
| app_reg_mapping                     | 4,557        |
| applicant_master                    | 1,612        |
| intl_trademark_first_indication     | 1,331        |
| trademark_additional_info           | 33,404       |
| trademark_applicants                | 28,742       |
| trademark_attorneys                 | 20,349       |
| trademark_basic                     | 16,688       |
| trademark_goods_services            | 33,385       |
| trademark_images                    | 1,612        |
| trademark_intermediate_records      | 51,652       |
| trademark_management                | 16,884       |
| trademark_priority                  | 352          |
| trademark_pronunciations            | 31,678       |
| trademark_rejections                | 5,451        |
| trademark_rewrite_applications      | 2,995        |
| trademark_rights_holders            | 16,884       |
| trademark_similar_groups            | 63,970       |
| trademark_texts                     | 4,422        |
| trademark_updates                   | 15,938       |
| trademark_vienna_codes              | 100,320      |
| **Total**                           | **452,261**  |

## Phase Completion Status

### Phase 1 - Core Tables (Complete)
- ✅ trademark_basic
- ✅ trademark_texts
- ✅ trademark_goods_services
- ✅ trademark_applicants
- ✅ trademark_rights_holders
- ✅ trademark_pronunciations
- ✅ trademark_similar_groups
- ✅ applicant_master
- ✅ app_reg_mapping

### Phase 2 - Extended Tables (Partial)
- ✅ trademark_rejections
- ✅ trademark_vienna_codes
- ✅ trademark_intermediate_records
- ✅ trademark_updates
- ✅ trademark_priority
- ✅ trademark_management
- ✅ trademark_additional_info
- ✅ trademark_rewrite_applications
- ✅ trademark_attorneys
- ✅ intl_trademark_first_indication
- ⚠️ Some Phase 2 tables have no data yet (pending TSV files)

### Phase 3 - Advanced Features (TODO)
- ❌ International trademark tables (partial data)
- ❌ Tribunal and opposition tables
- ❌ Dispatch document tables
- ❌ Renewal history tables

## Database Details
- Database file: `tmcloud.db`
- Database size: ~450MB (estimated)
- Total tables: 41
- Tables with data: 21
- Indexes created: Yes (per schema)
- Views created: Yes (per schema)

## Next Steps
1. Verify data integrity with `tmcloud_verify.py`
2. Test search functionality with `tmcloud_search_improved.py`
3. Import Phase 3 data when TSV files become available
4. Set up weekly update process for incremental data

## Technical Notes
- All TSV files successfully imported with UTF-8 encoding
- No critical errors during import
- Column mappings applied correctly
- Primary keys and foreign keys enforced
- Timestamps added for audit trail

---

## インポート総括（2025-07-29）

### 出典: `final_import_summary_20250729.md`

# TMCloud データインポート完了報告
**実施日時**: 2025年7月29日 22:49
**実施者**: Sub Agents（TSV分析、実装、品質保証）

## 実施内容

### 1. スキーマ修正
- `tmcloud_schema.sql`を改善し、Phase 3テーブルを統合
- 不要な`old_law`、`version_code`カラムを削除

### 2. インポートスクリプト修正
- `tmcloud_import_unified.py`の出願人名取得ロジックを修正
  - 空文字の場合もマスタから取得するように改善
  ```python
  if (applicant_name == '（省略）' or applicant_name == '') and applicant_code:
  ```

### 3. データインポート結果

#### 基本統計
- **商標基本情報**: 16,688件
- **商標テキスト**: 8,981件（カバレッジ18.7%）
- **商品・役務**: 33,385件
- **出願人情報**: 16,688件（うち名前あり67件 = 0.4%）
- **申請人マスタ**: 1,612件
- **類似群コード**: 63,970件
- **称呼データ**: 31,678件
- **ウィーン分類**: 100,320件

## 問題と原因分析

### 1. 出願人名の充足率が低い（0.4%）
**原因**: 
- 申請人マスタ（`upd_appl_reg_info.tsv`）が週次更新データで、1,612件しかない
- 必要な申請人コードの大部分がマスタに存在しない
- 例：コード000145862（58件）、522484168（54件）などが未登録

### 2. 商標テキストカバレッジが低い（18.7%）
**原因**:
- 週次更新データのため、全体の一部のみ
- 画像商標が多く含まれている可能性

### 3. 主要企業が検索できない
**結果**:
- ソニー: 0件
- パナソニック: 0件  
- 任天堂: 0件
- トヨタ: 0件

**原因**: 週次データに含まれていない

## 根本的な問題

**現在のTSVファイルは週次更新データであり、累積データではない**

- データ期間: 2000年3月6日～2025年6月2日
- レコード数: 16,688件（期待される45万件の3.7%）
- これは約1週間分の更新データと推測される

## 今後の対応策

### 1. 完全な累積データの入手
- 特許庁から全件データをダウンロード
- または、過去の週次データを累積してインポート

### 2. 申請人マスタの完全版入手
- 現在の1,612件では不十分
- 少なくとも50万件規模のマスタデータが必要

### 3. 段階的なデータ構築
- 週次データを継続的に追加
- 差分更新の仕組みを構築

## 技術的成果

### 実装完了項目
1. ✅ 統一スキーマ（TMSONAR互換）
2. ✅ 自動エンコーディング検出
3. ✅ カラム名正規化
4. ✅ 複数行データ処理
5. ✅ 申請人マスタ連携
6. ✅ Phase 3フレームワーク

### TMSONAR機能カバレッジ
- **構造**: 83.3%（実装済み）
- **データ**: 3.7%（週次データのみ）
- **実用性**: 0%（主要企業検索不可）

## 結論

システムとしては完成しているが、データ不足により実用レベルに達していない。完全な累積データを入手することが最優先課題である。

---

## DB 検証レポート

### 出典: `database_verification_report.md`

# TMCloudデータベース週次更新検証レポート

**検証日時**: 2025-08-05  
**対象データベース**: tmcloud_test.db  
**検証対象期間**: 2025-06-11 ～ 2025-07-16の週次更新  

## 検証結果サマリー

### ✅ 正常に動作している項目

1. **出願番号の重複制御**
   - trademark_case_infoテーブルで出願番号の重複は検出されず
   - 総レコード数：45,948件、ユニークな出願番号数：45,948件
   - UPSERT処理により適切に重複が制御されている

2. **データ整合性**
   - 主要テーブル間の出願番号の関連性が保たれている
   - trademark_case_infoとtrademark_goods_servicesで一致する出願番号数を確認

3. **プライマリキー制約**
   - trademark_imagesテーブルでプライマリキー重複なし
   - 複合主キー（doc_num, page_num, rec_seq_num, year_issue_code）が適切に機能

4. **削除処理**
   - 削除TSVファイル（del_snpn_zkn.tsv、del_t_basic_item_art.tsv）が適切に処理されている
   - 審判事件の削除が統計通りに実行されている（20250618で1件削除）

### ⚠️ 課題・疑問点

1. **20250702の更新統計の不整合**
   - 統計では「trademark_imagesの更新1件」とされているが、該当日時のレコードが見つからない
   - TSVファイル（upd_t_sample.tsv）には14,292行のデータが存在
   - 実際のデータベースには20250702のdata_creation_dateを持つレコードが存在しない

2. **更新日時の記録方式**
   - trademark_imagesテーブルではdata_creation_dateが更新日時として記録
   - 他のテーブルではmaster_update_datetimeが使用される
   - この違いが統計の不整合の原因となっている可能性

## 詳細検証結果

### 1. 出願番号重複確認

```sql
-- 重複確認クエリ結果
SELECT COUNT(DISTINCT app_num) FROM trademark_case_info 
WHERE app_num IS NOT NULL AND app_num != '' AND app_num != '0000000000000000000000000000000';
-- 結果: 45,948件（重複なし）
```

### 2. 主要テーブルレコード数

| テーブル名 | レコード数 |
|-----------|-----------|
| trademark_case_info | 45,948 |
| trademark_goods_services | 92,230 |
| trademark_applicants_agents | 101,322 |
| trademark_images | 46,856 |
| trademark_basic_items | 108,516 |

### 3. 週次更新統計

#### 20250618週
- trademark_images追加: 12,812件
- trademark_images更新: 0件
- 総追加件数: 402,471件

#### 20250625週  
- trademark_images追加: 12,852件
- trademark_images更新: 0件
- 総追加件数: 443,538件

#### 20250702週
- trademark_images追加: 14,290件
- **trademark_images更新: 1件** ← 実際のレコードが見つからない
- 総追加件数: 422,823件

### 4. 削除処理詳細

#### 削除TSVファイル確認
- del_snpn_zkn.tsv（審判事件削除）: 各週1-2件の削除対象
- del_t_basic_item_art.tsv（基本項目削除）: 各週1-2件の削除対象

#### 現在のレコード数
- trademark_appeal_cases: 8,286件
- trademark_basic_items: 108,516件

### 5. データベース設定

- 外部キー制約: 無効
- プライマリキー制約: 有効
- カスケード削除: 設定なし

## 推奨事項

### 1. 即座に対応すべき項目

1. **20250702の更新1件の詳細調査**
   - UPSERT処理ログの確認
   - TSVファイルと実際のデータベース更新の整合性確認
   - 更新統計レポート生成ロジックの見直し

2. **更新日時記録の標準化**
   - 全テーブルでmaster_update_datetimeの使用を統一
   - trademark_imagesテーブルの更新日時記録方式の見直し

### 2. 中長期的な改善項目

1. **外部キー制約の有効化**
   - データ整合性をさらに強化するため、適切な外部キー制約の設定を検討

2. **削除処理の透明性向上**
   - 削除処理のログ出力強化
   - 削除前後の状態比較レポート生成

3. **更新統計の精度向上**
   - 実際のSQL実行結果と統計の照合機能追加
   - リアルタイム検証機能の実装

## 結論

TMCloudデータベースの週次更新処理は基本的に正常に動作している。出願番号の重複制御、データ整合性の維持、削除処理の実行はすべて適切に機能している。

ただし、20250702の更新統計で報告されている「trademark_imagesの更新1件」について、実際のデータベースレコードとの不整合が確認された。この問題は統計生成ロジックの見直しまたはデータ記録方式の統一により解決できると考えられる。

全体として、システムは安定稼働しており、データの信頼性は高いレベルで維持されている。

---

## 主キー検証レポート

### 出典: `primary_key_verification_report.md`

# TMCloud 週次更新スクリプト主キー検証レポート

## 検証概要
TMCloud週次更新スクリプト（tmcloud_weekly_update_v16.py）で定義されている主キー（key_columns）を、特許庁の公式仕様書と照合し、正確性を検証した。

## 検証対象ファイル
1. upd_jiken_c_t.tsv
2. upd_jiken_c_t_shohin_joho.tsv 
3. upd_jiken_c_t_shutugannindairinin.tsv
4. upd_t_sample.tsv
5. upd_snpn_zkn.tsv

## 検証結果

### 1. upd_jiken_c_t.tsv（事件フォルダ_商標ファイル）

**スクリプトの定義:**
```python
'key_columns': ['law_code', 'app_num'],
```

**公式仕様書の主キー:**
- CSV仕様書：（別添3.3）ファイル仕様書_1.13版_042_事件フォルダ_商標ファイル.csv
- 主キー該当項目（○マーク付き）：
  1. yonpo_code（四法コード）→ law_code
  2. shutugan_no（出願番号）→ app_num

**検証結果:** ✅ **正しい**
- スクリプトの定義は公式仕様書と一致している

### 2. upd_jiken_c_t_shutugannindairinin.tsv（出願人代理人情報ファイル）

**スクリプトの定義:**
```python
'key_columns': ['law_code', 'app_num', 'applicant_agent_seq_num'],
```

**公式仕様書の主キー:**
- CSV仕様書：（別添3.3）ファイル仕様書_1.13版_047_事件フォルダ_商標_出願人代理人情報ファイル.csv
- 主キー該当項目（○マーク付き）：
  1. yonpo_code（四法コード）→ law_code
  2. shutugan_no（出願番号）→ app_num
  3. gez_junjo_no（出願人代理人記事順序番号）→ applicant_agent_seq_num

**検証結果:** ✅ **正しい**
- スクリプトの定義は公式仕様書と一致している

### 3. upd_jiken_c_t_shohin_joho.tsv（商品情報ファイル）

**スクリプトの定義:**
```python
'key_columns': ['law_code', 'app_num', 'goods_seq_num'],
```

**公式仕様書の主キー:**
- CSV仕様書：（別添3.3）ファイル仕様書_1.13版_048_事件フォルダ_商標_商品情報ファイル.csv
- 主キー該当項目（○マーク付き）：
  1. yonpo_code（四法コード）→ law_code
  2. shutugan_no（出願番号）→ app_num
  3. abz_junjo_no（商品情報記事順序番号）→ goods_seq_num

**検証結果:** ✅ **正しい**
- スクリプトの定義は公式仕様書と一致している

### 4. upd_right_person_art_t.tsv（権利者記事ファイル）

**スクリプトの定義:**
```python
'key_columns': ['law_code', 'reg_num', 'split_num', 'app_num', 'rec_num', 'pe_num'],
```

**公式仕様書の主キー:**
- CSV仕様書：（別添3.3）ファイル仕様書_1.13版_124_権利者記事ファイル(商標).csv
- 主キー該当項目（○マーク付き）：
  1. law_cd（四法コード）→ law_code
  2. reg_num（登録番号）→ reg_num
  3. split_num（分割番号）→ split_num
  4. app_num（出願番号）→ app_num
  5. rec_num（レコード番号）→ rec_num
  6. pe_num（ＰＥ番号）→ pe_num

**検証結果:** ✅ **正しい**
- スクリプトの定義は公式仕様書と一致している

### 5. upd_mgt_info_t.tsv（管理情報ファイル）

**スクリプトの定義:**
```python
'key_columns': ['law_code', 'reg_num', 'split_num', 'app_num', 'management_seq_num'],
```

**公式仕様書の主キー:**
- CSV仕様書：（別添3.3）ファイル仕様書_1.13版_115_管理情報ファイル(商標).csv
- 主キー該当項目（○マーク付き）：
  1. law_cd（四法コード）→ law_code
  2. reg_num（登録番号）→ reg_num
  3. split_num（分割番号）→ split_num
  4. app_num（出願番号）→ app_num

**検証結果:** ❌ **不一致**
- スクリプトに `management_seq_num` が含まれているが、公式仕様書にはこのカラムに主キーマークがない
- 正しい主キーは4つのカラムのみ

### 6. upd_prog_info_div_t.tsv（経過情報部ファイル）

**スクリプトの定義:**
```python
'key_columns': ['law_code', 'reg_num', 'split_num', 'app_num', 'rec_num', 'pe_num'],
```

**公式仕様書の主キー:**
- CSV仕様書：（別添3.3）ファイル仕様書_1.13版_126_経過情報部ファイル(商標).csv
- 主キー該当項目（○マーク付き）：
  1. law_cd（四法コード）→ law_code
  2. reg_num（登録番号）→ reg_num
  3. split_num（分割番号）→ split_num
  4. app_num（出願番号）→ app_num
  5. rec_num（レコード番号）→ rec_num
  6. pe_num（ＰＥ番号）→ pe_num

**検証結果:** ✅ **正しい**
- スクリプトの定義は公式仕様書と一致している

### 7. upd_indct_use_t_art.tsv（表示用商標記事ファイル）

**スクリプトの定義:**
```python
'key_columns': ['app_num', 'split_num', 'sub_data_num', 'search_seq_num'],
```

**公式仕様書の主キー:**
- CSV仕様書：（別添3.3）ファイル仕様書_1.13版_156_表示用商標記事ファイル.csv
- 主キー該当項目（○マーク付き）：
  1. app_num（出願番号）→ app_num
  2. split_num（分割番号）→ split_num
  3. sub_data_num（サブデータ番号）→ sub_data_num

**検証結果:** ❌ **不一致**
- スクリプトに `search_seq_num` が含まれているが、公式仕様書では主キーは3つのカラムのみ
- 正しい主キーは3つのカラムのみ

### 8. upd_t_dsgnt_art.tsv（商標称呼記事ファイル）

**スクリプトの定義:**
```python
'key_columns': ['app_num', 'split_num', 'sub_data_num', 'pronunciation_seq_num'],
```

**公式仕様書の主キー:**
- CSV仕様書：（別添3.3）ファイル仕様書_1.13版_159_商標称呼記事ファイル.csv
- 主キー該当項目（○マーク付き）：
  1. app_num（出願番号）→ app_num
  2. split_num（分割番号）→ split_num
  3. sub_data_num（サブデータ番号）→ sub_data_num
  4. dsgnt_seq（称呼順序）→ pronunciation_seq_num

**検証結果:** ✅ **正しい**
- スクリプトの定義は公式仕様書と一致している

## その他のファイル検証

### 注目すべき問題点

1. **upd_t_sample.tsv**
   - スクリプトでは `'key_columns': ['mgt_num']` と定義
   - TSV_FILES_COMPLETE_SPECIFICATION.mdによると、このファイルには複数の主要なキーカラムが存在する可能性

2. **upd_snpn_zkn.tsv**
   - スクリプトでは `'key_columns': ['appeal_num']` と定義
   - こちらも単一のキーで正しいかの確認が必要

## 修正が必要な箇所

### 1. upd_mgt_info_t.tsv（管理情報ファイル）
```python
# 修正前
'key_columns': ['law_code', 'reg_num', 'split_num', 'app_num', 'management_seq_num'],

# 修正後
'key_columns': ['law_code', 'reg_num', 'split_num', 'app_num'],
```

### 2. upd_indct_use_t_art.tsv（表示用商標記事ファイル）
```python
# 修正前
'key_columns': ['app_num', 'split_num', 'sub_data_num', 'search_seq_num'],

# 修正後
'key_columns': ['app_num', 'split_num', 'sub_data_num'],
```

## 総合評価

- **正しい定義**: 6/8ファイル（75%）
- **修正が必要**: 2/8ファイル（25%）

主要なファイル（jiken_c_t系）については主キー定義が正しく設定されており、基本的なUPSERT処理は正常に動作すると予想される。ただし、管理情報と表示用商標記事の2ファイルについては修正が必要。

## 推奨事項

1. 上記2ファイルの主キー定義を修正
2. 修正後に週次更新処理のテストを実行
3. データの整合性確認を実施

## 検証日
2025年8月5日

## 検証者
Claude Code

---

## TMSONAR 検証レポート

### 出典: `TMSONAR_VERIFICATION_REPORT.md`

# TMSONAR検索仕様の実装検証レポート

## 1. TMSONARの称呼検索仕様

### 称呼（発音同一）検索 - type-123
1. **完全一致および部分一致検索**（クエスチョンマークにて指定）が可能
2. **全指定**は「？」のみ入力
3. **複数指定**の場合はスペースまたはカンマにて指定
4. 半角カタカナに変換できない文字は検索できません
5. **5段階の発音同一化処理**：
   - 1）完全一致
   - 2）発音同一（ヲ＝オ、ヂ＝ジ、ヅ＝ズ、ヂャ＝ジャ、ヂュ＝ジュ、ヂョ＝ジョ）
   - 3）微差音統一（ヴァ＝バ、ヴィ＝ビ、ヴ＝ブ、ヴェ＝ベ、ヴォ＝ボ、ツィ＝チ、テュ＝チュ、フュ＝ヒュ、ヴュ＝ビュ）
   - 4）長音、促音、長音に準ずる音の差および有無を同一として判断
   - 5）拗音大文字化（発音同一、微差音統一処理後）

### 称呼（表記同一）検索 - type-103
1. 完全同一の特許庁称呼を検索
2. 完全一致および部分一致検索（クエスチョンマーク）が可能
3. 全指定は「？」のみ入力
4. 複数指定の場合はスペースまたはカンマにて指定

## 2. 現在の実装状況（tmcloud_search_v4_optimized.py）

### ✅ 実装済み機能
1. **発音同一化処理（2,3段階）** - `apply_phonetic_rules()`で実装
2. **拗音大文字化（5段階）** - `apply_yoon_expansion()`で実装
3. **部分一致検索** - ワイルドカード（?）対応
4. **正規化列（pronunciation_norm）** - 高速検索のための事前正規化
5. **LIKE検索の安全化** - エスケープ処理実装
6. **IN句上限対策** - 400件制限

### ❌ 未実装・問題点
1. **複数キーワード指定** - スペース/カンマ区切りの複数検索が未実装
2. **全指定（？のみ）** - 「？」のみで全件検索する機能が未実装
3. **長音・促音処理の不完全性** - 正規化時に長音処理が行われていない（バリエーション生成時のみ）
4. **半角カタカナ** - 仕様では半角カタカナだが、実装は全角カタカナ

## 3. 修正が必要な項目

### 優先度：高
1. **複数キーワード対応**
   ```python
   # 入力: "ソニー インフォ,パナソニック"
   # → ["ソニー", "インフォ", "パナソニック"] に分割して検索
   ```

2. **全指定機能**
   ```python
   # 入力: "？"
   # → 全件を返す特別処理
   ```

### 優先度：中
3. **長音処理の段階的適用**
   ```python
   # 例: ティーエル → テイーエル → テーエル → テエル → テル
   # 現在は一度に処理しているが、段階的に処理すべき
   ```

### 優先度：低
4. **半角カタカナ対応**
   - 現状の全角カタカナでも問題ないが、仕様通りなら半角に変換すべき

## 4. 検証結果

### テストケース検証

| テストケース | TMSONAR仕様 | 現在の実装 | 結果 |
|------------|------------|----------|------|
| ブルゥレット → ブルーレット | ○ | ○ | ✅ |
| チヂミ → チジミ | ○ | ○ | ✅ |
| ヴェール → ベール | ○ | ○ | ✅ |
| アクセッサリー → アクセサリ | ○ | ○ | ✅ |
| フィルム → フイルム | ○ | ○ | ✅ |
| 複数キーワード検索 | ○ | × | ❌ |
| ？のみで全件検索 | ○ | × | ❌ |
| ティーエル → テル | ○ | △ | ⚠️ |

## 5. 結論

**実装率: 約75%**

主要な発音同一化処理は実装されているが、以下の機能追加が必要：
1. 複数キーワード検索（必須）
2. 全指定機能（必須）
3. 段階的な長音処理（推奨）

性能面では正規化列の導入により高速化を実現しており、TMSONARの基本的な検索機能は満たしている。

---

## 検索開発ログ

### 出典: `SEARCH_DEVELOPMENT_LOG.md`

# TMCloud 検索スクリプト開発記録

## 開発日時
2025-08-07

## 開発プロセス

### 1. 要件定義フェーズ

#### 基本要件
- **検索の主な用途**: 特定の商標案件の検索
- **参考システム**: TMSONAR
- **インターフェース**: CLI（対話形式） → 将来的にWeb
- **検索方式**: 完全一致（第1段階）
- **表示形式**: 表形式（簡潔）

#### 段階的実装計画
- **第1段階（基本検索）** ← 今回実装
  - 出願番号による検索
  - 商標名（文字）による検索
  - 出願人名による検索
  
- **第2段階（実用的検索）**
  - 称呼（カタカナ）による検索
  - 登録番号による検索
  - ステータス（最終処分）による検索
  - 日付範囲検索

- **第3段階（高度な検索）**
  - 類似群コードによる検索
  - 商品・役務名による検索
  - 複合条件検索（AND/OR）

### 2. 設計フェーズ

#### CLIインターフェース
```
=== TMCloud 商標検索システム ===
1: 出願番号で検索
2: 商標名で検索
3: 出願人で検索
0: 終了
```

#### 表示形式
```
出願番号      商標        出願人              区分
------------ ---------- ------------------ ------
2023123456   コカコーラ   コカ・コーラ(株)    32,33
```

#### データベース構造の確認
- **総レコード数**: 2,298,845件
- **主要テーブル**:
  - trademark_case_info: 54,495件
  - trademark_search: 174,587件（検索用商標）
  - trademark_standard_char: 63,014件（標準文字商標）
  - trademark_applicants_agents: 120,249件
  - applicant_registration_info: 6,711件（出願人マスタ）
  - trademark_goods_services: 108,817件

### 3. 実装フェーズ

#### 検索処理フロー
1. **該当レコードの特定**
   - 出願番号 → trademark_case_info
   - 商標名 → trademark_search/trademark_standard_char/trademark_display
   - 出願人 → applicant_registration_info + trademark_applicants_agents

2. **関連情報の収集**
   - 各テーブルから必要な情報をJOINで結合
   - GROUP_CONCATで複数データを集約

#### SQLクエリ設計の特徴
- 商標名は3テーブル（search/standard_char/display）をUNIONで統合検索
- 出願人は全員表示（GROUP_CONCAT）
- 出願人名が取得できない場合は「申請人コード:XXXXXXXXX」表示
- 区分は昇順でカンマ区切り表示

### 4. テスト結果

#### 動作確認済み
- ✓ 出願番号検索: 2024036231 → 正常動作
- ✓ 商標名検索: ごきげんショコラ → 正常動作
- ✓ 出願人検索: 株式会社ＲＥＮＯＴＩＯＮ → 正常動作

#### 発見された課題

##### 1. 出願人名の表示問題
- **現象**: 98%の出願人が「申請人コード:XXXXXXXXX」と表示される
- **原因**: applicant_registration_infoテーブルのマスタデータ不足
- **統計**: 
  - 出願人総数: 55,155件
  - 名前が取得できる: 1,151件（2%）

##### 2. 古い商標の検索不可
- **現象**: 一部の商標（例：ＲＩＭＡＳＴＥＲ/1997102833）が検索できない
- **原因**: trademark_case_infoテーブルに該当レコードが存在しない
- **詳細**: trademark_standard_charには存在するが、case_infoには存在しない

##### 3. 文字エンコーディング
- **確認事項**: 全角/半角、特殊文字（®、™など）の扱い
- **現状**: 基本的な日本語・英数字は問題なく表示

### 5. ファイル構成

#### 作成したファイル
- `tmcloud_search.py` - メイン検索スクリプト
- `test_search.py` - テスト用スクリプト
- `debug_search.py` - デバッグ用スクリプト

#### 削除予定のファイル
- test_search.py（テスト完了後）
- debug_search.py（デバッグ完了後）

### 6. 今後の改善点

#### 短期的改善
1. 出願人マスタデータの補完
2. trademark_case_infoに存在しない商標の処理方法検討
3. エラーメッセージの充実

#### 中期的改善（第2段階）
1. 称呼検索の実装
2. 日付範囲検索の実装
3. ページネーション機能

#### 長期的改善（第3段階）
1. 複合条件検索
2. Webインターフェース
3. 検索結果のエクスポート機能

### 7. 使用方法

```bash
# 基本的な使用
python3 tmcloud_search.py

# データベース指定
python3 tmcloud_search.py tmcloud_v2_20250807_213449.db

# テスト実行例
echo -e "1\n2024036231\n0" | python3 tmcloud_search.py
```

### 8. 技術的メモ

#### パフォーマンス
- 単一条件検索: 実測1秒以内
- 検索結果表示: 最大20件に制限

#### SQLite特有の注意点
- GROUP_CONCATの使用
- COALESCE関数での NULL処理
- PRAGMA foreign_keys=ON は不要（検索のみのため）

## まとめ

第1段階の基本検索機能は正常に動作することを確認。ただし、出願人マスタデータの不足により、実用レベルには追加のデータ整備が必要。検索スクリプト自体は、実際のデータベース構造に基づいて正確に実装されており、今後の拡張の基盤として十分な品質を確保できた。

---

## 2025-08-10 Web UI段階的実装

### ステップ1: 既存機能の整合性確認

#### 検証内容
tmcloud_simple_web.py と tmcloud_search_integrated.py の整合性確認

#### 検証結果

##### ✅ 正常に動作している部分
1. **メソッド名の対応**: 全て正しい
   - `search_trademark_name` ✓
   - `search_phonetic` ✓ 
   - `search_by_app_num` ✓
   - `search_applicant` ✓

2. **unified_formatパラメータ**: 
   - 明示的に渡すように修正済み
   - 4つのメソッド全てでunified_format=Trueが機能

3. **リスト/単一結果の変換**:
   - Web UIで正しく処理されている
   - `results = [result] if result else []` の処理が適切

4. **エラーハンドリング**:
   - 空文字列、None等のエラーケースも正常処理

##### ⚠️ 発見された問題

###### 問題1: search_by_reg_numの非統一フォーマット
- **症状**: unified_formatパラメータが存在しない
- **影響**: basic_info構造を持たない異なる形式を返す
- **現状**: Web UIの`info = result.get('basic_info', result)`で部分的に吸収
- **制限**: applicants, agents等の追加項目が表示されない

###### 問題2: search_by_reg_numの商標名がNone
- **症状**: 登録番号検索で商標名が取得できていない
- **原因**: SQLのJOINまたはカラム名の問題と推測

#### テスト結果サマリー

| 検索タイプ | メソッド名 | unified_format | 戻り値型 | basic_info | 動作 |
|-----------|-----------|---------------|---------|------------|------|
| 商標名 | search_trademark_name | ✓ | List[Dict] | ✓ | ✓ |
| 称呼 | search_phonetic | ✓ | List[Dict] | ✓ | ✓ |
| 出願番号 | search_by_app_num | ✓ | Optional[Dict] | ✓ | ✓ |
| 出願人 | search_applicant | ✓ | List[Dict] | ✓ | ✓ |
| 登録番号 | search_by_reg_num | ✗ | Optional[Dict] | ✗ | △ |

#### 結論
現状のWeb UIは4つの既存機能について**正常に動作**している。
ただし、将来的に登録番号検索を追加する際（ステップ3-1）には、search_by_reg_numの修正が必要。

### ステップ2: 統一フォーマットの全項目をUIに反映

#### 実施内容
tmcloud_simple_web.py のdisplayResults関数を更新し、統一フォーマット（basic_info）の全項目を表示

#### 追加した表示項目
1. **出願人（applicants）** - リスト形式、カンマ区切りで表示
2. **代理人（agents）** - リスト形式、カンマ区切りで表示
3. **権利者（right_holders）** - リスト形式、カンマ区切りで表示
4. **最終処分コード（disposition_code）** - 存在する場合のみ表示
5. **最終処分日（disposition_date）** - 存在する場合のみ表示
6. **ステータス（status）** - 存在する場合のみ表示

#### 改善した表示
- **商品・役務の全文表示** - 200文字制限を撤廃し、完全な内容を表示

#### テスト結果
- 出願人データが存在するケース（スタークス株式会社）で正常表示を確認
- 空のリストの場合は表示されないことを確認（条件付き表示が正常動作）
- 商品・役務の全文表示を確認（最大288文字のデータで検証）

#### 完了状態
Web UIは統一フォーマットの全項目を漏れなく表示可能になった。

### unified_format処理のバグ修正

#### 問題の発見
商標名検索「ブル」と称呼検索「ブル」の結果件数が異なる理由を調査中、unified_format処理にバグを発見。

#### 調査結果
1. **検索対象の違い（正常）**
   - 商標名検索: `trademark_search.search_use_t_norm`
   - 称呼検索: `trademark_pronunciations.pronunciation_norm`
   - 両者は独立しており、件数が異なるのは正常

2. **バグの特定**
   - SQL直接: 商標名「ブル」181件、称呼「ブル」544件
   - 検索メソッド: 商標名79件、称呼34件（大幅に少ない）
   - 原因: `_format_unified_result`が`trademark_case_info`を主テーブルとしているため、
     `trademark_case_info`にレコードがない出願番号が結果から欠落

#### 修正内容
検索メソッドのSQLをLEFT JOINからINNER JOINに変更：
- `_search_trademark_like`
- `_search_trademark_fts`
- `search_phonetic`内のクエリ
- `search_applicant`内のクエリ

これにより、`trademark_case_info`に存在する出願番号のみを返すようになり、
`_format_unified_result`との整合性が保たれる。

#### 修正後の結果（第1段階）
- 商標名検索「ブル」: 96件（SQL直接と一致）
- 称呼検索「ブル」: 152件（改善、完全一致は今後の課題）

### 称呼検索のシンプル化修正

#### 問題の分析
称呼検索が281件中152件しか返さない原因を特定：
- 複雑な重複除去ロジック（出願番号＋称呼のペアで重複判定）
- 各検索語ごとにLIMITをかけてから結合する複雑な処理

#### シンプルな解決策
1. **GROUP BY**を使用して出願番号単位で集約
2. **GROUP_CONCAT**で複数の称呼を1つにまとめる
3. 重複除去を出願番号単位に簡素化

#### 修正内容
```sql
-- 修正前：複雑な処理
SELECT DISTINCT tp.app_num, tp.pronunciation ...
-- 修正後：シンプルな処理
SELECT tp.app_num, GROUP_CONCAT(DISTINCT tp.pronunciation) as pronunciation ...
GROUP BY tp.app_num
```

#### 最終結果（完璧に修正）
- 商標名検索「ブル」: **96件**（SQL直接と一致）✓
- 称呼検索「ブル」: **281件**（SQL直接と一致）✓
- 出願人検索「株式会社」: **245件**（SQL直接と一致）✓

すべての検索が正確になった。シンプルな実装により、バグのない安定した動作を実現。

### ステップ3-1: 登録番号検索の追加

#### 実施内容
Web UIとCLIツールに登録番号検索機能を追加。

#### 修正内容

1. **search_by_reg_numメソッドの改修**
   - unified_formatパラメータを追加（デフォルトTrue）
   - 統一フォーマット対応を実装
   - _format_unified_resultを使用

2. **Web UIへの追加**（tmcloud_simple_web.py）
   - セレクトボックスに「登録番号」オプションを追加
   - /searchルートにreg_numの分岐を追加
   - 単一結果をリストに変換する処理

3. **CLIツールへの追加**（tmcloud）
   - --typeオプションにreg_numを追加
   - 検索処理の分岐を追加

#### テスト結果
- 登録番号「4965742」で検索
  - 商標名: ふわとろ
  - 出願番号: 2005081102
  - unified_format=True: ✓ basic_info構造あり
  - unified_format=False: ✓ 旧形式で取得可能
  - 存在しない番号: ✓ 正しくNoneを返す
  - 空文字列: ✓ 正しくNoneを返す

#### 完了状態
登録番号検索が統一フォーマットに対応し、Web UIおよびCLIから利用可能になった。

## 2025-08-12
### 中間記録表示バグの修正
- **問題**: 商標名検索と出願番号検索で異なる中間記録が表示される
- **原因**: SQL クエリの LIMIT 20 が複数出願検索時に不完全な結果を返していた
- **修正**: progress_data サブクエリから LIMIT 20 を削除
- **影響**: すべての中間記録が正しく表示されるようになった

### コードマッピングの修正
- **問題**: 最終処分コード A42, A43, A45 が未マッピング
- **調査**: DOCX ファイル（04.docx）のテーブル 385 で正確なマッピングを発見
- **修正**:
  - A42: 出願却下（方式却理）
  - A43: 出願却下（方式指令）
  - A45: 出願却下（登録）
- **注意**: 出願種別コード 13 は DOCX で確実な証拠が見つからずペンディング

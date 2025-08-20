# CLAUDE.md — 不変ルール & 行動規範（v2025-08-09)

## TMCloud開発の絶対ルール
- **検索機能は全て`tmcloud_search_integrated.py`に実装** - 別スクリプト作成禁止
- **作業完了時の「まとめ」禁止** - 無駄なトークン消費を避ける
- **簡潔に結果のみ報告** - 冗長な説明は不要
- **ウィーンコード表示は統一フォーマット(`unified_format=True`)で全検索に実装済み** - 検索結果にウィーンコードが自動的に含まれる

> この文書は **指示（ガードレール）だけ**を記載する。運用手順・履歴・統計・仕様の詳細は **HISTORY.md / SPEC.md** を参照。  
> ここに無いことは実装しない。迷ったら**質問**してから動く。

---

## 0. 目的と適用範囲
- TMCloud（日本商標DB）の **安全・一貫・再現性** を担保するための不変ルール集。  
- 対象：初期インポート、週次更新、検索用整形（正規化）を行う**コード・SQL・データ変換**すべて。  
- 本ファイルは **不変**。変更は必ず別PRでレビュー。

---

## 1. 用語
- **SSoT**: Single Source of Truth（一次情報の優先順位）。  
- **key_columns**: UPSERT の衝突判定に使う **完全主キー列**。  
- **mapped_data**: TSV→`column_mapping` で DB 列名に写像した直後の辞書。  
- **defaults**: 欠損補完値（後述の安全注入ルールに従う）。

---

## 2. 参照優先順位（SSoT）
1. **スキーマ** `tmcloud_schema_v2.sql`（真実の源泉）  
2. **実DBメタ** `PRAGMA table_info(<table>)`（実体確認）  
3. **マッピング実装** `tmcloud_import_v2.py` / `tmcloud_weekly_update.py`  
> 相互矛盾時は **スキーマを真**として、実装を修正する提案を出す。

---

## 3. 絶対禁止（MUST NOT）
- 列名/型/主キーの**推測**・仮置きのまま実装。  
- `ON CONFLICT` が **PK/UNIQUE** と一致しない UPSERT。  
- **存在しない列**や `column_mapping` 外の列に defaults を注入して INSERT/UPDATE。  
- 複数行結合で **主キーの一部を落とす**（例：`key_columns[:-1]`）。

---

## 4. 実装原則（MUST）
### 4.1 UPSERT
- `key_columns` はスキーマの **PK/UNIQUE と完全一致**させる。  
- `key_columns` は **必ず `column_mapping` に含める**（TSV欠損時は安全な既定値を用意、またはスキップ）。

### 4.2 defaults の**安全注入**
- 対象列は **(実在カラム) ∩ (column_mapping ∪ key_columns)** のみ。  
- **空/NULL のときだけ**補完する。  
- 直前に **テーブル実在カラム** を `PRAGMA table_info()` で取得してフィルタ。

**Canonical snippet**
```python
cols_in_db = {r[1] for r in conn.execute(f"PRAGMA table_info({{table_name}})")}
valid_cols = set(column_mapping.values()) | set(key_columns)
safe_defaults = {k:v for k,v in defaults.items() if k in cols_in_db and k in valid_cols}

for col, val in safe_defaults.items():
    if (col not in mapped_data) or (mapped_data[col] in (None, "")):
        mapped_data[col] = val

# 最後に mapped_data も実在カラムでフィルタ
mapped_data = {k:v for k,v in mapped_data.items() if k in cols_in_db}
```

### 4.3 正規化の**順序**
TSV → `column_mapping` → `mapped_data` → **正規化**（例：`app_num` のハイフン除去）。

### 4.4 複数行結合
- 結合単位は **完全主キー一式**。部分キーでグルーピングしない。  
- `lengthchoka_flag='1'` 等の仕様結合は **同一キー内だけ**で行う。

### 4.5 画像ページ
- `page_num` はゼロ埋め **4桁**（既定 `'0001'`）。

### 4.6 FTS（全文検索）
- external-content 前提（`content = <base>`）。  
- SQL は **エイリアスで** `WHERE fts MATCH ?` を使う（元名直書き禁止）。

---

## 5. データ正規化（MINIMUM仕様）
### 5.1 文字列（商標名・出願人名・代理人名 など）
- ひら→カタ、英小/カナ小→大。  
- 長音・横線・ハイフンを `-` に統一。  
- **指定の特殊記号**（▲▼§￠＼∞）と **句読点・中点・点・カンマ・クォート**を除去。  
- 旧字体→新字体（辞書で段階対応）。  
- スペース（全/半）除去。  
- 商標名のみ：**ローマ数字→算用数字**（Ⅰ→1, Ⅲ→3）。  
- ※DB保存仕様で保持すべき記号（例：読点「。」、《》【】『』等）は **SPEC** に従い例外扱い。

### 5.2 称呼（発音同一）
1) 完全一致  
2) ヲ/ヂ/ヅ/ヂャ/ヂュ/ヂョ → オ/ジ/ズ/ジャ/ジュ/ジョ  
3) 微差音：ヴァ/ヴィ/ヴ/ヴェ/ヴォ → バ/ビ/ブ/ベ/ボ、ツィ→チ、テュ→チュ、フュ→ヒュ、ヴュ→ビュ  
4) 長音・促音・長音準ずる音の差/有無を同一視（エイ/オウ 等）  
5) 拗音は大文字化して判定（フィ/フェ等の揺れ統一）

### 5.3 番号・日付
- 出願番号：**ハイフン除去**、ゼロ埋め規則は SPEC に従う。  
- 日付：`YYYYMMDD`、`00000000` は NULL。

### 5.4 住所（日本語）
- 上記の共通正規化＋ **丁目の漢数字→算用**（1〜44）。

---

## 6. 主キー・制約・インデックス
- 公式TSVの **「主要キーカラム」** を唯一の真実として採用。  
- 週次で安定させるため、必要に応じて **UNIQUE INDEX** を追加（例：`(law_code, app_num)`）。  
- 欠損で主キーを満たさない行は **スキップ**（要ログ）か、**既定値で補完**したうえで投入（SPEC に準拠）。

---

## 7. 変更管理
- 曖昧な仕様は **質問→確認** の後に実装。  
- 破壊的変更（列名/PK変更・削除）は **提案→承認→Migration→実装**。  
- 影響範囲（週次・検索・既存SQL）と **ロールバック手順** をPRに明記。

---

## 8. Claude のふるまい
- 出力は **要点→理由→差分/SQL** の順で簡潔に。  
- **根拠**（スキーマ該当テーブル/列、PRAGMA結果、TSVヘッダー）を引用。  
- 不確実なら **最大3点までの質問** を先に出す。  
- 変更は **最小差分** で提案（周辺仕様を壊さない）。
- 口調は **優しい同級生のようなタメ口** で対応する。

---

## 9. PR前チェックリスト（Definition of Done）
- [ ] 列名/型/PK を SSoT 順で照合した  
- [ ] `ON CONFLICT(<keys>)` が PK/UNIQUE と**完全一致**  
- [ ] defaults は **実在∩(mapping∪keys)** のみに、空/NULLのみ補完  
- [ ] 正規化は mapped_data **後** に適用  
- [ ] 複数行結合は **完全主キー** でグルーピング  
- [ ] 画像 `page_num` は `zfill(4)` 既定 `'0001'`  
- [ ] FTS は external-content 前提 & `WHERE fts MATCH ?`  
- [ ] `--dry-run`：同一キーで **1回目=INSERT / 2回目=UPDATE** を確認  
- [ ] エラー（`no such column`など） 0 件ログ

---

## 10. 名前統一（頻出）
| TSV/旧名 | DB名 |
|---|---|
| shutugan_no | app_num |
| rui | class_num |
| yonpo_code / law_cd | law_code |
| toroku_no / intl_reg_no | reg_num |
| dsgnt / yomi | pronunciation |
| dsgnt_norm | pronunciation_norm |
| shohin | goods_services_name |
| desig_goods_or_desig_wrk_class | class_num_registered |

> **新しい別名は増やさない**。既存統一へ寄せる。

---

## 11. 定型スニペット（Do / Don’t）
**Do: 正しい UPSERT**
```sql
INSERT INTO trademark_case_info (...) VALUES (...)
ON CONFLICT(law_code, app_num) DO UPDATE SET ... ;
```
**Don’t: 存在しない列を混入**
```sql
-- trademark_search に law_code は無い
INSERT ... (app_num, ..., law_code)  -- NG
```

**Do: FTS（エイリアス使用）**
```sql
FROM trademark_search_fts AS fts
WHERE fts MATCH ?
```

**Don’t: 主キーの一部だけで結合**
```python
# key_columns[:-1] でグルーピング  -- NG
```

---

## 12. 改訂ルール
- 本ファイルに **運用/履歴は書かない**。  
- 変更は **別PR**。レビュワーはチェックリストを満たすまで承認しない。

---

## 付記
- 実装・運用の詳細、テーブル別の仕様、TSVの完全定義は **SPEC.md**。  
- 週次/検証/インポート結果の経緯は **HISTORY.md**。

---
name: implementation-developer
description: 実際のコードを書いて問題を解決する実装専門家
tools: Read, Write, Edit, MultiEdit, Bash, Grep
---

# 実装エージェント

## 役割
TSV分析エージェントとTMSONAR専門家の分析結果を基に、実際に動作するコードを実装する。インポートスクリプトの修正、検索機能の実装、データ修復処理など、具体的な問題解決を行う。

## 必須参照ファイル
- `/home/ygenk/TMCloud/tmcloud_import_unified.py` - 統合インポートスクリプト
- `/home/ygenk/TMCloud/tmcloud_schema.sql` - データベーススキーマ
- `/home/ygenk/TMCloud/CLAUDE.md` - プロジェクト固有の指示事項

## 主要タスク

### 1. Phase 3インポート機能の実装
**対象**: tmcloud_import_unified.py内の29個のTODO関数

#### 最優先実装（データ品質改善）
```python
def import_applicant_registration(self, file_path: Path):
    """申請人マスタ（upd_appl_reg_info.tsv）のインポート
    - 出願人名のNULL問題を解決
    - applicant_codeとapplicant_nameのマッピング
    """
    
def import_trademark_updates(self, file_path: Path):
    """商標更新記事（upd_t_updt_art.tsv）のインポート
    - 19,818件の更新情報
    - 存続期間管理に必須
    """
```

#### 国際商標対応（7関数）
```python
# マドリッドプロトコル対応
import_intl_registration()      # 基本情報
import_intl_progress()          # 進捗情報
import_intl_holder()            # 権利者
import_intl_goods_services()    # 商品・役務
import_intl_first_indication()  # 最初の表示
import_intl_priority()          # 優先権
import_design_state()           # 指定国
```

### 2. データ修復処理の実装
```python
class TMCloudDataRepair:
    """データ品質問題の修復"""
    
    def repair_applicant_names(self):
        """出願人名の補完処理
        1. applicant_masterから名前を取得
        2. trademark_applicantsのNULL値を更新
        3. 更新結果をログ出力
        """
        
    def unify_date_ranges(self):
        """データ年代範囲の統一
        - 全テーブルで同じ期間のデータに統一
        - 不整合データの削除または補完
        """
        
    def create_comprehensive_mapping(self):
        """出願番号・登録番号の完全マッピング
        - app_reg_mappingテーブルの充実
        - 複数ソースからのマッピング統合
        """
```

### 3. 高度な検索機能の実装
```python
class TMSONARSearchEngine:
    """TMSONARレベルの検索エンジン"""
    
    def fuzzy_search(self, query: str) -> List[Dict]:
        """ファジー検索（表記揺れ対応）
        - カタカナ/ひらがな/英語の相互変換
        - 類似度スコア計算
        """
        
    def combined_search(self, conditions: Dict) -> List[Dict]:
        """複合条件検索
        - AND/OR/NOT条件の組み合わせ
        - 動的SQLクエリ生成
        """
        
    def phonetic_search(self, pronunciation: str) -> List[Dict]:
        """称呼検索の完全実装
        - 発音同一/表記同一の判定
        - 類似称呼の検出
        """
```

### 4. パフォーマンス最適化
```python
class PerformanceOptimizer:
    """パフォーマンス最適化処理"""
    
    def create_fulltext_indexes(self):
        """全文検索インデックスの作成
        CREATE VIRTUAL TABLE trademark_texts_fts USING fts5(
            app_num, text_content, tokenize='unicode61'
        );
        """
        
    def implement_batch_processing(self):
        """バッチ処理の実装
        - 10,000件単位でのコミット
        - メモリ使用量の制御
        - 進捗表示とログ出力
        """
        
    def optimize_queries(self):
        """SQLクエリの最適化
        - EXPLAIN QUERY PLANによる分析
        - インデックスヒントの追加
        - サブクエリの除去
        """
```

## 実装パターン

### エンコーディング処理パターン
```python
def detect_encoding(self, file_path: Path) -> str:
    """TSV_FILES_COMPLETE_SPECIFICATION.mdに基づくエンコーディング検出"""
    encodings = ['utf-8', 'cp932', 'shift_jis', 'euc-jp', 'iso-2022-jp']
    best_encoding = None
    min_errors = float('inf')
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
                error_count = content.count('?')
                if error_count < min_errors:
                    min_errors = error_count
                    best_encoding = encoding
        except:
            continue
    
    return best_encoding or 'cp932'  # デフォルトはCP932
```

### 複数行データ処理パターン
```python
def process_multiline_data(self, rows: List[Dict], key_columns: List[str]) -> List[Dict]:
    """複数行データの結合処理"""
    result = []
    current_data = {}
    
    for row in rows:
        if row.get('lengthchoka_flag') == '1':
            # 複数行データの結合
            key = tuple(row[col] for col in key_columns)
            if key in current_data:
                current_data[key]['text'] += row['text']
            else:
                current_data[key] = row
        else:
            # 単一行データ
            result.append(row)
    
    result.extend(current_data.values())
    return result
```

### エラーハンドリングパターン
```python
def safe_import(self, import_func: Callable, file_path: Path) -> Tuple[int, int]:
    """安全なインポート処理"""
    success_count = 0
    error_count = 0
    
    try:
        with self.conn:  # トランザクション開始
            success_count = import_func(file_path)
            logger.info(f"Imported {success_count} records from {file_path.name}")
    except Exception as e:
        logger.error(f"Error importing {file_path.name}: {e}")
        error_count = 1
        self.conn.rollback()
    
    return success_count, error_count
```

## デバッグ用コマンド

```bash
# インポート前のデータ件数確認
sqlite3 tmcloud.db "SELECT name, COUNT(*) FROM sqlite_master WHERE type='table' GROUP BY name;"

# インポート後の検証
python3 -c "
import sqlite3
conn = sqlite3.connect('tmcloud.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM trademark_applicants WHERE applicant_name IS NOT NULL')
print(f'出願人名の充填率: {cursor.fetchone()[0]}件')
"

# パフォーマンス測定
time python3 tmcloud_cli_search.py --mark-text "ソニー" --limit 1000
```

## 成果物
1. **Phase 3対応版tmcloud_import_unified.py**
   - 29個の関数実装完了
   - エラーハンドリング強化
   - ログ出力充実
   
2. **tmcloud_data_repair.py**
   - 出願人名補完機能
   - データ整合性チェック
   - 修復レポート生成
   
3. **tmcloud_advanced_search.py**
   - ファジー検索
   - 複合条件検索
   - 称呼検索完全版
   
4. **performance_report.md**
   - ベンチマーク結果
   - ボトルネック分析
   - 改善提案
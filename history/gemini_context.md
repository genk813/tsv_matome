## 2025/07/03 (続き)

### 称呼の重複表示問題の解消
- `t_dsgnt_art_decoded.txt`の内容を確認し、同じ出願番号に複数の称呼が存在することを確認。
- `build_enhanced_index.py`の`build_mark_index`関数内のSQLクエリにおいて、`GROUP_CONCAT(td.dsgnt)`に`DISTINCT`キーワードを追加し、重複する称呼が表示されないように修正。
- `GROUP BY`句から`td.normalized_app_num`を削除し、`j.normalized_app_num`のみでグループ化するように修正。
- データベースを再構築し、ウェブアプリケーションで称呼の重複表示が解消されたことを確認。

### 検索用商標の表示
- `upd_search_use_t_art_table.tsv`の仕様書を確認し、`search_use_t`が検索用商標であることを特定。
- `build_enhanced_index.py`の`build_mark_index`関数内のSQLクエリにおいて、`indct_use_t_art`テーブルの代わりに`search_use_t_art_table`をJOINし、`search_use_t`カラムを`trademark_kana`として取得するように修正。
- `templates/index_enhanced.html`のテーブルヘッダーを「表示用商標」から「検索用商標」に修正。
- データベースを再構築し、ウェブアプリケーションで検索用商標が正しく表示されたことを確認。
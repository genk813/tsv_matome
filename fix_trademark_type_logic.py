#!/usr/bin/env python3
"""
商標タイプ判定ロジックの修正パッチ
dimensional_trademark_flagも見るように改善
"""

# tmcloud_search_integrated.pyの_determine_trademark_typeメソッドを修正する内容
FIXED_LOGIC = '''
def _determine_trademark_type(self, row) -> str:
    """商標タイプを判定（改良版）
    
    Args:
        row: データベースの行データ
    
    Returns:
        商標タイプ名（標準文字/立体商標/音商標/etc）
    """
    # sqlite3.Rowオブジェクトを辞書に変換
    row_dict = dict(row) if not isinstance(row, dict) else row
    
    # 標準文字商標（最優先で表示）
    if row_dict.get('standard_char_exist') == '1':
        return '標準文字'
    
    # 特殊商標タイプ（C1390コードで判定）
    special_type = row_dict.get('special_mark_type') or row_dict.get('special_trademark_type')
    if special_type and special_type in self.SPECIAL_MARK_TYPE_MAP:
        return self.SPECIAL_MARK_TYPE_MAP[special_type]
    
    # dimensional_trademark_flagもチェック（追加）
    if row_dict.get('dimensional_trademark_flag') == '1':
        return '立体商標'
    
    # 通常商標
    return '通常'
'''

print("修正内容:")
print(FIXED_LOGIC)
print("\n上記のコードでtmcloud_search_integrated.pyの_determine_trademark_typeメソッドを置き換えてください")
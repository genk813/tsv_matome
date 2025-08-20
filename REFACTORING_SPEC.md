# TMCloud Web表示機能リファクタリング仕様書

## 1. 現状の問題点

### 1.1 コードの重複
- displayResults関数が320行以上と巨大
- 同じパターンの条件判定とHTML生成が50箇所以上繰り返されている
- 各フィールドごとに個別のif文とHTML生成コード

### 1.2 保守性の問題
- 新しいフィールドを追加する際、複数箇所の修正が必要
- マドプロ案件の表示ロジックが分散
- フィールドの表示/非表示条件がハードコード

### 1.3 可読性の問題
- 関数が長すぎて全体像が把握しづらい
- HTML文字列の結合が複雑
- インデントが深くなりすぎている

## 2. リファクタリング方針

### 2.1 設定の外部化
```javascript
// フィールド定義を設定オブジェクトとして管理
const FIELD_CONFIG = {
    basic_info: [
        { key: 'app_num', label: '出願番号', condition: '!isMadrid' },
        { key: 'intl_reg_num', label: '国際登録番号', condition: 'isMadrid' },
        { key: 'reg_num', label: '登録番号' },
        // ...
    ]
};
```

### 2.2 関数の分割
- `displayResults()` → メイン制御
- `renderHeader()` → ヘッダー部分
- `renderSearchConditions()` → 検索条件表示
- `renderSingleResult()` → 1件の結果表示
- `renderFieldGroup()` → フィールドグループ表示
- `renderField()` → 個別フィールド表示

### 2.3 ユーティリティ関数の抽出
- `isMadridCase(info)` → マドプロ判定
- `formatDate(dateStr)` → 日付フォーマット
- `formatArray(arr, separator)` → 配列の結合
- `shouldShowField(field, info)` → フィールド表示判定

## 3. 段階的実装計画

### Phase 1: 準備（現在のコードを壊さない）
1. 既存のdisplayResults関数の上にユーティリティ関数を追加
2. フィールド設定オブジェクトの定義
3. テスト用の小さな関数から実装

### Phase 2: 基本フィールドの移行
1. 出願番号・登録番号などの基本フィールドを新方式に移行
2. 旧コードはコメントアウトして残す
3. 動作確認

### Phase 3: 複雑なフィールドの移行
1. 中間記録、優先権情報などの複雑なフィールドを移行
2. 商品・役務、類似群コードの特別処理を移行
3. 動作確認

### Phase 4: クリーンアップ
1. 旧コードの削除
2. 関数の整理と最適化
3. コメントとドキュメントの追加

## 4. フィールド設定構造

```javascript
const FIELD_DEFINITIONS = {
    // 基本情報グループ
    basic: {
        title: '基本情報',
        fields: [
            {
                key: 'app_num',
                label: '出願番号',
                condition: (info) => !isMadridCase(info),
                format: (value) => esc(value || 'N/A')
            },
            {
                key: 'intl_reg_num',
                label: '国際登録番号',
                condition: (info) => isMadridCase(info),
                format: (value) => esc(value)
            },
            // ...
        ]
    },
    
    // 関係者情報グループ
    parties: {
        title: '関係者情報',
        fields: [
            {
                key: 'applicants',
                label: '出願人',
                condition: (info) => info.applicants && info.applicants.length > 0,
                format: (value) => value.map(a => esc(a)).join(', ')
            },
            // ...
        ]
    },
    
    // 特殊処理が必要なフィールド
    special: {
        title: '詳細情報',
        customRenderer: (info) => {
            // カスタム処理
        }
    }
};
```

## 5. リファクタリング後の構造

```javascript
// === ユーティリティ関数 ===
function isMadridCase(info) {
    return info.intl_reg_num && info.intl_reg_num !== '0000000';
}

function formatDate(dateStr) {
    if (!dateStr || dateStr === '00000000') return null;
    // YYYYMMDD → YYYY/MM/DD
    return `${dateStr.slice(0,4)}/${dateStr.slice(4,6)}/${dateStr.slice(6,8)}`;
}

// === フィールド表示関数 ===
function renderField(fieldDef, info) {
    // 表示条件チェック
    if (fieldDef.condition && !fieldDef.condition(info)) {
        return '';
    }
    
    const value = info[fieldDef.key];
    if (!value) return '';
    
    const formattedValue = fieldDef.format ? 
        fieldDef.format(value) : esc(value);
    
    return `<div class="field">
        <span class="field-label">${fieldDef.label}:</span> 
        ${formattedValue}
    </div>`;
}

// === メイン表示関数（簡潔版） ===
function displayResults(data) {
    if (data.error) return showError(data.error);
    if (!data.results?.length) return showNoResults();
    
    const html = [
        renderHeader(data),
        renderSearchConditions(data),
        ...data.results.map((result, index) => 
            renderSingleResult(result, index)
        )
    ].join('');
    
    document.getElementById('results').innerHTML = html;
}
```

## 6. 実装時の注意点

### 6.1 互換性の維持
- 既存の機能を壊さない
- 段階的に移行する
- 各段階で動作確認

### 6.2 テスト項目
- [ ] 通常の商標検索
- [ ] マドプロ案件の表示
- [ ] 複合検索
- [ ] 国際登録番号検索
- [ ] ソート機能
- [ ] 特殊文字のエスケープ

### 6.3 パフォーマンス考慮
- 大量データ（3000件）でも問題なく動作すること
- DOM操作を最小限に
- 不要な再レンダリングを避ける

## 7. 期待される効果

### 7.1 保守性の向上
- 新フィールド追加が設定追加のみで可能
- マドプロ案件の表示ロジックが一元化
- コードの見通しが良くなる

### 7.2 コード量の削減
- 約320行 → 約150行（50%削減見込み）
- 重複コードの排除
- 構造の簡潔化

### 7.3 拡張性の向上
- 新しい表示形式の追加が容易
- カスタムレンダラーの追加が可能
- 条件の複雑化にも対応可能

## 8. 実装スケジュール

1. **Phase 1（30分）**: ユーティリティ関数とフィールド設定の追加
2. **Phase 2（30分）**: 基本フィールドの移行とテスト
3. **Phase 3（30分）**: 複雑なフィールドの移行とテスト
4. **Phase 4（15分）**: クリーンアップと最終確認

合計所要時間: 約1時間45分

## 9. リスクと対策

### リスク
- 既存機能の破壊
- パフォーマンスの低下
- 予期しないエッジケース

### 対策
- 段階的な実装
- 各段階での動作確認
- 旧コードのバックアップ
- ロールバック手順の明確化

## 10. 成功基準

- [ ] すべての既存機能が正常動作
- [ ] コード行数が50%以上削減
- [ ] 新フィールド追加が設定のみで可能
- [ ] マドプロ案件が正しく表示される
- [ ] 検索速度が劣化していない
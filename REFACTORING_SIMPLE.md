# TMCloud Webリファクタリング - シンプル版

## 基本方針
**現在の構造を大きく変えずに、重複だけを削除する**

## 1. 追加する共通関数（たった2つ）

```javascript
// 1. フィールド表示の共通化（現在50箇所で重複）
function addField(label, value) {
    if (!value || value === '' || value === 'N/A' || value === '0000000') return '';
    return `<div class="field"><span class="field-label">${label}:</span> ${esc(value)}</div>`;
}

// 2. 配列データの表示（現在20箇所で重複）
function addArrayField(label, arr) {
    if (!arr || !Array.isArray(arr) || arr.length === 0) return '';
    return addField(label, arr.map(item => esc(item)).join(', '));
}
```

## 2. 置き換え例

### Before（現在のコード）
```javascript
// 単純なフィールド
if (info.final_disposition_type) {
    html += `<div class="field"><span class="field-label">最終処分コード:</span> ${esc(info.final_disposition_type)}</div>`;
}

// 配列フィールド
if (info.applicants && info.applicants.length > 0) {
    html += `<div class="field"><span class="field-label">出願人:</span> ${info.applicants.map(a => esc(a)).join(', ')}</div>`;
}
```

### After（リファクタリング後）
```javascript
// 単純なフィールド
html += addField('最終処分コード', info.final_disposition_type);

// 配列フィールド
html += addArrayField('出願人', info.applicants);
```

## 3. 特別な処理はそのまま残す

以下は複雑なので**触らない**：
- 商標画像の表示
- マドプロ案件の判定と表示切り替え
- 中間記録の分類表示
- 優先権情報の詳細表示
- 商品・役務の区分別表示
- 類似群コードの区分別表示

これらは現在のコードをそのまま使う。

## 4. 実装手順

### Step 1: 関数追加（2分）
```javascript
// displayResults関数の上に2つの関数を追加
function addField(label, value) { ... }
function addArrayField(label, arr) { ... }
```

### Step 2: 単純置き換え（10分）
以下のフィールドを置き換え：
- 登録番号、出願日、登録日
- 最終処分コード、最終処分記事、最終処分日
- 公報発行日、存続期間満了日
- 審査種別、査定種別
- など約30箇所

### Step 3: 配列置き換え（5分）
以下を置き換え：
- 出願人、代理人、権利者
- 審判番号、審判種別
- 称呼、区分
- など約10箇所

## 5. メリット

1. **構造がシンプル**
   - 元のコードとほぼ同じ流れ
   - 新しい概念を導入しない
   - すぐに理解できる

2. **情報の欠落なし**
   - 全ての表示項目を維持
   - 特殊な処理も変更なし

3. **段階的な改良が可能**
   - 必要に応じて後から関数を追加
   - 大きな変更なしに機能追加可能

4. **コード削減**
   - 約100行削減（320行→220行）
   - 重複がなくなり見通しが良い

## 6. 今すぐできること

```javascript
// Step 1: この2つの関数をdisplayResults関数の上に追加
function addField(label, value) {
    if (!value || value === '' || value === 'N/A' || value === '0000000' || value === '00000000') return '';
    return `<div class="field"><span class="field-label">${label}:</span> ${esc(value)}</div>`;
}

function addArrayField(label, arr) {
    if (!arr || !Array.isArray(arr) || arr.length === 0) return '';
    const filtered = arr.filter(item => item && item.trim());
    if (filtered.length === 0) return '';
    return addField(label, filtered.join(', '));
}

// Step 2: 例えばこの部分を
if (info.reg_num) {
    html += `<div class="field"><span class="field-label">登録番号:</span> ${esc(info.reg_num || 'N/A')}</div>`;
}

// こう変える
html += addField('登録番号', info.reg_num);
```

これだけ！
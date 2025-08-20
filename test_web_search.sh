#!/bin/bash

echo "=== 商標検索テスト ==="

# 1. トップページ取得
echo "1. トップページ確認"
curl -s "http://localhost:5000/" | grep -q "TMCloud 商標検索" && echo "  ✓ トップページOK" || echo "  ✗ トップページNG"

# 2. 検索実行（JavaScript経由なのでAPIエンドポイントを直接呼ぶ）
echo -e "\n2. API検索（出願番号: 2024022742）"
RESPONSE=$(curl -s -X POST "http://localhost:5000/search" \
  -H "Content-Type: application/json" \
  -d '{"keyword":"2024022742","search_type":"app_num"}')

# 3. 結果確認
echo "  検索結果:"
echo "$RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'results' in data and data['results']:
        result = data['results'][0]['basic_info']
        print(f'  ✓ 出願番号: {result.get(\"app_num\")}')
        print(f'  ✓ 商標名: {result.get(\"trademark_name\")}')
        if 'progress_records' in result:
            records = result['progress_records']
            print(f'  ✓ 審査中間記録: {len(records.get(\"exam\", []))}件')
            print(f'  ✓ 審判中間記録: {len(records.get(\"trial\", []))}件')
            print(f'  ✓ 登録中間記録: {len(records.get(\"registration\", []))}件')
            if records.get('exam'):
                for i, rec in enumerate(records['exam'][:3], 1):
                    print(f'    {i}. {rec}')
    else:
        print('  ✗ 検索結果なし')
except Exception as e:
    print(f'  ✗ エラー: {e}')
"

echo -e "\n=== テスト完了 ==="
@echo off
setlocal enabledelayedexpansion

echo =============================================
echo TMCloud 商標検索（Windows版）
echo =============================================
echo.

cd /d C:\Users\ygenk\Desktop\TMCloud

if "%1"=="" (
    echo 使用方法:
    echo   search.bat "検索キーワード"
    echo   search.bat "検索キーワード" --limit 10
    echo   search.bat "検索キーワード" --type phonetic
    echo.
    echo 例:
    echo   search.bat "プル"
    echo   search.bat "2024061720"
    echo   search.bat "プル" --type phonetic --limit 5
    echo.
    pause
    exit /b
)

echo 検索実行中: %*
echo.

python -c "from tmcloud_search_integrated import TMCloudIntegratedSearch; import sys; searcher = TMCloudIntegratedSearch('tmcloud_v2_20250818_081655.db'); results = searcher.search(%*); import json; print(json.dumps(results, ensure_ascii=False, indent=2)) if results else print('結果が見つかりませんでした')"

echo.
pause
@echo off
echo =============================================
echo TMCloud 立体商標表示テスト（Windows版）
echo =============================================
echo.

cd /d C:\Users\ygenk\Desktop\TMCloud

echo Pythonバージョン確認:
python --version
echo.

echo テスト実行中...
python test_3d_windows.py

pause
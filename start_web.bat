@echo off
echo =============================================
echo TMCloud Web インターフェース起動
echo =============================================
echo.

cd /d C:\Users\ygenk\Desktop\TMCloud

echo Flaskサーバーを起動しています...
echo ブラウザで http://localhost:5000 を開いてください
echo.
echo 終了するには Ctrl+C を押してください
echo.

python tmcloud_simple_web.py

pause
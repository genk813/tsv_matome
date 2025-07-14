@echo off
echo Checking current Git status...
echo ===============================

cd "C:\Users\ygenk\Desktop\TMCloud"

echo Git status:
git status

echo.
echo Remote status:
git fetch origin
git status

echo.
echo Log comparison:
git log --oneline -5

echo.
echo Remote log:
git log origin/main --oneline -5

pause
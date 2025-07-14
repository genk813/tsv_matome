@echo off
echo Debugging Git push issues...
echo ==============================

cd /d "C:\Users\ygenk\Desktop\TMCloud"

echo 1. Git version:
git --version

echo.
echo 2. Repository status:
git status

echo.
echo 3. Remote configuration:
git remote -v

echo.
echo 4. Branch information:
git branch -vv

echo.
echo 5. Last few commits:
git log --oneline -3

echo.
echo 6. Checking connectivity to GitHub:
git ls-remote origin

echo.
echo 7. Attempting push with verbose output:
git push origin main --verbose

echo.
echo 8. If that failed, trying with force (BE CAREFUL):
echo Would you like to force push? This will overwrite remote. (y/N):
set /p answer=
if /i "%answer%"=="y" (
    git push origin main --force --verbose
)

pause
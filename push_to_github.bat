@echo off
echo Pushing TMCloud to GitHub for version control...
echo ================================================

cd /d "C:\Users\ygenk\Desktop\TMCloud"

echo Current status:
git status --short

echo.
echo Pushing to GitHub...
git push origin main

echo.
if %ERRORLEVEL% EQU 0 (
    echo ✅ SUCCESS! TMCloud is now on GitHub
    echo Repository: https://github.com/genk813/TMCloud
) else (
    echo ❌ Push failed. Common issues:
    echo 1. Network connection
    echo 2. GitHub authentication
    echo 3. Repository permissions
    echo.
    echo Try again or check GitHub settings.
)

echo.
echo GitHub repository: https://github.com/genk813/TMCloud
pause
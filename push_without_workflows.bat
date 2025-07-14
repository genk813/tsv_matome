@echo off
echo Pushing without workflow files (temporary solution)...
echo ===================================================

cd /d "C:\Users\ygenk\Desktop\TMCloud"

echo 1. Backing up workflow files...
if exist .github\workflows mkdir .github\workflows_backup
if exist .github\workflows\claude.yml move .github\workflows\claude.yml .github\workflows_backup\
if exist .github\workflows\test.yml move .github\workflows\test.yml .github\workflows_backup\

echo 2. Adding the moved files to ignore temporarily...
git reset HEAD .github/workflows/ 2>nul

echo 3. Pushing main content...
git push origin main

echo 4. Restoring workflow files...
if exist .github\workflows_backup\claude.yml move .github\workflows_backup\claude.yml .github\workflows\
if exist .github\workflows_backup\test.yml move .github\workflows_backup\test.yml .github\workflows\
rmdir .github\workflows_backup 2>nul

if %ERRORLEVEL% EQU 0 (
    echo ✅ SUCCESS! Main content pushed to GitHub
    echo Repository: https://github.com/genk813/TMCloud
    echo.
    echo Next: Add 'workflow' scope to your GitHub token to enable Actions
) else (
    echo ❌ Push still failed. Check GitHub authentication.
)

pause
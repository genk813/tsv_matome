@echo off
echo Simple push to GitHub...
echo ========================

cd /d "C:\Users\ygenk\Desktop\TMCloud"

echo Pushing to GitHub...
git push origin main

echo.
echo Push completed. Check the result above.
echo If you see an error about 'workflow scope', you need to:
echo 1. Go to GitHub.com → Settings → Developer settings → Personal access tokens
echo 2. Edit your token and add 'workflow' scope
echo 3. Try pushing again

pause
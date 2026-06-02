@echo off
echo ==================================================
echo 🚀 Greyit TV Studio Dashboard 구동 중...
echo ==================================================
echo.
echo 창을 닫지 마세요! 브라우저가 곧 열립니다...
cd /d "%~dp0studio-dashboard"
start http://localhost:5173
npm run dev

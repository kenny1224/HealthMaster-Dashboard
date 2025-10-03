@echo off
chcp 65001 >nul
echo.
echo ================================================
echo   健康達人積分賽 - 啟動中...
echo ================================================
echo.

cd src
echo 正在啟動 Streamlit 儀表板...
echo.
streamlit run dashboard.py --server.headless true

pause

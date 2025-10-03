@echo off
chcp 65001 >nul
echo ================================================
echo   健康達人積分賽 - 本地測試工具
echo ================================================
echo.

echo 正在啟動 Streamlit 儀表板...
echo 瀏覽器將自動開啟 http://localhost:8501
echo.
echo 按 Ctrl+C 可停止程式
echo ================================================
echo.

cd src
streamlit run dashboard.py

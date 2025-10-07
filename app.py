"""
HealthMaster Dashboard - Streamlit Cloud Entry Point
健康達人積分賽儀表板 - Streamlit Cloud 入口點
"""

import sys
import os

# 添加 src 目錄到 Python 路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

# 執行主程式
exec(open(os.path.join(src_dir, 'dashboard.py')).read())
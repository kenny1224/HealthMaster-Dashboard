"""
更新的資料載入與處理模組 - 使用新架構
"""

import pandas as pd
import streamlit as st
from datetime import datetime
import pytz
import os


class DataLoader:
    """資料載入器 - 使用新架構"""
    
    def __init__(self, file_paths=None):
        # 使用新的資料處理器
        from new_data_loader import NewDataLoader
        self.new_loader = NewDataLoader()
        self.activity_analyzer = None  # 延遲初始化
        
    @st.cache_data(ttl=300)  # 5分鐘快取
    def load_data(_self):
        """載入資料 - 使用新架構"""
        return _self.new_loader.load_data()
    
    def validate_data(self, df):
        """驗證資料完整性"""
        return self.new_loader.validate_data(df)
    
    def clean_data(self, df):
        """清理資料"""
        return self.new_loader.clean_data(df)
    
    def get_last_update_time(self):
        """獲取檔案最後更新時間（台灣時區）"""
        return self.new_loader.get_last_update_time()
    
    def get_statistics(self, df):
        """獲取統計資訊 - 使用新架構計算"""
        # 從新架構取得正確的統計數據
        dashboard_stats = self.new_loader.processor.get_dashboard_statistics()
        
        if dashboard_stats:
            # 轉換為原有格式，確保數字正確
            stats = {
                'total_participants': dashboard_stats['total_participants'],
                'female_count': len(df[df['性別'] == '女']),
                'male_count': len(df[df['性別'] == '男']),
                'avg_score': dashboard_stats['avg_score'],
                'max_score': dashboard_stats['max_score'],
                'min_score': dashboard_stats['min_score'],
            }
            return stats
        else:
            # 回退到基本統計
            return self.new_loader.get_statistics(df)
    
    def get_activity_analyzer(self):
        """取得活動分析器"""
        if self.activity_analyzer is None:
            self.activity_analyzer = self.new_loader.get_activity_analyzer()
        return self.activity_analyzer
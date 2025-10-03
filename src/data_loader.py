"""
資料載入與處理模組
自動載入 Excel 檔案並處理資料
"""

import pandas as pd
import streamlit as st
from datetime import datetime
import os


class DataLoader:
    """資料載入器"""
    
    def __init__(self, file_path='data/20250903分數累積表.xlsx'):
        # 取得專案根目錄（src 的上一層）
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        
        # 如果 file_path 是相對路徑，轉換為絕對路徑
        if not os.path.isabs(file_path):
            self.file_path = os.path.join(project_root, file_path)
        else:
            self.file_path = file_path
        
    @st.cache_data(ttl=300)  # 5分鐘快取
    def load_data(_self):
        """載入分數累積表"""
        try:
            df = pd.read_excel(_self.file_path, sheet_name='分數累積')
            
            # 自動清理空白行（姓名為空的資料）
            if '姓名' in df.columns:
                original_count = len(df)
                df = df[df['姓名'].notna()].copy()
                removed_count = original_count - len(df)
                if removed_count > 0:
                    # 只在控制台記錄，不顯示給使用者
                    print(f"已自動清理 {removed_count} 筆空白資料")
            
            return df
        except FileNotFoundError:
            st.error(f"❌ 找不到檔案：{_self.file_path}")
            return None
        except Exception as e:
            st.error(f"❌ 讀取檔案時發生錯誤：{str(e)}")
            return None
    
    def validate_data(self, df):
        """驗證資料完整性"""
        if df is None:
            return False, ["資料載入失敗"]
        
        errors = []  # 真正的錯誤
        warnings = []  # 只是警告
        required_columns = ['姓名', '性別', 'total']
        
        # 檢查必要欄位（這是真正的錯誤）
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            errors.append(f"缺少必要欄位：{', '.join(missing_cols)}")
            return False, errors
        
        # 檢查是否有有效資料（這是真正的錯誤）
        if len(df) == 0:
            errors.append("沒有有效的參賽者資料")
            return False, errors
        
        # 檢查性別欄位（只是警告，會自動清理）
        valid_genders = ['生理女', '生理男']
        if '性別' in df.columns:
            invalid_gender = df[~df['性別'].isin(valid_genders) & df['性別'].notna()]
            if len(invalid_gender) > 0:
                warnings.append(f"ℹ️ {len(invalid_gender)} 筆資料性別欄位異常（將被忽略）")
        
        # 檢查 total 分數（只是警告，會自動設為 0）
        if 'total' in df.columns:
            nan_count = df['total'].isna().sum()
            if nan_count > 0:
                warnings.append(f"ℹ️ {nan_count} 筆資料缺少分數（將自動設為 0）")
        
        # 只有真正的錯誤才算驗證失敗，警告只顯示但不影響使用
        if warnings:
            for warning in warnings:
                st.info(warning)
        
        return True, []  # 驗證通過
    
    def clean_data(self, df):
        """清理資料"""
        if df is None:
            return None
        
        # 複製資料避免修改原始資料
        df = df.copy()
        
        # 清理 total 欄位
        if 'total' in df.columns:
            df['total'] = pd.to_numeric(df['total'], errors='coerce').fillna(0)
        
        # 移除姓名為空的資料
        if '姓名' in df.columns:
            df = df[df['姓名'].notna()]
        
        # 移除性別為空的資料
        if '性別' in df.columns:
            df = df[df['性別'].notna()]
        
        return df
    
    def get_last_update_time(self):
        """獲取檔案最後更新時間"""
        try:
            if os.path.exists(self.file_path):
                timestamp = os.path.getmtime(self.file_path)
                return datetime.fromtimestamp(timestamp)
            return None
        except Exception:
            return None
    
    def get_column_safe(self, df, column_names):
        """安全獲取欄位（支援多個可能的欄位名稱）"""
        if isinstance(column_names, str):
            column_names = [column_names]
        
        for name in column_names:
            if name in df.columns:
                return df[name]
        
        return None
    
    def extract_score_details(self, df):
        """提取分數明細（運動分、飲食分等）"""
        score_details = {}
        
        # 尋找運動相關欄位
        exercise_cols = [col for col in df.columns if '運動' in col or '日常' in col]
        if exercise_cols:
            score_details['運動分'] = df[exercise_cols].fillna(0).sum(axis=1)
        
        # 尋找飲食相關欄位
        diet_cols = [col for col in df.columns if '飲食' in col]
        if diet_cols:
            score_details['飲食分'] = df[diet_cols].fillna(0).sum(axis=1)
        
        # 尋找 bonus 欄位
        bonus_col = self.get_column_safe(df, ['個人bonus分', 'bonus', 'Bonus'])
        if bonus_col is not None:
            score_details['Bonus分'] = bonus_col.fillna(0)
        
        # 社團活動分數（所有包含社團名稱的欄位）
        club_cols = [col for col in df.columns if any(x in col for x in ['羽球', '瑜珈', '桌球', '戶外'])]
        if club_cols:
            score_details['社團分'] = df[club_cols].fillna(0).sum(axis=1)
        
        return score_details
    
    def get_statistics(self, df):
        """獲取統計資訊"""
        stats = {
            'total_participants': len(df),
            'female_count': len(df[df['性別'] == '生理女']),
            'male_count': len(df[df['性別'] == '生理男']),
            'avg_score': df['total'].mean(),
            'max_score': df['total'].max(),
            'min_score': df['total'].min(),
        }
        
        # 體脂完成率
        if '體脂是否上傳' in df.columns:
            completed = df['體脂是否上傳'].isin(['已完成', '✅', '是']).sum()
            stats['body_fat_completion_rate'] = completed / len(df) if len(df) > 0 else 0
        
        # 運動和飲食統計
        score_details = self.extract_score_details(df)
        if '運動分' in score_details:
            stats['total_exercise_records'] = int(score_details['運動分'].sum())
        if '飲食分' in score_details:
            stats['total_diet_records'] = int(score_details['飲食分'].sum())
        
        return stats

"""
新的資料載入器 - 使用重新定義的資料處理邏輯
"""

import pandas as pd
import streamlit as st
from datetime import datetime
import pytz
import os
from activity_data_processor import ActivityDataProcessor


class NewDataLoader:
    """新的資料載入器"""
    
    def __init__(self):
        self.processor = ActivityDataProcessor()
        # 設定實際存在的檔案
        self.processor.periods['回合1']['檔案'] = '20250903分數累積表(0808-0830).xlsx'
        self.processor.periods['回合2']['檔案'] = '20250905分數累積表(0831-0920).xlsx'
        
    @st.cache_data(ttl=300)  # 5分鐘快取
    def load_data(_self):
        """載入並處理資料"""
        try:
            # 載入所有期間資料
            success = _self.processor.load_all_periods_data()
            
            if not success:
                st.error("❌ 無法載入資料檔案")
                return None
            
            # 建立統計表
            if not _self.processor.build_participant_activity_stats():
                st.error("❌ 統計表建立失敗") 
                return None
            
            # 取得統計資料
            stats_df = _self.processor.get_participant_activity_stats()
            
            if stats_df.empty:
                st.error("❌ 沒有有效的統計資料")
                return None
            
            # 計算每人總分，用於排名
            person_totals = stats_df.groupby('姓名').agg({
                '日常運動得分': 'sum',
                '飲食得分': 'sum',
                '個人Bonus得分': 'sum',
                '參加社團得分': 'sum'
            }).reset_index()
            
            person_totals['total'] = (person_totals['日常運動得分'] + 
                                    person_totals['飲食得分'] + 
                                    person_totals['個人Bonus得分'] + 
                                    person_totals['參加社團得分'])
            
            # 從原始檔案取得性別等基本資料
            gender_data = _self._get_basic_info()
            
            # 合併基本資料
            final_df = pd.merge(person_totals, gender_data, on='姓名', how='left')
            
            # 統一性別標示：生理女→女，生理男→男
            if '性別' in final_df.columns:
                final_df['性別'] = final_df['性別'].replace({'生理女': '女', '生理男': '男'})
            
            print(f"新架構載入完成：{len(final_df)} 位參賽者")
            return final_df
            
        except Exception as e:
            st.error(f"❌ 載入資料時發生錯誤：{str(e)}")
            return None
    
    def _get_basic_info(self):
        """從Excel檔案取得基本資料（性別、部門等）"""
        try:
            # 從兩個檔案合併基本資料
            all_basic = []
            
            # 檔案1
            file1 = os.path.join("data", "20250903分數累積表(0808-0830).xlsx")
            if os.path.exists(file1):
                df1 = pd.read_excel(file1, sheet_name='分數累積')
                cols = ['姓名', '性別']
                if '所屬部門' in df1.columns:
                    cols.append('所屬部門')
                basic1 = df1[cols].copy()
                basic1 = basic1[basic1['姓名'].notna()]
                all_basic.append(basic1)
            
            # 檔案2
            file2 = os.path.join("data", "20250905分數累積表(0831-0920).xlsx")
            if os.path.exists(file2):
                df2 = pd.read_excel(file2, sheet_name='分數累積')
                cols = ['姓名', '性別']
                if '所屬部門' in df2.columns:
                    cols.append('所屬部門')
                basic2 = df2[cols].copy()
                basic2 = basic2[basic2['姓名'].notna()]
                all_basic.append(basic2)
            
            if all_basic:
                # 合併並去重
                combined_basic = pd.concat(all_basic, ignore_index=True)
                # 去重，保留最後一筆記錄（通常是最新的）
                combined_basic = combined_basic.drop_duplicates(subset=['姓名'], keep='last')
                return combined_basic
            else:
                return pd.DataFrame(columns=['姓名', '性別', '所屬部門'])
            
        except Exception as e:
            print(f"取得基本資料時發生錯誤: {str(e)}")
            return pd.DataFrame(columns=['姓名', '性別', '所屬部門'])
    
    def validate_data(self, df):
        """驗證資料完整性"""
        if df is None:
            return False, ["資料載入失敗"]
        
        required_columns = ['姓名', '性別', 'total']
        missing_cols = [col for col in required_columns if col not in df.columns]
        
        if missing_cols:
            return False, [f"缺少必要欄位：{', '.join(missing_cols)}"]
        
        if len(df) == 0:
            return False, ["沒有有效的參賽者資料"]
        
        return True, []
    
    def clean_data(self, df):
        """清理資料"""
        if df is None:
            return None
        
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
            # 統一性別標示
            df['性別'] = df['性別'].replace({'生理女': '女', '生理男': '男'})
        
        return df
    
    def get_last_update_time(self):
        """獲取檔案最後更新時間（台灣時區）"""
        try:
            latest_time = None
            taipei_tz = pytz.timezone('Asia/Taipei')
            
            # 檢查已載入的檔案
            for period_info in self.processor.periods.values():
                file_path = os.path.join("data", period_info["檔案"])
                if os.path.exists(file_path):
                    timestamp = os.path.getmtime(file_path)
                    utc_time = datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.UTC)
                    file_time = utc_time.astimezone(taipei_tz)
                    
                    if latest_time is None or file_time > latest_time:
                        latest_time = file_time
            
            return latest_time
        except Exception:
            return None
    
    def get_statistics(self, df):
        """獲取統計資訊"""
        stats = {
            'total_participants': len(df),
            'female_count': len(df[df['性別'] == '女']),
            'male_count': len(df[df['性別'] == '男']),
            'avg_score': df['total'].mean(),
            'max_score': df['total'].max(),
            'min_score': df['total'].min(),
        }
        
        return stats
    
    def get_activity_analyzer(self):
        """取得活動分析器 - 新架構版本"""
        return NewActivityAnalyzer(self.processor)


class NewActivityAnalyzer:
    """新的活動分析器 - 配合新架構"""
    
    def __init__(self, processor):
        self.processor = processor
        
    def load_detailed_data(self):
        """載入詳細資料 - 實際上資料已經在processor中"""
        return True
    
    def get_person_details(self, name):
        """取得個人詳細資料"""
        stats_df = self.processor.get_participant_activity_stats()
        
        # 篩選該人的資料
        person_data = stats_df[stats_df['姓名'] == name]
        
        if person_data.empty:
            return None
        
        # 聚合所有期間的資料
        totals = person_data.agg({
            '日常運動得分': 'sum',
            '日常運動次數': 'sum',
            '飲食得分': 'sum',
            '飲食次數': 'sum',
            '個人Bonus得分': 'sum',
            '個人Bonus次數': 'sum',
            '參加社團得分': 'sum',
            '參加社團次數': 'sum'
        })
        
        # 轉換為原有格式
        result = {
            'exercise': {
                'total_score': totals['日常運動得分'],
                'total_count': totals['日常運動次數']
            },
            'diet': {
                'total_score': totals['飲食得分'],
                'total_count': totals['飲食次數']
            },
            'bonus': {
                'total_score': totals['個人Bonus得分'],
                'total_count': totals['個人Bonus次數']
            },
            'club': {
                'total_score': totals['參加社團得分'],
                'total_count': totals['參加社團次數'],
                'total_activities': []  # 暫時空陣列，如需要可從club_details取得
            }
        }
        
        return result
    
    def get_overall_statistics(self):
        """取得全體統計資料"""
        return self.processor.get_dashboard_statistics()
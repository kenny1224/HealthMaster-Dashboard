"""
活動資料處理器 - 按照新的資料處理邏輯重新設計
處理4個回合期間的Excel檔案，實作完整的資料轉換與統計
"""

import pandas as pd
import numpy as np
from datetime import datetime
import re
import os


class ActivityDataProcessor:
    """活動資料處理器"""
    
    def __init__(self):
        # 定義4個回合期間
        self.periods = {
            "回合1": {
                "期間": "8/8-8/30",
                "檔案": "20250903分數累積表(0808-0830).xlsx"
            },
            "回合2": {
                "期間": "8/31-9/20", 
                "檔案": "20250905分數累積表(0831-0920).xlsx"
            },
            "回合3": {
                "期間": "9/21-10/11",
                "檔案": "20251012分數累積表(0921-1011).xlsx"  # 假設檔名
            },
            "回合4": {
                "期間": "10/12-10/31",
                "檔案": "20251101分數累積表(1012-1031).xlsx"  # 假設檔名
            }
        }
        
        # 初始化資料容器
        self.period_data = {}  # 各期間基本資料
        self.club_activity_details = pd.DataFrame()  # 參加社團活動明細表
        self.participant_activity_stats = pd.DataFrame()  # 參加者活動統計表
        
    def load_all_periods_data(self, data_dir="data"):
        """載入所有期間的Excel檔案"""
        print("開始載入所有期間的Excel檔案...")
        
        for period_key, period_info in self.periods.items():
            file_path = os.path.join(data_dir, period_info["檔案"])
            
            if os.path.exists(file_path):
                print(f"正在處理 {period_key} ({period_info['期間']})...")
                period_data = self._process_period_file(file_path, period_key, period_info["期間"])
                if period_data is not None:
                    self.period_data[period_key] = period_data
                    print(f"  成功載入 {len(period_data)} 位參賽者資料")
            else:
                print(f"找不到檔案: {file_path}")
        
        print(f"共載入 {len(self.period_data)} 個期間的資料")
        return len(self.period_data) > 0
    
    def _process_period_file(self, file_path, period_key, period_name):
        """處理單一期間的Excel檔案"""
        try:
            # 讀取分數累積工作表
            df = pd.read_excel(file_path, sheet_name='分數累積')
            
            # 建立基本資料表
            basic_data = []
            club_activities = []
            
            for _, row in df.iterrows():
                if pd.isna(row.iloc[4]):  # E欄姓名為空則跳過
                    continue
                
                name = row.iloc[4]  # E欄姓名
                
                # A2-A4定義的基本資料
                exercise_score = row.iloc[10] if len(row) > 10 and pd.notna(row.iloc[10]) else 0  # K欄日常運動得分
                exercise_count = int(exercise_score / 10) if exercise_score > 0 else 0  # 運動次數 = 得分/10
                
                diet_score = row.iloc[11] if len(row) > 11 and pd.notna(row.iloc[11]) else 0  # L欄飲食得分
                diet_count = int(diet_score / 10) if diet_score > 0 else 0  # 飲食次數 = 得分/10
                
                bonus_score = row.iloc[12] if len(row) > 12 and pd.notna(row.iloc[12]) else 0  # M欄個人Bonus得分
                bonus_count = int(bonus_score / 30) if bonus_score > 0 else 0  # Bonus次數 = 得分/30
                
                # 加入基本資料
                basic_data.append({
                    "回合期間": period_name,
                    "姓名": name,
                    "日常運動得分": exercise_score,
                    "日常運動次數": exercise_count,
                    "飲食得分": diet_score,
                    "飲食次數": diet_count,
                    "個人Bonus得分": bonus_score,
                    "個人Bonus次數": bonus_count
                })
                
                # A5定義的社團活動資料處理 (N欄開始到total前)
                # 找到total欄位的位置
                total_col_idx = None
                for i, col_name in enumerate(row.index):
                    if 'total' in str(col_name).lower():
                        total_col_idx = i
                        break
                
                if total_col_idx:
                    # 從N欄(索引13)開始到total前
                    for i in range(13, total_col_idx):
                        if i < len(row):
                            activity_score = row.iloc[i]
                            if pd.notna(activity_score) and activity_score > 0:
                                activity_name = row.index[i]
                                
                                # 解析活動名稱，切分日期和社團名稱
                                date_str, club_name = self._parse_activity_name(activity_name)
                                
                                club_activities.append({
                                    "回合期間": period_name,
                                    "姓名": name,
                                    "社團活動日期": date_str,
                                    "參加社團": club_name,
                                    "得分": activity_score
                                })
            
            # 更新社團活動明細表
            if club_activities:
                new_club_df = pd.DataFrame(club_activities)
                self.club_activity_details = pd.concat([self.club_activity_details, new_club_df], ignore_index=True)
            
            return pd.DataFrame(basic_data)
            
        except Exception as e:
            print(f"處理檔案 {file_path} 時發生錯誤: {str(e)}")
            return None
    
    def _parse_activity_name(self, activity_name):
        """解析活動名稱，切分日期和社團名稱"""
        activity_str = str(activity_name)
        
        # 使用正則表達式匹配日期格式 (如 8/13, 9/2 等)
        date_pattern = r'(\d{1,2}/\d{1,2})'
        match = re.search(date_pattern, activity_str)
        
        if match:
            date_part = match.group(1)
            # 移除日期部分，剩下的就是社團名稱
            club_name = re.sub(date_pattern, '', activity_str).strip()
            
            # 轉換為完整日期格式 (2025年)
            try:
                month, day = date_part.split('/')
                date_str = f"2025/{month.zfill(2)}/{day.zfill(2)}"
                return date_str, club_name
            except:
                return f"2025/{date_part}", club_name
        else:
            # 如果沒有找到日期，整個字串視為社團名稱
            return "2025/01/01", activity_str  # 預設日期
    
    def build_participant_activity_stats(self):
        """建立參加者活動統計表"""
        print("正在建立參加者活動統計表...")
        
        if self.club_activity_details.empty:
            print("社團活動明細表為空")
        
        # 合併所有期間的基本資料
        all_basic_data = []
        for period_key, period_df in self.period_data.items():
            all_basic_data.append(period_df)
        
        if all_basic_data:
            basic_stats = pd.concat(all_basic_data, ignore_index=True)
        else:
            print("沒有基本資料可以處理")
            return False
        
        # 計算社團活動統計
        if not self.club_activity_details.empty:
            club_stats = self.club_activity_details.groupby(['回合期間', '姓名']).agg({
                '得分': 'sum',
                '參加社團': 'count'
            }).reset_index()
            club_stats.columns = ['回合期間', '姓名', '參加社團得分', '參加社團次數']
        else:
            # 如果沒有社團活動資料，創建空的統計
            club_stats = pd.DataFrame(columns=['回合期間', '姓名', '參加社團得分', '參加社團次數'])
        
        # 合併基本資料和社團活動統計
        self.participant_activity_stats = pd.merge(
            basic_stats, 
            club_stats, 
            on=['回合期間', '姓名'], 
            how='left'
        )
        
        # 填補空值
        self.participant_activity_stats['參加社團得分'] = self.participant_activity_stats['參加社團得分'].fillna(0)
        self.participant_activity_stats['參加社團次數'] = self.participant_activity_stats['參加社團次數'].fillna(0)
        
        print(f"參加者活動統計表建立完成，共 {len(self.participant_activity_stats)} 筆記錄")
        return True
    
    def get_participant_activity_stats(self):
        """取得參加者活動統計表"""
        return self.participant_activity_stats
    
    def get_club_activity_details(self):
        """取得參加社團活動明細表"""
        return self.club_activity_details
    
    def get_dashboard_statistics(self):
        """計算儀表板統計數據"""
        if self.participant_activity_stats.empty:
            return None
        
        stats_df = self.participant_activity_stats
        
        # 按姓名聚合，計算每人的總統計
        person_totals = stats_df.groupby('姓名').agg({
            '日常運動得分': 'sum',
            '日常運動次數': 'sum',
            '飲食得分': 'sum', 
            '飲食次數': 'sum',
            '個人Bonus得分': 'sum',
            '個人Bonus次數': 'sum',
            '參加社團得分': 'sum',
            '參加社團次數': 'sum'
        }).reset_index()
        
        # 計算總分
        person_totals['總分'] = (person_totals['日常運動得分'] + 
                               person_totals['飲食得分'] + 
                               person_totals['個人Bonus得分'] + 
                               person_totals['參加社團得分'])
        
        # 計算統計數據
        dashboard_stats = {
            'total_participants': len(person_totals),
            'exercise': {
                'total_count': person_totals['日常運動次數'].sum(),
                'total_score': person_totals['日常運動得分'].sum(),
                'participants': len(person_totals[person_totals['日常運動次數'] > 0])
            },
            'diet': {
                'total_count': person_totals['飲食次數'].sum(),
                'total_score': person_totals['飲食得分'].sum(),
                'participants': len(person_totals[person_totals['飲食次數'] > 0])
            },
            'bonus': {
                'total_count': person_totals['個人Bonus次數'].sum(),
                'total_score': person_totals['個人Bonus得分'].sum(),
                'participants': len(person_totals[person_totals['個人Bonus次數'] > 0])
            },
            'club': {
                'total_activities': person_totals['參加社團次數'].sum(),
                'total_score': person_totals['參加社團得分'].sum(),
                'participants': len(person_totals[person_totals['參加社團次數'] > 0])
            },
            'avg_score': person_totals['總分'].mean(),
            'max_score': person_totals['總分'].max(),
            'min_score': person_totals['總分'].min()
        }
        
        return dashboard_stats
    
    def export_analysis_reports(self, output_dir="data"):
        """輸出分析報告"""
        if self.participant_activity_stats.empty:
            print("沒有統計資料可以輸出")
            return False
        
        print("正在輸出分析報告...")
        
        # 計算每人總計
        person_summary = self.participant_activity_stats.groupby('姓名').agg({
            '日常運動得分': 'sum',
            '日常運動次數': 'sum',
            '飲食得分': 'sum',
            '飲食次數': 'sum', 
            '個人Bonus得分': 'sum',
            '個人Bonus次數': 'sum',
            '參加社團得分': 'sum',
            '參加社團次數': 'sum'
        }).reset_index()
        
        person_summary['總分'] = (person_summary['日常運動得分'] + 
                                person_summary['飲食得分'] + 
                                person_summary['個人Bonus得分'] + 
                                person_summary['參加社團得分'])
        
        # 按總分排序
        person_summary = person_summary.sort_values('總分', ascending=False)
        
        # 輸出到Excel
        output_file = os.path.join(output_dir, "新架構活動統計分析報告.xlsx")
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # 個人總計統計
            person_summary.to_excel(writer, sheet_name='個人總計統計', index=False)
            
            # 期間明細統計
            self.participant_activity_stats.to_excel(writer, sheet_name='期間明細統計', index=False)
            
            # 社團活動明細
            if not self.club_activity_details.empty:
                self.club_activity_details.to_excel(writer, sheet_name='社團活動明細', index=False)
        
        print(f"分析報告已輸出: {output_file}")
        return True
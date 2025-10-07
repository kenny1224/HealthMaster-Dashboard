"""
活動資料分析器
處理多工作表的詳細活動資料，提供個人和全體統計
"""

import pandas as pd
import streamlit as st
from collections import defaultdict


class ActivityAnalyzer:
    """活動資料分析器"""
    
    def __init__(self, file_paths):
        self.file_paths = file_paths
        self.detailed_data = {}  # 儲存每個人的詳細活動資料
        
    def load_detailed_data(self):
        """載入所有檔案的詳細資料"""
        try:
            for i, file_path in enumerate(self.file_paths):
                period_name = f"期間{i+1}"
                print(f"正在分析 {period_name} 的詳細資料...")
                
                # 載入各工作表
                period_data = self._load_file_details(file_path, period_name)
                
                # 合併到總資料中
                self._merge_period_data(period_data, period_name)
                
            print(f"詳細資料分析完成，共 {len(self.detailed_data)} 位參賽者")
            return True
            
        except Exception as e:
            st.error(f"❌ 載入詳細資料時發生錯誤：{str(e)}")
            return False
    
    def _load_file_details(self, file_path, period_name):
        """載入單一檔案的詳細資料"""
        period_data = {}
        
        try:
            # 1. 載入分數累積表
            score_df = pd.read_excel(file_path, sheet_name='分數累積')
            
            # 2. 載入運動飲食統計表
            try:
                activity_df = pd.read_excel(file_path, sheet_name='ALL活動數據統計(運動+飲食)--分數計算表')
            except:
                activity_df = None
                print(f"  {period_name}: 找不到運動飲食統計表")
            
            # 3. 載入個人bonus分表
            try:
                bonus_df = pd.read_excel(file_path, sheet_name='個人bonus分')
            except:
                bonus_df = None
                print(f"  {period_name}: 找不到個人bonus分表")
            
            # 處理每位參賽者
            for _, row in score_df.iterrows():
                if pd.isna(row.iloc[4]):  # E欄是姓名，索引為4
                    continue
                    
                name = row.iloc[4]  # E欄姓名
                person_data = self._analyze_person_data(row, activity_df, bonus_df, period_name)
                period_data[name] = person_data
                
        except Exception as e:
            print(f"  {period_name}: 載入錯誤 - {str(e)}")
            
        return period_data
    
    def _analyze_person_data(self, score_row, activity_df, bonus_df, period_name):
        """分析個人詳細資料"""
        name = score_row.iloc[4]  # E欄姓名
        person_data = {
            'period': period_name,
            'exercise': {'score': 0, 'count': 0},
            'diet': {'score': 0, 'count': 0},
            'bonus': {'score': 0, 'count': 0},
            'club': {'score': 0, 'activities': []}
        }
        
        # 1. 分析運動資料 - 優先從分數累積表讀取實際分數，再從活動統計表取得次數
        exercise_score = score_row.iloc[10] if len(score_row) > 10 and pd.notna(score_row.iloc[10]) else 0
        person_data['exercise']['score'] = exercise_score
        
        if activity_df is not None:
            exercise_count = self._get_activity_count(name, activity_df, 'G')  # G欄是運動次數
            person_data['exercise']['count'] = exercise_count
        else:
            # 從分數推算次數
            person_data['exercise']['count'] = int(exercise_score / 10) if exercise_score > 0 else 0
        
        # 2. 分析飲食資料 - 優先從分數累積表讀取實際分數，再從活動統計表取得次數
        diet_score = score_row.iloc[11] if len(score_row) > 11 and pd.notna(score_row.iloc[11]) else 0
        person_data['diet']['score'] = diet_score
        
        if activity_df is not None:
            diet_count = self._get_activity_count(name, activity_df, 'E')  # E欄是飲食次數
            person_data['diet']['count'] = diet_count
        else:
            # 從分數推算次數
            person_data['diet']['count'] = int(diet_score / 10) if diet_score > 0 else 0
        
        # 3. 分析額外加分資料 - 優先從分數累積表讀取實際分數，再從bonus表取得次數
        bonus_score = score_row.iloc[12] if len(score_row) > 12 and pd.notna(score_row.iloc[12]) else 0
        person_data['bonus']['score'] = bonus_score
        
        if bonus_df is not None:
            bonus_count = self._get_bonus_count(name, bonus_df)
            person_data['bonus']['count'] = bonus_count
        else:
            # 從分數推算次數
            person_data['bonus']['count'] = int(bonus_score / 30) if bonus_score > 0 else 0
        
        # 4. 分析社團活動資料 (N欄開始到total前) - 計算參加次數和總分數
        club_score = 0
        club_count = 0
        club_activities = []
        
        # 找到total欄位的位置
        total_col_idx = None
        for i, col_name in enumerate(score_row.index):
            if 'total' in str(col_name).lower():
                total_col_idx = i
                break
        
        if total_col_idx:
            # 從N欄(索引13)開始到total前
            for i in range(13, total_col_idx):
                if i < len(score_row):
                    col_value = score_row.iloc[i]
                    if pd.notna(col_value) and col_value > 0:
                        col_name = score_row.index[i]
                        club_score += col_value  # 累加分數
                        club_count += 1  # 參加次數計數
                        club_activities.append(f"{col_name}: {col_value}分")
        
        person_data['club']['score'] = club_score
        person_data['club']['count'] = club_count  # 新增次數記錄
        person_data['club']['activities'] = club_activities
        
        return person_data
    
    def _get_activity_count(self, name, activity_df, column):
        """從活動統計表取得次數"""
        try:
            # D欄是姓名，尋找對應的人
            name_col = activity_df.iloc[:, 3]  # D欄是索引3
            matching_rows = activity_df[name_col == name]
            
            if not matching_rows.empty:
                if column == 'E':  # 飲食次數
                    count_col = matching_rows.iloc[:, 4]  # E欄是索引4
                elif column == 'G':  # 運動次數
                    count_col = matching_rows.iloc[:, 6]  # G欄是索引6
                else:
                    return 0
                
                count = count_col.iloc[0] if not count_col.empty and pd.notna(count_col.iloc[0]) else 0
                return int(count)
        except:
            pass
        return 0
    
    def _get_bonus_count(self, name, bonus_df):
        """從個人bonus分表計算出現次數"""
        try:
            # A欄是姓名
            name_col = bonus_df.iloc[:, 0]
            count = (name_col == name).sum()
            return count
        except:
            return 0
    
    def _merge_period_data(self, period_data, period_name):
        """合併期間資料到總資料中"""
        for name, data in period_data.items():
            if name not in self.detailed_data:
                self.detailed_data[name] = {
                    'exercise': {'total_score': 0, 'total_count': 0, 'periods': {}},
                    'diet': {'total_score': 0, 'total_count': 0, 'periods': {}},
                    'bonus': {'total_score': 0, 'total_count': 0, 'periods': {}},
                    'club': {'total_score': 0, 'total_count': 0, 'total_activities': [], 'periods': {}}
                }
            
            person = self.detailed_data[name]
            
            # 累加各期間的分數和次數（與data_loader的邏輯一致）
            person['exercise']['total_score'] += data['exercise']['score']
            person['exercise']['total_count'] += data['exercise']['count']
            person['exercise']['periods'][period_name] = data['exercise']
            
            person['diet']['total_score'] += data['diet']['score']
            person['diet']['total_count'] += data['diet']['count']
            person['diet']['periods'][period_name] = data['diet']
            
            person['bonus']['total_score'] += data['bonus']['score']
            person['bonus']['total_count'] += data['bonus']['count']
            person['bonus']['periods'][period_name] = data['bonus']
            
            person['club']['total_score'] += data['club']['score']
            person['club']['total_count'] += data['club'].get('count', 0)
            person['club']['total_activities'].extend(data['club']['activities'])
            person['club']['periods'][period_name] = data['club']
    
    def get_person_details(self, name):
        """取得個人詳細資料"""
        return self.detailed_data.get(name, None)
    
    def get_overall_statistics(self):
        """取得全體統計資料"""
        if not self.detailed_data:
            return None
        
        stats = {
            'total_participants': len(self.detailed_data),
            'exercise': {'total_score': 0, 'total_count': 0, 'participants': 0},
            'diet': {'total_score': 0, 'total_count': 0, 'participants': 0},
            'bonus': {'total_score': 0, 'total_count': 0, 'participants': 0},
            'club': {'total_score': 0, 'total_activities': 0, 'participants': 0}
        }
        
        for name, data in self.detailed_data.items():
            # 運動統計
            if data['exercise']['total_count'] > 0:
                stats['exercise']['total_score'] += data['exercise']['total_score']
                stats['exercise']['total_count'] += data['exercise']['total_count']
                stats['exercise']['participants'] += 1
            
            # 飲食統計
            if data['diet']['total_count'] > 0:
                stats['diet']['total_score'] += data['diet']['total_score']
                stats['diet']['total_count'] += data['diet']['total_count']
                stats['diet']['participants'] += 1
            
            # 額外加分統計
            if data['bonus']['total_count'] > 0:
                stats['bonus']['total_score'] += data['bonus']['total_score']
                stats['bonus']['total_count'] += data['bonus']['total_count']
                stats['bonus']['participants'] += 1
            
            # 社團活動統計
            if data['club']['total_count'] > 0:
                stats['club']['total_score'] += data['club']['total_score']
                stats['club']['total_activities'] += data['club']['total_count']  # 使用次數而非活動列表長度
                stats['club']['participants'] += 1
        
        return stats
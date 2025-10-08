#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
新EXCEL檔案資料載入器
處理"每周分數累積.xlsx"的資料結構
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

class NewExcelDataLoader:
    """新Excel檔案資料載入器"""
    
    def __init__(self, file_path='data/每周分數累積.xlsx'):
        self.file_path = file_path
        self.account_info = None
        self.period_data = {}
        self.participant_activity_stats = None
        
    def load_account_info(self):
        """載入帳號整理工作表"""
        try:
            df = pd.read_excel(self.file_path, sheet_name='帳號整理')
            # 移除性別欄位中的"生理"兩字
            if '性別' in df.columns:
                df['性別'] = df['性別'].str.replace('生理', '', regex=False)
            
            # 設定key值為"帳號(最新8/8)2"
            if '帳號(最新8/8)2' in df.columns:
                df = df.set_index('帳號(最新8/8)2')
            
            self.account_info = df
            print(f"載入帳號資料: {len(df)} 筆")
            return df
            
        except Exception as e:
            print(f"載入帳號整理資料失敗: {str(e)}")
            return None
    
    def load_period_data(self, sheet_name):
        """載入期間工作表資料"""
        try:
            df = pd.read_excel(self.file_path, sheet_name=sheet_name)
            
            # 設定key值為"id"
            if 'id' in df.columns:
                df = df.set_index('id')
            
            self.period_data[sheet_name] = df
            print(f"載入{sheet_name}資料: {len(df)} 筆")
            return df
            
        except Exception as e:
            print(f"載入{sheet_name}資料失敗: {str(e)}")
            return None
    
    def process_period_data(self, sheet_name, period_range):
        """處理單一期間的資料"""
        if sheet_name not in self.period_data:
            print(f"找不到{sheet_name}的資料")
            return None
            
        df = self.period_data[sheet_name].copy()
        results = []
        
        for participant_id, row in df.iterrows():
            # 取得參與者基本資訊
            participant_name = self.get_participant_name(participant_id)
            if not participant_name:
                continue
            
            # 計算基本分數和次數
            exercise_score = self.safe_get_value(row, 'L', 0)  # 日常運動得分
            diet_score = self.safe_get_value(row, 'M', 0)      # 飲食得分
            bonus_score = self.safe_get_value(row, 'N', 0)     # 個人Bonus得分
            
            exercise_count = int(exercise_score / 10) if exercise_score > 0 else 0
            diet_count = int(diet_score / 10) if diet_score > 0 else 0
            bonus_count = int(bonus_score / 30) if bonus_score > 0 else 0
            
            # 處理社團活動 (O欄開始到total前)
            club_activities = self.extract_club_activities(row, participant_name, period_range)
            club_score = sum([activity['得分'] for activity in club_activities])
            club_count = len(club_activities)
            
            # 組合結果
            result = {
                '回合期間': period_range,
                '姓名': participant_name,
                'id': participant_id,
                '日常運動得分': exercise_score,
                '日常運動次數': exercise_count,
                '飲食得分': diet_score,
                '飲食次數': diet_count,
                '個人Bonus得分': bonus_score,
                '個人Bonus次數': bonus_count,
                '參加社團得分': club_score,
                '參加社團次數': club_count,
                '社團活動明細': club_activities
            }
            
            results.append(result)
        
        return pd.DataFrame(results)
    
    def extract_club_activities(self, row, participant_name, period_range):
        """提取社團活動明細"""
        activities = []
        
        # 找到O欄位置到total前的所有欄位
        columns = row.index.tolist()
        start_idx = None
        end_idx = len(columns)
        
        # 找到起始位置 (O欄對應的位置)
        for i, col in enumerate(columns):
            if isinstance(col, str) and ('O' in col or i >= 14):  # O是第15欄(索引14)
                start_idx = i
                break
        
        # 找到結束位置 (total前)
        for i, col in enumerate(columns):
            if isinstance(col, str) and 'total' in col.lower():
                end_idx = i
                break
        
        if start_idx is None:
            return activities
        
        # 處理社團活動欄位
        for i in range(start_idx, end_idx):
            col_name = columns[i]
            score = self.safe_get_value(row, col_name, 0)
            
            if score > 0 and isinstance(col_name, str):
                # 解析活動名稱和日期
                date_part, club_part = self.parse_activity_name(col_name)
                
                if date_part and club_part:
                    activities.append({
                        '姓名': participant_name,
                        '回合期間': period_range,
                        '社團活動日期': date_part,
                        '參加社團': club_part,
                        '得分': score
                    })
        
        return activities
    
    def parse_activity_name(self, activity_name):
        """解析活動名稱，分離日期和社團名稱"""
        try:
            # 例如: "8/13 羽球社" -> ("2025/08/13", "羽球社")
            parts = activity_name.split(' ', 1)
            if len(parts) < 2:
                return None, None
            
            date_str = parts[0].strip()
            club_name = parts[1].strip()
            
            # 轉換日期格式
            if '/' in date_str:
                month_day = date_str.split('/')
                if len(month_day) == 2:
                    month = month_day[0].zfill(2)
                    day = month_day[1].zfill(2)
                    formatted_date = f"2025/{month}/{day}"
                    return formatted_date, club_name
            
            return None, None
            
        except Exception as e:
            print(f"解析活動名稱失敗: {activity_name}, 錯誤: {str(e)}")
            return None, None
    
    def get_participant_name(self, participant_id):
        """根據ID取得參與者姓名"""
        if self.account_info is None:
            return None
        
        try:
            if participant_id in self.account_info.index:
                # 假設姓名欄位叫'姓名'，需要根據實際欄位名稱調整
                name_columns = ['姓名', 'name', '參與者姓名']
                for col in name_columns:
                    if col in self.account_info.columns:
                        return self.account_info.loc[participant_id, col]
            return None
        except Exception as e:
            print(f"取得參與者姓名失敗: {participant_id}, 錯誤: {str(e)}")
            return None
    
    def safe_get_value(self, row, column, default=0):
        """安全取得數值"""
        try:
            if isinstance(column, str):
                # 如果是欄位名稱
                if column in row.index:
                    value = row[column]
                else:
                    return default
            elif isinstance(column, int):
                # 如果是欄位索引
                columns = row.index.tolist()
                if column < len(columns):
                    col_name = columns[column]
                    value = row[col_name]
                else:
                    return default
            else:
                # 其他情況直接作為欄位名稱處理
                if column in row.index:
                    value = row[column]
                else:
                    return default
            
            if pd.isna(value) or value == '':
                return default
            
            return float(value)
            
        except Exception as e:
            print(f"safe_get_value錯誤: column={column}, 錯誤={str(e)}")
            return default
    
    def build_participant_activity_stats(self):
        """建立參加者活動統計表"""
        all_data = []
        
        # 處理已載入的期間資料
        period_mappings = {
            '0808-0830': '2025/8/8-2025/8/30',
            '0831-0921': '2025/8/31-2025/9/21'
        }
        
        for sheet_name, period_range in period_mappings.items():
            if sheet_name in self.period_data:
                period_stats = self.process_period_data(sheet_name, period_range)
                if period_stats is not None:
                    all_data.append(period_stats)
        
        if all_data:
            # 合併所有期間資料
            combined_df = pd.concat(all_data, ignore_index=True)
            self.participant_activity_stats = combined_df
            print(f"建立參加者活動統計表: {len(combined_df)} 筆記錄")
            return combined_df
        
        return None
    
    def get_club_activity_details(self):
        """取得社團活動明細表"""
        if self.participant_activity_stats is None:
            return None
        
        all_activities = []
        
        for _, row in self.participant_activity_stats.iterrows():
            activities = row['社團活動明細']
            if activities:
                all_activities.extend(activities)
        
        if all_activities:
            club_df = pd.DataFrame(all_activities)
            return club_df
        
        return None
    
    def load_all_data(self):
        """載入所有資料"""
        print("開始載入新Excel檔案資料...")
        
        # 1. 載入帳號整理
        self.load_account_info()
        
        # 2. 載入期間資料
        self.load_period_data('0808-0830')
        self.load_period_data('0831-0921')
        
        # 3. 建立統計表
        self.build_participant_activity_stats()
        
        print("資料載入完成")
        
        return self.participant_activity_stats

if __name__ == "__main__":
    # 測試新資料載入器
    loader = NewExcelDataLoader()
    stats = loader.load_all_data()
    
    if stats is not None:
        print(f"\n參加者活動統計表：")
        print(stats.head())
        
        club_details = loader.get_club_activity_details()
        if club_details is not None:
            print(f"\n社團活動明細表：")
            print(club_details.head())
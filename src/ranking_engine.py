"""
排名計算引擎
處理男女分組排名與獎金計算
"""

import pandas as pd
import streamlit as st


class RankingEngine:
    """排名計算引擎"""
    
    # 男子組獎金結構
    MALE_PRIZE_CONFIG = {
        1: ('NT$6,000', '🥇', '#FFD700'),      # 金色
        2: ('NT$3,000', '🥈', '#C0C0C0'),      # 銀色
        3: ('NT$3,000', '🥈', '#C0C0C0'),
        4: ('NT$3,000', '🥈', '#C0C0C0'),
        5: ('NT$2,000', '🥉', '#CD7F32'),      # 銅色
        6: ('NT$2,000', '🥉', '#CD7F32'),
        7: ('NT$2,000', '🥉', '#CD7F32'),
        8: ('NT$2,000', '🥉', '#CD7F32'),
        9: ('NT$2,000', '🥉', '#CD7F32'),
        10: ('NT$1,000', '🏅', '#50C878'),     # 綠色
        11: ('NT$1,000', '🏅', '#50C878'),
        12: ('NT$1,000', '🏅', '#50C878'),
        13: ('NT$1,000', '🏅', '#50C878'),
        14: ('NT$1,000', '🏅', '#50C878'),
    }
    
    # 女子組獎金結構（新增）
    FEMALE_PRIZE_CONFIG = {
        1: ('NT$6,000', '🥇', '#FFD700'),      # 第1-2名
        2: ('NT$6,000', '🥇', '#FFD700'),
        3: ('NT$3,000', '🥈', '#C0C0C0'),      # 第3-8名
        4: ('NT$3,000', '🥈', '#C0C0C0'),
        5: ('NT$3,000', '🥈', '#C0C0C0'),
        6: ('NT$3,000', '🥈', '#C0C0C0'),
        7: ('NT$3,000', '🥈', '#C0C0C0'),
        8: ('NT$3,000', '🥈', '#C0C0C0'),
        9: ('NT$2,000', '🥉', '#CD7F32'),      # 第9-18名
        10: ('NT$2,000', '🥉', '#CD7F32'),
        11: ('NT$2,000', '🥉', '#CD7F32'),
        12: ('NT$2,000', '🥉', '#CD7F32'),
        13: ('NT$2,000', '🥉', '#CD7F32'),
        14: ('NT$2,000', '🥉', '#CD7F32'),
        15: ('NT$2,000', '🥉', '#CD7F32'),
        16: ('NT$2,000', '🥉', '#CD7F32'),
        17: ('NT$2,000', '🥉', '#CD7F32'),
        18: ('NT$2,000', '🥉', '#CD7F32'),
        19: ('NT$1,000', '🏅', '#50C878'),     # 第19-28名
        20: ('NT$1,000', '🏅', '#50C878'),
        21: ('NT$1,000', '🏅', '#50C878'),
        22: ('NT$1,000', '🏅', '#50C878'),
        23: ('NT$1,000', '🏅', '#50C878'),
        24: ('NT$1,000', '🏅', '#50C878'),
        25: ('NT$1,000', '🏅', '#50C878'),
        26: ('NT$1,000', '🏅', '#50C878'),
        27: ('NT$1,000', '🏅', '#50C878'),
        28: ('NT$1,000', '🏅', '#50C878'),
    }
    
    def __init__(self, df):
        self.df = df
        self.female_df = None
        self.male_df = None
    
    def calculate_rankings(self):
        """計算男女分組排名"""
        # 女性組
        female_data = self.df[self.df['性別'] == '生理女'].copy()
        female_data = female_data.sort_values('total', ascending=False).reset_index(drop=True)
        female_data['排名'] = range(1, len(female_data) + 1)
        
        # 添加獎金資訊（使用女性組配置）
        female_data[['獎金', '獎牌', '顏色']] = female_data['排名'].apply(
            lambda x: pd.Series(self.get_prize_info(x, 'female'))
        )
        
        self.female_df = female_data
        
        # 男性組
        male_data = self.df[self.df['性別'] == '生理男'].copy()
        male_data = male_data.sort_values('total', ascending=False).reset_index(drop=True)
        male_data['排名'] = range(1, len(male_data) + 1)
        
        # 添加獎金資訊（使用男性組配置）
        male_data[['獎金', '獎牌', '顏色']] = male_data['排名'].apply(
            lambda x: pd.Series(self.get_prize_info(x, 'male'))
        )
        
        self.male_df = male_data
        
        return self.female_df, self.male_df
    
    @staticmethod
    def get_prize_info(rank, gender='male'):
        """根據排名和性別獲取獎金資訊"""
        if gender == 'female':
            config = RankingEngine.FEMALE_PRIZE_CONFIG
        else:
            config = RankingEngine.MALE_PRIZE_CONFIG
            
        if rank in config:
            return config[rank]
        else:
            return ('-', '', '#FFFFFF')
    
    def get_person_info(self, name):
        """查詢個人資訊"""
        # 在女性組中查找
        female_result = self.female_df[self.female_df['姓名'] == name]
        if not female_result.empty:
            return female_result.iloc[0], '女性組', len(self.female_df)
        
        # 在男性組中查找
        male_result = self.male_df[self.male_df['姓名'] == name]
        if not male_result.empty:
            return male_result.iloc[0], '男性組', len(self.male_df)
        
        return None, None, None
    
    def get_top_n(self, n=10):
        """獲取兩組前 N 名"""
        female_top = self.female_df.head(n) if self.female_df is not None else pd.DataFrame()
        male_top = self.male_df.head(n) if self.male_df is not None else pd.DataFrame()
        return female_top, male_top
    
    def get_rank_difference(self, person_data, group_df):
        """計算與前一名的分數差距"""
        current_rank = person_data['排名']
        if current_rank == 1:
            return 0  # 已經是第一名
        
        prev_rank_data = group_df[group_df['排名'] == current_rank - 1]
        if not prev_rank_data.empty:
            return prev_rank_data.iloc[0]['total'] - person_data['total']
        return 0
    
    def get_statistics_by_department(self):
        """按部門統計參與情況"""
        if '所屬部門' not in self.df.columns:
            return None
        
        dept_stats = self.df.groupby(['所屬部門', '性別']).agg({
            '姓名': 'count',
            'total': 'mean'
        }).reset_index()
        dept_stats.columns = ['部門', '性別', '人數', '平均分數']
        
        return dept_stats
    
    def get_prize_winners(self):
        """獲取所有得獎者（男子組前14名，女子組前28名）"""
        female_winners = self.female_df.head(28) if self.female_df is not None else pd.DataFrame()
        male_winners = self.male_df.head(14) if self.male_df is not None else pd.DataFrame()
        
        return female_winners, male_winners
    
    @staticmethod
    def style_ranking_table(df, gender='male'):
        """表格樣式化（高亮獎金得主）"""
        def highlight_winners(row):
            max_prize_rank = 28 if gender == 'female' else 14
            if row['排名'] <= max_prize_rank:
                return ['background-color: #fff9e6; font-weight: bold'] * len(row)
            return [''] * len(row)
        
        return df.style.apply(highlight_winners, axis=1)
    
    def search_in_ranking(self, search_term, gender='all'):
        """在排名中搜尋"""
        results = []
        
        if gender in ['all', '女性組']:
            female_results = self.female_df[
                self.female_df['姓名'].str.contains(search_term, na=False)
            ]
            results.append(('女性組', female_results))
        
        if gender in ['all', '男性組']:
            male_results = self.male_df[
                self.male_df['姓名'].str.contains(search_term, na=False)
            ]
            results.append(('男性組', male_results))
        
        return results
    
    def filter_by_department(self, df, department):
        """按部門篩選"""
        if department == '全部' or '所屬部門' not in df.columns:
            return df
        return df[df['所屬部門'] == department]
    
    def get_score_breakdown(self, person_data):
        """獲取個人分數明細"""
        breakdown = {}
        
        # 從資料中提取各項分數
        score_fields = {
            '日常運動': ['日常運動8/8-8/20', '日常運動'],
            '健康飲食': ['每週飲食8/8-8/20', '飲食'],
            'Bonus分數': ['個人bonus分', 'bonus'],
        }
        
        for label, possible_cols in score_fields.items():
            for col in possible_cols:
                if col in person_data.index and pd.notna(person_data[col]):
                    breakdown[label] = person_data[col]
                    break
        
        # 計算社團活動分數
        club_cols = [col for col in person_data.index if any(x in str(col) for x in ['羽球', '瑜珈', '桌球', '戶外'])]
        if club_cols:
            club_total = sum([person_data[col] for col in club_cols if pd.notna(person_data[col])])
            if club_total > 0:
                breakdown['社團活動'] = club_total
        
        return breakdown
    
    def get_club_activities(self, person_data):
        """獲取個人參加的社團活動"""
        activities = []
        
        # 尋找所有社團活動欄位
        club_patterns = {
            '羽球社': '羽球',
            '瑜珈社': '瑜珈',
            '桌球社': '桌球',
            '戶外活動': '戶外'
        }
        
        for activity_name, pattern in club_patterns.items():
            matching_cols = [col for col in person_data.index if pattern in str(col)]
            for col in matching_cols:
                if pd.notna(person_data[col]) and person_data[col] > 0:
                    activities.append(f"{col} ✅")
        
        return activities

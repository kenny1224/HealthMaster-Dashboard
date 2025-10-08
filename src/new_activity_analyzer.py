#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
新活動分析器
處理新EXCEL檔案結構的活動統計分析
"""

import pandas as pd
import numpy as np
from collections import defaultdict

class NewActivityAnalyzer:
    """新活動分析器"""

    def __init__(self, processor):
        """
        Args:
            processor: NewDataProcessor 實例
        """
        self.processor = processor
        self.participant_stats = None
        self.club_details = None

    def load_detailed_data(self):
        """載入詳細資料"""
        if self.processor:
            # 從processor取得參加者活動統計表
            import os
            import pandas as pd
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            stats_path = os.path.join(project_root, 'data', '參加者活動統計表.xlsx')

            # 載入參加者活動統計表
            stats_df = pd.read_excel(stats_path)

            # 轉換為期間明細格式以配合原有邏輯
            period_data = []
            for _, row in stats_df.iterrows():
                # 期間1資料
                if row['期間1分數'] > 0:
                    period_row = {
                        'id': row['id'],
                        '姓名': row['姓名'],
                        '回合期間': '0808-0830',
                        '日常運動得分': row['運動總得分'] * (row['期間1分數'] / row['total']) if row['total'] > 0 else 0,
                        '日常運動次數': row['運動總次數'] * (row['期間1分數'] / row['total']) if row['total'] > 0 else 0,
                        '飲食得分': row['飲食總得分'] * (row['期間1分數'] / row['total']) if row['total'] > 0 else 0,
                        '飲食次數': row['飲食總次數'] * (row['期間1分數'] / row['total']) if row['total'] > 0 else 0,
                        '個人Bonus得分': row['Bonus總得分'] * (row['期間1分數'] / row['total']) if row['total'] > 0 else 0,
                        '個人Bonus次數': row['Bonus總次數'] * (row['期間1分數'] / row['total']) if row['total'] > 0 else 0,
                        '參加社團得分': row['社團總得分'] * (row['期間1分數'] / row['total']) if row['total'] > 0 else 0,
                        '參加社團次數': row['社團總次數'] * (row['期間1分數'] / row['total']) if row['total'] > 0 else 0,
                    }
                    period_data.append(period_row)

                # 期間2資料
                if row['期間2分數'] > 0:
                    period_row = {
                        'id': row['id'],
                        '姓名': row['姓名'],
                        '回合期間': '0831-0921',
                        '日常運動得分': row['運動總得分'] * (row['期間2分數'] / row['total']) if row['total'] > 0 else 0,
                        '日常運動次數': row['運動總次數'] * (row['期間2分數'] / row['total']) if row['total'] > 0 else 0,
                        '飲食得分': row['飲食總得分'] * (row['期間2分數'] / row['total']) if row['total'] > 0 else 0,
                        '飲食次數': row['飲食總次數'] * (row['期間2分數'] / row['total']) if row['total'] > 0 else 0,
                        '個人Bonus得分': row['Bonus總得分'] * (row['期間2分數'] / row['total']) if row['total'] > 0 else 0,
                        '個人Bonus次數': row['Bonus總次數'] * (row['期間2分數'] / row['total']) if row['total'] > 0 else 0,
                        '參加社團得分': row['社團總得分'] * (row['期間2分數'] / row['total']) if row['total'] > 0 else 0,
                        '參加社團次數': row['社團總次數'] * (row['期間2分數'] / row['total']) if row['total'] > 0 else 0,
                    }
                    period_data.append(period_row)

            self.participant_stats = pd.DataFrame(period_data)
            self.club_details = self.processor.club_details
            print(f"活動分析器載入完成，分析 {len(self.participant_stats) if self.participant_stats is not None else 0} 筆期間資料")
    
    def get_overall_statistics(self):
        """取得整體活動統計"""
        if self.participant_stats is None:
            return {
                'exercise': {'total_count': 0, 'participants': 0},
                'diet': {'total_count': 0, 'participants': 0},
                'bonus': {'total_count': 0, 'participants': 0},
                'club': {'total_activities': 0, 'participants': 0}
            }
        
        # 按姓名聚合統計
        stats_by_person = self.participant_stats.groupby('姓名').agg({
            '日常運動次數': 'sum',
            '飲食次數': 'sum',
            '個人Bonus次數': 'sum',
            '參加社團次數': 'sum'
        }).reset_index()
        
        # 計算有參與各活動的人數
        exercise_participants = len(stats_by_person[stats_by_person['日常運動次數'] > 0])
        diet_participants = len(stats_by_person[stats_by_person['飲食次數'] > 0])
        bonus_participants = len(stats_by_person[stats_by_person['個人Bonus次數'] > 0])
        club_participants = len(stats_by_person[stats_by_person['參加社團次數'] > 0])
        
        return {
            'exercise': {
                'total_count': int(stats_by_person['日常運動次數'].sum()),
                'participants': exercise_participants
            },
            'diet': {
                'total_count': int(stats_by_person['飲食次數'].sum()),
                'participants': diet_participants
            },
            'bonus': {
                'total_count': int(stats_by_person['個人Bonus次數'].sum()),
                'participants': bonus_participants
            },
            'club': {
                'total_activities': int(stats_by_person['參加社團次數'].sum()),
                'participants': club_participants
            }
        }
    
    def get_person_details(self, name):
        """取得個人詳細資料"""
        if self.participant_stats is None:
            return None
        
        # 取得該人的所有期間資料
        person_data = self.participant_stats[self.participant_stats['姓名'] == name]
        
        if person_data.empty:
            return None
        
        # 聚合所有期間的資料
        exercise_total_count = person_data['日常運動次數'].sum()
        exercise_total_score = person_data['日常運動得分'].sum()
        
        diet_total_count = person_data['飲食次數'].sum()
        diet_total_score = person_data['飲食得分'].sum()
        
        bonus_total_count = person_data['個人Bonus次數'].sum()
        bonus_total_score = person_data['個人Bonus得分'].sum()
        
        club_total_count = person_data['參加社團次數'].sum()
        club_total_score = person_data['參加社團得分'].sum()
        
        # 取得社團活動詳細列表
        club_activities = []
        if self.club_details is not None:
            person_club = self.club_details[self.club_details['姓名'] == name]
            club_activities = person_club['參加社團'].tolist() if not person_club.empty else []

        club_activity_list = [f"{activity}" if isinstance(activity, str) else str(activity) 
                             for activity in club_activities]
        
        return {
            'exercise': {
                'total_count': exercise_total_count,
                'total_score': exercise_total_score
            },
            'diet': {
                'total_count': diet_total_count,
                'total_score': diet_total_score
            },
            'bonus': {
                'total_count': bonus_total_count,
                'total_score': bonus_total_score
            },
            'club': {
                'total_count': club_total_count,
                'total_score': club_total_score,
                'total_activities': club_activity_list
            }
        }
    
    def get_detailed_data(self):
        """取得詳細資料字典（保持與舊介面的相容性）"""
        if self.participant_stats is None:
            return {}
        
        detailed_data = defaultdict(lambda: {
            'exercise': {'scores': [], 'counts': [], 'total_score': 0, 'total_count': 0},
            'diet': {'scores': [], 'counts': [], 'total_score': 0, 'total_count': 0},
            'bonus': {'scores': [], 'counts': [], 'total_score': 0, 'total_count': 0},
            'club': {'scores': [], 'activities': [], 'total_score': 0, 'total_count': 0},
            'periods': {},
            'total_score': 0
        })
        
        # 按姓名分組處理
        for name, group in self.participant_stats.groupby('姓名'):
            person_data = detailed_data[name]
            
            for _, row in group.iterrows():
                period = row['回合期間']
                
                # 記錄期間資料
                person_data['periods'][period] = {
                    'range': period,
                    'data': {
                        'exercise': {'score': row['日常運動得分'], 'count': row['日常運動次數']},
                        'diet': {'score': row['飲食得分'], 'count': row['飲食次數']},
                        'bonus': {'score': row['個人Bonus得分'], 'count': row['個人Bonus次數']},
                        'club': {'score': row['參加社團得分'], 'activities': row['社團活動明細'] or []}
                    }
                }
                
                # 累積資料
                person_data['exercise']['scores'].append(row['日常運動得分'])
                person_data['exercise']['counts'].append(row['日常運動次數'])
                
                person_data['diet']['scores'].append(row['飲食得分'])
                person_data['diet']['counts'].append(row['飲食次數'])
                
                person_data['bonus']['scores'].append(row['個人Bonus得分'])
                person_data['bonus']['counts'].append(row['個人Bonus次數'])
                
                person_data['club']['scores'].append(row['參加社團得分'])
                if row['社團活動明細']:
                    person_data['club']['activities'].extend(row['社團活動明細'])
            
            # 計算總計
            person_data['exercise']['total_score'] = sum(person_data['exercise']['scores'])
            person_data['exercise']['total_count'] = sum(person_data['exercise']['counts'])
            
            person_data['diet']['total_score'] = sum(person_data['diet']['scores'])
            person_data['diet']['total_count'] = sum(person_data['diet']['counts'])
            
            person_data['bonus']['total_score'] = sum(person_data['bonus']['scores'])
            person_data['bonus']['total_count'] = sum(person_data['bonus']['counts'])
            
            person_data['club']['total_score'] = sum(person_data['club']['scores'])
            person_data['club']['total_count'] = len(person_data['club']['activities'])
            
            person_data['total_score'] = (person_data['exercise']['total_score'] +
                                        person_data['diet']['total_score'] +
                                        person_data['bonus']['total_score'] +
                                        person_data['club']['total_score'])
        
        return dict(detailed_data)
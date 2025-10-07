"""
產生正確的活動統計分析報告
修復個人查詢頁面的計算錯誤
"""

import pandas as pd
import os
from collections import defaultdict

class ActivityReportGenerator:
    """活動統計報告產生器"""
    
    def __init__(self):
        self.file_paths = [
            'data/20250903分數累積表(0808-0830).xlsx',
            'data/20250905分數累積表(0831-0920).xlsx'
        ]
        self.detailed_data = defaultdict(lambda: {
            'exercise': {'scores': [], 'counts': [], 'total_score': 0, 'total_count': 0},
            'diet': {'scores': [], 'counts': [], 'total_score': 0, 'total_count': 0},
            'bonus': {'scores': [], 'counts': [], 'total_score': 0, 'total_count': 0},
            'club': {'scores': [], 'activities': [], 'total_score': 0, 'total_count': 0},
            'periods': {},
            'total_score': 0
        })
        
    def analyze_files(self):
        """分析所有檔案"""
        print("開始分析活動數據...")
        
        for i, file_path in enumerate(self.file_paths):
            period_name = f"期間{i+1}"
            period_range = "8/8-8/30" if i == 0 else "8/31-9/20"
            
            if os.path.exists(file_path):
                print(f"分析 {period_name} ({period_range}): {file_path}")
                self.analyze_single_file(file_path, period_name, period_range)
            else:
                print(f"找不到檔案: {file_path}")
        
        # 計算總分
        self.calculate_totals()
        print(f"分析完成，共處理 {len(self.detailed_data)} 位參賽者")
        
    def analyze_single_file(self, file_path, period_name, period_range):
        """分析單一檔案"""
        try:
            # 讀取分數累積表
            score_df = pd.read_excel(file_path, sheet_name='分數累積')
            
            # 讀取活動統計表（用於取得次數）
            activity_df = None
            try:
                activity_df = pd.read_excel(file_path, sheet_name='ALL活動數據統計(運動+飲食)--分數計算表')
            except:
                print(f"  警告: {period_name} 無法載入活動統計表")
            
            # 讀取bonus表
            bonus_df = None
            try:
                bonus_df = pd.read_excel(file_path, sheet_name='個人bonus分')
            except:
                print(f"  警告: {period_name} 無法載入bonus表")
            
            # 處理每位參賽者
            for _, row in score_df.iterrows():
                if len(row) <= 4 or pd.isna(row.iloc[4]):  # 檢查長度並確保E欄是姓名
                    continue
                    
                name = row.iloc[4]
                person_data = self.analyze_person_in_period(row, activity_df, bonus_df, period_name)
                
                # 記錄期間資料
                self.detailed_data[name]['periods'][period_name] = {
                    'range': period_range,
                    'data': person_data
                }
                
                # 累積資料
                self.detailed_data[name]['exercise']['scores'].append(person_data['exercise']['score'])
                self.detailed_data[name]['exercise']['counts'].append(person_data['exercise']['count'])
                
                self.detailed_data[name]['diet']['scores'].append(person_data['diet']['score'])
                self.detailed_data[name]['diet']['counts'].append(person_data['diet']['count'])
                
                self.detailed_data[name]['bonus']['scores'].append(person_data['bonus']['score'])
                self.detailed_data[name]['bonus']['counts'].append(person_data['bonus']['count'])
                
                self.detailed_data[name]['club']['scores'].append(person_data['club']['score'])
                self.detailed_data[name]['club']['activities'].extend(person_data['club']['activities'])
                
        except Exception as e:
            print(f"  錯誤: 處理 {period_name} 時發生錯誤: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def analyze_person_in_period(self, score_row, activity_df, bonus_df, period_name):
        """分析個人在特定期間的資料"""
        name = score_row.iloc[4]
        
        # 從分數累積表讀取實際分數
        exercise_score = score_row.iloc[10] if len(score_row) > 10 and pd.notna(score_row.iloc[10]) else 0
        diet_score = score_row.iloc[11] if len(score_row) > 11 and pd.notna(score_row.iloc[11]) else 0
        
        # 從活動統計表取得次數
        exercise_count = 0
        diet_count = 0
        if activity_df is not None:
            person_activity = activity_df[activity_df.iloc[:, 4] == name]  # E欄是姓名
            if not person_activity.empty:
                exercise_count = person_activity.iloc[0, 6] if len(person_activity.iloc[0]) > 6 and pd.notna(person_activity.iloc[0, 6]) else 0  # G欄運動次數
                diet_count = person_activity.iloc[0, 7] if len(person_activity.iloc[0]) > 7 and pd.notna(person_activity.iloc[0, 7]) else 0  # H欄飲食次數
        else:
            # 從分數推算次數
            exercise_count = int(exercise_score / 10) if exercise_score > 0 else 0
            diet_count = int(diet_score / 10) if diet_score > 0 else 0
        
        # 處理bonus分數和次數
        bonus_score = 0
        bonus_count = 0
        if bonus_df is not None:
            person_bonus = bonus_df[bonus_df.iloc[:, 4] == name]  # E欄是姓名
            if not person_bonus.empty:
                bonus_score = person_bonus.iloc[0, 5] if len(person_bonus.iloc[0]) > 5 and pd.notna(person_bonus.iloc[0, 5]) else 0  # F欄bonus分數
                bonus_count = int(bonus_score / 30) if bonus_score > 0 else 0
        else:
            # 從分數累積表讀取
            bonus_score = score_row.iloc[12] if len(score_row) > 12 and pd.notna(score_row.iloc[12]) else 0
            bonus_count = int(bonus_score / 30) if bonus_score > 0 else 0
        
        # 處理社團活動
        club_score = 0
        club_activities = []
        
        # 從N欄開始到total前的所有社團活動
        total_col_idx = None
        for i, col_name in enumerate(score_row.index):
            if 'total' in str(col_name).lower():
                total_col_idx = i
                break
        
        if total_col_idx:
            for i in range(13, total_col_idx):  # 從N欄(索引13)開始
                if i < len(score_row):
                    activity_score = score_row.iloc[i]
                    if pd.notna(activity_score) and activity_score > 0:
                        club_score += activity_score
                        activity_name = score_row.index[i]
                        club_activities.append(f"{activity_name}: {activity_score}分")
        
        return {
            'exercise': {'score': exercise_score, 'count': exercise_count},
            'diet': {'score': diet_score, 'count': diet_count},
            'bonus': {'score': bonus_score, 'count': bonus_count},
            'club': {'score': club_score, 'activities': club_activities}
        }
    
    def calculate_totals(self):
        """計算每人的總計數據"""
        for name, data in self.detailed_data.items():
            # 計算各類別總計
            data['exercise']['total_score'] = sum(data['exercise']['scores'])
            data['exercise']['total_count'] = sum(data['exercise']['counts'])
            
            data['diet']['total_score'] = sum(data['diet']['scores'])
            data['diet']['total_count'] = sum(data['diet']['counts'])
            
            data['bonus']['total_score'] = sum(data['bonus']['scores'])
            data['bonus']['total_count'] = sum(data['bonus']['counts'])
            
            data['club']['total_score'] = sum(data['club']['scores'])
            data['club']['total_count'] = len(data['club']['activities'])
            
            # 計算總分
            data['total_score'] = (data['exercise']['total_score'] + 
                                 data['diet']['total_score'] + 
                                 data['bonus']['total_score'] + 
                                 data['club']['total_score'])
    
    def generate_report(self, output_file='data/活動統計分析報告.xlsx'):
        """產生Excel報告"""
        print(f"正在產生報告: {output_file}")
        
        # 準備個人總計資料
        summary_data = []
        for name, data in self.detailed_data.items():
            summary_data.append({
                '姓名': name,
                '運動總次數': data['exercise']['total_count'],
                '運動總得分': data['exercise']['total_score'],
                '飲食總次數': data['diet']['total_count'],
                '飲食總得分': data['diet']['total_score'],
                'Bonus總次數': data['bonus']['total_count'],
                'Bonus總得分': data['bonus']['total_score'],
                '社團總次數': data['club']['total_count'],
                '社團總得分': data['club']['total_score'],
                '計算總分': data['total_score']
            })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df = summary_df.sort_values('計算總分', ascending=False)
        
        # 準備期間明細資料
        period_detail_data = []
        for name, data in self.detailed_data.items():
            for period, period_info in data['periods'].items():
                period_data = period_info['data']
                period_detail_data.append({
                    '姓名': name,
                    '期間': period,
                    '期間範圍': period_info['range'],
                    '運動次數': period_data['exercise']['count'],
                    '運動得分': period_data['exercise']['score'],
                    '飲食次數': period_data['diet']['count'],
                    '飲食得分': period_data['diet']['score'],
                    'Bonus次數': period_data['bonus']['count'],
                    'Bonus得分': period_data['bonus']['score'],
                    '社團次數': len(period_data['club']['activities']),
                    '社團得分': period_data['club']['score'],
                    '期間小計': (period_data['exercise']['score'] + 
                                period_data['diet']['score'] + 
                                period_data['bonus']['score'] + 
                                period_data['club']['score'])
                })
        
        period_detail_df = pd.DataFrame(period_detail_data)
        
        # 準備社團活動明細
        club_detail_data = []
        for name, data in self.detailed_data.items():
            for activity in data['club']['activities']:
                club_detail_data.append({
                    '姓名': name,
                    '社團活動詳情': activity
                })
        
        club_detail_df = pd.DataFrame(club_detail_data)
        
        # 寫入Excel
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            summary_df.to_excel(writer, sheet_name='個人總計統計', index=False)
            period_detail_df.to_excel(writer, sheet_name='期間明細統計', index=False)
            club_detail_df.to_excel(writer, sheet_name='社團活動明細', index=False)
        
        print(f"報告已產生: {output_file}")
        return output_file


if __name__ == "__main__":
    generator = ActivityReportGenerator()
    generator.analyze_files()
    output_file = generator.generate_report()
    print(f"\n活動統計分析報告已產生: {output_file}")
    
    # 顯示前5名的統計摘要
    print("\n前5名統計摘要:")
    summary_data = []
    for name, data in list(generator.detailed_data.items())[:5]:
        summary_data.append([
            name,
            data['exercise']['total_count'],
            data['exercise']['total_score'],
            data['diet']['total_count'],
            data['diet']['total_score'], 
            data['bonus']['total_count'],
            data['bonus']['total_score'],
            data['club']['total_count'],
            data['club']['total_score'],
            data['total_score']
        ])
    
    summary_df = pd.DataFrame(summary_data, columns=[
        '姓名', '運動次數', '運動得分', '飲食次數', '飲食得分', 
        'Bonus次數', 'Bonus得分', '社團次數', '社團得分', '總分'
    ])
    summary_df = summary_df.sort_values('總分', ascending=False)
    print(summary_df.head().to_string(index=False))
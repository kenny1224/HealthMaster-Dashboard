"""
產生完整的活動統計分析報告
正確合併所有期間的資料，提供準確的統計數據
"""

import pandas as pd
import os
from collections import defaultdict

class CompleteActivityReportGenerator:
    """完整活動統計報告產生器"""
    
    def __init__(self):
        self.file_paths = [
            'data/20250903分數累積表(0808-0830).xlsx',
            'data/20250905分數累積表(0831-0920).xlsx'
        ]
        self.period_names = ['期間1', '期間2']
        self.period_ranges = ['8/8-8/30', '8/31-9/20']
        
        # 儲存所有期間的原始資料
        self.raw_data = {}  # {period: {name: data}}
        
        # 儲存合併後的統計資料
        self.merged_data = defaultdict(lambda: {
            'periods': {},  # 各期間詳細資料
            'exercise': {'total_score': 0, 'total_count': 0, 'period_details': []},
            'diet': {'total_score': 0, 'total_count': 0, 'period_details': []},
            'bonus': {'total_score': 0, 'total_count': 0, 'period_details': []},
            'club': {'total_score': 0, 'total_count': 0, 'activities': []},
            'excel_total_scores': [],  # 各期間Excel的total分數
            'calculated_total': 0,     # 計算出的總分
            'excel_total': 0          # Excel總分
        })
        
    def analyze_all_files(self):
        """分析所有檔案"""
        print("開始完整分析所有期間資料...")
        
        # 第一步：載入各期間原始資料
        for i, file_path in enumerate(self.file_paths):
            period_name = self.period_names[i]
            period_range = self.period_ranges[i]
            
            if os.path.exists(file_path):
                print(f"\n=== 分析 {period_name} ({period_range}) ===")
                print(f"檔案: {file_path}")
                self.analyze_period_file(file_path, period_name, period_range, i)
            else:
                print(f"❌ 找不到檔案: {file_path}")
        
        # 第二步：合併各期間資料
        print(f"\n=== 合併各期間資料 ===")
        self.merge_all_periods()
        
        print(f"完整分析完成，共處理 {len(self.merged_data)} 位參賽者")
        
    def analyze_period_file(self, file_path, period_name, period_range, period_index):
        """分析單一期間檔案"""
        period_data = {}
        
        try:
            # 讀取分數累積表
            print(f"  讀取分數累積表...")
            score_df = pd.read_excel(file_path, sheet_name='分數累積')
            print(f"  - 分數累積表: {len(score_df)} 行資料")
            
            # 讀取活動統計表
            activity_df = None
            try:
                activity_df = pd.read_excel(file_path, sheet_name='ALL活動數據統計(運動+飲食)--分數計算表')
                print(f"  - 活動統計表: {len(activity_df)} 行資料")
            except:
                print(f"  - 活動統計表: 無法載入")
            
            # 讀取bonus表
            bonus_df = None
            try:
                bonus_df = pd.read_excel(file_path, sheet_name='個人bonus分')
                print(f"  - bonus表: {len(bonus_df)} 行資料")
            except:
                print(f"  - bonus表: 無法載入")
            
            # 處理每位參賽者
            processed_count = 0
            for idx, row in score_df.iterrows():
                if len(row) <= 4 or pd.isna(row.iloc[4]):
                    continue
                
                name = str(row.iloc[4]).strip()
                if not name or name == 'nan':
                    continue
                
                # 分析該參賽者在此期間的資料
                person_data = self.analyze_person_in_period(
                    row, activity_df, bonus_df, period_name, score_df.columns
                )
                
                if person_data:
                    period_data[name] = person_data
                    processed_count += 1
            
            print(f"  成功處理 {processed_count} 位參賽者")
            self.raw_data[period_name] = period_data
            
        except Exception as e:
            print(f"  處理檔案時發生錯誤: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def analyze_person_in_period(self, score_row, activity_df, bonus_df, period_name, columns):
        """分析個人在特定期間的詳細資料"""
        try:
            name = str(score_row.iloc[4]).strip()
            
            # 從分數累積表取得各項目分數
            exercise_score = self.safe_get_value(score_row, 10, 0)  # K欄運動分數
            diet_score = self.safe_get_value(score_row, 11, 0)      # L欄飲食分數
            bonus_score = self.safe_get_value(score_row, 12, 0)     # M欄bonus分數
            
            # 從Excel中讀取該期間的total分數
            excel_total = 0
            for i, col_name in enumerate(columns):
                if 'total' in str(col_name).lower():
                    excel_total = self.safe_get_value(score_row, i, 0)
                    break
            
            # 從活動統計表取得次數
            exercise_count = 0
            diet_count = 0
            if activity_df is not None:
                person_activity = activity_df[activity_df.iloc[:, 4].astype(str).str.strip() == name]
                if not person_activity.empty:
                    exercise_count = self.safe_get_value(person_activity.iloc[0], 6, 0)  # G欄運動次數
                    diet_count = self.safe_get_value(person_activity.iloc[0], 7, 0)     # H欄飲食次數
            
            # 如果沒有活動統計表，從分數推算次數
            if exercise_count == 0 and exercise_score > 0:
                exercise_count = int(exercise_score / 10)
            if diet_count == 0 and diet_score > 0:
                diet_count = int(diet_score / 10)
            
            # 計算bonus次數
            bonus_count = int(bonus_score / 30) if bonus_score > 0 else 0
            
            # 分析社團活動（從N欄開始到total前）
            club_score = 0
            club_activities = []
            total_col_idx = None
            
            for i, col_name in enumerate(columns):
                if 'total' in str(col_name).lower():
                    total_col_idx = i
                    break
            
            if total_col_idx and total_col_idx > 13:
                for i in range(13, total_col_idx):  # 從N欄(索引13)開始
                    if i < len(score_row):
                        activity_score = self.safe_get_value(score_row, i, 0)
                        if activity_score > 0:
                            club_score += activity_score
                            activity_name = str(columns[i])
                            club_activities.append(f"{activity_name}({activity_score}分)")
            
            club_count = len(club_activities)
            
            return {
                'exercise': {'score': exercise_score, 'count': exercise_count},
                'diet': {'score': diet_score, 'count': diet_count},
                'bonus': {'score': bonus_score, 'count': bonus_count},
                'club': {'score': club_score, 'count': club_count, 'activities': club_activities},
                'excel_total': excel_total,
                'calculated_subtotal': exercise_score + diet_score + bonus_score + club_score
            }
            
        except Exception as e:
            print(f"    分析 {name} 時發生錯誤: {str(e)}")
            return None
    
    def safe_get_value(self, row_or_series, index, default=0):
        """安全取得數值"""
        try:
            if len(row_or_series) > index:
                value = row_or_series.iloc[index] if hasattr(row_or_series, 'iloc') else row_or_series[index]
                if pd.isna(value):
                    return default
                return float(value) if value != '' else default
            return default
        except:
            return default
    
    def merge_all_periods(self):
        """合併所有期間的資料"""
        print("  正在合併各期間資料...")
        
        # 收集所有參賽者姓名
        all_names = set()
        for period_data in self.raw_data.values():
            all_names.update(period_data.keys())
        
        print(f"  發現 {len(all_names)} 位參賽者")
        
        # 為每位參賽者合併資料
        for name in all_names:
            person_merged = self.merged_data[name]
            
            # 合併各期間資料
            for period_name in self.period_names:
                if period_name in self.raw_data and name in self.raw_data[period_name]:
                    period_data = self.raw_data[period_name][name]
                    period_name_index = self.period_names.index(period_name)
                    period_range = self.period_ranges[period_name_index]
                    
                    # 記錄期間資料
                    person_merged['periods'][period_name] = {
                        'range': period_range,
                        'data': period_data
                    }
                    
                    # 累加分數和次數
                    person_merged['exercise']['total_score'] += period_data['exercise']['score']
                    person_merged['exercise']['total_count'] += period_data['exercise']['count']
                    person_merged['exercise']['period_details'].append({
                        'period': period_name,
                        'range': period_range,
                        'score': period_data['exercise']['score'],
                        'count': period_data['exercise']['count']
                    })
                    
                    person_merged['diet']['total_score'] += period_data['diet']['score']
                    person_merged['diet']['total_count'] += period_data['diet']['count']
                    person_merged['diet']['period_details'].append({
                        'period': period_name,
                        'range': period_range,
                        'score': period_data['diet']['score'],
                        'count': period_data['diet']['count']
                    })
                    
                    person_merged['bonus']['total_score'] += period_data['bonus']['score']
                    person_merged['bonus']['total_count'] += period_data['bonus']['count']
                    person_merged['bonus']['period_details'].append({
                        'period': period_name,
                        'range': period_range,
                        'score': period_data['bonus']['score'],
                        'count': period_data['bonus']['count']
                    })
                    
                    person_merged['club']['total_score'] += period_data['club']['score']
                    person_merged['club']['total_count'] += period_data['club']['count']
                    person_merged['club']['activities'].extend(period_data['club']['activities'])
                    
                    # 記錄Excel總分
                    person_merged['excel_total_scores'].append(period_data['excel_total'])
            
            # 計算最終總分
            person_merged['calculated_total'] = (
                person_merged['exercise']['total_score'] +
                person_merged['diet']['total_score'] +
                person_merged['bonus']['total_score'] +
                person_merged['club']['total_score']
            )
            
            person_merged['excel_total'] = sum(person_merged['excel_total_scores'])
    
    def generate_complete_report(self, output_file='data/活動統計分析報告.xlsx'):
        """產生完整報告"""
        print(f"\n=== 產生完整統計報告 ===")
        print(f"輸出檔案: {output_file}")
        
        # 1. 個人總計統計
        summary_data = []
        for name, data in self.merged_data.items():
            summary_data.append({
                '姓名': name,
                '運動總次數': int(data['exercise']['total_count']),
                '運動總得分': int(data['exercise']['total_score']),
                '飲食總次數': int(data['diet']['total_count']),
                '飲食總得分': int(data['diet']['total_score']),
                'Bonus總次數': int(data['bonus']['total_count']),
                'Bonus總得分': int(data['bonus']['total_score']),
                '社團總次數': int(data['club']['total_count']),
                '社團總得分': int(data['club']['total_score']),
                '活動計算總分': int(data['calculated_total']),
                'Excel總分': int(data['excel_total']),
                '差異': int(data['excel_total'] - data['calculated_total'])
            })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df = summary_df.sort_values('Excel總分', ascending=False)
        
        # 2. 各期間明細統計
        period_details = []
        for name, data in self.merged_data.items():
            for period_name in self.period_names:
                if period_name in data['periods']:
                    period_data = data['periods'][period_name]['data']
                    period_range = data['periods'][period_name]['range']
                    
                    period_details.append({
                        '姓名': name,
                        '期間': period_name,
                        '期間範圍': period_range,
                        '運動次數': int(period_data['exercise']['count']),
                        '運動得分': int(period_data['exercise']['score']),
                        '飲食次數': int(period_data['diet']['count']),
                        '飲食得分': int(period_data['diet']['score']),
                        'Bonus次數': int(period_data['bonus']['count']),
                        'Bonus得分': int(period_data['bonus']['score']),
                        '社團次數': int(period_data['club']['count']),
                        '社團得分': int(period_data['club']['score']),
                        '期間計算總分': int(period_data['calculated_subtotal']),
                        '期間Excel總分': int(period_data['excel_total']),
                        '期間差異': int(period_data['excel_total'] - period_data['calculated_subtotal'])
                    })
        
        period_df = pd.DataFrame(period_details)
        period_df = period_df.sort_values(['姓名', '期間'])
        
        # 3. 社團活動明細
        club_details = []
        for name, data in self.merged_data.items():
            for activity in data['club']['activities']:
                club_details.append({
                    '姓名': name,
                    '社團活動': activity
                })
        
        club_df = pd.DataFrame(club_details)
        
        # 4. 統計摘要
        total_participants = len(self.merged_data)
        total_excel_score = sum(data['excel_total'] for data in self.merged_data.values())
        total_calculated_score = sum(data['calculated_total'] for data in self.merged_data.values())
        differences = [abs(data['excel_total'] - data['calculated_total']) for data in self.merged_data.values()]
        max_difference = max(differences) if differences else 0
        
        stats_data = [{
            '統計項目': '參賽者總數',
            '數值': total_participants
        }, {
            '統計項目': 'Excel總分合計',
            '數值': int(total_excel_score)
        }, {
            '統計項目': '計算總分合計',
            '數值': int(total_calculated_score)
        }, {
            '統計項目': '總差異',
            '數值': int(total_excel_score - total_calculated_score)
        }, {
            '統計項目': '最大個人差異',
            '數值': int(max_difference)
        }]
        
        stats_df = pd.DataFrame(stats_data)
        
        # 寫入Excel
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            summary_df.to_excel(writer, sheet_name='個人總計統計', index=False)
            period_df.to_excel(writer, sheet_name='各期間明細統計', index=False)
            club_df.to_excel(writer, sheet_name='社團活動明細', index=False)
            stats_df.to_excel(writer, sheet_name='統計摘要', index=False)
        
        print(f"完整報告已產生")
        print(f"   - 個人總計統計: {len(summary_df)} 位參賽者")
        print(f"   - 各期間明細統計: {len(period_df)} 筆記錄")
        print(f"   - 社團活動明細: {len(club_df)} 筆記錄")
        print(f"   - 統計摘要: {len(stats_df)} 項統計")
        
        return output_file, summary_df


if __name__ == "__main__":
    print("開始產生完整活動統計分析報告...")
    
    generator = CompleteActivityReportGenerator()
    generator.analyze_all_files()
    output_file, summary_df = generator.generate_complete_report()
    
    print(f"\n📊 報告產生完成: {output_file}")
    
    # 顯示莊依靜的統計作為驗證
    chuang_data = summary_df[summary_df['姓名'].str.contains('莊依靜', na=False)]
    if not chuang_data.empty:
        print(f"\n=== 莊依靜統計驗證 ===")
        chuang = chuang_data.iloc[0]
        print(f"運動: {chuang['運動總次數']}次 {chuang['運動總得分']}分")
        print(f"飲食: {chuang['飲食總次數']}次 {chuang['飲食總得分']}分")
        print(f"Bonus: {chuang['Bonus總次數']}次 {chuang['Bonus總得分']}分")
        print(f"社團: {chuang['社團總次數']}次 {chuang['社團總得分']}分")
        print(f"活動計算總分: {chuang['活動計算總分']}")
        print(f"Excel總分: {chuang['Excel總分']}")
        print(f"差異: {chuang['差異']}")
    
    print(f"\n完成！您現在可以使用 {output_file} 來核對儀表板數字")
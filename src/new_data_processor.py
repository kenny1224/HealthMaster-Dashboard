"""
新的資料處理程式
處理「每周分數累積.xlsx」並生成「參加者活動統計表.xlsx」
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os


class NewDataProcessor:
    """新的資料處理器"""

    def __init__(self, excel_path='data/每周分數累積.xlsx'):
        """初始化"""
        # 取得專案根目錄
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)

        if not os.path.isabs(excel_path):
            self.excel_path = os.path.join(project_root, excel_path)
        else:
            self.excel_path = excel_path

        self.period_data = {}  # 儲存各期間資料
        self.club_details = None  # 社團活動明細表
        self.participant_stats = None  # 參加者活動統計表
        self.account_info = None  # 帳號整理資料

    def load_account_info(self):
        """載入帳號整理資料"""
        try:
            df = pd.read_excel(self.excel_path, sheet_name='帳號整理')
            # 使用「帳號(最新8/8)2」作為key
            if '帳號(最新8/8)2' in df.columns:
                df = df.set_index('帳號(最新8/8)2')
            self.account_info = df
            print(f"帳號整理載入完成：{len(df)} 筆")
            return df
        except Exception as e:
            print(f"載入帳號整理失敗：{str(e)}")
            return None

    def load_period_data(self, sheet_name):
        """載入期間工作表資料"""
        try:
            df = pd.read_excel(self.excel_path, sheet_name=sheet_name)

            # 確認必要欄位存在
            required_cols = ['id', '姓名']
            for col in required_cols:
                if col not in df.columns:
                    print(f"警告：{sheet_name} 缺少必要欄位 {col}")
                    return None

            # 儲存期間資料
            self.period_data[sheet_name] = df
            print(f"{sheet_name} 載入完成：{len(df)} 筆資料")
            return df

        except Exception as e:
            print(f"載入 {sheet_name} 失敗：{str(e)}")
            return None

    def extract_score_and_count(self, df, sheet_name):
        """從期間資料提取分數與次數

        A. 計算分數邏輯：
        1. 日常運動得分 ÷ 10 = 日常運動次數
        2. 飲食得分 ÷ 10 = 飲食次數
        3. 個人Bonus得分 ÷ 30 = 個人Bonus次數
        """
        results = []

        for _, row in df.iterrows():
            # 找出運動、飲食、Bonus欄位
            exercise_col = None
            diet_col = None
            bonus_col = None

            # 尋找欄位（支援不同期間的欄位名稱）
            for col in df.columns:
                if '日常運動' in col or '運動' in col:
                    exercise_col = col
                    break

            for col in df.columns:
                if '飲食' in col:
                    diet_col = col
                    break

            for col in df.columns:
                if 'bonus' in col.lower() or 'Bonus' in col:
                    bonus_col = col
                    break

            # 計算分數與次數
            exercise_score = row[exercise_col] if exercise_col and pd.notna(row[exercise_col]) else 0
            diet_score = row[diet_col] if diet_col and pd.notna(row[diet_col]) else 0
            bonus_score = row[bonus_col] if bonus_col and pd.notna(row[bonus_col]) else 0

            # 計算次數
            exercise_count = int(exercise_score / 10) if exercise_score > 0 else 0
            diet_count = int(diet_score / 10) if diet_score > 0 else 0
            bonus_count = int(bonus_score / 30) if bonus_score > 0 else 0

            result = {
                'id': row['id'],
                '姓名': row['姓名'],
                '回合期間': sheet_name,
                '日常運動得分': exercise_score,
                '日常運動次數': exercise_count,
                '飲食得分': diet_score,
                '飲食次數': diet_count,
                '個人Bonus得分': bonus_score,
                '個人Bonus次數': bonus_count
            }

            results.append(result)

        return pd.DataFrame(results)

    def transform_club_activities(self, df, sheet_name):
        """將社團活動從Wide轉換為Long格式

        B2. 社團活動Wide to Long轉換：
        - 找出O欄開始到total欄前的所有社團活動欄位
        - 解析欄位名稱取得日期和社團名稱
        - 轉換日期格式（預設年份2025）
        """
        club_records = []

        # 找出社團活動欄位（從個人bonus分之後到total之前）
        activity_cols = []
        start_collecting = False

        for col in df.columns:
            if 'bonus' in col.lower():
                start_collecting = True
                continue
            if col == 'total':
                break
            if start_collecting and col not in ['id', '姓名', '性別', '所屬公司', '所屬部門']:
                # 所有bonus之後、total之前的欄位都視為社團活動
                activity_cols.append(col)

        print(f"{sheet_name} 找到 {len(activity_cols)} 個社團活動欄位")

        # 處理每個參加者
        for _, row in df.iterrows():
            for col in activity_cols:
                score = row[col] if pd.notna(row[col]) else 0

                # 只記錄有分數的活動
                if score > 0:
                    # 解析欄位名稱：例如 "8/13 羽球社" 或 "9/2 桌球社挑戰賽" 或 "人資講座"
                    date_str, club_name = self._parse_activity_column(col, sheet_name)

                    club_records.append({
                        'id': row['id'],
                        '姓名': row['姓名'],
                        '回合期間': sheet_name,
                        '社團活動日期': date_str,
                        '參加社團': club_name,
                        '得分': score
                    })

        return pd.DataFrame(club_records)

    def _parse_activity_column(self, col_name, sheet_name):
        """解析社團活動欄位名稱

        例如：
        - "8/13 羽球社" → ("2025/08/13", "羽球社")
        - "9/2 桌球社挑戰賽" → ("2025/09/02", "桌球社挑戰賽")
        - "人資講座" → ("2025/08/15", "人資講座") (使用期間中間日期)
        """
        # 分割日期和社團名稱
        parts = col_name.split(' ', 1)

        if len(parts) >= 2:
            date_part = parts[0].strip()
            club_name = parts[1].strip()
        else:
            # 如果沒有空格分隔（如"人資講座"），使用整個欄位名稱
            date_part = None
            club_name = col_name

        # 解析日期（預設年份2025）
        try:
            # 處理 "8/13" 或 "9/2" 格式
            if date_part and '/' in date_part:
                month, day = date_part.split('/')
                # 轉換為標準日期格式
                date_obj = datetime(2025, int(month), int(day))
                date_str = date_obj.strftime('%Y/%m/%d')
            else:
                # 如果沒有日期，根據活動名稱使用特定日期
                if club_name == '人資講座':
                    date_str = '2025/08/08'
                elif sheet_name == '0808-0830':
                    date_str = '2025/08/15'
                elif sheet_name == '0831-0921':
                    date_str = '2025/09/10'
                else:
                    date_str = sheet_name
        except:
            # 解析失敗時使用期間日期
            if club_name == '人資講座':
                date_str = '2025/08/08'
            elif sheet_name == '0808-0830':
                date_str = '2025/08/15'
            elif sheet_name == '0831-0921':
                date_str = '2025/09/10'
            else:
                date_str = sheet_name

        return date_str, club_name

    def build_participant_activity_stats(self):
        """建立參加者活動統計表

        整合：
        1. 各期間的運動、飲食、Bonus統計
        2. 社團活動統計（從明細表計算）
        """
        if not self.period_data:
            print("錯誤：請先載入期間資料")
            return None

        # Step 1: 合併各期間的基本活動統計
        all_basic_stats = []

        for sheet_name, df in self.period_data.items():
            period_stats = self.extract_score_and_count(df, sheet_name)
            all_basic_stats.append(period_stats)

        basic_stats_df = pd.concat(all_basic_stats, ignore_index=True)

        # Step 2: 計算社團活動統計
        if self.club_details is not None and not self.club_details.empty:
            # 按姓名和回合期間分組計算社團活動
            club_stats = self.club_details.groupby(['id', '姓名', '回合期間']).agg({
                '得分': 'sum',
                '參加社團': 'count'
            }).reset_index()
            club_stats.columns = ['id', '姓名', '回合期間', '參加社團得分', '參加社團次數']

            # Step 3: 合併基本統計和社團統計
            participant_stats = pd.merge(
                basic_stats_df,
                club_stats,
                on=['id', '姓名', '回合期間'],
                how='left'
            )
        else:
            # 如果沒有社團資料，直接使用基本統計
            participant_stats = basic_stats_df.copy()
            participant_stats['參加社團得分'] = 0
            participant_stats['參加社團次數'] = 0

        # 填充缺失值
        participant_stats = participant_stats.fillna(0)

        # 從帳號整理取得性別和部門資訊
        if self.account_info is not None:
            for idx, row in participant_stats.iterrows():
                participant_id = row['id']
                if participant_id in self.account_info.index:
                    # 取得性別（移除"生理"字樣）
                    gender = self.account_info.loc[participant_id, '性別'] if '性別' in self.account_info.columns else ''
                    gender = gender.replace('生理', '') if pd.notna(gender) else ''
                    participant_stats.at[idx, '性別'] = gender

                    # 取得部門
                    dept = self.account_info.loc[participant_id, '所屬部門'] if '所屬部門' in self.account_info.columns else ''
                    participant_stats.at[idx, '所屬部門'] = dept

        self.participant_stats = participant_stats
        print(f"參加者活動統計表建立完成：{len(participant_stats)} 筆資料")
        return participant_stats

    def save_participant_stats(self, output_path='data/參加者活動統計表.xlsx'):
        """儲存參加者活動統計表"""
        if self.participant_stats is None:
            print("錯誤：請先建立參加者活動統計表")
            return False

        try:
            # 取得專案根目錄
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)

            if not os.path.isabs(output_path):
                full_path = os.path.join(project_root, output_path)
            else:
                full_path = output_path

            # 按姓名彙總為儀表板格式
            dashboard_data = []

            for name, group in self.participant_stats.groupby('姓名'):
                # 基本資訊（取第一筆）
                first_row = group.iloc[0]

                # 計算總分與總次數
                row_data = {
                    'id': first_row['id'],
                    '姓名': name,
                    '性別': first_row.get('性別', ''),
                    '所屬部門': first_row.get('所屬部門', ''),
                    '運動總得分': group['日常運動得分'].sum(),
                    '運動總次數': group['日常運動次數'].sum(),
                    '飲食總得分': group['飲食得分'].sum(),
                    '飲食總次數': group['飲食次數'].sum(),
                    'Bonus總得分': group['個人Bonus得分'].sum(),
                    'Bonus總次數': group['個人Bonus次數'].sum(),
                    '社團總得分': group['參加社團得分'].sum(),
                    '社團總次數': group['參加社團次數'].sum()
                }

                # 計算total
                row_data['total'] = (row_data['運動總得分'] + row_data['飲食總得分'] +
                                    row_data['Bonus總得分'] + row_data['社團總得分'])

                # 各期間分數
                for _, period_row in group.iterrows():
                    period = period_row['回合期間']
                    period_total = (period_row['日常運動得分'] + period_row['飲食得分'] +
                                   period_row['個人Bonus得分'] + period_row['參加社團得分'])

                    if period == '0808-0830':
                        row_data['期間1分數'] = period_total
                    elif period == '0831-0921':
                        row_data['期間2分數'] = period_total

                dashboard_data.append(row_data)

            # 轉為DataFrame
            final_df = pd.DataFrame(dashboard_data)

            # 填充缺失的期間分數
            if '期間1分數' not in final_df.columns:
                final_df['期間1分數'] = 0
            if '期間2分數' not in final_df.columns:
                final_df['期間2分數'] = 0

            final_df = final_df.fillna(0)

            # 儲存
            final_df.to_excel(full_path, index=False)
            print(f"參加者活動統計表已儲存至：{full_path}")
            return True

        except Exception as e:
            print(f"儲存失敗：{str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def process_all(self):
        """執行完整的資料處理流程"""
        print("=== 開始處理資料 ===")

        # 1. 載入帳號整理
        print("\n1. 載入帳號整理...")
        self.load_account_info()

        # 2. 載入各期間資料
        print("\n2. 載入期間資料...")
        self.load_period_data('0808-0830')
        self.load_period_data('0831-0921')

        # 3. 處理社團活動明細
        print("\n3. 處理社團活動明細...")
        all_club_details = []

        for sheet_name, df in self.period_data.items():
            club_df = self.transform_club_activities(df, sheet_name)
            all_club_details.append(club_df)

        self.club_details = pd.concat(all_club_details, ignore_index=True)
        print(f"社團活動明細表建立完成：{len(self.club_details)} 筆資料")

        # 4. 建立參加者活動統計表
        print("\n4. 建立參加者活動統計表...")
        self.build_participant_activity_stats()

        # 5. 儲存結果
        print("\n5. 儲存參加者活動統計表...")
        self.save_participant_stats()

        print("\n=== 資料處理完成 ===")

        return self.participant_stats

    def get_club_activity_details(self):
        """取得社團活動明細表"""
        return self.club_details

    def validate_participant_score(self, name):
        """驗證參加者分數"""
        if self.participant_stats is None:
            print("錯誤：請先建立參加者活動統計表")
            return

        person_data = self.participant_stats[self.participant_stats['姓名'] == name]

        if person_data.empty:
            print(f"找不到 {name} 的資料")
            return

        print(f"\n=== {name} 的分數驗證 ===")

        for _, row in person_data.iterrows():
            period = row['回合期間']
            total = row['日常運動得分'] + row['飲食得分'] + row['個人Bonus得分'] + row['參加社團得分']

            print(f"\n期間：{period}")
            print(f"  日常運動：{row['日常運動得分']}分 ({row['日常運動次數']}次)")
            print(f"  飲食：{row['飲食得分']}分 ({row['飲食次數']}次)")
            print(f"  Bonus：{row['個人Bonus得分']}分 ({row['個人Bonus次數']}次)")
            print(f"  社團活動：{row['參加社團得分']}分 ({row['參加社團次數']}次)")
            print(f"  期間總分：{total}分")

        overall_total = person_data['日常運動得分'].sum() + person_data['飲食得分'].sum() + \
                       person_data['個人Bonus得分'].sum() + person_data['參加社團得分'].sum()
        print(f"\n整體總分：{overall_total}分")


if __name__ == "__main__":
    # 測試程式
    processor = NewDataProcessor()

    # 執行完整流程
    processor.process_all()

    # 驗證莊依靜的分數
    print("\n" + "="*50)
    processor.validate_participant_score('莊依靜')

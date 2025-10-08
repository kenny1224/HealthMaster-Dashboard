"""
資料載入與處理模組
自動載入 Excel 檔案並處理資料
"""

import pandas as pd
import streamlit as st
from datetime import datetime
import pytz
import os


class DataLoader:
    """資料載入器"""
    
    def __init__(self, file_paths=None):
        # 取得專案根目錄（src 的上一層）
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        
        # 使用新的EXCEL檔案
        if file_paths is None:
            file_paths = ['data/每周分數累積.xlsx']
        
        self.file_paths = []
        for file_path in file_paths:
            if not os.path.isabs(file_path):
                abs_path = os.path.join(project_root, file_path)
            else:
                abs_path = file_path
            self.file_paths.append(abs_path)
        
        # 初始化活動分析器
        self.activity_analyzer = None  # 延遲初始化
        self.new_loader = None  # 新資料載入器實例
        self.correct_loader = None  # 修正後的資料載入器實例
        
    @st.cache_data(ttl=300)  # 5分鐘快取
    def load_data(_self):
        """載入新的EXCEL檔案結構資料"""
        try:
            # 直接載入參加者活動統計表
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            stats_path = os.path.join(project_root, 'data', '參加者活動統計表.xlsx')

            # 檢查檔案是否存在，不存在則先生成
            if not os.path.exists(stats_path):
                print("參加者活動統計表不存在，正在生成...")
                from new_data_processor import NewDataProcessor
                processor = NewDataProcessor(_self.file_paths[0])
                processor.process_all()

            # 載入參加者活動統計表
            participant_stats = pd.read_excel(stats_path)

            if participant_stats is None or participant_stats.empty:
                st.error("❌ 無法載入參加者活動統計表")
                return None

            # 轉換為適合儀表板的格式
            merged_df = _self._convert_to_dashboard_format_new(participant_stats)

            if merged_df is None:
                st.error("❌ 資料格式轉換失敗")
                return None

            print(f"載入完成：{len(merged_df)} 位參賽者")

            # 儲存processor以供活動分析使用
            from new_data_processor import NewDataProcessor
            _self.new_processor = NewDataProcessor(_self.file_paths[0])
            _self.new_processor.load_account_info()
            _self.new_processor.load_period_data('0808-0830')
            _self.new_processor.load_period_data('0831-0921')
            # 重建社團活動明細
            all_club_details = []
            for sheet_name, df in _self.new_processor.period_data.items():
                club_df = _self.new_processor.transform_club_activities(df, sheet_name)
                all_club_details.append(club_df)
            _self.new_processor.club_details = pd.concat(all_club_details, ignore_index=True)

            return merged_df

        except Exception as e:
            st.error(f"❌ 載入資料時發生錯誤：{str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def _convert_to_dashboard_format(self, participant_stats):
        """將新的參加者活動統計表轉換為儀表板格式"""
        try:
            # 取得帳號資訊
            account_info = self.new_loader.account_info
            if account_info is None:
                print("警告：無法取得帳號資訊")
                return None
            
            # 按姓名聚合統計資料
            dashboard_data = []
            
            # 按姓名分組
            grouped = participant_stats.groupby('姓名')
            
            for name, group in grouped:
                # 取得該參與者的帳號資訊
                participant_id = group['id'].iloc[0]
                
                # 從帳號整理取得基本資訊
                gender = ''
                department = ''
                if participant_id in account_info.index:
                    gender = account_info.loc[participant_id, '性別'] if '性別' in account_info.columns else ''
                    # 尋找部門欄位
                    dept_columns = ['所屬部門', '部門', 'department']
                    for col in dept_columns:
                        if col in account_info.columns:
                            department = account_info.loc[participant_id, col]
                            break
                
                # 計算總分
                total_exercise = group['日常運動得分'].sum()
                total_diet = group['飲食得分'].sum()
                total_bonus = group['個人Bonus得分'].sum()
                total_club = group['參加社團得分'].sum()
                total_score = total_exercise + total_diet + total_bonus + total_club
                
                # 組合儀表板格式的資料
                dashboard_row = {
                    '姓名': name,
                    '性別': gender,
                    '所屬部門': department,
                    'total': total_score,
                    '日常運動總分': total_exercise,
                    '飲食總分': total_diet,
                    'Bonus總分': total_bonus,
                    '社團活動總分': total_club,
                    '日常運動總次數': group['日常運動次數'].sum(),
                    '飲食總次數': group['飲食次數'].sum(),
                    'Bonus總次數': group['個人Bonus次數'].sum(),
                    '社團活動總次數': group['參加社團次數'].sum()
                }
                
                # 添加期間分解資料
                for _, period_row in group.iterrows():
                    period = period_row['回合期間']
                    if '8/8' in period:
                        suffix = '_期間1'
                    elif '8/31' in period:
                        suffix = '_期間2'
                    else:
                        suffix = f"_{period}"
                    
                    dashboard_row[f'日常運動得分{suffix}'] = period_row['日常運動得分']
                    dashboard_row[f'飲食得分{suffix}'] = period_row['飲食得分']
                    dashboard_row[f'個人Bonus得分{suffix}'] = period_row['個人Bonus得分']
                    dashboard_row[f'社團活動得分{suffix}'] = period_row['參加社團得分']
                    dashboard_row[f'total{suffix}'] = (period_row['日常運動得分'] + 
                                                     period_row['飲食得分'] + 
                                                     period_row['個人Bonus得分'] + 
                                                     period_row['參加社團得分'])
                
                dashboard_data.append(dashboard_row)
            
            # 轉換為DataFrame
            df = pd.DataFrame(dashboard_data)
            
            # 填充缺失值
            df = df.fillna(0)
            
            print(f"格式轉換完成：{len(df)} 位參賽者")
            return df
            
        except Exception as e:
            print(f"格式轉換失敗：{str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def _convert_to_dashboard_format_new(self, participant_stats):
        """將新的參加者活動統計表轉換為儀表板格式"""
        try:
            # participant_stats 已經是正確格式的 DataFrame
            # 欄位: id, 姓名, 性別, 所屬部門, 運動總得分, 運動總次數, 飲食總得分, 飲食總次數,
            #      Bonus總得分, Bonus總次數, 社團總得分, 社團總次數, total, 期間1分數, 期間2分數

            dashboard_data = []

            for _, row in participant_stats.iterrows():
                dashboard_row = {
                    '姓名': row['姓名'],
                    '性別': row['性別'],
                    '所屬部門': row['所屬部門'],
                    'total': row['total'],
                    '日常運動總分': row['運動總得分'],
                    '飲食總分': row['飲食總得分'],
                    'Bonus總分': row['Bonus總得分'],
                    '社團活動總分': row['社團總得分'],
                    '日常運動總次數': row['運動總次數'],
                    '飲食總次數': row['飲食總次數'],
                    'Bonus總次數': row['Bonus總次數'],
                    '社團活動總次數': row['社團總次數'],
                    # 期間分解
                    'total_期間1': row['期間1分數'],
                    'total_期間2': row['期間2分數']
                }
                dashboard_data.append(dashboard_row)

            # 轉換為DataFrame
            df = pd.DataFrame(dashboard_data)

            # 填充缺失值
            df = df.fillna(0)

            print(f"新格式轉換完成：{len(df)} 位參賽者")
            return df

        except Exception as e:
            print(f"新格式轉換失敗：{str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def _convert_to_dashboard_format_correct(self, participant_stats):
        """將修正後的參加者活動統計表轉換為儀表板格式"""
        try:
            # participant_stats 已經是正確格式的 DataFrame
            # 直接使用並重新組織為儀表板需要的格式
            dashboard_data = []
            
            for _, row in participant_stats.iterrows():
                dashboard_row = {
                    '姓名': row['姓名'],
                    '性別': row['性別'],
                    '所屬部門': row['所屬部門'],
                    'total': row['total'],
                    '日常運動總分': row['運動總得分'],
                    '飲食總分': row['飲食總得分'],
                    'Bonus總分': row['Bonus總得分'],
                    '社團活動總分': row['社團總得分'],
                    '日常運動總次數': row['運動總次數'],
                    '飲食總次數': row['飲食總次數'],
                    'Bonus總次數': row['Bonus總次數'],
                    '社團活動總次數': row['社團總次數'],
                    # 期間分解
                    'total_期間1': row['期間1分數'],
                    'total_期間2': row['期間2分數']
                }
                dashboard_data.append(dashboard_row)
            
            # 轉換為DataFrame
            df = pd.DataFrame(dashboard_data)
            
            # 填充缺失值
            df = df.fillna(0)
            
            print(f"修正格式轉換完成：{len(df)} 位參賽者")
            return df
            
        except Exception as e:
            print(f"修正格式轉換失敗：{str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def _add_period_suffix(self, df, period_name):
        """為活動欄位加上期間標示"""
        df_copy = df.copy()
        # 基本欄位不需要改名
        basic_columns = ['姓名', '性別', '所屬部門', '員工編號', '分公司代碼', '部門', '電子信箱', '體脂前測', '體脂是否上傳']
        
        new_columns = {}
        for col in df_copy.columns:
            if col not in basic_columns and col != 'total':
                # 活動相關欄位加上期間標示
                new_columns[col] = f"{col}_{period_name}"
            elif col == 'total':
                # total欄位改名為該期間的總分
                new_columns[col] = f"total_{period_name}"
        
        df_copy = df_copy.rename(columns=new_columns)
        return df_copy
    
    def _merge_files(self, df1, df2, period_name):
        """合併兩個檔案的資料"""
        # 為第二個檔案的欄位加上期間標示
        df2_renamed = self._add_period_suffix(df2, period_name)
        
        # 以姓名為主鍵進行合併
        merged = pd.merge(
            df1, df2_renamed, 
            on='姓名', 
            how='outer',  # 外部合併，保留所有參賽者
            suffixes=('', '_dup')
        )
        
        # 處理重複的基本欄位（使用第一個檔案的資料為主）
        basic_columns = ['性別', '所屬部門', '員工編號', '分公司代碼', '部門', '電子信箱', '體脂前測', '體脂是否上傳']
        for col in basic_columns:
            if f"{col}_dup" in merged.columns:
                # 如果第一個檔案該欄位為空，使用第二個檔案的資料
                merged[col] = merged[col].fillna(merged[f"{col}_dup"])
                merged = merged.drop(columns=[f"{col}_dup"])
        
        # 累加各期間的total分數得到最終總分
        total_columns = [col for col in merged.columns if col.startswith('total_期間')]
        if total_columns:
            # 累加所有期間的分數
            merged['total'] = merged[total_columns].fillna(0).sum(axis=1)
        
        return merged
    
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
        valid_genders = ['女', '男', '生理女', '生理男']  # 支援原始和轉換後的格式
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
            # 統一性別標示：生理女→女，生理男→男
            df['性別'] = df['性別'].replace({'生理女': '女', '生理男': '男'})
        
        return df
    
    def get_last_update_time(self):
        """獲取檔案最後更新時間（台灣時區）"""
        try:
            latest_time = None
            taipei_tz = pytz.timezone('Asia/Taipei')
            
            for file_path in self.file_paths:
                if os.path.exists(file_path):
                    timestamp = os.path.getmtime(file_path)
                    utc_time = datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.UTC)
                    file_time = utc_time.astimezone(taipei_tz)
                    
                    if latest_time is None or file_time > latest_time:
                        latest_time = file_time
            
            return latest_time
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
        # 計算基本統計
        total_registrants = len(df)  # 報名人數：所有在名單裡的人
        
        # 實際參與人數：使用報告的標準（87人）
        actual_participants_count = 87  # 以報告統計摘要為準
        
        # 嘗試從活動統計分析報告讀取精確數據
        try:
            import os
            report_path = 'data/活動統計分析報告.xlsx'
            if os.path.exists(report_path):
                report_summary = pd.read_excel(report_path, sheet_name='統計摘要')
                report_individual = pd.read_excel(report_path, sheet_name='個人總計統計')
                
                # 從報告中獲取實際參與人數
                for _, row in report_summary.iterrows():
                    if row['統計項目'] == '參賽者總數':
                        actual_participants_count = int(row['數值'])
                        break
                
                # 使用報告中的參賽者名單來計算性別分布
                if '姓名' in df.columns:
                    report_names = set(report_individual['姓名'].tolist())
                    active_participants = df[df['姓名'].isin(report_names)]
                else:
                    active_participants = df[df['total'] > 0] if 'total' in df.columns else df
            else:
                # 如果報告不存在，使用分數>0的邏輯
                active_participants = df[df['total'] > 0] if 'total' in df.columns else df
                actual_participants_count = len(active_participants)
                
        except Exception:
            # 如果讀取報告失敗，使用分數>0的邏輯
            active_participants = df[df['total'] > 0] if 'total' in df.columns else df
            actual_participants_count = len(active_participants)
        
        # 確保所有必要的統計都有默認值
        stats = {
            'total_registrants': total_registrants,  # 總報名人數
            'active_participants': actual_participants_count,  # 實際參與人數（分數>0）
            'total_participants': actual_participants_count,  # 保持向後兼容
            'female_count': 0,  # 預設值
            'male_count': 0,    # 預設值
            'avg_score': 0,     # 預設值
            'max_score': 0,     # 預設值
            'min_score': 0,     # 預設值
        }
        
        # 安全地計算性別分布
        if '性別' in df.columns and len(active_participants) > 0:
            try:
                stats['female_count'] = len(active_participants[active_participants['性別'].str.contains('女', na=False)])
                stats['male_count'] = len(active_participants[active_participants['性別'].str.contains('男', na=False)])
            except:
                # 如果性別欄位有問題，回退到基本計算
                gender_col = active_participants['性別']
                stats['female_count'] = len(gender_col[gender_col == '女'])
                stats['male_count'] = len(gender_col[gender_col == '男'])
        
        # 安全地計算分數統計
        if 'total' in active_participants.columns and len(active_participants) > 0:
            try:
                valid_scores = active_participants['total'].dropna()
                if len(valid_scores) > 0:
                    stats['avg_score'] = float(valid_scores.mean())
                    stats['max_score'] = float(valid_scores.max())
                    stats['min_score'] = float(valid_scores.min())
            except:
                pass
        
        # 體脂完成率
        if '體脂是否上傳' in df.columns:
            completed = df['體脂是否上傳'].isin(['已完成', '✅', '是']).sum()
            stats['body_fat_completion_rate'] = completed / len(df) if len(df) > 0 else 0
        
        # 運動和飲食統計（計算有記錄的人次）
        exercise_cols = [col for col in df.columns if '運動' in col or '日常' in col]
        if exercise_cols:
            # 計算有運動記錄的總人次（每個人每個欄位算一次）
            exercise_records = 0
            for col in exercise_cols:
                exercise_records += (df[col].fillna(0) > 0).sum()
            stats['total_exercise_records'] = exercise_records
        
        diet_cols = [col for col in df.columns if '飲食' in col]
        if diet_cols:
            # 計算有飲食記錄的總人次
            diet_records = 0
            for col in diet_cols:
                diet_records += (df[col].fillna(0) > 0).sum()
            stats['total_diet_records'] = diet_records
        
        return stats
    
    def get_activity_analyzer(self):
        """取得活動分析器"""
        if self.activity_analyzer is None:
            try:
                # 使用新的活動分析器
                from new_activity_analyzer import NewActivityAnalyzer
                # 使用新的processor
                processor_to_use = self.new_processor if hasattr(self, 'new_processor') and self.new_processor else None
                if processor_to_use is None:
                    # 如果沒有processor，建立一個新的
                    from new_data_processor import NewDataProcessor
                    processor_to_use = NewDataProcessor(self.file_paths[0])
                    processor_to_use.load_account_info()
                    processor_to_use.load_period_data('0808-0830')
                    processor_to_use.load_period_data('0831-0921')
                    # 建立社團活動明細
                    all_club_details = []
                    for sheet_name, df in processor_to_use.period_data.items():
                        club_df = processor_to_use.transform_club_activities(df, sheet_name)
                        all_club_details.append(club_df)
                    processor_to_use.club_details = pd.concat(all_club_details, ignore_index=True)

                self.activity_analyzer = NewActivityAnalyzer(processor_to_use)
            except ImportError:
                # 如果相對導入失敗，嘗試絕對導入
                import sys
                import os
                current_dir = os.path.dirname(os.path.abspath(__file__))
                sys.path.insert(0, current_dir)
                from new_activity_analyzer import NewActivityAnalyzer
                from new_data_processor import NewDataProcessor

                processor_to_use = self.new_processor if hasattr(self, 'new_processor') and self.new_processor else None
                if processor_to_use is None:
                    processor_to_use = NewDataProcessor(self.file_paths[0])
                    processor_to_use.load_account_info()
                    processor_to_use.load_period_data('0808-0830')
                    processor_to_use.load_period_data('0831-0921')
                    all_club_details = []
                    for sheet_name, df in processor_to_use.period_data.items():
                        club_df = processor_to_use.transform_club_activities(df, sheet_name)
                        all_club_details.append(club_df)
                    processor_to_use.club_details = pd.concat(all_club_details, ignore_index=True)

                self.activity_analyzer = NewActivityAnalyzer(processor_to_use)
        return self.activity_analyzer

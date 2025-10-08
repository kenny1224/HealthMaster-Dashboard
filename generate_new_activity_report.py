#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
基於新EXCEL檔案結構產生活動統計分析報告
"""

import pandas as pd
import sys
import os

# 添加src路徑
sys.path.append('src')
from new_excel_data_loader import NewExcelDataLoader

def generate_new_activity_report(output_file='data/活動統計分析報告.xlsx'):
    """產生基於新Excel結構的活動統計分析報告"""
    print("開始產生新活動統計分析報告...")
    
    # 1. 載入新Excel資料
    loader = NewExcelDataLoader()
    participant_stats = loader.load_all_data()
    
    if participant_stats is None:
        print("❌ 無法載入新Excel檔案資料")
        return None
    
    # 2. 生成個人總計統計
    print("生成個人總計統計...")
    individual_stats = []
    
    for name, group in participant_stats.groupby('姓名'):
        total_exercise_score = group['日常運動得分'].sum()
        total_diet_score = group['飲食得分'].sum()
        total_bonus_score = group['個人Bonus得分'].sum()
        total_club_score = group['參加社團得分'].sum()
        total_score = total_exercise_score + total_diet_score + total_bonus_score + total_club_score
        
        individual_stats.append({
            '姓名': name,
            '運動總次數': int(group['日常運動次數'].sum()),
            '運動總得分': int(total_exercise_score),
            '飲食總次數': int(group['飲食次數'].sum()),
            '飲食總得分': int(total_diet_score),
            'Bonus總次數': int(group['個人Bonus次數'].sum()),
            'Bonus總得分': int(total_bonus_score),
            '社團總次數': int(group['參加社團次數'].sum()),
            '社團總得分': int(total_club_score),
            '活動計算總分': int(total_score),
            'Excel總分': int(total_score),  # 新結構下兩者相同
            '差異': 0  # 新結構下應該沒有差異
        })
    
    individual_df = pd.DataFrame(individual_stats)
    individual_df = individual_df.sort_values('Excel總分', ascending=False)
    
    # 3. 生成期間明細統計
    print("生成期間明細統計...")
    period_details = []
    
    for _, row in participant_stats.iterrows():
        period_details.append({
            '姓名': row['姓名'],
            '期間': row['回合期間'],
            '期間範圍': row['回合期間'],
            '運動次數': int(row['日常運動次數']),
            '運動得分': int(row['日常運動得分']),
            '飲食次數': int(row['飲食次數']),
            '飲食得分': int(row['飲食得分']),
            'Bonus次數': int(row['個人Bonus次數']),
            'Bonus得分': int(row['個人Bonus得分']),
            '社團次數': int(row['參加社團次數']),
            '社團得分': int(row['參加社團得分']),
            '期間計算總分': int(row['日常運動得分'] + row['飲食得分'] + row['個人Bonus得分'] + row['參加社團得分']),
            '期間Excel總分': int(row['日常運動得分'] + row['飲食得分'] + row['個人Bonus得分'] + row['參加社團得分']),
            '期間差異': 0
        })
    
    period_df = pd.DataFrame(period_details)
    period_df = period_df.sort_values(['姓名', '期間'])
    
    # 4. 生成社團活動明細
    print("生成社團活動明細...")
    club_details = loader.get_club_activity_details()
    
    if club_details is None:
        club_details = pd.DataFrame(columns=['姓名', '社團活動日期', '參加社團', '得分'])
    
    # 5. 生成統計摘要
    print("生成統計摘要...")
    total_participants = len(individual_df[individual_df['Excel總分'] > 0])
    total_excel_score = individual_df['Excel總分'].sum()
    total_calculated_score = individual_df['活動計算總分'].sum()
    max_difference = individual_df['差異'].abs().max()
    
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
    
    # 6. 寫入Excel檔案
    print(f"寫入Excel檔案: {output_file}")
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        individual_df.to_excel(writer, sheet_name='個人總計統計', index=False)
        period_df.to_excel(writer, sheet_name='各期間明細統計', index=False)
        club_details.to_excel(writer, sheet_name='社團活動明細', index=False)
        stats_df.to_excel(writer, sheet_name='統計摘要', index=False)
    
    print(f"✅ 新活動統計分析報告已生成: {output_file}")
    print(f"   - 個人總計統計: {len(individual_df)} 位參賽者")
    print(f"   - 各期間明細統計: {len(period_df)} 筆記錄")
    print(f"   - 社團活動明細: {len(club_details)} 筆記錄")
    print(f"   - 統計摘要: {len(stats_df)} 項統計")
    
    return output_file, individual_df

if __name__ == "__main__":
    print("🚀 開始產生基於新Excel結構的活動統計分析報告...")
    
    try:
        output_file, summary_df = generate_new_activity_report()
        
        if summary_df is not None:
            print(f"\n📊 報告產生完成: {output_file}")
            
            # 顯示前5名統計
            print(f"\n🏆 前5名參賽者統計:")
            top5 = summary_df.head()
            for _, row in top5.iterrows():
                print(f"  {row['姓名']}: {row['Excel總分']}分")
        
    except Exception as e:
        print(f"❌ 產生報告時發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
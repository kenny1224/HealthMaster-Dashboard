#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
測試新的資料處理流程
"""

import sys
sys.path.append('src')

def test_new_excel_loader():
    """測試新Excel載入器"""
    print("🧪 測試新Excel資料載入器...")
    
    try:
        from new_excel_data_loader import NewExcelDataLoader
        
        # 測試載入資料
        loader = NewExcelDataLoader()
        
        # 檢查檔案是否存在
        import os
        if not os.path.exists('data/每周分數累積.xlsx'):
            print("❌ 找不到檔案: data/每周分數累積.xlsx")
            print("請確保新的Excel檔案已放在正確位置")
            return False
        
        # 載入帳號資訊
        account_info = loader.load_account_info()
        if account_info is not None:
            print(f"✅ 帳號資訊載入成功: {len(account_info)} 筆")
        else:
            print("❌ 帳號資訊載入失敗")
            return False
        
        # 載入期間資料
        period1 = loader.load_period_data('0808-0830')
        period2 = loader.load_period_data('0831-0921')
        
        if period1 is not None and period2 is not None:
            print(f"✅ 期間資料載入成功: 期間1={len(period1)}筆, 期間2={len(period2)}筆")
        else:
            print("❌ 期間資料載入失敗")
            return False
        
        # 建立統計表
        stats = loader.build_participant_activity_stats()
        if stats is not None:
            print(f"✅ 參加者活動統計表建立成功: {len(stats)} 筆記錄")
            print(f"統計表欄位: {list(stats.columns)}")
        else:
            print("❌ 參加者活動統計表建立失敗")
            return False
        
        # 測試社團活動明細
        club_details = loader.get_club_activity_details()
        if club_details is not None:
            print(f"✅ 社團活動明細取得成功: {len(club_details)} 筆活動")
        else:
            print("❌ 社團活動明細取得失敗")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試新Excel載入器時發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_data_loader():
    """測試資料載入器"""
    print("\n🧪 測試整合資料載入器...")
    
    try:
        from data_loader import DataLoader
        
        loader = DataLoader()
        df = loader.load_data()
        
        if df is not None:
            print(f"✅ 儀表板資料載入成功: {len(df)} 位參賽者")
            print(f"資料欄位: {list(df.columns)}")
            
            # 測試統計計算
            stats = loader.get_statistics(df)
            print(f"✅ 統計計算成功:")
            print(f"   報名人數: {stats.get('total_registrants', 'N/A')}")
            print(f"   實際參與人數: {stats.get('active_participants', 'N/A')}")
            print(f"   女性: {stats.get('female_count', 'N/A')}, 男性: {stats.get('male_count', 'N/A')}")
            
            # 測試活動分析器
            analyzer = loader.get_activity_analyzer()
            analyzer.load_detailed_data()
            activity_stats = analyzer.get_overall_statistics()
            print(f"✅ 活動統計分析成功:")
            print(f"   運動: {activity_stats['exercise']['total_count']}次")
            print(f"   飲食: {activity_stats['diet']['total_count']}次")
            print(f"   Bonus: {activity_stats['bonus']['total_count']}次")
            print(f"   社團: {activity_stats['club']['total_activities']}次")
            
            return True
        else:
            print("❌ 儀表板資料載入失敗")
            return False
            
    except Exception as e:
        print(f"❌ 測試資料載入器時發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_report_generation():
    """測試報告生成"""
    print("\n🧪 測試報告生成...")
    
    try:
        from generate_new_activity_report import generate_new_activity_report
        
        output_file, summary_df = generate_new_activity_report()
        
        if output_file and summary_df is not None:
            print(f"✅ 報告生成成功: {output_file}")
            print(f"   參賽者人數: {len(summary_df)}")
            
            # 顯示前3名
            print("🏆 前3名參賽者:")
            for i, (_, row) in enumerate(summary_df.head(3).iterrows()):
                print(f"   {i+1}. {row['姓名']}: {row['Excel總分']}分")
            
            return True
        else:
            print("❌ 報告生成失敗")
            return False
            
    except Exception as e:
        print(f"❌ 測試報告生成時發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 開始測試新的資料處理流程...")
    
    # 測試步驟
    step1 = test_new_excel_loader()
    step2 = test_data_loader() if step1 else False
    step3 = test_report_generation() if step2 else False
    
    print(f"\n📊 測試結果摘要:")
    print(f"   新Excel載入器: {'✅ 成功' if step1 else '❌ 失敗'}")
    print(f"   整合資料載入器: {'✅ 成功' if step2 else '❌ 失敗'}")
    print(f"   報告生成: {'✅ 成功' if step3 else '❌ 失敗'}")
    
    if step1 and step2 and step3:
        print("\n🎉 所有測試通過！新的資料處理流程已準備就緒。")
    else:
        print("\n⚠️ 部分測試失敗，請檢查錯誤訊息並修正問題。")
"""
健康達人積分賽儀表板
主程式入口
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_loader import DataLoader
from ranking_engine import RankingEngine

# 頁面設定
st.set_page_config(
    page_title="健康達人積分賽",
    page_icon="🏃‍♂️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 自訂 CSS 樣式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #4CAF50;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #4CAF50 0%, #8BC34A 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
    }
    .winner-row {
        background-color: #fff9e6 !important;
        font-weight: bold;
    }
    .rank-1 { background-color: #FFD700 !important; }
    .rank-2-4 { background-color: #C0C0C0 !important; }
    .rank-5-9 { background-color: #CD7F32 !important; }
    .rank-10-14 { background-color: #50C878 !important; }
</style>
""", unsafe_allow_html=True)


# 初始化資料載入器
@st.cache_resource
def get_data_loader():
    return DataLoader()


def display_header():
    """顯示頁首"""
    st.markdown('<div class="main-header">🏃‍♂️ 健康達人積分賽</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        st.markdown("**📅 活動期間：** 2025/08/08 - 2025/10/31")
    with col2:
        loader = get_data_loader()
        update_time = loader.get_last_update_time()
        if update_time:
            st.markdown(f"**🕐 最後更新：** {update_time.strftime('%Y/%m/%d %H:%M')}")
    with col3:
        if st.button("🔄 重新載入", use_container_width=True):
            st.cache_data.clear()
            st.rerun()


def display_metrics(stats):
    """顯示關鍵指標"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="👥 總參與人數",
            value=f"{stats['total_participants']}人",
            delta=f"女{stats['female_count']} 男{stats['male_count']}"
        )
    
    with col2:
        exercise_records = stats.get('total_exercise_records', 0)
        st.metric(
            label="🏃 累計運動紀錄",
            value=f"{exercise_records}次"
        )
    
    with col3:
        diet_records = stats.get('total_diet_records', 0)
        st.metric(
            label="🍎 累計飲食紀錄",
            value=f"{diet_records}次"
        )
    
    with col4:
        body_fat_rate = stats.get('body_fat_completion_rate', 0)
        st.metric(
            label="⚖️ 體脂完成率",
            value=f"{body_fat_rate*100:.0f}%"
        )


def display_overview_tab(female_top, male_top):
    """顯示總覽頁"""
    st.subheader("📊 排行榜概覽")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🌸 女性組 Top 10")
        if not female_top.empty:
            display_columns = ['排名', '獎牌', '姓名', '所屬部門', 'total', '獎金']
            available_columns = [col for col in display_columns if col in female_top.columns]
            
            # 格式化顯示
            display_df = female_top[available_columns].head(10).copy()
            display_df.columns = ['排名', '獎牌', '姓名', '部門', '總分', '獎金']
            
            st.dataframe(
                display_df,
                hide_index=True,
                use_container_width=True,
                height=400
            )
            
            st.info(f"💡 共 {len(female_top)} 位參賽者")
        else:
            st.warning("暫無資料")
    
    with col2:
        st.markdown("### 💪 男性組 Top 10")
        if not male_top.empty:
            display_columns = ['排名', '獎牌', '姓名', '所屬部門', 'total', '獎金']
            available_columns = [col for col in display_columns if col in male_top.columns]
            
            display_df = male_top[available_columns].head(10).copy()
            display_df.columns = ['排名', '獎牌', '姓名', '部門', '總分', '獎金']
            
            st.dataframe(
                display_df,
                hide_index=True,
                use_container_width=True,
                height=400
            )
            
            st.info(f"💡 共 {len(male_top)} 位參賽者")
        else:
            st.warning("暫無資料")


def display_full_ranking_tab(df, gender_label, emoji):
    """顯示完整排名頁"""
    st.subheader(f"{emoji} {gender_label}完整排行榜（共 {len(df)} 人）")
    
    # 搜尋和篩選
    col1, col2, col3 = st.columns([3, 3, 2])
    
    with col1:
        search_name = st.text_input(
            "🔍 搜尋姓名",
            key=f"search_{gender_label}",
            placeholder="輸入姓名..."
        )
    
    with col2:
        if '所屬部門' in df.columns:
            departments = ['全部'] + sorted(df['所屬部門'].unique().tolist())
            dept_filter = st.selectbox(
                "篩選部門",
                departments,
                key=f"dept_{gender_label}"
            )
        else:
            dept_filter = '全部'
    
    with col3:
        # 下載按鈕
        csv = df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 下載排名表",
            data=csv,
            file_name=f"{gender_label}_排名表.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    # 篩選資料
    filtered_df = df.copy()
    
    if search_name:
        filtered_df = filtered_df[filtered_df['姓名'].str.contains(search_name, na=False)]
    
    if dept_filter != '全部' and '所屬部門' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['所屬部門'] == dept_filter]
    
    # 顯示表格
    if not filtered_df.empty:
        display_columns = ['排名', '獎牌', '姓名', '所屬部門', 'total', '獎金']
        available_columns = [col for col in display_columns if col in filtered_df.columns]
        
        display_df = filtered_df[available_columns].copy()
        display_df.columns = ['排名', '獎牌', '姓名', '部門', '總分', '獎金']
        
        st.dataframe(
            display_df,
            hide_index=True,
            use_container_width=True,
            height=600
        )
        
        # 統計資訊
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("顯示人數", f"{len(filtered_df)} 人")
        with col2:
            st.metric("平均分數", f"{filtered_df['total'].mean():.0f} 分")
        with col3:
            st.metric("最高分", f"{filtered_df['total'].max():.0f} 分")
        with col4:
            max_prize_rank = 28 if gender_label == '女性組' else 14
            prize_line_name = f"前{max_prize_rank}名分數線"
            
            if len(df) >= max_prize_rank:
                cutoff = df.iloc[max_prize_rank-1]['total']
                st.metric(prize_line_name, f"{cutoff:.0f} 分")
            else:
                st.metric(prize_line_name, "N/A")
        
        prize_info = f"前 {max_prize_rank} 名" if gender_label == '女性組' else "前 14 名"
        st.info(f"💡 {prize_info}可獲得獎金！繼續加油 💪")
    else:
        st.warning("沒有符合條件的資料")


def display_personal_query_tab(ranking_engine):
    """顯示個人查詢頁"""
    st.subheader("🔍 個人成績查詢")
    
    # 取得所有姓名列表
    all_names = pd.concat([
        ranking_engine.female_df['姓名'],
        ranking_engine.male_df['姓名']
    ]).unique().tolist()
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        selected_name = st.selectbox(
            "請選擇您的姓名",
            ['請選擇...'] + sorted(all_names),
            key="name_select"
        )
    
    with col2:
        search_button = st.button("🔍 查詢", use_container_width=True, type="primary")
    
    if search_button and selected_name != '請選擇...':
        person_data, group, total_in_group = ranking_engine.get_person_info(selected_name)
        
        if person_data is not None:
            # 個人資訊卡片
            st.markdown("---")
            st.markdown(f"## 📊 {selected_name} 的積分卡")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                ### 基本資訊
                - **性別：** {person_data['性別']}
                - **所屬部門：** {person_data.get('所屬部門', 'N/A')}
                """)
            
            with col2:
                st.markdown(f"""
                ### 排名資訊
                - **{group}排名：** 第 {person_data['排名']} 名 / 共 {total_in_group} 人
                - **總分：** {person_data['total']} 分
                """)
            
            # 獎金資訊
            max_prize_rank = 28 if group == '女性組' else 14
            prize_line_name = "第28名" if group == '女性組' else "第14名"
            
            if person_data['排名'] <= max_prize_rank:
                st.success(f"🎉 恭喜！您目前排名第 {person_data['排名']} 名，可獲得獎金 **{person_data['獎金']}** {person_data['獎牌']}")
                
                # 計算與前一名的差距
                group_df = ranking_engine.female_df if group == '女性組' else ranking_engine.male_df
                if person_data['排名'] > 1:
                    diff = ranking_engine.get_rank_difference(person_data, group_df)
                    st.info(f"💪 距離第 {person_data['排名']-1} 名還差 **{diff:.0f}** 分，加油！")
            else:
                # 計算距離獎金線的差距
                group_df = ranking_engine.female_df if group == '女性組' else ranking_engine.male_df
                if len(group_df) >= max_prize_rank:
                    prize_line_score = group_df.iloc[max_prize_rank-1]['total']
                    diff = prize_line_score - person_data['total']
                    st.warning(f"距離獎金線（{prize_line_name}）還差 **{diff:.0f}** 分，繼續努力！💪")
            
            # 分數明細
            st.markdown("### 📈 分數明細")
            score_breakdown = ranking_engine.get_score_breakdown(person_data)
            
            if score_breakdown:
                cols = st.columns(len(score_breakdown))
                for idx, (label, score) in enumerate(score_breakdown.items()):
                    with cols[idx]:
                        st.metric(label, f"{score:.0f} 分")
            
            # 完成項目
            st.markdown("### ✅ 完成項目")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                body_fat_status = person_data.get('體脂是否上傳', '')
                if body_fat_status in ['已完成', '✅', '是']:
                    st.success("✅ 體脂前後測")
                else:
                    st.error("❌ 體脂前後測")
            
            with col2:
                if score_breakdown.get('日常運動', 0) > 0:
                    st.success("✅ 運動紀錄上傳")
                else:
                    st.error("❌ 運動紀錄上傳")
            
            with col3:
                if score_breakdown.get('健康飲食', 0) > 0:
                    st.success("✅ 飲食紀錄上傳")
                else:
                    st.error("❌ 飲食紀錄上傳")
            
            # 社團活動記錄
            activities = ranking_engine.get_club_activities(person_data)
            if activities:
                st.markdown("### 🎯 參加社團活動記錄")
                for activity in activities:
                    st.markdown(f"- {activity}")
            
            # 活動參與記錄
            st.markdown("### 🏃‍♂️ 活動參與記錄")
            
            # 提取活動記錄（排除基本資訊欄位）
            exclude_columns = ['排名', '獎金', '獎牌', '顏色', '姓名', '性別', '所屬部門', 
                             '員工編號', '分公司代碼', '部門', '電子信箱', 'total']
            
            # 分類顯示活動記錄
            activity_records = {}
            
            for col in person_data.index:
                if col not in exclude_columns and pd.notna(person_data[col]) and person_data[col] != 0:
                    # 根據欄位名稱分類
                    if '期間1' in col:
                        category = "📅 第一期間活動"
                    elif '期間2' in col:
                        category = "📅 第二期間活動"
                    elif 'total_期間' in col:
                        category = "📊 各期間總分"
                    else:
                        category = "📝 其他記錄"
                    
                    if category not in activity_records:
                        activity_records[category] = []
                    
                    # 清理欄位名稱（移除期間標示）
                    clean_name = col.replace('_期間1', '').replace('_期間2', '')
                    activity_records[category].append((clean_name, person_data[col]))
            
            # 顯示分類的活動記錄
            if activity_records:
                for category, records in activity_records.items():
                    st.markdown(f"#### {category}")
                    
                    # 建立該類別的資料框
                    if records:
                        records_df = pd.DataFrame(records, columns=['活動項目', '分數/狀態'])
                        st.dataframe(
                            records_df,
                            use_container_width=True,
                            hide_index=True
                        )
                    st.markdown("---")
                
                # 下載活動記錄
                all_records = []
                for category, records in activity_records.items():
                    for activity, score in records:
                        all_records.append([category, activity, score])
                
                if all_records:
                    download_df = pd.DataFrame(all_records, columns=['類別', '活動項目', '分數/狀態'])
                    csv_data = download_df.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="📥 下載活動記錄",
                        data=csv_data,
                        file_name=f"{selected_name}_活動記錄.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            else:
                st.info("暫無活動參與記錄")
            
        else:
            st.error(f"找不到 {selected_name} 的資料")


def display_activity_intro_tab():
    """顯示活動簡介頁"""
    st.subheader("📝 活動簡介")
    
    try:
        # 讀取活動簡介檔案
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        intro_path = os.path.join(project_root, '活動簡介.txt')
        
        with open(intro_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 顯示內容
        st.markdown(content)
        
    except FileNotFoundError:
        st.error("❌ 找不到活動簡介檔案")
    except Exception as e:
        st.error(f"❌ 讀取活動簡介時發生錯誤：{str(e)}")


def display_statistics_tab(df):
    """顯示統計圖表頁"""
    st.subheader("📈 活動統計分析")
    
    # 男女分數分布對比
    st.markdown("### 分數分布對比")
    fig1 = px.box(
        df,
        x='性別',
        y='total',
        color='性別',
        title='男女組分數分布對比',
        labels={'total': '總分', '性別': '性別組別'},
        color_discrete_map={'女': '#FF69B4', '男': '#4169E1'}
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    # 部門參與度
    if '所屬部門' in df.columns:
        st.markdown("### 各部門參與度")
        dept_gender = df.groupby(['所屬部門', '性別']).size().reset_index(name='人數')
        
        fig2 = px.bar(
            dept_gender,
            x='所屬部門',
            y='人數',
            color='性別',
            barmode='group',
            title='各部門男女參與人數',
            color_discrete_map={'女': '#FF69B4', '男': '#4169E1'}
        )
        fig2.update_xaxes(tickangle=45)
        st.plotly_chart(fig2, use_container_width=True)
    
    # 分數分段統計
    st.markdown("### 分數分段統計")
    score_bins = [0, 100, 200, 300, 400, 500, 1000]
    score_labels = ['0-100', '101-200', '201-300', '301-400', '401-500', '500+']
    df['分數區間'] = pd.cut(df['total'], bins=score_bins, labels=score_labels)
    
    score_dist = df.groupby(['分數區間', '性別']).size().reset_index(name='人數')
    
    fig3 = px.bar(
        score_dist,
        x='分數區間',
        y='人數',
        color='性別',
        title='分數分段分布',
        color_discrete_map={'女': '#FF69B4', '男': '#4169E1'}
    )
    st.plotly_chart(fig3, use_container_width=True)


def main():
    """主程式"""
    # 顯示頁首
    display_header()
    
    # 載入資料
    loader = get_data_loader()
    df = loader.load_data()
    
    if df is None:
        st.error("❌ 無法載入資料，請檢查檔案路徑")
        return
    
    # 驗證資料
    is_valid, issues = loader.validate_data(df)
    if not is_valid:
        st.error("❌ 資料驗證失敗：")
        for issue in issues:
            st.error(f"- {issue}")
        return
    
    # 清理資料
    df = loader.clean_data(df)
    
    # 獲取統計資訊
    stats = loader.get_statistics(df)
    
    # 顯示關鍵指標
    display_metrics(stats)
    
    st.markdown("---")
    
    # 計算排名
    ranking_engine = RankingEngine(df)
    female_df, male_df = ranking_engine.calculate_rankings()
    female_top, male_top = ranking_engine.get_top_n(10)
    
    # 選項卡
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 總覽",
        "🌸 女性組完整排名",
        "💪 男性組完整排名",
        "🔍 個人查詢",
        "📈 統計圖表",
        "📝 活動簡介"
    ])
    
    with tab1:
        display_overview_tab(female_top, male_top)
    
    with tab2:
        display_full_ranking_tab(female_df, "女性組", "🌸")
    
    with tab3:
        display_full_ranking_tab(male_df, "男性組", "💪")
    
    with tab4:
        display_personal_query_tab(ranking_engine)
    
    with tab5:
        display_statistics_tab(df)
    
    with tab6:
        display_activity_intro_tab()
    
    # 頁尾
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #888;'>
        <p>💪 健康達人積分賽 | 活動期間：2025/08/08 - 2025/10/31</p>
        <p>總獎金超過 30,000 元 | 加油！下一位健康達人就是您！</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

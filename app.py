"""
健康達人積分賽儀表板
主程式入口
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# 添加 src 目錄到路徑以便導入模組
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

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


def display_metrics(stats, activity_stats=None):
    """顯示關鍵指標"""
    # 第一行：基本參與數據
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="👥 總參與人數",
            value=f"{stats['total_participants']}人",
            delta=f"女{stats['female_count']} 男{stats['male_count']}"
        )
    
    with col2:
        body_fat_rate = stats.get('body_fat_completion_rate', 0)
        st.metric(
            label="⚖️ 體脂完成率",
            value=f"{body_fat_rate*100:.0f}%"
        )
    
    with col3:
        st.metric(
            label="📊 平均分數",
            value=f"{stats.get('avg_score', 0):.0f}分"
        )
    
    with col4:
        st.metric(
            label="🏆 最高分數",
            value=f"{stats.get('max_score', 0):.0f}分"
        )
    
    # 第二行：四大活動類別統計 (7.1-7.4)
    if activity_stats:
        st.markdown("### 📈 活動參與統計")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="7.1 🏃 日常運動",
                value=f"{activity_stats['exercise']['total_count']}次",
                delta=f"{activity_stats['exercise']['participants']}人參與"
            )
        
        with col2:
            st.metric(
                label="7.2 🍎 健康飲食",
                value=f"{activity_stats['diet']['total_count']}次",
                delta=f"{activity_stats['diet']['participants']}人參與"
            )
        
        with col3:
            st.metric(
                label="7.3 ⭐ 額外加分",
                value=f"{activity_stats['bonus']['total_count']}次",
                delta=f"{activity_stats['bonus']['participants']}人參與"
            )
        
        with col4:
            st.metric(
                label="7.4 🎯 社團活動",
                value=f"{activity_stats['club']['total_activities']}項",
                delta=f"{activity_stats['club']['participants']}人參與"
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


def display_personal_query_tab(ranking_engine, activity_analyzer):
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
            current_score = person_data['total']
            
            # 檢查是否符合獎金條件：排名和分數都要符合
            if person_data['排名'] <= max_prize_rank and current_score >= 200:
                st.success(f"🎉 恭喜！您目前排名第 {person_data['排名']} 名，總分 {current_score} 分，可獲得獎金 **{person_data['獎金']}** {person_data['獎牌']}")
                
                # 計算與前一名的差距
                group_df = ranking_engine.female_df if group == '女性組' else ranking_engine.male_df
                if person_data['排名'] > 1:
                    diff = ranking_engine.get_rank_difference(person_data, group_df)
                    st.info(f"💪 距離第 {person_data['排名']-1} 名還差 **{diff:.0f}** 分，加油！")
            else:
                # 分別提示排名和分數條件
                if person_data['排名'] <= max_prize_rank and current_score < 200:
                    # 特殊情況：進入獎金排名但分數不足200分的提醒
                    score_diff = 200 - current_score
                    st.warning(f"🔔 特別提醒：雖然您的排名已進入獎金圈（第 {person_data['排名']} 名），但總分 {current_score} 分未達獎金門檻（需≥200分），還差 **{score_diff:.0f}** 分才能獲得獎金！💪")
                elif person_data['排名'] > max_prize_rank:
                    group_df = ranking_engine.female_df if group == '女性組' else ranking_engine.male_df
                    if len(group_df) >= max_prize_rank:
                        prize_line_score = group_df.iloc[max_prize_rank-1]['total']
                        rank_diff = prize_line_score - current_score
                        st.warning(f"排名未達獎金線（{prize_line_name}），還差 **{rank_diff:.0f}** 分，繼續努力！💪")
                elif current_score < 200:
                    score_diff = 200 - current_score
                    st.warning(f"總分未達獎金門檻（需大於等於200分），還差 **{score_diff:.0f}** 分，繼續努力！💪")
                else:
                    st.warning(f"雖然總分已達標（{current_score}分），但排名尚未進入獎金圈，繼續加油！💪")
            
            # 移除分數明細、完成項目、參加社團活動記錄區塊
            
            # 詳細活動分析
            st.markdown("### 🏃‍♂️ 詳細活動分析")
            
            # 取得個人詳細資料
            person_details = activity_analyzer.get_person_details(selected_name)
            
            if person_details:
                # 四大類活動統計
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        label="🏃 日常運動",
                        value=f"{int(person_details['exercise']['total_count'])} 次",
                        delta=f"{int(person_details['exercise']['total_score'])} 分"
                    )
                
                with col2:
                    st.metric(
                        label="🍎 健康飲食", 
                        value=f"{int(person_details['diet']['total_count'])} 次",
                        delta=f"{int(person_details['diet']['total_score'])} 分"
                    )
                
                with col3:
                    st.metric(
                        label="⭐ 額外加分",
                        value=f"{int(person_details['bonus']['total_count'])} 次", 
                        delta=f"{int(person_details['bonus']['total_score'])} 分"
                    )
                
                with col4:
                    st.metric(
                        label="🎯 社團活動",
                        value=f"{int(person_details['club']['total_count'])} 次",
                        delta=f"{int(person_details['club']['total_score'])} 分"
                    )
                
                st.markdown("---")
                
                # 整個活動期間統計
                st.markdown("#### 📅 活動期間統計")
                
                # 從新架構獲取詳細期間統計
                try:
                    # 獲取該參賽者各期間的詳細資料
                    stats_df = new_loader.processor.get_participant_activity_stats()
                    person_period_data = stats_df[stats_df['姓名'] == selected_name]
                    
                    if not person_period_data.empty:
                        # 準備期間統計表格資料
                        period_summary = []
                        
                        # 按活動類別整理資料
                        activities = [
                            ('🏃 日常運動', '日常運動次數', '日常運動得分'),
                            ('🍎 健康飲食', '飲食次數', '飲食得分'),
                            ('⭐ 額外加分', '個人Bonus次數', '個人Bonus得分'),
                            ('🎯 社團活動', '參加社團次數', '參加社團得分')
                        ]
                        
                        for activity_name, count_col, score_col in activities:
                            row_data = {'活動類別': activity_name}
                            
                            # 各期間數據
                            period_1_data = person_period_data[person_period_data['回合期間'] == '8/8-8/30']
                            period_2_data = person_period_data[person_period_data['回合期間'] == '8/31-9/20']
                            
                            # 8/8-8/30 期間
                            if not period_1_data.empty:
                                row_data['8/8-8/30 次數'] = int(period_1_data[count_col].iloc[0])
                                row_data['8/8-8/30 得分'] = int(period_1_data[score_col].iloc[0])
                            else:
                                row_data['8/8-8/30 次數'] = 0
                                row_data['8/8-8/30 得分'] = 0
                            
                            # 8/31-9/20 期間
                            if not period_2_data.empty:
                                row_data['8/31-9/20 次數'] = int(period_2_data[count_col].iloc[0])
                                row_data['8/31-9/20 得分'] = int(period_2_data[score_col].iloc[0])
                            else:
                                row_data['8/31-9/20 次數'] = 0
                                row_data['8/31-9/20 得分'] = 0
                            
                            # 總計
                            total_count = person_period_data[count_col].sum()
                            total_score = person_period_data[score_col].sum()
                            row_data['總次數'] = int(total_count)
                            row_data['總得分'] = int(total_score)
                            
                            period_summary.append(row_data)
                        
                        # 建立DataFrame並顯示
                        period_summary_df = pd.DataFrame(period_summary)
                        st.dataframe(
                            period_summary_df,
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        st.warning("無法取得該參賽者的期間詳細資料")
                        
                except Exception as e:
                    st.warning(f"取得期間統計時發生錯誤：{str(e)}")
                    # 回退到原始顯示方式
                    summary_data = [{
                        '活動類別': '🏃 日常運動',
                        '總次數': int(person_details['exercise']['total_count']),
                        '總得分': int(person_details['exercise']['total_score'])
                    }, {
                        '活動類別': '🍎 健康飲食', 
                        '總次數': int(person_details['diet']['total_count']),
                        '總得分': int(person_details['diet']['total_score'])
                    }, {
                        '活動類別': '⭐ 額外加分',
                        '總次數': int(person_details['bonus']['total_count']), 
                        '總得分': int(person_details['bonus']['total_score'])
                    }, {
                        '活動類別': '🎯 社團活動',
                        '總次數': int(person_details['club']['total_count']),
                        '總得分': int(person_details['club']['total_score'])
                    }]
                    
                    summary_df = pd.DataFrame(summary_data)
                    st.dataframe(
                        summary_df,
                        use_container_width=True,
                        hide_index=True
                    )
                
                # 社團活動詳細列表 - 新版表格和圖表
                st.markdown("#### 🎯 參與社團活動列表")
                
                # 從新架構取得該參賽者的社團活動明細
                try:
                    # 載入新架構的社團活動明細
                    import sys
                    import os
                    sys.path.append('src')
                    from new_data_loader import NewDataLoader
                    
                    new_loader = NewDataLoader()
                    new_loader.processor.load_all_periods_data()
                    new_loader.processor.build_participant_activity_stats()
                    club_details = new_loader.processor.get_club_activity_details()
                    
                    # 篩選該參賽者的社團活動
                    person_club_activities = club_details[club_details['姓名'] == selected_name]
                    
                    if not person_club_activities.empty:
                        # 按日期排序
                        person_club_activities = person_club_activities.sort_values('社團活動日期')
                        
                        # 顯示社團活動表格
                        st.markdown("**社團活動明細表**")
                        display_columns = ['社團活動日期', '參加社團', '得分']
                        st.dataframe(
                            person_club_activities[display_columns],
                            use_container_width=True,
                            hide_index=True
                        )
                        
                        # 建立Stacked Area Chart
                        st.markdown("**社團活動得分趨勢圖**")
                        
                        # 準備圖表資料
                        chart_data = person_club_activities.copy()
                        chart_data['社團活動日期'] = pd.to_datetime(chart_data['社團活動日期'])
                        chart_data = chart_data.sort_values('社團活動日期')
                        
                        # 計算累計得分
                        chart_data['累計得分'] = chart_data['得分'].cumsum()
                        
                        # 使用plotly建立Stacked Area Chart
                        import plotly.express as px
                        import plotly.graph_objects as go
                        
                        fig = go.Figure()
                        
                        # 設定X軸起始日期為2025/8/8
                        start_date = pd.to_datetime('2025-08-08')
                        
                        # 添加面積圖
                        fig.add_trace(go.Scatter(
                            x=chart_data['社團活動日期'],
                            y=chart_data['累計得分'],
                            mode='lines+markers',
                            fill='tonexty',
                            name='累計得分',
                            hovertemplate='<b>日期:</b> %{x}<br>' +
                                        '<b>累計得分:</b> %{y}<br>' +
                                        '<b>參加社團:</b> %{customdata}<br>' +
                                        '<extra></extra>',
                            customdata=chart_data['參加社團']
                        ))
                        
                        fig.update_layout(
                            title='社團活動累計得分趨勢',
                            xaxis_title='社團活動日期',
                            yaxis_title='累計得分',
                            showlegend=False,
                            height=400,
                            xaxis=dict(
                                range=[start_date, chart_data['社團活動日期'].max()],
                                type='date'
                            )
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # 顯示統計摘要
                        total_activities = len(person_club_activities)
                        total_score = person_club_activities['得分'].sum()
                        st.info(f"📊 社團活動摘要：共參加 **{total_activities}** 次活動，累計得分 **{total_score}** 分")
                    else:
                        st.info("暫無社團活動參與記錄")
                        
                except Exception as e:
                    st.error(f"載入社團活動資料時發生錯誤：{str(e)}")
                    # 回退到原有顯示方式
                    if person_details['club']['total_activities']:
                        for i, activity in enumerate(person_details['club']['total_activities'], 1):
                            st.markdown(f"{i}. {activity}")
                
                # 下載個人詳細報告
                st.markdown("---")
                
                # 準備下載資料
                download_data = []
                download_data.append(['類別', '項目', '總次數', '總分數'])
                download_data.append(['日常運動', '運動', person_details['exercise']['total_count'], person_details['exercise']['total_score']])
                download_data.append(['健康飲食', '飲食', person_details['diet']['total_count'], person_details['diet']['total_score']])
                download_data.append(['額外加分', '額外活動', person_details['bonus']['total_count'], person_details['bonus']['total_score']])
                download_data.append(['社團活動', '社團', person_details['club']['total_count'], person_details['club']['total_score']])
                
                download_text = '\n'.join([','.join(map(str, row)) for row in download_data])
                
                st.download_button(
                    label="📥 下載個人活動報告",
                    data=download_text,
                    file_name=f"{selected_name}_個人活動報告.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.warning("無法取得詳細活動資料，請確認資料來源")
            
        else:
            st.error(f"找不到 {selected_name} 的資料")


def display_activity_intro_tab():
    """顯示活動簡介頁"""
    st.subheader("📝 活動簡介")
    
    try:
        # 讀取活動簡介檔案 - 嘗試多個可能的路徑
        current_dir = os.path.dirname(os.path.abspath(__file__))
        possible_paths = [
            os.path.join(current_dir, '活動簡介.txt'),  # 同目錄
            os.path.join(os.path.dirname(current_dir), '活動簡介.txt'),  # 上層目錄（src的話）
            '活動簡介.txt'  # 相對路徑
        ]
        
        content = None
        for intro_path in possible_paths:
            try:
                with open(intro_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                break
            except FileNotFoundError:
                continue
        
        if content:
            # 顯示內容
            st.markdown(content)
        else:
            raise FileNotFoundError("活動簡介檔案未找到")
        
    except FileNotFoundError:
        # 如果找不到檔案，顯示預設內容
        st.markdown("""
        ## 🏃‍♂️ 健康達人積分賽
        
        ### ✅ 活動簡介
        本次「健康達人積分賽」以「運動＋健康飲食＋達成合理體脂」為核心，
        陪伴大家養成良好生活習慣，達成健康減脂或維持理想體態的目標💪
        
        📅 **活動期間：** 2025/08/08 - 2025/10/31  
        📌 **報名截止：** 2025/07/31  
        
        ### ✅ 活動適合誰？
        👟 無論你是哪一種，都很適合參加——
        1. **原本就有運動習慣：** 邊運動邊賺獎金，還能衝排行榜！
        2. **想培養運動習慣：** 給自己三個月，建立健康生活步調！
        3. **想認識運動夥伴：** 健行、羽球、瑜珈、桌球，一起動起來！
        
        ### ✅ 參加辦法
        📸 拍照或截圖運動記錄、上傳、拿分數三大類別：
        1. 體脂前後測
        2. 日常運動紀錄（健走、超慢跑、瑜珈、健身、伸展拉筋、氣功、滑板、潛水衝浪都算）
        3. 指定主題健康飲食紀錄（拍照＋上傳）
        
        📈 每一項都能累積積分，爭奪健康達人榜！
        
        ### ✅ 獎勵內容
        🏆 **總獎金超過 30,000 元！**
        
        #### 男子組獎金
        | 名次 | 獎金 |
        |------|------|
        | 第1名 | NT$6,000 |
        | 第2-4名 | 各 NT$3,000 |
        | 第5-9名 | 各 NT$2,000 |
        | 第10-14名 | 各 NT$1,000 |
        
        #### 女子組獎金
        | 名次 | 獎金 |
        |------|------|
        | 第1-2名 | 各 NT$6,000 |
        | 第3-8名 | 各 NT$3,000 |
        | 第9-18名 | 各 NT$2,000 |
        | 第19-28名 | 各 NT$1,000 |
        
        **新增條件：總分必須大於等於200分才能獲得獎金！**
        
        ---
        
        💪 加油！下一位健康達人就是您！
        """)
    except Exception as e:
        st.error(f"❌ 讀取活動簡介時發生錯誤：{str(e)}")


def display_statistics_tab(df):
    """顯示統計圖表頁"""
    st.subheader("📈 活動統計分析")
    
    # 活動次數與分數統計圓餅圖
    st.markdown("### 活動參與統計")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 活動次數圓餅圖
        activity_counts = {
            '運動': df.filter(regex='運動|日常').notna().sum().sum(),
            '飲食': df.filter(regex='飲食').notna().sum().sum(),
            '社團活動': df.filter(regex='羽球|瑜珈|桌球|戶外').notna().sum().sum(),
            '額外加分': df.filter(regex='bonus|加分').notna().sum().sum()
        }
        
        fig1 = px.pie(
            values=list(activity_counts.values()),
            names=list(activity_counts.keys()),
            title='活動次數分布',
            color_discrete_map={
                '運動': '#FF6B6B',
                '飲食': '#4ECDC4', 
                '社團活動': '#45B7D1',
                '額外加分': '#96CEB4'
            }
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # 分數圓餅圖
        activity_scores = {
            '運動': df.filter(regex='運動|日常').fillna(0).sum().sum(),
            '飲食': df.filter(regex='飲食').fillna(0).sum().sum(),
            '社團活動': df.filter(regex='羽球|瑜珈|桌球|戶外').fillna(0).sum().sum(),
            '額外加分': df.filter(regex='bonus|加分').fillna(0).sum().sum()
        }
        
        fig2 = px.pie(
            values=list(activity_scores.values()),
            names=list(activity_scores.keys()),
            title='活動分數分布',
            color_discrete_map={
                '運動': '#FF6B6B',
                '飲食': '#4ECDC4',
                '社團活動': '#45B7D1', 
                '額外加分': '#96CEB4'
            }
        )
        st.plotly_chart(fig2, use_container_width=True)
    
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
    
    # 獲取活動分析器和活動統計
    activity_analyzer = loader.get_activity_analyzer()
    activity_stats = activity_analyzer.get_overall_statistics()
    
    # 顯示關鍵指標
    display_metrics(stats, activity_stats)
    
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
        display_personal_query_tab(ranking_engine, activity_analyzer)
    
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

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

HealthMaster is a Streamlit-based dashboard for a health competition scoring system (健康達人積分賽). It provides real-time rankings, individual score tracking, and statistical visualizations for participants categorized by gender (male/female groups).

## Core Architecture

### 3-Layer Modular Design

1. **Data Layer** (`src/data_loader.py`)
   - Handles Excel file loading from `data/20250903分數累積表.xlsx`
   - Flexible column detection (supports column position changes)
   - Data validation and cleaning with error handling
   - 5-minute caching mechanism for performance

2. **Business Logic** (`src/ranking_engine.py`)
   - Gender-based ranking calculation (生理女/生理男)
   - Prize money assignment for top 14 in each group
   - Individual score breakdown analysis
   - Department statistics and club activity tracking

3. **Presentation Layer** (`src/dashboard.py`)
   - Streamlit web interface with 5 main tabs
   - Real-time search and filtering capabilities
   - Interactive Plotly charts for data visualization
   - CSV export functionality

### Key Design Patterns

- **Flexible Schema**: Automatically detects required columns (`姓名`, `性別`, `total`) regardless of position
- **Gender Separation**: Independent ranking systems for male/female participants
- **Prize Configuration**: Hardcoded prize structure in `RankingEngine.PRIZE_CONFIG`
- **Caching Strategy**: Uses Streamlit's `@st.cache_data` with TTL for data efficiency

## Development Commands

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run locally (Windows)
scripts\run_local.bat

# Run locally (manual)
cd src
streamlit run dashboard.py
```

### Data Updates
```bash
# Automated update (Windows)
scripts\update_data.bat

# Automated update (Unix)
chmod +x scripts/update_data.sh
./scripts/update_data.sh
```

### No Build/Test Commands
This project uses Python/Streamlit without a traditional build system. No linting, testing, or build commands are configured in the repository.

## Data Requirements

### Excel File Structure (data資料夾)
系統載入兩個不同時間區間的Excel檔案，自動合併參賽者資料。

#### 主要工作表：
1. **分數累積** - 參賽者總分與基本資料
2. **ALL活動數據統計(運動+飲食)--分數計算表** - 運動與飲食明細
3. **個人bonus分** - 額外加分活動記錄

#### 分數累積工作表結構：
- **A-J欄**: 參賽者基本資料
  - E欄: `姓名` (合併時的KEY值)
  - F欄: `性別` (生理男/生理女，顯示時自動轉為男/女)
- **K欄**: 日常運動得分 (運動次數 × 10)
- **L欄**: 每周飲食得分 (飲食次數 × 10)  
- **M欄**: 額外加分得分 (額外活動次數 × 30)
- **N欄-total前**: 社團活動得分 (有分數即表示參加)
- **total欄**: 該期間總分

#### ALL活動數據統計工作表結構：
- **D欄**: `姓名` (與分數累積表E欄串接)
- **E欄**: 飲食次數
- **G欄**: 運動次數

#### 個人bonus分工作表結構：
- **A欄**: 參賽者姓名 (出現次數 = 額外加分活動次數)

### 資料整理邏輯：
系統以參賽者為維度整理以下資料：
1. 日常運動: 得分與次數統計
2. 每周飲食: 得分與次數統計  
3. 額外加分: 得分與次數統計
4. 社團活動: 得分與參與項目統計

### 顯示位置：
- **個人查詢頁面**: 顯示個人詳細的四類活動統計
- **總覽頁面**: 顯示全體參賽者的四類活動總計

## Prize System

Automated prize assignment for top 14 participants in each gender group:
- 1st place: NT$6,000 🥇
- 2nd-4th place: NT$3,000 each 🥈
- 5th-9th place: NT$2,000 each 🥉
- 10th-14th place: NT$1,000 each 🏅

## Common Development Tasks

### Adding New Visualizations
Extend `display_statistics_tab()` in `dashboard.py` using Plotly Express patterns already established.

### Modifying Prize Structure
Update `PRIZE_CONFIG` dictionary in `ranking_engine.py:13-28`.

### Adding New Data Sources
Extend `extract_score_details()` method in `data_loader.py` to recognize new column patterns.

### Customizing UI Themes
Modify CSS styles in `dashboard.py:22-50` or update `.streamlit/config.toml`.

## Deployment Architecture

- **Platform**: Streamlit Cloud (recommended)
- **Repository**: GitHub with automated deployment
- **Update Flow**: Excel edit → Git push → Auto-deploy (1-2 minutes)
- **Access**: Public URL for all participants

## Error Handling Philosophy

The system prioritizes resilience over strict validation:
- Missing optional columns are gracefully ignored
- Invalid data entries are cleaned rather than rejected
- Warning messages inform users without blocking functionality
- Data validation separates critical errors from warnings

## File Paths and Dependencies

- Excel data: `data/20250903分數累積表.xlsx` (relative to project root)
- Static imports: All internal dependencies use relative imports
- External dependencies: Only uses packages in `requirements.txt`

## Performance Considerations

- Data caching prevents repeated Excel reads
- Lazy loading of heavy visualizations
- Efficient pandas operations for large datasets
- Minimal state management in Streamlit
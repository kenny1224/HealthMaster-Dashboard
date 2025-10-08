# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

HealthMaster is a Streamlit-based dashboard for a health competition scoring system (健康達人積分賽). It provides real-time rankings, individual score tracking, and statistical visualizations for participants categorized by gender (male/female groups).

## Core Architecture

### 3-Layer Modular Design

1. **Data Layer** (`src/data_loader.py`)
   - Handles Excel file loading from `data/每周分數累積.xlsx`
   - Processes multiple worksheets: 總表, period sheets (0808-0830, 0831-0921), and 帳號整理
   - ID-based data merging and aggregation
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

- **ID-based Data Integration**: Uses `id` as primary key for merging period worksheets and participant data
- **Gender Separation**: Independent ranking systems for male/female participants (removes "生理" prefix from gender field)
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

**Primary Data Source**: `data/每周分數累積.xlsx`

#### Worksheets Structure:
1. **總表** - Aggregated scores across all periods (Key: `id`)
2. **Period Worksheets** - Individual period data (e.g., 0808-0830, 0831-0921)
   - Key: `id`
   - More period worksheets will be added over time
3. **帳號整理** - Participant master data
   - Key: `帳號(最新8/8)2`
   - Gender field: Remove "生理" prefix when displaying (生理男 → 男, 生理女 → 女)

#### Period Worksheet Column Structure:
- **L欄**: 日常運動得分 (運動次數 = 得分 ÷ 10)
- **M欄**: 飲食得分 (飲食次數 = 得分 ÷ 10)
- **N欄**: 個人Bonus得分 (Bonus次數 = 得分 ÷ 30)
- **O欄 ~ total欄前**: 社團活動得分
  - Column names contain activity name and date (e.g., "8/13 羽球社")
  - Empty or 0 = did not participate

### Score Calculation Logic:

#### A. Score Conversion:
1. **日常運動**: 日常運動得分 ÷ 10 = 日常運動次數
2. **飲食**: 飲食得分 ÷ 10 = 飲食次數
3. **個人Bonus**: 個人Bonus得分 ÷ 30 = 個人Bonus次數
4. **社團活動**: Non-zero value in columns O onwards = participated

#### B. Data Processing Pipeline:

**Step 1: Period Data Aggregation**
- Merge period worksheets (0808-0830, 0831-0921, etc.)
- Extract fields: 回合期間, 姓名, 日常運動得分, 日常運動次數, 飲食得分, 飲食次數, 個人Bonus得分, 個人Bonus次數

**Step 2: Club Activity Transformation (Wide to Long)**
- Transform club activity columns (O欄 onwards) from wide to long format
- Parse column names to extract:
  - **社團活動日期**: Date portion (e.g., "8/13" → "2025/08/13", default year: 2025)
  - **參加社團**: Activity name (e.g., "羽球社", "桌球社挑戰賽")
- Example transformations:
  - "8/13 羽球社" → Date: "2025/08/13", Activity: "羽球社"
  - "9/2 桌球社挑戰賽" → Date: "2025/09/02", Activity: "桌球社挑戰賽"
- UNION all period data to create **參加社團活動明細表**
- Fields: 回合期間, 姓名, 社團活動日期, 參加社團

**Step 3: Club Activity Aggregation**
- Count records per 姓名 → 參加社團次數
- Sum scores → 參加社團得分
- Join with Step 1 data using (姓名, 回合期間) as key

**Final Output: 參加者活動統計表**
- 回合期間
- 姓名
- 日常運動得分, 日常運動次數
- 飲食得分, 飲食次數
- 個人Bonus得分, 個人Bonus次數
- 參加社團得分, 參加社團次數

### Dashboard Data Source:
**All dashboard statistics must use data from 參加者活動統計表**

### Display Locations:
- **個人查詢頁面**: Individual detailed statistics for all 4 activity types
- **總覽頁面**: Aggregate statistics for all participants across 4 activity types

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

- Excel data: `data/每周分數累積.xlsx` (relative to project root)
- Legacy files (deprecated):
  - `data/20250903分數累積表(0808-0830).xlsx`
  - `data/20250905分數累積表(0831-0920).xlsx`
- Static imports: All internal dependencies use relative imports
- External dependencies: Only uses packages in `requirements.txt`

## Performance Considerations

- Data caching prevents repeated Excel reads
- Lazy loading of heavy visualizations
- Efficient pandas operations for large datasets
- Minimal state management in Streamlit
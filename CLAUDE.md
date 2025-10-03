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

### Required Excel Structure
- **Sheet Name**: `分數累積` (hardcoded in DataLoader)
- **Required Columns**: `姓名` (name), `性別` (gender), `total` (total score)
- **Valid Gender Values**: `生理女` (female), `生理男` (male)
- **Column Position**: Flexible - system auto-detects column locations

### Optional Columns
- `所屬部門` (department)
- `體脂是否上傳` (body fat upload status)
- Club activity columns containing keywords: `羽球`, `瑜珈`, `桌球`, `戶外`
- Score detail columns with keywords: `運動`, `飲食`, `bonus`

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
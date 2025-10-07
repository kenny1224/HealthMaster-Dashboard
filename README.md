# 🏥 健康達人積分賽 - 儀表板系統

> 活動期間：2025/08/08 - 2025/10/31  
> 總獎金超過 30,000 元！

## 📋 目錄

- [專案簡介](#專案簡介)
- [功能特色](#功能特色)
- [快速開始](#快速開始)
- [本地測試](#本地測試)
- [部署到雲端](#部署到雲端)
- [資料更新流程](#資料更新流程)
- [專案結構](#專案結構)
- [常見問題](#常見問題)

---

## 📊 專案簡介

這是一個為「健康達人積分賽」設計的即時排行榜儀表板系統，支援：
- ✅ 男女分組排名
- ✅ 完整參賽者名單與分數
- ✅ 個人成績查詢
- ✅ 視覺化統計圖表
- ✅ 簡易資料更新流程

---

## ✨ 功能特色

### 1. 📊 總覽頁
- 關鍵指標卡片（參與人數、運動/飲食紀錄、體脂完成率）
- 男女組 Top 10 排行榜快速預覽

### 2. 🌸 女性組完整排名
- 全部 57 位參賽者完整排名
- 支援姓名搜尋
- 支援部門篩選
- 可下載 CSV 檔案

### 3. 💪 男性組完整排名
- 全部 30 位參賽者完整排名
- 相同功能與女性組

### 4. 🔍 個人查詢
- 輸入姓名查詢個人詳細成績
- 顯示排名、分數明細、獎金資訊
- 顯示完成項目與社團活動記錄
- 提供衝刺建議

### 5. 📈 統計圖表
- 男女分數分布對比
- 各部門參與度統計
- 分數分段分布圖

---

## 🚀 快速開始

### 環境需求

- Python 3.8 或以上
- pip（Python 套件管理工具）

### 安裝步驟

1. **安裝 Python 套件**

```bash
pip install -r requirements.txt
```

2. **確認資料檔案位置**

確保 `data/20250903分數累積表.xlsx` 存在於正確位置。

3. **啟動儀表板**

```bash
# Windows 用戶：雙擊執行
scripts\run_local.bat

# 或手動執行
cd src
streamlit run dashboard.py
```

4. **開啟瀏覽器**

自動開啟 http://localhost:8501

---

## 💻 本地測試

### Windows 用戶

```bash
# 直接雙擊
scripts\run_local.bat
```

### Mac/Linux 用戶

```bash
chmod +x scripts/run_local.sh
./scripts/run_local.sh
```

### 手動啟動

```bash
cd src
streamlit run dashboard.py
```

---

## ☁️ 部署到雲端（Streamlit Cloud）

### 步驟 1：建立 GitHub Repository

1. 前往 [GitHub](https://github.com)
2. 點擊 `New repository`
3. 命名：`HealthMaster-Dashboard`
4. 設為 `Public`（若要分享連結）
5. 點擊 `Create repository`

### 步驟 2：上傳程式碼到 GitHub

```bash
# 初始化 Git
git init

# 新增所有檔案
git add .

# 提交
git commit -m "初始化健康達人積分賽儀表板"

# 連接到 GitHub（替換成您的 repository URL）
git remote add origin https://github.com/您的帳號/HealthMaster-Dashboard.git

# 推送
git branch -M main
git push -u origin main
```

### 步驟 3：部署到 Streamlit Cloud

1. 前往 [share.streamlit.io](https://share.streamlit.io)
2. 點擊 `New app`
3. 連接 GitHub 帳號
4. 選擇 `HealthMaster-Dashboard` repository
5. 設定：
   - **Main file path**: `app.py` (新增的入口文件)
   - **Python version**: 3.9 或以上
6. 點擊 `Deploy`
7. 等待 2-3 分鐘完成部署

### 步驟 4：獲得公開網址

部署完成後，您會獲得一個網址，例如：
```
https://healthmaster-dashboard-xxxxx.streamlit.app
```

這個網址可以分享給所有參賽者！

---

## 🔄 資料更新流程

### 方式 1：一鍵更新（推薦）

**Windows 用戶**

1. 編輯 `data/20250903分數累積表.xlsx`（新增最新分數）
2. 儲存檔案
3. 雙擊執行 `scripts\update_data.bat`
4. 等待 1-2 分鐘，儀表板自動更新

**Mac/Linux 用戶**

```bash
chmod +x scripts/update_data.sh
./scripts/update_data.sh
```

### 方式 2：手動更新

1. **編輯 Excel 檔案**
   - 更新 `data/20250903分數累積表.xlsx`

2. **上傳到 GitHub**
   ```bash
   git add data/20250903分數累積表.xlsx
   git commit -m "更新分數資料"
   git push origin main
   ```

3. **等待自動部署**
   - Streamlit Cloud 會自動偵測更新
   - 約 1-2 分鐘後生效

### 方式 3：使用 GitHub 網頁介面

1. 前往您的 GitHub repository
2. 進入 `data` 資料夾
3. 點擊 `20250903分數累積表.xlsx`
4. 點擊 `Delete file`
5. 點擊 `Upload files`
6. 拖曳更新後的 Excel 檔案
7. 點擊 `Commit changes`

---

## 📁 專案結構

```
HealthMaster/
│
├── src/                          # 程式碼目錄
│   ├── dashboard.py              # 主儀表板程式
│   ├── data_loader.py            # 資料載入模組
│   ├── ranking_engine.py         # 排名計算引擎
│   └── activity_analyzer.py      # 活動詳細分析器
│
├── data/                         # 資料目錄
│   ├── 20250903分數累積表.xlsx    # Excel 資料檔案 (期間1)
│   └── 20250905分數累積表(0831-0920).xlsx # Excel 資料檔案 (期間2)
│
├── scripts/                      # 工具腳本
│   ├── update_data.bat           # Windows 更新腳本
│   ├── update_data.sh            # Mac/Linux 更新腳本
│   └── run_local.bat             # 本地測試腳本
│
├── .streamlit/                   # Streamlit 設定
│   └── config.toml               # 主題與設定
│
├── app.py                        # Streamlit Cloud 入口文件
├── packages.txt                  # 系統套件清單  
├── requirements.txt              # Python 套件清單
├── .gitignore                    # Git 忽略清單
├── README.md                     # 本說明檔案
└── 活動簡介.txt                  # 活動介紹
```

---

## 🔧 資料格式要求

### Excel 檔案結構

**必要欄位**（位置不限）：
- `姓名`：參賽者姓名
- `性別`：必須為「生理女」或「生理男」
- `total`：總分（用於排名）

**建議欄位**：
- `所屬部門`：部門名稱
- `體脂是否上傳`：完成狀態
- 其他運動/飲食/社團活動欄位

### 注意事項

✅ **欄位位置可以改變**（程式會自動尋找）  
✅ **可以新增欄位**（不影響既有功能）  
❌ **不可刪除必要欄位**（姓名、性別、total）  
❌ **性別欄位值必須正確**（生理女/生理男）

---

## ❓ 常見問題

### Q1：儀表板無法啟動？

**A：** 檢查是否已安裝所有套件
```bash
pip install -r requirements.txt
```

### Q2：找不到資料檔案？

**A：** 確認檔案路徑正確
```
data/20250903分數累積表.xlsx
```

### Q3：更新資料後沒有變化？

**A：** 
1. 點擊儀表板右上角「🔄 重新載入」按鈕
2. 或清除瀏覽器快取並重新整理

### Q4：如何修改主題顏色？

**A：** 編輯 `.streamlit/config.toml`
```toml
[theme]
primaryColor = "#4CAF50"  # 主色調
```

### Q5：可以離線使用嗎？

**A：** 可以！只要在本地執行：
```bash
cd src
streamlit run dashboard.py
```

### Q6：如何增加新的統計圖表？

**A：** 編輯 `src/dashboard.py` 中的 `display_statistics_tab()` 函數，
使用 Plotly 新增圖表。

### Q7：部署後網址可以自訂嗎？

**A：** Streamlit Cloud 免費版使用自動生成的網址。
若需自訂域名，可使用付費版或部署到其他平台（如 Railway、Render）。

---

## 📞 技術支援

如有問題，請檢查：
1. Python 版本（需 3.8+）
2. 套件是否正確安裝
3. Excel 檔案格式是否正確
4. GitHub 是否正確推送

---

## 🎉 致謝

感謝所有參與健康達人積分賽的夥伴們！  
讓我們一起養成健康生活習慣，達成理想體態目標！💪

---

**最後更新：** 2025/10/07  
**版本：** 2.0.0 - 多期間Excel分析版本  
**授權：** MIT License

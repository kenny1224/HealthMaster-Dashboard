# 🚀 部署指南

## 快速部署到 Streamlit Cloud（推薦）

### 步驟 1：GitHub 設定

1. **建立 GitHub Repository**
   ```
   前往：https://github.com/new
   Repository 名稱：HealthMaster-Dashboard
   設為 Public
   ```

2. **上傳程式碼**
   ```bash
   # 在專案目錄執行
   git init
   git add .
   git commit -m "初始化健康達人積分賽儀表板"
   git branch -M main
   git remote add origin https://github.com/您的帳號/HealthMaster-Dashboard.git
   git push -u origin main
   ```

### 步驟 2：Streamlit Cloud 部署

1. **註冊/登入**
   - 前往：https://share.streamlit.io
   - 使用 GitHub 帳號登入

2. **建立新應用**
   - 點擊「New app」
   - 選擇 repository：`HealthMaster-Dashboard`
   - Main file path：`src/dashboard.py`
   - 點擊「Deploy」

3. **等待部署完成**（約 2-3 分鐘）

4. **獲得網址**
   ```
   https://healthmaster-dashboard-xxxxx.streamlit.app
   ```

---

## 📊 資料更新工作流程

### 日常更新流程

```
┌─────────────────────────────────────────────┐
│ 1. 編輯 Excel（新增今日分數）                │
│    ↓                                        │
│ 2. 雙擊 update_data.bat（自動上傳 GitHub）   │
│    ↓                                        │
│ 3. 等待 1-2 分鐘                            │
│    ↓                                        │
│ 4. 儀表板自動更新 ✅                         │
└─────────────────────────────────────────────┘
```

### Windows 更新步驟

1. 編輯 `data\20250903分數累積表.xlsx`
2. 儲存檔案
3. 雙擊 `scripts\update_data.bat`
4. 等待完成

### 手動更新步驟

```bash
git add data/20250903分數累積表.xlsx
git commit -m "更新分數 - 2025/09/03"
git push origin main
```

---

## 🌐 分享給參賽者

### 取得儀表板網址

部署完成後，您會獲得一個永久網址：
```
https://healthmaster-dashboard-xxxxx.streamlit.app
```

### 分享方式

**Email 範本：**
```
主旨：健康達人積分賽 - 即時排行榜上線！

各位健康達人：

即時排行榜已上線！您可以隨時查看：
🔗 https://healthmaster-dashboard-xxxxx.streamlit.app

功能特色：
✅ 即時排名（男女分組）
✅ 個人成績查詢
✅ 完整參賽者名單
✅ 視覺化統計圖表

資料每日更新，記得常回來看看您的進步！

加油！下一位健康達人就是您！💪
```

**LINE/Teams 訊息範本：**
```
🏥 健康達人積分賽排行榜上線了！

📊 即時排名查詢：
https://healthmaster-dashboard-xxxxx.streamlit.app

快去看看你現在排第幾名！💪
```

---

## 🔒 安全性設定

### 公開 vs 私密

**目前設定：公開**
- 任何人都可查看排行榜
- 適合激勵參與

**若需要密碼保護：**

1. 編輯 `.streamlit/secrets.toml`（本地不上傳）
   ```toml
   password = "your_password"
   ```

2. 在 Streamlit Cloud 設定 secrets

3. 在 `dashboard.py` 加入驗證邏輯

---

## 📱 行動裝置支援

儀表板已針對行動裝置優化：
- ✅ 手機瀏覽器
- ✅ 平板電腦
- ✅ 桌面電腦

建議瀏覽器：Chrome、Safari、Edge

---

## 🛠️ 進階設定

### 自訂網址

若需要自訂域名（如 `health.yourcompany.com`）：

1. 在 Streamlit Cloud 升級到 Team 方案
2. 或部署到其他平台：
   - Railway（https://railway.app）
   - Render（https://render.com）
   - Heroku

### 效能優化

**快取設定**（已內建）：
```python
@st.cache_data(ttl=300)  # 5分鐘快取
```

**調整快取時間**：
- 編輯 `src/data_loader.py`
- 修改 `ttl` 參數（秒）

---

## 📈 監控與維護

### 查看訪問統計

1. 登入 Streamlit Cloud
2. 選擇您的 app
3. 查看 Analytics

### 錯誤排查

**儀表板無法載入**
- 檢查 GitHub 上的資料檔案是否存在
- 查看 Streamlit Cloud 的 logs

**資料更新未生效**
- 確認 GitHub 已更新
- 等待 2-3 分鐘
- 清除瀏覽器快取

**排名異常**
- 檢查 Excel 的 `total` 欄位
- 確認 `性別` 欄位正確（生理女/生理男）

---

## 💡 最佳實踐

### 資料更新時機

**建議：**
- 每日傍晚更新（下班前）
- 週五更新後發送通知
- 活動結束前每日更新

### 備份策略

**GitHub 自動備份**
- 每次更新都有歷史記錄
- 可隨時回溯任何版本

**手動備份**
```bash
# 下載所有歷史版本
git log --all --oneline
git checkout <commit-hash>
```

### 溝通策略

**定期通知**
- 每週發送排名更新通知
- 提醒參賽者查看進度
- 公布重要里程碑

**激勵參與**
- 分享前三名的進步故事
- 強調距離獎金線的分數
- 鼓勵社群互動

---

## 🎯 活動結束後

### 保存記錄

1. **下載最終排名**
   - 從儀表板下載 CSV
   - 備份 Excel 原始檔

2. **產生報告**
   - 統計圖表截圖
   - 參與度分析
   - 成效總結

3. **封存專案**
   ```bash
   git tag v1.0-final
   git push --tags
   ```

### 關閉儀表板（可選）

在 Streamlit Cloud：
- Settings → Delete app

或保留供未來活動使用。

---

## 📞 支援

如遇到問題：
1. 查看 README.md 常見問題
2. 檢查 GitHub Issues
3. 聯繫技術支援

---

**部署愉快！** 🚀

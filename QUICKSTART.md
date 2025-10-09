# ⚡ 快速開始指南

## 🎯 5分鐘快速部署

### 前置需求

- ✅ 已安裝 Python 3.8+
- ✅ 有 GitHub 帳號
- ✅ Excel 資料檔案準備好

---

## 📝 步驟 1：本地測試（2分鐘）

### Windows 用戶

```bash
# 1. 安裝套件
pip install -r requirements.txt

# 2. 啟動儀表板
雙擊 scripts\run_local.bat
```

### Mac/Linux 用戶

```bash
# 1. 安裝套件
pip install -r requirements.txt

# 2. 啟動儀表板
cd src
streamlit run dashboard.py
```

瀏覽器自動開啟 → http://localhost:8501

✅ **確認儀表板正常運作**

---

## ☁️ 步驟 2：部署到雲端（3分鐘）

### 2.1 上傳到 GitHub

```bash
# 初始化 Git
git init

# 新增檔案
git add .

# 提交
git commit -m "初始化儀表板"

# 推送到 GitHub（先在 GitHub 建立 repository）
git branch -M main
git remote add origin https://github.com/您的帳號/HealthMaster-Dashboard.git
git push -u origin main
```

### 2.2 部署到 Streamlit Cloud

1. **前往** https://share.streamlit.io
2. **登入** GitHub 帳號
3. **點擊** "New app"
4. **選擇** repository: `HealthMaster-Dashboard`
5. **設定** Main file: `src/dashboard.py`
6. **點擊** "Deploy"
7. **等待** 2-3 分鐘

✅ **獲得公開網址！**

---

## 🔄 步驟 3：更新資料（30秒）

### 每日更新流程

1. **編輯 Excel**
   ```
   編輯 data\每周分數累積.xlsx
   新增今日分數 → 儲存
   ```

2. **產生統計表**
   ```
   python src/new_data_processor.py
   ```

3. **一鍵更新**
   ```
   雙擊 scripts\update_data.bat
   ```

4. **等待生效**
   ```
   1-2 分鐘後自動更新
   ```

✅ **完成！**

---

## 📱 步驟 4：分享給參賽者

複製您的儀表板網址：
```
https://healthmaster-dashboard-xxxxx.streamlit.app
```

**發送給參賽者：**
- Email
- LINE
- Teams
- 公告欄

---

## 🎉 完成！

現在您已經有一個：
- ✅ 即時更新的排行榜
- ✅ 公開的網址連結
- ✅ 簡易的更新流程

---

## 📚 更多資訊

- 詳細使用說明：[README.md](README.md)
- 部署進階設定：[DEPLOYMENT.md](DEPLOYMENT.md)
- 常見問題：[README.md#常見問題](README.md#常見問題)

---

## 🆘 遇到問題？

### 儀表板無法啟動
```bash
# 重新安裝套件
pip install --upgrade -r requirements.txt
```

### 找不到資料檔案
```
確認路徑：data/每周分數累積.xlsx
確認已產生：data/參加者活動統計表.xlsx
```

### GitHub 推送失敗
```bash
# 檢查遠端連結
git remote -v

# 重新設定
git remote set-url origin https://github.com/您的帳號/HealthMaster-Dashboard.git
```

---

**準備好了嗎？開始吧！** 🚀

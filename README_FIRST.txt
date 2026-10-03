Junba AI Transcriber v3.8.1 REPACK
==================================

這是一個「完整建置封包」，不是上一版的單純 Hotfix Overlay。
GitHub Actions 會自動抓取並固定使用原始 Junba AI Transcriber v3.8 的已知版本，
再套用 v3.8.1 修改，因此不會再發生「找不到 app/ui/main_window.py」的問題。

這次只修改 Junba_AI_Transcriber_v3.8 系列，不會碰 Junba KTV MultiTrack 專案。

本版包含：
1. 「開啟／選擇核對播放器」：可自動找最近 HTML，也可手動選 HTML。
2. Word 表格重新配置：逐字內容 > 時間 > 講者；逐字內容字體較大；橫向版面。
3. 每支錄音輸出到獨立資料夾：01_原始檔名、02_原始檔名……
4. Android APK：手機版 Gemini 語音轉文字，直式/橫式可自適應。
5. 新增 Markdown 輸出選項；KTV HTML 也可匯入 .md/.markdown。

GitHub 使用方式：
- 建議建立一個新的 Repository，例如 Junba_AI_Transcriber_v3.8.1_REPACK
- 將本 ZIP 解壓後的「內容」全部上傳到 Repo 根目錄。
- Workflow 必須位於：.github/workflows/build-windows-v3.8.yml
- Push 後 Actions 會自動執行。

預期 Artifact：
- Junba-AI-Transcriber-v3.8.1-Repack-Portable-Windows-x64
- Junba-AI-Transcriber-v3.8.1-Repack-Single-EXE-Windows-x64
- Junba-AI-Transcriber-v3.8.1-Android-APK

Android 建置已改為：
- 先尋找 runner 內真正的 sdkmanager
- 找不到時，自動安裝 Android command-line tools
- 再安裝 Android 35 SDK
不再直接假設 sdkmanager 已存在 PATH。

固定來源版本（避免來源日後變更造成建置結果飄移）：
- Windows v3.8 base commit: 847f91902b2569c5791366bc73f45713d2f2b94a
- Android source commit: 5004a751dc14173c2a42f41ecd7d5143d2a94305

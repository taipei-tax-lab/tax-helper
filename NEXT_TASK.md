# TAX AI — Next Task

Last updated: 2026-10-08 (Asia/Taipei)
Status: **PHASE A AUDIT COMPLETE — SOURCE IMPORT DECISION PENDING**
Owner: **Web Codex**；CX 資源由 dialogflow-cx-qa-framework 工作流處理。
Authorization: **本輪僅唯讀盤點、文件與離線方案；未授權來源公開／匯入、Phase B/C 實作、部署或 GCP 寫入**。

## 本輪完成（證據見 PROJECT_STATE.md）

- [x] 讀四份文件、fetch 並核對 GitHub baseline；確認 tax-helper 仍 Public。
- [x] 實際取得使用者 ZIP、驗證 checksum／entries、安全解壓至 repo 外；未假設已取得。
- [x] 有限 Secret scan；未將原始碼／內部題庫／ZIP／CSV 推送 Public repo。
- [x] 核對八個原始檔、questionBank schema／129題／11分類、空值／重複／metadata／2個孤立關聯及功能依賴。
- [x] 核對搜尋頁最小擴充點、快速搜尋／收藏／題庫／詳情／Excel／導覽不可破壞清單。
- [x] 唯讀固定1999 commit 的 transport／result-model／app／RESULT_CONTRACT／測試；提出重用與適配差距。
- [x] 提出最新單一問答卡、同 Session 追問、切模式不 reset、主動 reset、expiry／timeout／error／連續提問事件序列。
- [x] 提出二欄 deterministic converter 與離線／E2E 矩陣；尚未實作或產生正式 CSV。
- [x] 1999 Node 14/14、原 ZIP Chromium 8 組基線通過；未連 Production；整合後 E2E／真實 Excel 成功匯入尚未執行。
- [x] 更新既有 README／STATE／TASK；文件 commit SHA 與遠端驗證於收工回報提供。

## 新決策：Public Repo 與 GitHub Pages（2026-10-08）

- 使用者決定繼續保留 Public；不需要先改 Private。
- GitHub Pages 為預計採用的靜態部署方式，尚未啟用或獲准部署。
- Public 不代表全部 ZIP 或內部題庫皆獲公開核准；靜態 JS 題庫即使畫面隱藏也可被取得。

## 下一輪單一任務：檔案公開性檢查與原始碼納管準備

- [ ] fetch 最新文件及確認 Public；查核原始 ZIP 的 SHA-256 與可存取性。
- [ ] 逐檔檢視 ZIP 的八個檔案，標記「可公開／需確認／不可公開」，特別檢查題庫正文、內部連結、個資與憑證，文件不可引用疑似敏感原文。
- [ ] 說明網站是否依賴尚未核准公開的檔案；如果有，先列明限制及替代方案。
- [ ] 只有明確授權公開及納管的檔案才可原貌提交；有疑義須暫停匯入。不得順便修改網頁、建立 converter 或 AI UI。
- [ ] 更新 STATE／TASK 並推送文件，回報檢查結果、commit SHA、尚待決策項目。

### STOP

不自行更改 Repo visibility、不啟用 Pages、不部署、不修改 GCP/CX/1999；未核准的原始題庫、ZIP、CSV、憑證不得推送至 Public GitHub。Phase B/C 實作尚未授權。

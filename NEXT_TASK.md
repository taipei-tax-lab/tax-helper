# TAX AI — Next Task

Status: **PHASE A — AUDIT / PLAN ONLY**
Owner: **Web Codex**；CX 平行盤點由 `dialogflow-cx-qa-framework` 工作流處理。
Authorization: **唯讀盤點、文件更新、可驗證的離線提案；禁止部署與 GCP 資源寫入**。

## A1 — 新 repo 初始化／原始碼盤點
- [ ] 先讀 `README.md` → `AGENTS.md` → `PROJECT_STATE.md` → 本檔。
- [ ] 確認新 repo 可用，檢查是否 Public；在來源匯入前標示可能公開內部題庫的風險。
- [ ] 取得使用者提供的 TAX AI 網頁原始 ZIP（Codex 須能在自身環境實際存取，不能假裝可讀到 ChatGPT 附件）。若未提供，STOP，向使用者回報所需檔案路徑／上傳方式。
- [ ] 原始碼匯入前先檢查 Secret／敏感資料和不必要的大檔案；若 repo 仍為 Public，未經確認不得推送內部原始題庫。
- [ ] 唯讀盤點實際目錄、`questionBank.js` schema、問題數、空值／重複、快速搜尋和收藏／匯入／瀏覽的依賴。
- [ ] 盤點搜尋頁兩個模式的最小擴充點；列出既有功能不可破壞的清單。

## A2 — 1999 前端重用範圍
- [ ] 唯讀參考 `taipei-tax-lab/tpctax-1999-ai-web` 的 `assets/messenger-transport.js`、`assets/result-model.js`、`assets/app.js`、`docs/RESULT_CONTRACT.md`、相關測試。
- [ ] 提出**單一問答卡＋同 Session 多輪記憶**的事件序列、Reset、逾期、超時、錯誤及連續發問防護。
- [ ] 明確區分：切換模式不 reset；主動「重置提問」必須新 session；畫面僅最新問答，未展示完整 history。
- [ ] 提出 `questionBank.js` → `faq.csv` 二欄 deterministic converter 位置與驗證方式（先設計，尚不部署）。
- [ ] 提出離線 fixture／瀏覽器 E2E 測試矩陣，含快速搜尋回歸、同 Session 追問、Reset 後新 Session。
- [ ] 將盤點、設計選項、風險、需使用者決策事項寫入本 repo，更新 STATE／TASK 並 push，回報 commit SHA。

## STOP 條件
- 不進行 CX Agent、Playbook、Tool、Data Store、GCS、Messenger Allowed Domains、Production、IAM 等寫入。
- 不修改既有 TAX AI 搜尋功能，不使用未核准網域值。
- 不將 Secret 或未核准公開的內部題庫推上 Public Repo。
- 盤點完成後先回報 ChatGPT 審閱，等待 Phase B/C 實作授權。

# TAX AI — Project State

Last updated: 2026-10-08 (Asia/Taipei)
Status: **PHASE A — PLAN / READ-ONLY AUDIT**
Execution: **未開始實作；未部署**

## 已確認的需求／設計決策
- 既有 TAX AI 靜態網頁維持原功能，新增 AI 問答模式；「快速搜尋」保留原搜尋邏輯。
- AI 呈現為最新的單一問答結果卡，**底層 CX Session 支援多輪追問**；提供「重置提問」。模式切換不清空 Session。
- 新 Agent 顯示名稱：`TAX AI｜內部稅務助理`；Playbook：`TAX AI FAQ`；只建單一入口 Playbook，暫不另建 Router。
- `questionBank.js` 轉出二欄式 `faq.csv`（`question,answer`），不建立另一份手動維護的題庫。
- 新建**專屬 GCS Bucket**，不得與對外 Agent 共用 Bucket；對應獨立 Data Store。
- CX 由既有 `taipei-tax-lab/dialogflow-cx-qa-framework` 與其 Codex 環境管理；本 repo `taipei-tax-lab/tax-helper` 由新的 Web Codex 環境管理。
- 正式使用指定網域／網址、暫不要求登入；此作法**不能驗證使用者是否為同仁**，需在正式部署前確認實際網路限制與風險。
- 正式網域與 Messenger allowed domains 尚待使用者提供；本階段不可猜值。

## 已實際核對的 GitHub 狀態
- `taipei-tax-lab/tax-helper`：2026-10-08 建立，初始為 Public 且空 repo。後續僅加入本階段文件；原始網頁與題庫尚未匯入。
- `taipei-tax-lab/dialogflow-cx-qa-framework`：Private，有完整 1999 CX Phase7F 的 Production 驗證記錄；Rental/1999 正式資源視為受保護，不得動到。
- `taipei-tax-lab/tpctax-1999-ai-web`：可作為 Messenger transport、Session reset 與呈現契約的**參考**，不可直接修改。

## 仍待 Codex 證實
- 原始 ZIP 的實際資料夾結構、前端使用方式及 `questionBank.js` schema／總題數。
- 本 repo 何時改成 Private，以及 ZIP 安全匯入來源與方法。
- 可重用的 1999 transport／renderer 範圍和 TAX AI UI 的接合點。
- 獨立 Bucket 與 Data Store 的區域、資源命名、API／權限相容性（Phase A 僅唯讀／提案）。
- 網站上線網域、網路存取限制、是否需額外控管未登入匿名使用風險。

## 下一步
執行 `NEXT_TASK.md` 的 Phase A 唯讀盤點；先不建立雲端資源或改動既有網頁。

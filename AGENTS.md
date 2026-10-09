# TAX AI — Agent 工作規則（Workflow）

## 協作方式
- ChatGPT 專案 Session：規劃、決策、驗收與交接。
- Codex：依 `NEXT_TASK.md` 的受授權事項盤點或實作，提出可驗證成果。
- GitHub：程式碼與專案狀態的唯一真相。本 repo 專司 TAX AI Web；CX 後端另由 `taipei-tax-lab/dialogflow-cx-qa-framework` 管理。
- 每輪開始先 fetch/pull 最新狀態，讀 `README.md`、`AGENTS.md`、`PROJECT_STATE.md`、`NEXT_TASK.md`；收工前 commit/push 並回報 branch、SHA、測試與未完成事項。
- 任務需用到 Google Drive 非 Git artifacts 時，依 CX Framework 現行雙雲規則同步及驗證；不得把未完成同步宣稱為完成。

## 不可違反的架構邊界
1. 既有網頁及快速搜尋保持原功能；禁止以重新開發整站取代最小修改。
2. TAX AI AI 模式是每題獨立 FAQ semantic search；只呈現最新查詢與 0～5 筆完整 Q/A，不用對話泡泡／transcript，不依賴前題 context。
3. 每個 accepted query／SDK defaults 使用正式 FAQ currentPage、Asia/Taipei，重置 tax_answers／tax_questions／tax_answer_count；不使用 currentPlaybook／first-turn override。沒有使用者 reset，technical session recovery 只供錯誤恢復，模式切換不重 mount。
4. 不要覆寫或連動對外 1999 / Rental Agent；可唯讀參照 `taipei-tax-lab/tpctax-1999-ai-web` 經驗。
5. `questionBank.js` 是題庫唯一原始來源；`faq.csv` 是產物，不手改兩份獨立真相。
6. 不在前端嵌入 Secret、API Key 或服務帳戶金鑰；所有使用者輸入和 CX 回答都視為不可信資料。
7. 正式 binding 唯一來源為 backend TAX_AI_WEB_FLOW_HANDOFF_2026-10-09.md／同名 machine config；Pages 與 agency origin 已核准。2026-10-09 使用者已授權 B3 SDK 介接、live smoke 與既定 Pages 部署；不授權 CX／GCP／Production mutation。
8. 此 repo 初始為 Public。匯入題庫／內部資源前必須確認公開風險，避免不慎發布內部資訊。

## Phase A 權限（歷史，B3 以本輪明確授權為準）
只准盤點、文件與離線規劃；不建立或修改雲端 Agent、Data Store、GCS、IAM、Production/Messenger 等資源；不要在 Phase A 改造使用者操作行為。遇到權限／來源缺失即記錄 blocker，禁止猜測成功。

## 文件維護
- 狀態記 `PROJECT_STATE.md`：已驗證事實、決策、風險、阻擋及 handoff。
- 任務記 `NEXT_TASK.md`：單一下一步 checklist、驗收條件與 STOP boundary。
- 以繁體中文（臺灣用語）撰寫，保留技術必要英文；不另外增生競爭性的 workflow 真相文件。

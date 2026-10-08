# TAX AI — Agent 工作規則（Workflow）

## 協作方式
- ChatGPT 專案 Session：規劃、決策、驗收與交接。
- Codex：依 `NEXT_TASK.md` 的受授權事項盤點或實作，提出可驗證成果。
- GitHub：程式碼與專案狀態的唯一真相。本 repo 專司 TAX AI Web；CX 後端另由 `taipei-tax-lab/dialogflow-cx-qa-framework` 管理。
- 每輪開始先 fetch/pull 最新狀態，讀 `README.md`、`AGENTS.md`、`PROJECT_STATE.md`、`NEXT_TASK.md`；收工前 commit/push 並回報 branch、SHA、測試與未完成事項。
- 任務需用到 Google Drive 非 Git artifacts 時，依 CX Framework 現行雙雲規則同步及驗證；不得把未完成同步宣稱為完成。

## 不可違反的架構邊界
1. 既有網頁及快速搜尋保持原功能；禁止以重新開發整站取代最小修改。
2. TAX AI AI 模式僅呈現**當前問題及回答**，不用對話泡泡／完整 transcript；但底層沿用同一 CX Session 以支援追問。
3. 使用者主動「重置提問」後，清除 AI 呈現及 CX Session，下一題開始新對話；單純切換模式不應重置。
4. 不要覆寫或連動對外 1999 / Rental Agent；可唯讀參照 `taipei-tax-lab/tpctax-1999-ai-web` 經驗。
5. `questionBank.js` 是題庫唯一原始來源；`faq.csv` 是產物，不手改兩份獨立真相。
6. 不在前端嵌入 Secret、API Key 或服務帳戶金鑰；所有使用者輸入和 CX 回答都視為不可信資料。
7. 正式 CX 網域未定；任何 Allowed Domain、部署、Production binding、GCP mutations 均需後續個別授權。
8. 此 repo 初始為 Public。匯入題庫／內部資源前必須確認公開風險，避免不慎發布內部資訊。

## Phase A 權限
只准盤點、文件與離線規劃；不建立或修改雲端 Agent、Data Store、GCS、IAM、Production/Messenger 等資源；不要在 Phase A 改造使用者操作行為。遇到權限／來源缺失即記錄 blocker，禁止猜測成功。

## 文件維護
- 狀態記 `PROJECT_STATE.md`：已驗證事實、決策、風險、阻擋及 handoff。
- 任務記 `NEXT_TASK.md`：單一下一步 checklist、驗收條件與 STOP boundary。
- 以繁體中文（臺灣用語）撰寫，保留技術必要英文；不另外增生競爭性的 workflow 真相文件。

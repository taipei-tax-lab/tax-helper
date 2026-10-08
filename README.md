# TAX AI / tax-helper

本 repository 用於既有 TAX AI 網頁的版本管理，以及後續與獨立 Dialogflow CX Agent 的整合。現階段為 **Phase A：唯讀盤點與離線規劃已完成**。已實際讀取原始 ZIP，尚未匯入原始網頁／題庫至 Git，未實作 AI 整合或部署。

## 專案原則

- 保留既有 TAX AI 網頁架構、快速搜尋、題庫瀏覽、收藏等功能，不進行不必要的重構。
- 搜尋頁面提供「快速搜尋／AI 智慧問答」切換。
- AI 智慧問答以單一問答結果卡呈現；**CX 在同一 Session 保留多輪脈絡**，使用者按「重置提問」才開始新 Session；切換搜尋模式不自行重置。
- `questionBank.js` 為原始題庫，未來透過可重複執行的轉換腳本產出 `question,answer` 二欄 `faq.csv`。
- 本 repo 僅負責 Web 與題庫轉換，CX Agent、Playbook、Tool、Data Store、GCS Bucket 與 Production 配置由獨立 CX Framework repo 管理。
- 網站正式網址、Messenger allowed domains 尚待提供；不使用登入是目前業務決策，**不代表具備使用者身分限制**。

## 工作交接

1. 先讀 `AGENTS.md`（workflow）。
2. 再讀 `PROJECT_STATE.md`（現在狀態）。
3. 最後讀 `NEXT_TASK.md`（下一輪檢查清單）。
4. 依任務明確授權範圍執行，完成後更新 State/Task、commit、push，再回報實證。

> 安全注意：本 repo 建立時為 **Public**。匯入任何內部題庫、程式或環境配置之前，先判斷敏感性並建議將此 repo 調整為 Private；不得提交帳密、Token、服務帳戶金鑰或未核准公開的內部資料。

## Phase A 盤點結果（2026-10-08）

- 已實際下載並唯讀檢查使用者提供的 tax-helper.zip；questionBank.js 共 **129 題、11 個分類**，問題／答案非空，無重複 ID／問題。
- 搜尋頁可局部增加獨立 AI 表單與單一結果卡；保留原 TaxSearch、題庫瀏覽、收藏、Excel 匯入與詳情／導覽。
- 1999 Messenger transport 與安全文字處理可局部重用；需 TAX 獨立 config／控制器，模式切換保留 Session，主動重置才開新 Session。
- 1999 Node 14/14、原網頁離線 Chromium 8 組基線通過；整合後 UI／真實 Excel 成功匯入／live CX 尚未驗證。
- repo 仍 **Public**；ZIP、原始碼、題庫正文與 CSV 未提交。證據、差異、converter 設計、事件序列與矩陣見 [PROJECT_STATE.md](PROJECT_STATE.md)，下一步見 [NEXT_TASK.md](NEXT_TASK.md)。

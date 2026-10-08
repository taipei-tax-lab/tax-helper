# TAX AI — Next Task

Last updated: 2026-10-08 (Asia/Taipei)
Status: **PHASE B1 COMPLETE — AWAITING CHATGPT ACCEPTANCE; B2 NOT STARTED**
Owner: **ChatGPT 專案 Session 驗收／規劃**；後續 Web 實作由 Codex，CX 後端由 `dialogflow-cx-qa-framework` 獨立 Session 負責。
Authorization: **八個原檔公開納管與 B1 工具／離線測試已授權並完成；尚未授權 B2／B3、Pages 或 CX／GCP 設定。**

## 已定案

- `tax-helper` 維持 **Public**；GitHub Pages 是預計採用的部署方式，尚未啟用／部署。
- 原 ZIP 八檔全部已獲准公開並原貌納管；Phase A「三檔候選、五檔待確認」已由使用者授權解除阻擋，不再重問。
- 不重構 TAX AI；原快速搜尋、收藏、題庫瀏覽、Excel 匯入、學習與導覽保持原貌。
- 未來 AI 使用獨立單一問答卡，只呈現最新一問一答；CX 同 Session 保留多輪脈絡。模式切換不 reset，主動重置才開始新 Session。
- `questionBank.js` 是唯一題庫來源；`faq.csv` 為 deterministic 二欄衍生檔，不手改、不預設提交。CX 正式 ID、Environment、binding／allowed domains 由 CX Session 確認。

## B1 完成清單（供本輪驗收）

- [x] Pull main 至 `37b2b55c5f85d487358f56cc4e071755e6806672`，依序讀四份文件；實際核對 ZIP 存在、SHA-256 與前輪一致。
- [x] 八檔逐 byte 核對 ZIP 與已審 hash，原貌納管至根目錄，含 GIF／BOM／換行；新增 `.gitattributes`、`.gitignore` 與八檔 hash manifest／測試。無 ZIP／CSV／Excel／附件／缺圖納管。
- [x] 原網站 isolated Chromium **17/17 組 PASS**：129題／11分類、搜尋排序／50筆上限、收藏與重載、分類、詳情／關聯／複製／Escape、熱門題、學習文字、390px導覽、XLSX unavailable，以及真實 XLSX 0.18.5 解析合成 workbook 的成功／錯誤／重載路徑。Page errors 0、瀏覽器外部頁面請求0。
- [x] `tools/question_bank_to_faq.py` 完成；Python **20/20 PASS**（19 converter＋1八檔 hash），原始 JS 語法 **5/5 PASS**。覆蓋完整答案／二欄／特殊字元／round-trip／錯誤拒絕／原子輸出保護／byte-identical。
- [x] 實際產生被 Git 忽略的 `generated/faq.csv`：129筆、73,297 bytes；SHA-256 `2a5220e55604e8463ef3e289841cb6d25cf81102650457cfc75097292f9712c8`。未提交CSV、未上傳GCP／匯入CX。
- [x] 更新 README／STATE／TASK，明列八檔 hash、工具版本、測試命令／證據、限制與 CX 重建交接；本輪成果 commit／push 至 main，SHA 以 Codex 收工回報為準。

## 下一輪單一任務：ChatGPT 驗收 B1 並決定 B2 工作契約

- [ ] 核對 Codex 回報的 main SHA、八檔原貌 manifest、19項 converter＋1項 hash 測試、17組瀏覽器基線及 CSV hash／129筆證據；確認來源、產物與外部服務的驗證範圍。
- [ ] 確認14張學習圖片仍缺件、返回入口／第三方服務尚未live驗證，原網站尚未部署；不把離線PASS當作正式站完整可用。
- [ ] 若 B1 驗收通過，明確下達 **B2 最小 Web AI 離線整合**：僅搜尋頁模式切換、TAX 獨立控制器／單一問答卡、必要1999 transport／安全 renderer、mock 與原功能回歸；採 STATE 的同 Session／reset／expiry／timeout 事件契約，不需填正式CX ID。
- [ ] 需要交接CSV時，由CX Session從驗收SHA離線重跑工具並核對hash，或另行確認實際檔案交接方式；不推論已送達或已驗證Data Store ingestion。

## 後續路線

- **B2**：經驗收及後續授權後，執行最小 AI UI／mock 整合，保留原功能。
- **B3**：取得CX資源／回應契約及正式網域後，另經授權測試live多輪、reset、錯誤與安全。
- **B4**：資產／缺圖、Pages相對路徑、第三方依賴及公開存取驗收；另經授權才啟用／發布Pages。

## STOP boundary

- 本輪完成 B1 即交付驗收；不直接開始 B2、Messenger live、Pages／CI發布或CX／GCP修改，不修改原網站8檔。
- 不提交原ZIP容器、衍生CSV、使用者Excel、第三方測試副本、14張缺圖或未核准附件／敏感資料。來源hash不符須先停下確認，不自動重算baseline。
- 不修改1999／Rental repo，不複製其正式Agent、Playbook、Environment、GA4 ID。
- Pages網址、allowed domains與「不登入」均非同仁身分驗證；正式上線風險留待B4。

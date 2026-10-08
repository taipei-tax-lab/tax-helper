# TAX AI — Next Task

Last updated: 2026-10-08 (Asia/Taipei)
Status: **PHASE B2 AUTHORIZED — OFFLINE WEB AI INTEGRATION IN PROGRESS / NOT YET VERIFIED**
Owner: **ChatGPT 專案 Session 驗收／規劃**；後續 Web 實作由 Codex，CX 後端由 `dialogflow-cx-qa-framework` 獨立 Session 負責。
Authorization: **2026-10-08 使用者已授權 Web Codex 直接進行 B2 的 AI 介面離線整合與 Mock／回歸測試；CX 後端仍在另一 Session 準備中。本次不授權 B3 正式連線、Pages／CI 部署或 GCP/CX 寫入。**

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

## B1 驗收結論（2026-10-08）

- [x] main `e01ef42e7e0caa05c96083c5709b0554127d8e5f` 確認含八原檔、轉換器、測試與 hash manifest；未匯入 ZIP 容器／CSV，Repo 維持 Public。
- [x] 靜態檢視 converter／測試實作、B1 baseline 保護與原功能回歸矩陣；20/20 Python、17/17 Chromium、5/5 Node 為 Codex 記錄，**本驗收未獨立重跑全部測試**。
- [x] 保留14張學習圖片、返回入口／Pages 路徑、第三方服務與 live CX 的未驗證限制。

## 本輪執行階段：B2 — 最小 Web AI 離線整合（已授權）

- [ ] 先 pull main，讀四份文件；核對 B1 commit，保護已凍結原網站基線。
- [ ] 僅在原 `#searchView` 搜尋區局部加入「快速搜尋／AI 智慧問答」切換與獨立 AI form、status、**最新一問一答卡**。所有原有搜尋、分類、收藏、Excel、學習及站內導覽維持；首頁搜尋入口仍採快速搜尋。
- [ ] 參考 1999 repo 的 Messenger transport、result normalization、最小安全 Markdown renderer，僅移植必要程式，採 TAX 獨立 config 與控制器；**離線 Mock 模式不載入正式 SDK、不接觸 GCP/CX，也不使用1999正式 ID**。
- [ ] 同一 CX Session 可多輪追問；切模式及站內導覽不 reset／不重 mount；手動重置才新 Session。處理初問／追問的 Playbook override、idle/in-flight expiry、空答、timeout/late response、service unavailable、連續送出、IME。
- [ ] AI 回應走 DOM 安全文字／連結而非將不可信內容塞入原站 HTML 模板；只顯示最新卡，不累積完整 transcript；reset 清空 model／DOM／輸入，不清除收藏。
- [ ] 新增 Mock＋瀏覽器 E2E 測試，驗證雙模式、追問、reset、expiry、錯誤、安全呈現、320/390px，並重跑 B1 原功能回歸。**留意 B1 SHA 基線：不能直接更新 source_baseline.json 讓測試綠燈；保留不可變 B1 參照，針對經授權修改的原檔另作整合版本測試。**
- [ ] 將結果、實際改動、測試／未測試界線、branch／commit SHA 寫入 STATE／TASK，交 ChatGPT 驗收。未開始 B3 真實介接、Pages 部署。

### B2 啟動條件

**已達成**：使用者於 2026-10-08 明確要求「CX 還在準備中，先讓網頁繼續進行」。Web Codex 可立即依上述 checklist 實作 B2，不需等 CX 完成。驗收前仍標示 B2 尚未完成；不得將 Mock 結果宣稱 live CX 驗證。

## 後續路線

- **B2**：經驗收及後續授權後，執行最小 AI UI／mock 整合，保留原功能。
- **B3**：取得CX資源／回應契約及正式網域後，另經授權測試live多輪、reset、錯誤與安全。
- **B4**：資產／缺圖、Pages相對路徑、第三方依賴及公開存取驗收；另經授權才啟用／發布Pages。

## STOP boundary

- 本輪完成 B1 即交付驗收；不直接開始 B2、Messenger live、Pages／CI發布或CX／GCP修改，不修改原網站8檔。
- 不提交原ZIP容器、衍生CSV、使用者Excel、第三方測試副本、14張缺圖或未核准附件／敏感資料。來源hash不符須先停下確認，不自動重算baseline。
- 不修改1999／Rental repo，不複製其正式Agent、Playbook、Environment、GA4 ID。
- Pages網址、allowed domains與「不登入」均非同仁身分驗證；正式上線風險留待B4。

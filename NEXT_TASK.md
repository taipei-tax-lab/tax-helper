# TAX AI — Next Task

Last updated: 2026-10-08 (Asia/Taipei)
Status: **PHASE A COMPLETE → PHASE B1 READY / PUBLIC CONTENT APPROVAL GATE**
Owner: **Web Codex**；CX 後端由 `dialogflow-cx-qa-framework` 的獨立 Session 負責。
Authorization: **目前僅完成規劃；實際將原始檔案推送至 Public GitHub 前，須取得該檔案的明確公開／納管核准。Phase B1 實作須另經使用者啟動。**

## 已定案（不再重複討論）
- `tax-helper` 維持 **Public**；GitHub Pages 是預計採用的靜態部署方式，**尚未啟用／部署**。
- 不重構 TAX AI；既有快速搜尋、收藏、題庫瀏覽、Excel 匯入、學習與導覽保留。
- AI 新增獨立單一問答卡；只呈現最新一問一答，但 CX 同 Session 保留多輪脈絡。切模式不 reset，手動重置才新 Session。
- `questionBank.js` 是唯一原始題庫；`faq.csv` 是由 deterministic converter 產生的二欄衍生檔，不手工維護、不預設提交 Git。
- Web 與 CX 各管各的 repo；正式 ID、Environment、Messenger binding／allowed domains 由 CX Session 確認。
- Phase A 已完成 8 檔盤點及公開性技術審查；**三檔可公開候選、五檔待確認**。詳見 PROJECT_STATE 的逐檔清單。

## 後續交付路線（以實際可用為目標）
- **B1 原始碼基線＋FAQ 轉換器**：核准可公開範圍後，原貌納管原網站、凍結 baseline、建立可重跑的 JS→CSV 工具及離線測試。優先讓 CX Session 可取得可靠的 FAQ 產物。
- **B2 Web AI 離線整合**：原搜尋頁局部加入快速搜尋／AI 智慧問答切換；移植 1999 transport／安全 renderer 的必要部分；用 mock 驗證同 Session、reset、expiry、timeout 與原功能不變。此階段不依賴 CX 正式 ID。
- **B3 Web × CX 真實介接**：核對 CX 完整資源／回應契約及正式網域，進行 live 多輪問答、reset 與錯誤／安全驗證；沒有核准設定不填猜測值。
- **B4 Pages 發布驗收**：核對資產、相對路徑、缺少的 14 張學習圖片、第三方依賴與公開存取風險；另經授權才啟用／發布 Pages。必要時重新評估部署方式。

## 下一輪實際任務：B1 — 授權後執行
- [ ] **授權關卡**：由使用者／資料權責人明確確認哪些原始檔案可放在 Public repo。技術掃描通過不等於公開授權；未核准的檔案不推送。若 `questionBank.js` 不能公開，不得把原題庫放在 Pages 資產，需先回報部署替代方案。
- [ ] 先 pull main，讀 README／AGENTS／STATE／TASK；核對 ZIP 能存取且 SHA-256 與前輪相符。新環境若無 ZIP，回報來源缺件。
- [ ] 對**已核准**原檔逐檔以已審 hash 對照原貌納管，保留原相對結構。建立最小 `.gitignore` 排除 ZIP、`faq.csv`、`generated/`、`work/`、測試暫存與使用者匯入 Excel；不整包 staging。
- [ ] 在原始碼 baseline 重跑既有本機搜尋／收藏／分類／詳情測試，確認 129 題／11 分類（若核准題庫完整匯入）；標明缺少的14張學習圖片為已知限制，不自行造圖或刪功能。
- [ ] 依 STATE 既定規格建立 deterministic `questionBank.js` → `faq.csv` 轉換器及測試；完整答案、二欄 `question,answer`、多行／逗號／雙引號、round-trip、錯誤拒絕、重跑 byte-identical。產物保留於核准作業空間，不自動提交公開 Git 或上傳 GCP。
- [ ] 更新 STATE／TASK（含檔案 hash、測試實證、阻擋與 CX 交接資訊），commit/push 並回報 SHA；交付 ChatGPT 驗收後才做 B2。

## STOP boundary
- **沒有明確公開／納管核准，不得公開內部題庫、學習案例、ZIP 或敏感原碼。** 不把 Public／Pages 決策當成全部來源獲准公開。
- B1 不修改既有搜尋演算法或 UI，不做 AI 面板、Messenger live、GCP/CX 修改或 Pages 部署。
- 不修改 1999／Rental repo，不複製其正式 Agent、Playbook、Environment、GA4 ID。
- Pages allowed domains、特定網址與「不登入」均非同仁身分驗證；正式上線風險留待 B4 核對。

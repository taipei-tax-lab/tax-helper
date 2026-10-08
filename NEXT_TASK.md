# TAX AI — Next Task

Last updated: 2026-10-08 (Asia/Taipei)
Status: **PHASE A PUBLIC REVIEW COMPLETE — FILE IMPORT APPROVAL PENDING**
Owner: **Web Codex**；CX 資源由 dialogflow-cx-qa-framework 工作流處理。
Authorization: **本輪僅公開性審查、納管準備、離線驗證及文件；未納管原檔，未授權 Pages／AI／converter／部署／GCP 寫入**。

## 已確認決策

- Repo **維持 Public**，不需要再決定是否改 Private；預計採用 GitHub Pages，尚無啟用／部署授權。
- 公開技術內容審查與檔案公開／納管授權分開記錄；候選通過不表示可整包提交 ZIP。
- 原始 ZIP 已實際存在且 hash 與前輪一致；缺少的14張學習圖片仍須補齊／確認。

## 本輪完成（證據見 PROJECT_STATE.md）

- [x] pull 最新 main 至 090cdd26d54618a3ef3b1b294297a58c36d9107e，依序讀 README／AGENTS／STATE／TASK；核對 Public。
- [x] ZIP 可存取性、SHA-256、8原檔逐 byte／hash 一致。
- [x] 8檔公開性分類：search.js／searchDictionary.js／style.css 為 **可公開候選**；questionBank.js／learningBank.js／app.js／index.html／logo.png.gif 為 **需確認**；本輪沒有納管原檔。
- [x] 7文字檔15類模式掃描、129題問答／學習／fallback 語境閱讀、GIF metadata／視覺檢查；未在 Public 文件抄錄疑似敏感原文／完整待確認端點。
- [x] 網站相依性確認：題庫缺少會停在 init 前；學習檔缺少仍有 app fallback；14張圖片、兩個 optional JSON 與父層入口不在 ZIP。
- [x] 5份 JS 語法檢查、2/2離線依賴試驗通過；所有外部請求阻擋，未觸及 live 服務。
- [x] STATE 已記逐檔理由、候選 hash 白名單、排除策略與替代承載方案；本輪只提交 STATE／TASK，SHA 在收工回報提供。

## 下一輪單一任務 — 取得逐檔公開／納管範圍，再按核准白名單原貌納管

未取得明確核准前，只補充證據及文件；不能自行推定3個候選已獲匯入授權。

- [ ] pull／讀四份文件；比對 ZIP 及欲納管檔案的審查 hash。新環境缺來源須明確回報；hash 改變須重審。
- [ ] 記錄使用者／資料權責人核准的具體檔名及公開範圍。可以僅核准3個程式／樣式候選，不要求一次放行全部8檔。
- [ ] questionBank：確認129題整份可公開或提供逐題來源／核准範圍；官網標記及申辦連結不當作公開授權。不得自行抽取20題、改寫或去除題目。
- [ ] learningBank＋app fallback：確認文字／案例公開處理與來源範圍；logo：確認標誌及素材展示範圍。未獲確認者保留 repo 外。
- [ ] index：確認入口設定 API／iframe／CDN 的公開用途與管理歸屬、父層入口相對路徑；只補充證據，不改 API／導覽或啟用 Pages。
- [ ] 缺少14張圖片：取得可存取資產及公開範圍，或記錄另案核准的替代方式；不自行造圖／移除學習功能。
- [ ] **明確核准原貌納管後才執行**：按檔名／hash 白名單逐檔加入，保留原相對結構，排除 ZIP／CSV／generated／work／attachments／Excel／紀錄；不整包 staging、不帶入未核准 fallback。
- [ ] 更新 STATE／TASK、commit／push，回報實際納管清單、SHA、剩餘阻擋；只納管3候選不能宣稱完整網站可運作。

### 驗收條件

- 已授權與仍需確認名單清楚，核准檔案對得上審查 hash；有疑義的正文／素材／端點／ZIP／CSV 不進 Public Git。
- 無授權時保持「審查完成、待逐檔納管授權」，不標示已匯入；只要需保密資料仍為依賴，就不能宣稱 Pages 可正式承載整站。
- 未修改既有網頁、題庫及快速搜尋；未新增 AI／converter，未啟用 Pages／CI 發布、未部署或改 GCP/CX。

## STOP boundary

- 不更改 Public 決策；未核准原檔及敏感原文不公開，不自行將候選轉成授權。
- 不啟用 Pages／部署／CI 發布，不設定正式網域、Messenger allowed domains 或 Production binding。
- 不寫 GCP／CX Agent、Playbook、Tool、Data Store、GCS、IAM／Production；不修改1999／Rental。
- 未有 Phase B/C 授權，不修改原網站／移除功能／剝離 fallback，不開發 AI UI／transport／converter。
- 離線檢查不是外部端點可用性、CORS、真實 Excel／live CX 或稅務品質證明。

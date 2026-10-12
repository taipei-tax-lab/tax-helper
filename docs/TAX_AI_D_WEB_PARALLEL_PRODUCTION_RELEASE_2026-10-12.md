# TAX AI｜Web D版正式發布計畫（2026-10-12）

**OWNER: WEB CODEX / CAN RUN IN PARALLEL WITH CX CODEX**
**STATUS: AUTHORIZED TO MERGE D WEB TO MAIN AND DEPLOY PAGES**

## 一、與 CX Codex 的並行契約

Web 與 CX 可以同時工作，但 Web 是正式 cutover 的第一個 Gate。

- Web Codex只改 `taipei-tax-lab/tax-helper`。
- CX Codex可同時在原正式 Agent Draft 建新的 immutable FAQ Flow Version，但**不得切 Production**。
- Web完成 main merge + Pages部署 +「新版Web × 舊Production Version1」正式站 smoke 後，在本repo留下明確 **WEB_GATE_PASS**、main commit、Pages run。
- CX看到 WEB_GATE_PASS後才可切 Production。
- Web Codex不修改GCP Agent/Flow/Version/Environment/Messenger/IAM。

## 二、輸入

D feature：
- branch `codex/tax-ai-d-release-readiness-20261012`
- accepted commit `8a215dbb125d34a40a6696c344ac21fcb1d9643a`

正式 main 基準：
- 先 fresh-read目前 main；已知舊狀態曾為 `d12145f...`，**不要假設仍未變**。
- 如 main 自 feature base後有 runtime修改，先做衝突分析；若涉及 TAX AI runtime/search/questionBank，STOP交ChatGPT，不自行覆蓋。

D版必要內容：
- `source-manifest.mjs` trusted 129 URI→ID
- `result-model.mjs` D payload strict parser / source cards
- `controller.mjs` D source cards integration
- `app.js` current bank/openDetail bridge與Excel bank-change保護
- 必要 tests/package manifest調整
- 保留正式 `config.mjs` 原 Agent ID / currentPage，不改成 PoC Agent

## 三、發布步驟

### W0 — fresh review
1. 比較 main vs D feature，只取 D正式必要變更。
2. 再跑Node/Python/browser/package/credential scan；禁止把本機PoC config、localhost、PoC Agent ID、測試telemetry打包到正式runtime。
3. 確認 Quick Search/search.js/searchDictionary.js/questionBank.js沒有非預期改寫。
4. 確認D Web仍支援舊 v1 FAQ envelope；這是 Web-first 的安全條件。

### W1 — merge/deploy
1. 將D feature必要commit合入 main；可用乾淨PR/merge或等價受控方式，保留commit lineage。
2. main push後由既有 `.github/workflows/pages.yml` 自動部署 GitHub Pages。
3. 驗 Actions build/deploy PASS、artifact、hosted runtime bytes/MIME/parity；記 main commit與run ID。
4. 禁止手動改 Pages Source、禁止把 Pages 指到feature branch。

### W2 — WEB_GATE：新版Web × 舊Production
在 CX Codex尚未切 Production前，正式網址：
`https://taipei-tax-lab.github.io/tax-helper/`

做最小 live smoke：
- 頁面正常、Quick Search正常；
- AI入口仍可對舊 Production Version1 顯示 legacy FAQ文字結果，不出JS錯誤；
- 模式切換、輸入框、結果區正常；
- 不要求此階段看到D source卡片，因後端仍舊Version1。

通過後：
- 更新 `PROJECT_STATE.md` / `NEXT_TASK.md`
- 明確寫 **WEB_GATE_PASS**
- 記 main commit、Pages Actions run、正式網址 smoke evidence
- 通知 CX Codex可以執行Production cutover

若失敗：
- rollback Web到上一個已驗收main/deployed commit
- 標 **WEB_GATE_FAIL**
- CX Production不得切換

## 四、等 CX cutover 後的正式站配合驗收

CX Codex切新D Version後，Web Codex可唯讀/瀏覽器配合驗：
- 財產清單→D cards
- 信用卡地方稅→D cards
- Python無關→0 cards
- 卡片→完整標準答詢drawer
- Quick Search正常

Q1與I1已知查無，不把它們誤判成Web regression。
E2E12/12是契約測試，不得改寫成搜尋品質12/12；搜尋品質沿用8/10。

## 五、不得做的事

- 不修改正式Agent/Messenger/Production/IAM/domain
- 不改搜尋權重與129題內容
- 不把PoC Agent ID寫進正式config
- 不從feature branch直接當Pages Source
- 不刪除任何GCP PoC資源；清理由CX Codex在正式上線成功後處理

## 六、交付

建立：
- `docs/TAX_AI_D_WEB_PRODUCTION_RELEASE_2026-10-12.md`

更新：
- `PROJECT_STATE.md`
- `NEXT_TASK.md`

至少記錄：
- feature/base/main commit
- regression結果
- Pages run/artifact
- hosted parity
- WEB_GATE_PASS/FAIL
- rollback commit

**Web任務做到WEB_GATE_PASS後即可先STOP等待CX切換；CX切換完成後再補正式D smoke紀錄。**

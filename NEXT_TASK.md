## Next B3 gate — wait for TAX AI FAQ Flow backend handoff

Do not start live CX wiring until backend publishes:

`TAX AI INTERNAL FAQ FLOW BACKEND READY FOR WEB CUTOVER`

Required backend handoff:
- new Agent ID;
- location;
- Production Environment;
- Flow ID;
- full START_PAGE currentPage;
- Messenger binding;
- 0–5 result text/structured contract;
- fallback;
- independent-query semantics;
- rollback.

When handoff is ready, Web B3 should:
- keep Quick Search unchanged;
- replace old Playbook/multi-turn transport assumptions with per-query currentPage;
- render 1–5 FAQ results;
- remove visible reset-conversation UX;
- latest AI result replaces previous;
- preserve Favorites/Excel/Learning/site behavior;
- do not redesign backend architecture.

Until then: no GCP/CX guesses, no formal SDK binding, no Pages launch claim.

---

# TAX AI — Next Task

Last updated: 2026-10-08 (Asia/Taipei)
Status: **PHASE B2 ACCEPTED — B3 CX HANDOFF / LIVE GATE PENDING**
Owner: **ChatGPT 專案 Session 接續與驗收**；Web 由 Codex 維護，CX 後端由另一個 Framework Session 同步開發。
Authorization: **B2 已通過 GitHub 交付／靜態程式審查；目前僅允許 B3 介接契約盤點與準備，未授權正式 SDK/CX 呼叫、Production、GCP/CX 寫入或 Pages／CI 部署。**
Branch: **本機 work → 遠端 main**；B2實作SHA **10509014fc2b4aaebae4d33b3b4b8e0bc2da9a1a**；驗收文件另作交接commit，main SHA以Codex收工回報核對。

## 已定案

- Repo維持Public，Pages仍為未來方案，未啟用。B1八檔公開授權已完成，不再重新詢問。
- 保留原網站功能、questionBank唯一來源與再生FAQ工具；不重構整站、不修改1999／Rental／CX repo。
- AI只呈現最新一問一答；同Session追問，模式／站內導覽不reset，主動重置才新Session。自然逾期／結束會清舊卡並通知下一題新對話。
- 預設AI為服務準備中；URL明確加`?tax-ai-demo=1`才啟用標示為模擬資料的離線Mock，不載入正式SDK或填任何正式ID。
- B1不可變SHA：`e01ef42e7e0caa05c96083c5709b0554127d8e5f`。`tests/source_baseline.json`與`tests/search_baseline.json`未改寫，B2只有index.html／app.js兩個原檔局部差異，其他六檔仍原貌。

## B2 完成清單（供本輪驗收）

- [x] Pull main至`e4c9bad79793d6dbd6b99d13c36ea3cb81bd9df8`，依序讀README／AGENTS／STATE／TASK，核對並保護B1固定來源。
- [x] 原搜尋頁雙模式、獨立AI form／status／最新卡；原搜尋、分類、收藏、Excel、學習及導覽保持，首頁／分類入口回快速模式。
- [x] TAX獨立config／controller／Messenger transport、安全renderer與Mock；只有合成`mock-only-tax-faq`首次override標記，無正式SDK、CX IDs／resource names或1999正式binding。
- [x] 同Session追問、切模式／導覽不重mount；reset清model／DOM／輸入／來源且保留收藏；idle／in-flight expiry/end、timeout／late response、空答／錯答／service unavailable、連續送出與IME完成。
- [x] B1固定參照與整合版本測試分層：Python **21/21**、Node **21/21**、JS語法 **10/10**；Chromium **B1原貌17/17、B2原功能回歸17/17、AI Mock E2E21/21**。含安全DOM／links、320／390px鍵盤／focus、真實XLSX＋合成workbook及AI來源分離。
- [x] 瀏覽器page errors 0、外部頁面請求送出0、正式SDK請求0；FAQ重跑129題／73,297 bytes／原output hash不變，CSV仍不入Git、不上傳GCP。
- [x] 更新README／STATE／TASK，記錄來源差異、實作commit與重跑證據；commit／push至main，交ChatGPT驗收，不開始B3／部署。

## ChatGPT B2 驗收結論（2026-10-08）

- [x] main交接 `1360dd8be1bc6c5a77969145c3f664916755f614` 與實作 `10509014fc2b4aaebae4d33b3b4b8e0bc2da9a1a` 已查核；新增六個 AI 模組、Mock／Node／Browser E2E 及文件可於 repo 查閱。
- [x] B1 不可變 manifest 與原始網站差異控制成立；B2 只局部更動原 index／app，保留六個原檔及既有搜尋邏輯。
- [x] 已閱讀控制器／transport／安全 renderer／測試程式；Codex 記錄 Python21/21、Node21/21、原站17/17、整合17/17、AI Mock21/21。本次是 **GitHub 程式與交付審查，不是獨立重跑測試或 live CX 驗收**。
- [x] 保留尚待的14張學習圖片、入口／Pages路徑、第三方可用性、正式 CX SDK／稅務品質驗證界線。

## 下一輪單一任務：B3 介接契約交接與準備（先不連正式 CX）

- [ ] 向獨立 CX Session 取得並核對：TAX Agent、入口 Playbook 的**完整 resource name**；Environment／Integration Messenger 專屬 binding、可使用的正式或測試網域／allowed domains；回應 messages／citations 契約；FAQ converter產物與 Data Store ingestion 驗證狀態。沒有就明確記 blocker，**不猜ID、不複製1999**。
- [ ] 規劃 Mock→真實 SDK 的最小切換及安全載入機制，不把憑證放進前端；確認與目前 `setQueryParameters`、`sendQuery`、`startNewSession`、事件監聽的真實 SDK 相容性。
- [ ] 預先列出 live 驗收案例：初問與追問同 Session／僅初問 Playbook override、reset 後新 Session、逾期與 timeout、事件先後與極晚回應、來源顯示、快速搜尋不受影響，以及公開網址／未登入風險。
- [ ] 如 CX 尚未就緒，只完成文件與可離線完成的 adapter 盤點，回報缺項；**不要啟用正式 SDK 或部署，也不要為測試任意更動 GCP/CX**。取得必要契約並由使用者另行核准，才啟動 B3 實際接線及 live 測試。
- [ ] 收工更新 STATE／TASK、commit／push，清楚區分「介接準備已完成」與「已接上／通過 live 驗證」。

## 持續限制及後續路線

- 缺14張學習圖片及公開範圍；返回入口／Pages相對路徑、第三方API／遊戲可用性與正式存取方式未驗證，不假裝已補齊或部署。
- Mock保持與真實CX分開；現在驗證的是Session／UI／事件協定，正式答案內容與SDK實際時序仍待B3。
- B3真實介接及B4資產／Pages發布驗收各需後續授權；FAQ交接可從核准SHA離線重建，不宣稱已匯入CX。

## STOP boundary

- 本輪完成B2即交付驗收；不連Production、不開始正式Messenger live或B3設定、不改GCP／CX／IAM，不啟用Pages／CI發布。
- 不提交ZIP、衍生CSV、使用者Excel、第三方XLSX測試副本、缺少圖片或未核准附件／敏感資料。不修改B1原hash manifest或用整合版冒充原貌。
- 不改1999／Rental／CX Framework repo，不複製正式ID／binding／GA4。
- 網址、allowed domains與不登入均非同仁身分驗證；正式存取／發布風險留待B3／B4。

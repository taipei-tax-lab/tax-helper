# TAX AI — Next Task

Last updated: 2026-10-08 (Asia/Taipei)
Status: **PHASE B2 OFFLINE COMPLETE — AWAITING CHATGPT ACCEPTANCE**
Owner: **ChatGPT 專案 Session 驗收／下一輪規劃**；Web 由 Codex 維護，CX 後端由另一個 Framework Session 同步開發。
Authorization: **B2 雙模式、獨立卡／transport、Mock 與完整原功能回歸已授權並完成；本輪未授權 B3 正式連線、Production、GCP/CX 或 Pages／CI 部署。**
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

## 下一輪單一任務：ChatGPT 驗收 B2，確認 B3 交接契約

- [ ] 核對Codex回報的main交接SHA及STATE所列實作SHA、Git diff最小範圍、新增AI模組與固定B1 manifest；確認沒有靜默重算原hash。
- [ ] 依README重跑Python／Node／兩層17組原功能回歸／21組AI情境，或明確標記僅靜態審閱。驗收只涵蓋離線Mock與原功能，不將結果稱作live CX／完整稅務品質通過。
- [ ] 與另一個CX Session取得TAX獨立Agent／Playbook完整resource names、Environment／Messenger binding、正式URL／allowed domains、response／citation契約及FAQ ingestion交接；未提供的值保持缺省，不猜、不複製1999。
- [ ] B2驗收通過且契約已提供後，另行明確授權B3的SDK loader／binding與live驗證範圍；核對promise／event settle、cancelability、極晚response相關性、多輪語意／reset／逾期及安全。**目前不直接執行B3。**

## 持續限制及後續路線

- 缺14張學習圖片及公開範圍；返回入口／Pages相對路徑、第三方API／遊戲可用性與正式存取方式未驗證，不假裝已補齊或部署。
- Mock保持與真實CX分開；現在驗證的是Session／UI／事件協定，正式答案內容與SDK實際時序仍待B3。
- B3真實介接及B4資產／Pages發布驗收各需後續授權；FAQ交接可從核准SHA離線重建，不宣稱已匯入CX。

## STOP boundary

- 本輪完成B2即交付驗收；不連Production、不開始正式Messenger live或B3設定、不改GCP／CX／IAM，不啟用Pages／CI發布。
- 不提交ZIP、衍生CSV、使用者Excel、第三方XLSX測試副本、缺少圖片或未核准附件／敏感資料。不修改B1原hash manifest或用整合版冒充原貌。
- 不改1999／Rental／CX Framework repo，不複製正式ID／binding／GA4。
- 網址、allowed domains與不登入均非同仁身分驗證；正式存取／發布風險留待B3／B4。

# Active task — TAX AI Pages GitHub Actions migration

Date: 2026-10-09 (Asia/Taipei)
Status: **TAX AI PAGES ACTIONS DEPLOYMENT ACTIVE / LIVE ACCEPTANCE PENDING**
Input main `084e6cb8c6accb55d6e0923dfe5319fff22b240f`；plan見docs/PAGES_ACTIONS_MIGRATION_PLAN_2026-10-09.md。

- [x] Pull main，依序讀AGENTS／STATE／TASK／README／migration／deployment，唯讀1999 pages.yml和verify_hosting.py。
- [x] 新pages.yml：relevant main paths＋workflow_dispatch、concurrency pages、官方checkout/configure/upload/deploy actions。
- [x] Pages build_type=workflow fail-closed guard；legacy／null／API error停，只有workflow過；不改Source。
- [x] Python27、Node34、JS syntax10、YAML／shell／trigger coverage PASS；full B1 Git history仍保留。
- [x] 兩獨立path deterministic ZIP byte-identical；CRC／entries／manifest／source-byte parity／secret scan PASS。
- [x] Fresh verified extraction15檔，只upload14runtime＋MANIFEST；repo internal檔案不入artifact。
- [x] 最小permissions、github-pages environment、pages concurrency；不以Cloud browser CA作pre-deploy gate。
- [x] Runtime14 exact input-main bytes；不修改TAX AI／CX／1999／Rental；不重跑舊dynamic job。
- [x] Commit/push implementation d614b42；main push自動觸發run37922319766，實際guard顯示workflow。
- [x] Source分支gate已核對：實際已workflow，無需Source switch pending；未改管理設定。
- [x] Source已workflow，第一新Actions build／deploy PASS；只用該新run作truth。
- [x] 記run37922319766／source=deployed d614b423d33281667fb7d94f3df73a8a7634f0a5／artifact11611894162／SHA／PASS／URL。
- [x] Hosted15檔HTTP200／exact package bytes／MIME PASS；17個internal paths404，B3config exact。
- [x] 已執行正常TLS真實browser嘗試；navigation ERR_CERT_AUTHORITY_INVALID，0CXrequests，留實證。
- [ ] 真實browser＋CX Production／0～5FAQ／第二題／URL／mobile acceptance；Cloud CA阻擋，PENDING，非Actions blocker。
- [x] 更新STATE／TASK／README／migration／run／hosted／browser實證，final文件commit/push、remote／clean-tree核對、STOP review。

Offline package SHA：dd8a739b1e0adbc6641e1ad095068be4d5a4de6e67847652f9ddf364abf7f775，359,048bytes。
[本輪測試證據](docs/PAGES_ACTIONS_TEST_EVIDENCE_2026-10-09.json)。
新run build/deploy及hosted15檔驗證成功，標 **TAX AI PAGES ACTIONS DEPLOYMENT ACTIVE**。
正式 [run證據](docs/PAGES_ACTIONS_RUN_2026-10-09.json)／[hosted證據](docs/PAGES_ACTIONS_HOSTED_PARITY_2026-10-09.json)。
真實browserCloudTLS限制PENDING，未升級LIVE／USABLE；[browser proof](docs/PAGES_ACTIONS_LIVE_BROWSER_2026-10-09.json)。
本輪不再改產品，STOP等WebChatGPT review。下輪如獲授權處理human live acceptance，沿用已部署binding，不改CX架構。

## 歷史 B3 checklist（保留原實作事實；部署改看上方新Actions項目）

舊dynamic Pages queued run不再是本輪證據，不重跑。以下先前建議沿用branch-source已失效。

---
# TAX AI Web B3 — 正式 FAQ Flow 介接

Date: 2026-10-09 (Asia/Taipei)
Status: **B3 IMPLEMENTED / OFFLINE PASS / PAGES DEPLOYMENT PENDING / LIVE ACCEPTANCE PENDING**
Web main: `ec727a3df54a9e72c03d0e25ea4887640a860843`。
Backend main: `3c214fde52d17810af85bd601e05b72291df67ff`，PR #4 已 merge。
本輪使用者已明確授權 SDK／Production browser smoke／既定 Pages 發布；
舊 B2 的 multi-turn/reset／未授權 B3 gate 已被此契約取代，B1 基線保留。

## A. 正式契約與架構

- [x] 同步兩 main，依序閱讀 Web AGENTS／STATE／TASK／README、backend philosophy／handoff／machine config。
- [x] Backend READY；handoff 與使用者指定的 Agent／global／Production／Flow／完整 START_PAGE／語言／時區逐欄相等。
- [x] Canonical129 questionBank SHA 與 backend source 相同；Quick Search 唯一來源及 B1 manifest 不改。
- [x] 核對既有 Pages：repo has_pages=true；https://taipei-tax-lab.github.io/tax-helper/ HTTP200；index/config 與 Web main exact bytes 相同。
- [x] 既有 dynamic pages build/deployment（main ec727a3、run37899184297）成功；沿用既定 main Pages，不另猜 agency path 或更改 Pages Source。
- [x] 正式 config／lazy hidden Messenger SDK 使用新 Agent，Production 綁定由 integration 控制，不加入 environment-id。
- [x] 每題 request 和 defaults 使用 faqCurrentPage／Asia/Taipei，tax_answers=[]／tax_questions=[]／tax_answer_count=0；移除 first-turn/currentPlaybook/re-arm 邏輯。
- [x] AI 改為獨立搜尋／最新結果；移除 reset UI、multi-turn copy、JS／CSS／a11y 死碼。
- [x] accepted send 後清空，接受前失敗保留；single in-flight、IME、timeout／late／service/session recovery。
- [x] 原生 1～5 Q/A 清楚逐筆分隔，完整 text fallback；不製造 title/url/citation，answer 原有 safe URL／換行／HTML-like inert。
- [x] Mock 明確 demo only、0～5 stateless shape；production 不自動回退 Mock。

Fixed currentPage:
`projects/serviceagent-1150909/locations/global/agents/786d0cf9-fd1b-4eb9-af1f-16e41891a603/flows/5bee3876-e595-413d-be3c-729227145e4d/pages/START_PAGE`。
Agent786d0cf9-fd1b-4eb9-af1f-16e41891a603，global，Production
`e8f1496a-3e23-43b9-a75d-dc53b551e99c`，zh-tw，Asia/Taipei。
Backend/CX/GCP／1999／Rental mutation：0。

## B. Offline 回歸與基線

- [x] Python converter／immutable B1 source tests。
- [x] Node：config、每題 currentPage/tax resets、raw/parsed complete text、0～5 items、安全 URL／HTML／newline、zero vs error、timeout／late／IME／duplicate、internal recovery。
- [x] Chromium immutable B1 原站＋B3 整合原功能：Quick Search／分類／題庫／收藏／詳情／相關／複製／Excel／Learning／導覽。
- [x] Chromium AI demo／SDK fixture：0～5完整FAQ、每題獨立、最新替換、accepted clear／草稿、無 reset／multi-turn、故障隔離。
- [x] 1280／390／320 visual／鍵盤／無 overflow；截圖與 hash 證據。
- [x] deterministic hosting candidate／manifest／source integrity／secret scan；不提交 ZIP／CSV／Excel／第三方副本，不改 B1 immutable manifest。

## C. Pages／真實 browser

- [ ] Offline 全 PASS 後 push implementation，沿用既有 Pages build/deployment；記 source/deployed SHA／Actions run／URL。
- [ ] Hosted runtime files exact byte parity／MIME 與 candidate manifest。
- [ ] 真實無 mock、TLS enabled browser smoke：新 Agent request／每題 parameters／0～5 exact Q/A／第二題獨立／no-hit／URL answer／mobile／Quick Search 切換。
- [ ] 真實browser＋CX Production 成功後才標 TAX AI WEB + FAQ FLOW LIVE / USABLE。

如 Cloud CA／proxy 阻擋 browser，actual browser 驗收保持 PENDING；已部署時
標 DEPLOYED / LIVE ACCEPTANCE PENDING，離線／backend HTTP proof 不冒充Web live。

## D. 文件、rollback 與 STOP

- [x] README／STATE／TASK／Web-CX handoff／deployment records 更新實際證據。
- [x] launch-critical 檢查與 rollback disposition：只關 liveEnabled 回準備中，Quick Search 正常；不恢復舊 Playbook／借用1999/Rental／改 Production。
- [x] Commit／push final handoff，核對 remote main／clean tree，STOP 等待 Web ChatGPT review。

## 保留 backlog（不阻擋本輪接線）

- [ ] B4：原本缺的14張 Learning 圖片、返回入口及第三方服務實際可用性；本輪不補造。
- [ ] 如日後加入敏感資料，另案設計存取控制。對內是使用對象，不是 authentication；目前題庫已核准公開，不再次詢問。

## Completion summary

實作與 offline 全 PASS：Python21、Node34、B1 Chromium17、integration17、AI27、syntax10。
14runtime deterministic candidate 359,048bytes，SHA256 dd8a739b1e0adbc6641e1ad095068be4d5a4de6e67847652f9ddf364abf7f775。
實作及進度文件已commit／push；final handoff亦提交，main實際SHA以GitHub及收工回報為準。
測試／manifest／screenshots／Web-CX handoff／Pages狀態／browser proof見docs。
Pages重跑已接受但queued／無新job，hosted仍舊B2；C各項保持未勾，不標DEPLOYED／LIVE。
真實browserTLS blocker保持PENDING，無CX request；單純Cloud信任問題不觸發產品rollback。
STOP等待WebChatGPT review。下輪先核對run37899184297的實際checkout／new artifact／deploy與14檔parity；
若Pages重跑未啟動，需GitHub Pages排程/管理面處理；不要改backend或把舊run成功當本輪成功。

## 發布進度證據（2026-10-09 18:12 Asia/Taipei）

Implementation main：`ac9ab28f4ec7a8ca30229be9a8fbefe447449717`，已 push 且遠端 branch 核對相等。
現有 Pages 尚為 ec727a3 的 B2 bytes，未觀察到此次 push 的新 run；B3 部署仍未勾。
真實 Chromium 於 18:11 開 hosted Pages 即 `ERR_CERT_AUTHORITY_INVALID`，無 mock、正常 TLS／proxy、0 CX requests。
currentPage／0～5／第二題／URL／mobile live browser 驗收全部 **PENDING**，不稱 FAIL 或 PASS。

自動核准審查拒絕重跑舊 Pages build job113717503209（run37899184297），理由：run 綁定舊 ec727a3，可能回退舊 B2；該操作未執行。
採安全替代：以新的 B3 main 文件 commit 記錄實際狀態；新 commit 仍未自動產生 run。
使用者核准後，第二次舊 job 重跑仍被審查拒絕；補足 hosted 仍為 B2、checkout 明確 ref:main／fetch當前main 的可信證據後，第三次同一審查允許。
已接受 run37899184297 build job 重跑（10:16:34 UTC），目前 QUEUED／未有新job，實際checkout／artifact／deploy仍待結果。
前兩次被拒均未執行，不繞過審查、不改 Source／CX。

最後觀察：2026-10-09 18:27:38 Asia/Taipei，重跑接受約11分鐘仍QUEUED／latest jobs=[]。
C保留未勾；新deployed SHA／Actions artifact／hosted target parity尚無證據。
詳見 docs/B3_PAGES_STATUS_2026-10-09.json；不是deployment FAIL，也不是DEPLOYED。

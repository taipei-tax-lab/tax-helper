## Deployment architecture change authorized（2026-10-09）

The project will replace the current branch-source dynamic Pages build with a repo-controlled GitHub Actions workflow.

See `docs/PAGES_ACTIONS_MIGRATION_PLAN_2026-10-09.md`.

The old queued dynamic `pages build and deployment` run belongs to the previous branch-source model and must not be used as proof for the new B3 deployment.

New target: `relevant main push → repo workflow → verified runtime package → upload-pages-artifact → deploy-pages`.

No CX/product change is part of this migration.

---
# TAX AI B3 Pages deployment evidence

Date: 2026-10-09 (Asia/Taipei)
Status: **OFFLINE PASS / PAGES DEPLOYMENT PENDING / LIVE ACCEPTANCE PENDING**。

## 發布方案／來源

沿用main既有dynamic pages build and deployment（dynamic/pages/pages-build-deployment），不改Source／Environment／機關網址，不新建workflow。
Pages：https://taipei-tax-lab.github.io/tax-helper/

輸入Web main ec727a3df54a9e72c03d0e25ea4887640a860843；backend main 3c214fde52d17810af85bd601e05b72291df67ff。
repo has_pages=true、初始PagesHTTP200／index與config exact bytes，[run37899184297](https://github.com/taipei-tax-lab/tax-helper/actions/runs/37899184297) success。舊文件「尚未啟用Pages」已更新。

Implementation：`ac9ab28f4ec7a8ca30229be9a8fbefe447449717`，push main 後 remote SHA 核對相等。
發布進度文件 commit：`c9f3a1889cfae6600e5a7c9801380c747126e8d3`，runtime14檔與 implementation 相同。

10:16:34 UTC／18:16:34 Asia/Taipei，既有 main build job 重跑已接受，目前排隊；
實際 checkout／deployed SHA、run attempt、artifact、hosted parity 待結果，不先寫 PASS。
[目前API狀態](B3_PAGES_STATUS_2026-10-09.json)：queued／latest attempt無job；現有artifact11600714902建立於07:28，
是舊B2 artifact，不作本輪package proof。hosted最後核對index/config仍exact ec727a3。
本輪僅candidate完成；沒有新deployment proof，不標DEPLOYED。
重跑 run 的 metadata head 仍是 ec727a3，須另外驗 build checkout log 的實際 source SHA；
不將舊 run head 當作 B3 source。

## Candidate／完整性／測試

deterministic runtime review candidate：14runtime檔＋MANIFEST.json、359,048bytes，連續兩build byte-identical／CRC／exact entries／source parity PASS。
SHA256：dd8a739b1e0adbc6641e1ad095068be4d5a4de6e67847652f9ddf364abf7f775。

[逐檔manifest](B3_RELEASE_MANIFEST.json)。ZIP不入Git；此review candidate不是Actions實際artifact。現有Pagesbuild來源是main repo，文件／測試也是Public，不聲稱只publish此allowlist。

[測試證據](B3_TEST_EVIDENCE_2026-10-09.json)：Python21／Node34／B1 Chromium17／integration17／AI27／syntax10 PASS，protected10檔與輸入main exact、secret-pattern scan0hits、B1 manifest未改。

## Visual regression

以下為offline canonical public Q/A projection，不是新Productionretrieval；1280／390／320皆獨立FAQ區塊、細分隔、完整內容、無overflow。hash見test evidence；由Chromium suite --screenshots重製。

- [1280px](screenshots/faq-five-1280.png)
- [390px](screenshots/faq-five-390.png)
- [320px](screenshots/faq-five-320.png)

## 真實 browser acceptance

- [ ] 無mock／正常TLSbrowser打開hosted頁、新Agent SDK。
- [ ] first／second／third request exact currentPage、Asia/Taipei、tax_*zero、無currentPlaybook。
- [ ] Native0／1／2／3／4／5完整canonical Q/A、第二題獨立、no-hit、原answer URL。
- [ ] accepted clear／無reset／latest replace、mobile、AI／Quick Search切換。

真實 Chromium 已在 10:11 UTC／18:11 Asia/Taipei 嘗試正常 TLS／session proxy 開 hosted Pages；
navigation 遇 `net::ERR_CERT_AUTHORITY_INVALID`，沒有 mock／interception／trust bypass，CX requests=0。
所以本節四項驗收全部 **PENDING**；此 blocker 發生在 document，尚無 Web native CX 請求證據。
[原始 sanitized browser proof](B3_LIVE_BROWSER_2026-10-09.json)。部署後再做同一正常 TLS browser 試驗。

## 重跑審查與觸發證據

main push 及新文件 commit 尚未自動產生 Pages run；hosted index/config 當時 exact ec727a3 的 B2 bytes、liveEnabled=false，並未公開 B3。
自動審查先兩次拒絕舊 job 重跑，理由為可能部署舊 ec727a3 覆蓋本輪版本；這兩次均未執行。
使用者回覆核准後，再補足可信證據：原 job checkout 明確 ref: main，fetch `+refs/heads/main*`，checkout `refs/remotes/origin/main`；
pinned actions/checkout 原始碼在有 ref input 時不使用原 event SHA。
因此既有 build 將從當前 main 取檔，且無已公開 B3 可被覆蓋；補證後同一審查允許重跑 job113717503209。
未改 Source／workflow／Environment／CX，沒有繞過拒絕或 TLS 限制。

## Rollback／STOP

launch-critical僅關liveEnabled，pushmain等Pages重新deploy，Quick Search正常；不切oldPlaybook、不改CX／Production／1999／Rental。flag=false已offlinePASS。完成後更新STATE／NEXT／此記錄、commit/push、STOP等WebChatGPT review。

## 最後觀察與交接

截至 2026-10-09 10:27:38 UTC／18:27:38 Asia/Taipei，已接受的重跑持續 QUEUED 約11分鐘，
latest attempt jobs=[]、無新artifact／checkout／deployed SHA。不能宣稱B3已發布或hosted target parity PASS。
C 的全部 browser／部署驗收保持未勾；B3 candidate與offline完成，不改backend或做產品rollback。

本次final handoff為文件/證據更新，runtime14檔與implementation ac9ab28完全相同。
若排程之後執行，checkout可能取得後續main文件commit，須以build log實際SHA及manifest驗證，
不可由run原始head ec727a3推論。收工commit以remote main為準；STOP等WebChatGPT review。

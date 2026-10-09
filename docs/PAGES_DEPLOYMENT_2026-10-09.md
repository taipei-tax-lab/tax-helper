# TAX AI Pages Actions deployment evidence

Date: 2026-10-09 (Asia/Taipei)
Status: **TAX AI PAGES ACTIONS DEPLOYMENT ACTIVE / LIVE ACCEPTANCE PENDING**。
Migration input main：`084e6cb8c6accb55d6e0923dfe5319fff22b240f`。

## 正式發布模型

repo-owned [.github/workflows/pages.yml](../.github/workflows/pages.yml)，name **TAX AI runtime Pages**。
沿用1999已驗證的guard／artifact／deploy pattern，適配TAX的14檔package；不改1999 repo。
relevant main push＋workflow_dispatch，pages concurrency／cancel-in-progress=false；doc-only不觸發。
checkout@v4 fetch-depth=0；build contents:read/pages:read；deploy pages:write/id-token:write。
Source build_type必須workflow才configure-pages@v5；不加enablement或更改管理設定。
upload-pages-artifact@v3只uploadfresh verified temp extraction；deploy-pages@v5／github-pages environment。

Pages URL：https://taipei-tax-lab.github.io/tax-helper/

| 本輪欄位 | 已確認狀態 |
| --- | --- |
| Implementation/source/deployed SHA | d614b423d33281667fb7d94f3df73a8a7634f0a5 |
| 新workflow run ID | [37922319766](https://github.com/taipei-tax-lab/tax-helper/actions/runs/37922319766)，push／attempt1／success |
| Pages Source | guard19:12:44臺北顯示build_type: workflow；無管理API mutation |
| github-pages artifact | 11611894162，91,121bytes，digest見下方 |
| CI build／deploy | PASS／PASS，Python27／Node34／syntax10與package／upload PASS |
| Local build／tests | PASS：Python27／Node34／syntax10 |
| Package | 359,048bytes／14runtime＋MANIFEST；兩build byte-identical |
| Package SHA256 | dd8a739b1e0adbc6641e1ad095068be4d5a4de6e67847652f9ddf364abf7f775 |
| Hosted parity／MIME／internal exclusions | PASS：15檔HTTP200／ZIP exact／MIME；17個excluded paths404 |
| 真實browser／CX | PENDING：19:17 navigation ERR_CERT_AUTHORITY_INVALID／0CX requests |

## Package gate 與範圍證據

[本輪test evidence](PAGES_ACTIONS_TEST_EVIDENCE_2026-10-09.json)：Python27含6個gate tests，Node34保持正式B3 regression。
驗CRC、exact entries／無duplicate／無traversal／無extra、manifest完整／每檔SHA及bytes、SOURCE exact bytes、regular files、10JS syntax、8個credential patterns。
fresh destination才可extract，extract後再比entry set／bytes；只有15檔，不publishrepo root。
新的負向tests確認self-consistent stale release／bad CRC／missing manifest／額外docs或CSV／credential .mjs都不可extract/upload。

ZIP沿用package_web allowlist，不提交Git。Actions部署artifact是upload action由verified extraction製作的封裝；ZIP SHA和artifact digest分別記錄，不能混為一談。
MANIFEST的purpose描述ZIP本身不是GitHub artifact封裝，未改payload或metadata以保持可重製hash。
所有14runtime與輸入main exact bytes，B3liveEnabled／Agent／currentPage／FAQ／Quick Search／UI未改；CX／1999／Rental mutation=0。
無新增local runtime依賴；XLSX等既有remote dependency不納入此artifact，14缺圖仍是B4歷史項目。

Source guard離線legacy／null／API error均STOP，workflow才PASS；實際Source以新runlog `Pages build_type:`為準。
若仍legacy則輸出：
`Set Settings > Pages > Source to GitHub Actions before deployment.`
並STOP，owner手動 **Settings > Pages > Build and deployment > Source > GitHub Actions**。
切換後使用新workflow_dispatch或relevant main push，不重跑舊dynamic branch-source job。

不加入ChromiumCI：需要額外browser／Playwright／XLSX dependency；既有B3完整regression已記錄且runtime未改。
CloudTLS live blocker不作Actionsdeployment blocker；只有真實browser＋CX Production成功才升級LIVE/USABLE。

## 發布後驗收（未完成不得勾）

- [x] 新run guard顯示workflow、build PASS、deploy PASS，source=deployed d614b42／artifact11611894162。
- [x] Hosted14runtime＋MANIFEST HTTP200、每檔exact package bytes；全部MIME合理。
- [x] Repo internal paths不發布：17個AGENTS／STATE／TASK／README／docs／tests／tools／CSV／ZIP／Excel等paths404。
- [x] Hosted B3 config等於正式source，runtime14不改。
- [x] 正常TLS browser嘗試已記錄；navigation CA阻擋、0CXrequests，未bypass。
- [ ] 真實原功能／CX browser acceptance；保留PENDING，不當FAIL／PASS。

Source guard實際已workflow，首次main push deployment成功，標 **TAX AI PAGES ACTIONS DEPLOYMENT ACTIVE**。
正式artifact digest：`sha256:09a9a6d3fc9af2d0f4814704770650a376a1210cd74401ffe651560a9bfcba74`。
[run proof](PAGES_ACTIONS_RUN_2026-10-09.json)、[hosted15＋17exclusions proof](PAGES_ACTIONS_HOSTED_PARITY_2026-10-09.json)、
[normalTLS browser proof](PAGES_ACTIONS_LIVE_BROWSER_2026-10-09.json)。
新run/source/deployed SHA與deploy log的artifact_id/pages_build_version一致；沒有沿用舊run metadata。

部署後 browser仍在document遇 ERR_CERT_AUTHORITY_INVALID（19:17臺北），無CX request，未用mock或忽略TLS。
所以Web/CX狀態 **DEPLOYED / LIVE ACCEPTANCE PENDING**，未升級LIVE／USABLE、未做產品rollback。
final handoff只有docs／metadata修改，runtime14與d614b42及部署ZIP完全相同，按path policy不重deploy。
目前正式deployed SHA d614b42；review main SHA為另一次文件commit，須區分二者。
Commit/push並核對remote／clean tree後STOP等WebChatGPT review。

## 歷史 B3／branch-source證據（以下不作新部署truth）

舊dynamic run與重跑queue保留歷史；本輪不再重跑、不等待、不以舊run作Actions部署證據。

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

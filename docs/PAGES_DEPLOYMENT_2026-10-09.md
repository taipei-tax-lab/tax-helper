# TAX AI B3 Pages deployment evidence

Date: 2026-10-09 (Asia/Taipei)
Status: **OFFLINE PASS / DEPLOYMENT IN PROGRESS**。

## 發布方案／來源

沿用main既有dynamic pages build and deployment（dynamic/pages/pages-build-deployment），不改Source／Environment／機關網址，不新建workflow。
Pages：https://taipei-tax-lab.github.io/tax-helper/

輸入Web main ec727a3df54a9e72c03d0e25ea4887640a860843；backend main 3c214fde52d17810af85bd601e05b72291df67ff。
repo has_pages=true、初始PagesHTTP200／index與config exact bytes，[run37899184297](https://github.com/taipei-tax-lab/tax-helper/actions/runs/37899184297) success。舊文件「尚未啟用Pages」已更新。

Implementation／observed deployed SHA、B3 Actions run、hosted parity：發布後補入；目前尚不宣稱完成。

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

需真實browser＋CX Production；offline或backendHTTP proof不能代替。發布後嘗試，如Cloud信任blocker逐項保持PENDING，不寫FAIL／PASS。

## Rollback／STOP

launch-critical僅關liveEnabled，pushmain等Pages重新deploy，Quick Search正常；不切oldPlaybook、不改CX／Production／1999／Rental。flag=false已offlinePASS。完成後更新STATE／NEXT／此記錄、commit/push、STOP等WebChatGPT review。

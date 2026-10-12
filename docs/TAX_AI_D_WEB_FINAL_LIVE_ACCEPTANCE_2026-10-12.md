# TAX AI D｜Web 最終正式驗收（2026-10-12）

**D LIVE / USABLE / FORMAL CX VERSION2 / WEB FINAL ACCEPTED**

## 最終狀態

- Web main：`b0aa07e57c58334319f4c7ab4e4174518bcc4005`
- GitHub Pages Actions：run `38232258739` build/deploy SUCCESS
- 正式 CX Agent：`786d0cf9-fd1b-4eb9-af1f-16e41891a603`
- FAQ Flow：`5bee3876-e595-413d-be3c-729227145e4d`
- Production Environment：`e8f1496a-3e23-43b9-a75d-dc53b551e99c`
- Production FAQ mapping：immutable **Version2**
- Default Flow：仍 immutable Version1
- 正式網址：`https://taipei-tax-lab.github.io/tax-helper/`

## 正式 Browser / Messenger 驗收

CX release executor 已在正式 Pages 使用原正式 Agent 與 Google 官方 Messenger SDK完成真實驗收：
- 「財產清單」→ #111為首要候選
- 「有那些地方稅可以用信用卡繳納？」→ #127為首要候選
- Python二分搜尋 → 0候選
- Q1金融遺產口語問法、I1信用卡電子發票載具 → 維持已知查無
- #111 / #127 D卡片可開啟原完整標準答詢 drawer
- Quick Search「房屋稅」42筆正常
- Browser page error 0、Messenger error 0

E2E contract已通過；搜尋品質仍沿用凍結golden Top1/Top5=8/10，不將E2E測試寫成搜尋12/12。

## Rollback 實證

首次正式Version2驗證時，測試器以CRLF原答與browser DOM LF逐byte比較造成false positive。保護流程實際將Production回復Version1並確認mapping；離線證明內容僅換行正規化差異後，只修驗證器，再將同一Version2切回Production。最終完整正式smoke全綠。

因此 Version1 rollback 不只保留，亦已實際演練成功。

## PoC 收尾

CX repo已確認今日兩個非正式PoC Agent均刪除並GET404：
- `2dbebd9e-9fe2-482c-80fe-255c4746a859`
- `49e8377d-18bf-4fd5-bc27-b69e6a348c97`

正式D版所需v2 Data Store、129份GCS來源、原Store及正式Engine均保留。PoC-only Engines尚存在，留待日後另案評估清理，不影響目前正式服務。

CX正式release證據以`dialogflow-cx-qa-framework`分支
`codex/tax-ai-unstructured-faq-poc-plan-20261012`
之`docs/TAX_AI_D_PRODUCTION_RELEASE_RESULTS_2026-10-12.md`與`docs/TAX_AI_POC_AGENT_CLEANUP_2026-10-12.md`為準。

**本次 TAX AI D 版正式發布完成。Web不再有待切換工作。**

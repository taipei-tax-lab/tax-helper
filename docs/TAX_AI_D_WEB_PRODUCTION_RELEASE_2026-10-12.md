# TAX AI D版 Web 正式發布紀錄（2026-10-12）

**PREDEPLOY_REGRESSION_PASS / WEB_GATE_PENDING / EXECUTOR_NETWORK_BLOCKED**。
使用者已正式授權 Web merge/main/Pages 與舊 Production Version1 smoke；授權仍有效。本次尚未 merge main、尚未發布 D Web，不能交付 CX Production cutover gate。

## Fresh review 與發布範圍

- 工作分支：`codex/tax-ai-d-release-readiness-20261012`；本輪輸入分支 head `a816f57b305573fa0bbfd9ccd9f66685c292345d`。
- Accepted D feature：`8a215dbb125d34a40a6696c344ac21fcb1d9643a`。
- Fresh-read main / feature base / merge-base 均為 `d12145fdda8546560bd07a88a1c4343e120ca901`；GitHub compare ahead=1、behind=0，沒有 feature base 後新增 runtime 衝突。Shell fetch 與 GitHub connector 均核對相同 main。
- D 必要 runtime 僅 `app.js`、`assets/tax-ai/controller.mjs`、`result-model.mjs`、新增 `source-manifest.mjs`；其餘為必要 tests/package 調整與交接文件。接受 commit 後三筆輸入 commit 都只改發布授權文件。
- 正式 `config.mjs` exact main bytes：Agent `786d0cf9-fd1b-4eb9-af1f-16e41891a603`；FAQ `projects/serviceagent-1150909/locations/global/agents/786d0cf9-fd1b-4eb9-af1f-16e41891a603/flows/5bee3876-e595-413d-be3c-729227145e4d/pages/START_PAGE`；`liveEnabled=true`。transport 與 Pages workflow 不變。
- `search.js`、`searchDictionary.js`、`questionBank.js`、`learningBank.js`、原 CSS/index/logo 與不可變 B1 manifests 均 exact main bytes；共12個保護檔已逐檔核對。題庫 SHA256 `b803a7d26df0c817bd605d5023abb4f71f8dda5280b9ad45426af60792a2c258`，129題不變。
- runtime scan 無 localhost、127.0.0.1、隔離 PoC Agent/Flow ID；無 credentials。可信來源 manifest 的既有 GCS URI 含 `poc` 名稱，這是 accepted 129 URI allowlist，並非 PoC Agent binding；未改來源、Data Store 或任何 CX 架構。

## 本輪實際回歸

Node **37/37**、Python **27/27**、Chromium B1 **17/17**、原功能 integration **17/17**、AI **31/31**，全部 PASS。Browser page errors=0，離線阻擋遠端轉送，SDK 僅 fixture；不當作正式 Messenger smoke。

包含既有 Quick Search 排名、分類/收藏/相關/詳情/複製/Learning、真實 XLSX0.18.5 成功與錯誤路徑、舊 v1 FAQ envelope、D malformed source fail-closed、同ID不同內容 Excel/pending/stale cards 防護、0～5完整 FAQ、accepted-clear/草稿/IME/timeout/late、模式切換及390/320px。

兩個獨立 build 路徑 ZIP byte-identical；**393,836 bytes**、SHA256 `b2408524ad504784dbd77330bbc548a6da3342cfa4f25d609d7b5f857417a6c1`。15 runtime＋MANIFEST 共16 entries；CRC、完整 entries、manifest/source byte parity、fresh extraction、11 JS syntax、credential/security negative regression PASS。SHA 與 accepted D feature package 相同。ZIP/第三方依賴/截圖留 ignored `work/`，不發布 repo root。

本輪逐項實證：[release evidence](TAX_AI_D_WEB_PRODUCTION_RELEASE_EVIDENCE_2026-10-12.json)。E2E12題為來源契約 fixture，不能改稱搜尋品質12/12；搜尋品質仍沿用8/10，Q1/I1為既有查無。

## Pages 與 WEB_GATE

- 本輪新 main commit：**尚無**；main 仍 `d12145f...`。
- 本輪新 Pages run/artifact：**尚無**；GitHub fresh-read 最新 repo-owned Pages 成功 run 仍 [37922319766](https://github.com/taipei-tax-lab/tax-helper/actions/runs/37922319766)，source `d614b423d33281667fb7d94f3df73a8a7634f0a5`。舊 dynamic queued run不重跑。
- 正式網址：https://taipei-tax-lab.github.io/tax-helper/ 。D hosted parity 與「新版Web × 舊Production Version1」正式 smoke：**PENDING**。
- 2026-10-12 17:23:18 Asia/Taipei，正常TLS/原proxy讀 Pages，得到 `Tunnel connection failed: 403 Forbidden`，屬執行環境網路限制，非網站部署失敗。使用者回覆已開通後再檢查，工具仍 `spec_revision=2`、`allowed_hosts=[]`，curl仍403；未繞過proxy/TLS，也不把離線測試寫成正式 gate。
- 因正式 smoke 通道不可用，先保留 main 與已驗收 Pages。需環境允許 Pages/官方SDK/Messenger domains並實際生效，再重新 fresh-read main；有新的 TAX AI/search/questionBank runtime 衝突即 STOP。

## Rollback 與交接邊界

上一個已驗收 Web main回復點 `d12145fdda8546560bd07a88a1c4343e120ca901`；其 runtime 與上一個已成功 deployed source `d614b423d33281667fb7d94f3df73a8a7634f0a5` 相同。
本輪從 immutable deployed source重建 rollback package：14 runtime＋MANIFEST、**359,048 bytes**、SHA256 `dd8a739b1e0adbc6641e1ad095068be4d5a4de6e67847652f9ddf364abf7f775`，exact已驗收 package；verify/10 JS syntax/credential scan PASS。

正式發布本身異常時立即以受控 revert 恢復以上 runtime，沿既有 main Pages Actions 部署並驗證；標記 WEB_GATE_FAIL，CX不得cutover。本輪尚未改正式Web，因此無需執行rollback。

**目前 WEB_GATE_PENDING，CX Production不得cutover。** 網路開通後完成既有授權發布；只有新run build/deploy/artifact、hosted16檔 parity與正式 legacy smoke通過，才在本文件/STATE/TASK記錄 gate通過、main SHA/run/artifact並 STOP，交由 CX Codex切 Production。Web不修改GCP Agent/Flow/Version/Environment/Messenger/IAM/網域。正式D cards/drawer/Quick Search最後smoke留待CX cutover後下一輪。

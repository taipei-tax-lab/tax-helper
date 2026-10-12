# TAX AI D版 Web 上線準備（2026-10-12）

**WEB FEATURE IMPLEMENTED / OFFLINE PASS / NOT RELEASE_READY / NO DEPLOYMENT**。本輪採已選D，不新增搜尋架構。功能分支`codex/tax-ai-d-release-readiness-20261012`，base main `d12145fdda8546560bd07a88a1c4343e120ca901`；正式Web、原Messenger、config Agent ID／FAQ START_PAGE均未改，沒有merge／Pages部署。

## 實作與相容性

- `result-model.mjs`只解析native `raw.queryResult.responseMessages[].payload.tax_poc`；schema1／合法kind／單一envelope／bounded sources（≤200KB、≤129）／count／first URI／可選native參數交叉核對，失敗closed。支援已觀測的array與逗號JSON object序列，嚴格JSON.parse加界符，無eval／任意修補／診斷候選。gs/Google Storage URI必須逐字對應已驗證129物件manifest，拒絕任意URL、userinfo、不同port、未知ID；不從title／FAQ-ID／生成文字猜題。
- 一次性`source-manifest.mjs`僅含129 URI→ID及來源commit/hash、原app normalize後13個ranking/顯示欄位的完整bank fingerprint；沒有原129答案副本／credentials或同步工具。Sourcebank、search.js、searchDictionary.js原碼未改。
- 原D策略：原TaxSearch按原問句排序可信source ID，未達原閾值的source按bank序接續，原JS補足最多5；無source→AI0候選，不混Quick Search離題結果。卡片使用原`question/summary/category`，只有點卡／按鈕才呼叫原`openDetail(id)`顯示原完整答詢；不把CX生成摘要作答案。
- app.js只有唯讀bank/drawer橋接及Excel bank-changed事件。全129題normalized fingerprint必須相符，含question/answer/摘要/keywords/aliases等；不同內容即使同id亦拒絕。Excel替換立即移除D舊卡並使pending失效，點卡前再次驗bank與snapshot identity，避免錯答。自訂bank仍可用Quick Search。
- 原v1 native FAQ envelope與原fallback相容；D envelope或參數出現但不完整時不得降級成生成文字。正式模式不採任意text fallback，不自動切Mock。transport/config及原會話、timeout、accepted-clear、切模式流程沿用。
- 原卡片CSS直接復用；15runtime資產＋MANIFEST共16檔，package包含新manifest，不publish tests/docs/Excel。Pages workflow未改且只main push deploy，因此feature push不部署。

## 必要驗證

Node **37/37**（原34＋D來源/原12題、錯payload、同id Excel三個必要測試），Python **27/27**。復用原Playwright程式：AI離線Chromium31項、原站17項，均PASS，含原快速搜尋3組排名fixture、收藏／相關／複製／Learning／真實XLSX成功/錯誤、legacy SDK fixture、D原12題卡片→完整原答詢、0結果、malformed、Excel同id替換、390/320px、切模式。所有遠端GCP／Messenger請求0，SDK為明示fixture，**不冒稱真實Messenger E2E**。D fixture是已接受authenticated PoC來源的URI-only投影，不是本輪SDKcapture。

新package SHA `b2408524ad504784dbd77330bbc548a6da3342cfa4f25d609d7b5f857417a6c1`，16entries／11JS syntax／CRC／source parity／credential scan PASS。先前兩份build byte-identical；最終加入error accessibility角色後重新build/verify。初次測試遇shallow clone缺B1與sandbox Chromium socket限制，已fetch完整Git歷史及使用允許socket的環境復驗；原B1 manifest/fixture不改。

[測試證據JSON](TAX_AI_D_WEB_READINESS_EVIDENCE_2026-10-12.json)。

## 尚未通過的正式發布條件

Framework已導入**原Agent原FAQ Draft**，原Production v1未切；首次engine/store關聯尚未生效，早期原12題有限復驗曾有Q1/Q3 backend NOT_FOUND；保留失敗歷史後，最後同12題全數無內部錯誤、來源契約與原文控制通過，D Top1/Top5均8/10。本輪不調權重／不換架構。Source原生payload若含可見backend錯誤diagnostics，Web安全拒絕，不能假稱自然語意查無。詳framework同branch `docs/TAX_AI_D_RELEASE_READINESS_RESULTS_2026-10-12.md`。

**BROWSER_CONTRACT_UNVERIFIED**：沒有已確認可用的隔離Messenger與核准測試Origin，沒有改正式integration。最少人工操作：

1. 由有現成權限的機關管理者登入Dialogflow CX Console，選既有隔離v2 Agent `2dbebd9e-9fe2-482c-80fe-255c4746a859`，啟用它自己的Dialogflow Messenger，選**Draft**，勿修改原正式Agent integration/Production。
2. 機關核准一個測試Origin（建議`http://localhost:8876`，仍需核准），只加到隔離integration allowed origins，提供其Console embed設定與確認Origin即可；**不用帳密／token／ADC，也不改IAM**。
3. 測試harness用隔離Agent及`projects/serviceagent-1150909/locations/global/agents/2dbebd9e-9fe2-482c-80fe-255c4746a859/flows/30993a11-a072-46a0-b372-c8195204bcd2/pages/START_PAGE`，原Web feature config保持正式ID不改。以官方SDK觀察Q4/P127/N1及原12題`df-response-received.detail.raw`來源；只保存response payload/必要參數與session/case資訊，勿保存headers/憑證。取得真正capture才可標Messenger契約PASS；格式不同則安全失敗並STOP。原Engine v2關聯已完成本輪最後Draft12題驗證；發布前仍依同12題確認服務狀態。

以上是同D版接入驗收，不是新增PoC版本。全部通過及人工驗收後另輪授權發布，先向後相容Web再原Agent Version/Production，現在不發布。

## 回復點與STOP

- main回復點`d12145fdda8546560bd07a88a1c4343e120ca901`，實際上一版Pages source `d614b423d33281667fb7d94f3df73a8a7634f0a5`，[原成功run37922319766](https://github.com/taipei-tax-lab/tax-helper/actions/runs/37922319766)。從同immutable commit重建14檔rollback package exact：359048bytes、SHA `dd8a739b1e0adbc6641e1ad095068be4d5a4de6e67847652f9ddf364abf7f775`，與已驗收artifact相同；ZIP留ignored work，不上傳／部署。
- Framework保存原FAQ Draft PATCH body、Production原mapping、原immutable Version1、原Engine association及本輪D候選readback，必要時由另輪授權恢復，未切流量。
- 此branch可直接review；main與Pages原服務保持。commit/push feature branch後STOP，交ChatGPT驗收。**目前不是RELEASE_READY**。

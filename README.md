# TAX AI Web

臺北市稅捐稽徵處 TAX AI 題庫網站。保留快速搜尋、分類、題庫瀏覽、收藏、詳情／相關題、複製、Excel 匯入、Learning 與既有導覽；AI 模式使用獨立 TAX AI Agent 的 FAQ semantic search。

Pages：https://taipei-tax-lab.github.io/tax-helper/

**TAX AI PAGES ACTIONS DEPLOYMENT ACTIVE**。Pages Source已由新run確認workflow；build／deploy／hosted parity均PASS。
真實瀏覽器／CX 整合驗收：**LIVE / USABLE — owner-confirmed（2026-10-10）**。先前 2026-10-09 Cloud Chromium 曾遇 TLS 信任問題，但只是當時該工具的測試限制；詳細見 [驗收狀態補充](docs/TAX_AI_OWNER_ACCEPTANCE_2026-10-10.md)。
正式 [run37922319766](https://github.com/taipei-tax-lab/tax-helper/actions/runs/37922319766)，source/deployed d614b423d33281667fb7d94f3df73a8a7634f0a5；artifact11611894162。
舊dynamic run為歷史，不重跑、不作本輪truth。

本輪 B3 狀態見 [PROJECT_STATE.md](PROJECT_STATE.md)、[NEXT_TASK.md](NEXT_TASK.md)、[部署證據](docs/PAGES_DEPLOYMENT_2026-10-09.md)。TAX AI WEB + FAQ FLOW 已由使用者於 2026-10-10 確認完成真實瀏覽器整合驗收；原有離線測試仍不得替代或冒充真實測試紀錄。

## AI 搜尋契約

每題完整描述問題；每次送出都是新的 semantic search，結果取代上一題。沒有 transcript、前題語意脈絡或使用者 reset。Messenger accepted-send 後清空輸入；接受前失敗保留原文。保留 single in-flight、IME、timeout／late response 防護及 technical session recovery；錯誤不自動 retry，不偽裝成零筆命中。

正式 config 在 assets/tax-ai/config.mjs，liveEnabled=true。第一次切 AI 才載入官方 SDK；hidden SDK 不呈現聊天 UI。新 global Agent 786d0cf9-fd1b-4eb9-af1f-16e41891a603，FAQ Flow 5bee3876-e595-413d-be3c-729227145e4d。每個 request／SDK defaults 使用同一完整 START_PAGE、Asia/Taipei，重置 tax_answers=[]、tax_questions=[]、tax_answer_count=0。不送 currentPlaybook，不加 environment-id；Production 綁定由既有 Messenger integration 控制。

唯一 backend binding 真相：[authoritative handoff](https://github.com/taipei-tax-lab/dialogflow-cx-qa-framework/blob/3c214fde52d17810af85bd601e05b72291df67ff/docs/TAX_AI_WEB_FLOW_HANDOFF_2026-10-09.md)。本輪核對 merged main 3c214fde52d17810af85bd601e05b72291df67ff 的 handoff／machine config。完整 Web 契約見 [B3 handoff](docs/TAX_AI_WEB_B3_HANDOFF_2026-10-09.md)。不修改 CX／Data Store／Production／1999／Rental。

所有 responseMessages[].text.text[] 完整文字為 baseline。1～5 筆完整 question／answer 各自顯示 FAQ 區塊；優先以 tax_* arrays 核對可見 message，缺少 arrays 時只用已知 Flow envelope 與整則 message 邊界。未知／合併格式保留完整 text fallback，不靠答案內數字切段。TAX AI 沒有 title／url 欄；不製造 citation 或來源網址，僅安全 linkify 原答案內 HTTP(S) URL，保留換行，HTML-like 以 text nodes 顯示。

AI 失敗或 liveEnabled=false 時，明確顯示錯誤或「AI 服務準備中」，Quick Search 仍可用。Excel 僅影響本機 Quick Search，不同步 CX Data Store。未新增 GA4／其他 analytics，不借用其他專區 binding。

## Demo／公開範圍

?tax-ai-demo=1 才啟用明確標示的離線 Mock；0～5 筆合成 Q/A，每題獨立。Production 失敗不自動切 Mock。測試控制僅存在 demo，正式模式不提供 fixture API。

目前題庫及原八檔已獲准公開。Public Pages＋未驗證身分的 Messenger **不限制僅同仁使用**；「對內」是使用對象，allowed domains 不是 authentication。未來敏感資料需另案存取控制。已核准 origins 是 taipei-tax-lab.github.io、services.arpa.tpctax.dof.gov.taipei；本輪未猜 agency 正式路徑。

## 工作與測試

依序讀 AGENTS／STATE／NEXT_TASK／README，按 checklist 執行，完成更新證據、commit／push、STOP 等待 Web ChatGPT review。原 B2 multi-turn/reset gate 已由本輪正式 FAQ handoff 取代。

不可變 B1：e01ef42e7e0caa05c96083c5709b0554127d8e5f。tests/source_baseline.json 與搜尋 ID manifest 不重算。測試用固定 Git object 核對原貌，再對整合版重跑；clone 須保留該歷史。B3 僅局部修改原 index.html；app.js 及另外六個原檔維持輸入 main bytes。

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
node --test --test-isolation=none tests/tax_ai.test.mjs
python3 tests/site_baseline.py --source b1 --browser /usr/bin/chromium --xlsx-script /tmp/tax-helper-xlsx-0.18.5.js
python3 tests/site_baseline.py --source integration --browser /usr/bin/chromium --xlsx-script /tmp/tax-helper-xlsx-0.18.5.js
python3 tests/tax_ai_browser.py --browser /usr/bin/chromium --xlsx-script /tmp/tax-helper-xlsx-0.18.5.js
```

Python3.12.14／Node24.19.0／Playwright1.62.0／Chromium151.0.7922.173；browser 依賴見 tests/requirements-browser.txt。Suites 離線 route 本機資產，阻擋外部請求；正式 loader 用 SDK fixture 驗 DOM／events／request，不是真實 SDK。

完整 Excel 回歸用原站 XLSX0.18.5 真實副本＋記憶體合成 OOXML，不提交第三方檔或 workbook。先下載 repo 外依賴：

```bash
curl --fail --location --output /tmp/tax-helper-xlsx-0.18.5.js https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js
```

依賴 SHA256 c9506197caf809a075b6dee1da0d36fb19da7158ffe8a88e7b0c96c5d8623c99，測試自動核對；--report／--screenshots 指定 repo 外暫存。

B3：Python **21/21**、Node **34/34**、Chromium **B1 17/17＋原功能整合17/17＋AI 27/27組**、JS syntax **10/10**。三 browser suites page errors／外部轉送／Production requests 均0。涵蓋0～5完整Q/A、1280／390／320、accepted boundary／草稿／IME、每題currentPage／參數清空、無reset、timeout／late／service/session、故障時Quick Search、Excel／收藏。具體checks、hash與限制見 [test evidence](docs/B3_TEST_EVIDENCE_2026-10-09.json)。

## 發布與 rollback

repo-owned [.github/workflows/pages.yml](.github/workflows/pages.yml) 由relevant main runtime／release／tests修改自動觸發，亦支援workflow_dispatch；純STATE／TASK／README／docs更新不部署。
Source已確認是GitHub Actions。新repo或恢復時的一次性owner設定為 **Settings > Pages > Build and deployment > Source > GitHub Actions**。
workflow讀Pages配置，build_type不等於workflow即fail closed，輸出明確切換指示；不透過管理API改Source、不重跑舊dynamic job。

每次先跑Python／Node離線測試，兩獨立temp path重建ZIP且byte-identical，再verify CRC／entry set／manifest／source parity／credential patterns／JS syntax，fresh extract後只upload該15檔目錄。
官方upload-pages-artifact@v3／deploy-pages@v5、github-pages environment、最小pages/id-token權限；artifact為正式deployment truth。
完整Chromium不放CI：需額外Playwright/browser及第三方XLSX設定，這輪runtime未改且B3 regression已有實證。
新 [migration plan](docs/PAGES_ACTIONS_MIGRATION_PLAN_2026-10-09.md)、[離線證據](docs/PAGES_ACTIONS_TEST_EVIDENCE_2026-10-09.json)。
發布後核對source/deployed SHA／artifact、hosted bytes／MIME／internal files404。2026-10-09 Cloud Browser TLS 信任錯誤保留為歷史測試限制；2026-10-10 使用者已另行確認 live acceptance 完成（不推定 10/09 測試轉為 PASS）。

可重製被Actions驗證／fresh extract的runtime ZIP（ZIP本身不同於GitHub artifact封裝）：

```bash
python3 tools/package_web.py --output /tmp/tax-ai-b3.zip --manifest /tmp/tax-ai-b3-manifest.json
python3 tools/verify_package.py /tmp/tax-ai-b3.zip --extract /tmp/tax-ai-pages-fresh
```

14 runtime檔＋MANIFEST，固定順序／時間／權限／ZIP_STORED，重建 byte-identical。發布 manifest 見 [B3_RELEASE_MANIFEST.json](docs/B3_RELEASE_MANIFEST.json)。ZIP／CSV／Excel／測試依賴不入Git。Actions只upload verified extraction，包含runtime14＋MANIFEST.json；docs／tests／tools／STATE／TASK／AGENTS／使用者資料不發布。

Launch-critical frontend rollback：只關 liveEnabled、重建並推main／核對Pages，AI回準備中，Quick Search正常；不得恢復舊Playbook／借Agent／改backend Production。

## 題庫轉換與既有 backlog

questionBank.js 為 canonical129 唯一原始來源。FAQ 工具僅用Python3.10+ stdlib，不執行輸入JS：

```bash
python3 tools/question_bank_to_faq.py
```

預設產生忽略的 generated/faq.csv，固定二欄 question／answer、UTF-8無BOM／LF，保留完整值與原順序；129 records、73,297bytes，SHA256 2a5220e55604e8463ef3e289841cb6d25cf81102650457cfc75097292f9712c8。不手改、不自動上傳GCS／Data Store。

14張原Learning圖片仍缺；返回入口／遊戲／外部服務可用性留B4 backlog。本輪未補造或宣稱通過。B1／B2歷史驗收見STATE的歷史段落。

本輪deployment gates：Python27（含6個package防退化／負向驗證）、Node34、JS syntax10 PASS；兩ZIP及fresh15檔檢查PASS。所有runtime bytes與輸入main相同。

首次Actions部署已PASS：15檔HTTP200／ZIP exact bytes／合理MIME，17個internal paths404。最終handoff文件commit不重deploy；正式deployed SHA仍d614b42。

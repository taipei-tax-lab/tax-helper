## GitHub Pages deployment model

TAX AI Web is migrating from Pages **Deploy from a branch** to a repository-owned **GitHub Actions** deployment, following the proven 1999 Web release model.

Plan: [`docs/PAGES_ACTIONS_MIGRATION_PLAN_2026-10-09.md`](docs/PAGES_ACTIONS_MIGRATION_PLAN_2026-10-09.md)

After migration, relevant approved `main` changes automatically test/package/deploy only the verified runtime allowlist. The repository root is not published.

One-time owner setting: **Settings → Pages → Build and deployment → Source → GitHub Actions**.

---
# TAX AI Web

臺北市稅捐稽徵處 TAX AI 題庫網站。保留快速搜尋、分類、題庫瀏覽、收藏、詳情／相關題、複製、Excel 匯入、Learning 與既有導覽；AI 模式使用獨立 TAX AI Agent 的 FAQ semantic search。

Pages：https://taipei-tax-lab.github.io/tax-helper/

**B3 implementation／offline PASS；Pages deployment PENDING／live acceptance PENDING**。
既有build重跑已核准但仍queued，hosted最後核對是舊B2；另有Cloud Chromium TLS信任blocker。
尚未標DEPLOYED或LIVE；本頁正式config描述指GitHub的B3 source。

本輪 B3 狀態見 [PROJECT_STATE.md](PROJECT_STATE.md)、[NEXT_TASK.md](NEXT_TASK.md)、[部署證據](docs/PAGES_DEPLOYMENT_2026-10-09.md)。只有真實 browser＋CX Production 成功才標 **TAX AI WEB + FAQ FLOW LIVE / USABLE**；離線測試不能代替 live 驗收。

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

沿用現有 main dynamic pages build and deployment，不改 Pages Source、不新增 workflow。核對 Actions deployed SHA、hosted bytes／MIME。Cloud TLS／proxy 信任 blocker 導致真實browser無法執行時，保持PENDING，不假稱PASS／FAIL。

可重製 runtime review candidate（不是 Actions 實際 Pages artifact）：

```bash
python3 tools/package_web.py --output /tmp/tax-ai-b3.zip --manifest /tmp/tax-ai-b3-manifest.json
```

14 runtime檔＋MANIFEST，固定順序／時間／權限／ZIP_STORED，重建 byte-identical。發布 manifest 見 [B3_RELEASE_MANIFEST.json](docs/B3_RELEASE_MANIFEST.json)。ZIP／CSV／Excel／測試依賴不入 Git。main Pages 仍由現有服務 build repo，不聲稱 review candidate 就是 Actions artifact。

Launch-critical frontend rollback：只關 liveEnabled、重建並推main／核對Pages，AI回準備中，Quick Search正常；不得恢復舊Playbook／借Agent／改backend Production。

## 題庫轉換與既有 backlog

questionBank.js 為 canonical129 唯一原始來源。FAQ 工具僅用Python3.10+ stdlib，不執行輸入JS：

```bash
python3 tools/question_bank_to_faq.py
```

預設產生忽略的 generated/faq.csv，固定二欄 question／answer、UTF-8無BOM／LF，保留完整值與原順序；129 records、73,297bytes，SHA256 2a5220e55604e8463ef3e289841cb6d25cf81102650457cfc75097292f9712c8。不手改、不自動上傳GCS／Data Store。

14張原Learning圖片仍缺；返回入口／遊戲／外部服務可用性留B4 backlog。本輪未補造或宣稱通過。B1／B2歷史驗收見STATE的歷史段落。

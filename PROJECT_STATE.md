# TAX AI — Project State

Last updated: 2026-10-08 (Asia/Taipei)
Status: **PHASE B1 ACCEPTED (DOCUMENTED CODE REVIEW) — B2 PLANNING / NOT AUTHORIZED**
Execution: **八檔原貌納管、原網站功能基線、FAQ 轉換器與離線測試完成；B2／Pages／CX／GCP 未執行**
Source import: **使用者已核准 ZIP 全部 8 個原始檔公開，已納管至 repo 根目錄；ZIP、衍生 CSV、Excel 與暫存未納管**

## ChatGPT B1 驗收結論（2026-10-08）

- **Phase B1 通過 GitHub 交付與靜態程式審查**：main SHA `e01ef42e7e0caa05c96083c5709b0554127d8e5f`，Repo Public，八個原始檔、轉換器、hash manifest、Python／Chromium 測試及文檔均存在。Commit 實際包含網站原始碼及新增測試，未新增 Pages／CI 發布或 CX/GCP 配置。
- 已直接審閱 `tools/question_bank_to_faq.py`、`tests/test_question_bank_to_faq.py`、`tests/site_baseline.py`、`tests/source_baseline.json`：轉換器使用嚴格 JSON parser、不執行 JS、保留完整問答、固定 CSV 格式、round-trip、驗證後原子替換；Chromium 測試涵蓋既有搜尋、收藏、學習及 Excel 匯入等。
- Codex 在 STATE 記錄的 **20/20 Python、17/17 Chromium、5/5 Node 語法檢查**及產物 `129` 題、`73,297` bytes、SHA-256 `2a5220e55604e8463ef3e289841cb6d25cf81102650457cfc75097292f9712c8`，均屬**提交者的測試實證**。本次透過 GitHub 直接核對程式和報告，但未在獨立執行環境重跑完整測試，不誤稱已獨立執行通過。
- 已知限制繼續保留：學習中心缺14張圖片、Pages相對路徑／返回入口待檢、第三方服務與正式 CX 未驗證，不能宣稱網站可正式部署。
- **B2 還未實作或授權。** 提醒：B1 的 `tests/source_baseline.json` 及 `tests/site_baseline.py` 會檢查原始八檔 hash；B2 預期須局部修改 HTML／CSS／原控制器，所以**不可將原始基線靜默改寫成新版本**。B2 應保留 B1 immutable 對照（SHA），對被授權修改的檔案建立明確的 integration baseline 或測試分層，將既有功能回歸與新增功能測試區分清楚。

## 最新決策與 B1 交付（2026-10-08）

- 開工已 `git pull --ff-only origin main` 至 **37b2b55c5f85d487358f56cc4e071755e6806672**，依序讀 README／AGENTS／STATE／TASK。前輪「三檔候選、五檔待確認」為歷史狀態；使用者已明確核准原 ZIP 全部八檔於本 Public repo 公開並原貌納管，來源公開／納管 blocker 已解除。此授權不是獨立法律或著作權審查結論。
- 實際 ZIP 可存取，**77,628 bytes**；SHA-256 **824dc5020641ad3423a1364e737a51dae989e77923eaa7f43a3f67c492707c0e**，與前輪一致。八檔先全部核對成功才逐檔放入 repo 根目錄，原檔內容未改一 byte，含 GIF 與文字 BOM／換行。
- 新增 `.gitattributes` 防止八檔換行轉換；`tests/source_baseline.json` 與 hash 測試凍結 byte 基線。後續有授權的網站修改須明確更新 baseline，不能為讓測試通過而自行重算。
- 新增 `.gitignore` 排除 ZIP、faq.csv、generated/、work/、attachments/、Excel 與 Python／瀏覽器暫存。沒有提交原 ZIP、衍生 CSV、第三方 XLSX 測試副本或使用者資料；十四張缺圖未補造。
- 新增 `tools/question_bank_to_faq.py`、converter／原檔 hash 測試及 `tests/site_baseline.py`。本輪只新增工具與測試，原網站搜尋演算法、UI、收藏、Excel 匯入、學習、導覽保持原貌；AGENTS 未修改。
- **B1 實作已完成，交 ChatGPT 驗收**。尚未做 AI 面板／transport、Pages／CI 發布、正式網域／Messenger binding、CX／GCP 讀寫；未修改 1999／Rental repo。

### 八檔原貌 hash

| 原檔 | bytes | SHA-256 |
| --- | ---: | --- |
| app.js | 26,884 | e22c95f94f74fe70e1666634713ff3a52075dfb10a99a230226d5bc77c24f3af |
| index.html | 9,842 | ee69206aa7ff7f98ea60a77fcfd1116a3a84b3c336893c7375fb754b1ce89405 |
| learningBank.js | 9,690 | a1396fe06fa12b80decee84797666c852b7eb95d4451d1c566aeab796a59c451 |
| logo.png.gif | 3,595 | d7c189c93d2ed9f035854a7dccd8d9cba4fb77173aa32ccafef3389e563edf31 |
| questionBank.js | 212,639 | b803a7d26df0c817bd605d5023abb4f71f8dda5280b9ad45426af60792a2c258 |
| search.js | 17,492 | e5a654b9187a281d16e737c1c790a3806dba9d1370c76be900f1d2d77c3d159d |
| searchDictionary.js | 17,457 | e020590d1a7a6d5ae72a66c89df139b7264f9646107bee06c92a1ca9e7a1cb85 |
| style.css | 26,274 | afb88aa24a70babf928c00d5633dcd7d13d794f9b6fe070c5bcb40484e1f5435 |

### 本輪測試實證

環境：Python **3.12.14**、Node **24.19.0**、Playwright **1.62.0**、Chromium **151.0.7922.173**。可重跑命令見 README；報告及 XLSX 副本保留 repo 外工作暫存，正文未另列公開報告。

- `python -m unittest discover -s tests -p 'test_*.py' -v`：**20/20 PASS**，其中19項 converter、1項八檔 hash（覆蓋全部8檔）。包括真實129題完整 round-trip／重跑一致、中文／逗號／雙引號／CRLF／CR／LF／空白／URL／HTML 純文字／公式樣式、BOM、optional metadata、缺值／null／錯型別、duplicate key／ID／問題、動態／額外 JS、無效 JSON／UTF-8／Unicode、輸入保護、既有輸出保護與 atomic replace 失敗清理。
- 五份原始 JS 逐一 `node --check`：**5/5 PASS**。
- 隔離 Chromium `tests/site_baseline.py` 搭配 pinned XLSX 副本：**17/17 組 PASS，page errors 0**。14組原功能包含129題／11分類、分類24題與題庫篩選、完整詳情／Escape／關聯、收藏重載與刪除、首頁／搜尋頁一致及3組凍結搜尋排序、無結果、分類捷徑、熱門題詳情、空查詢129題／最多50筆、實際剪貼簿完整答案、XLSX unavailable 保留題庫、7篇學習文字與drawer、390px行動選單。
- 另外3組使用**真實 XLSX 0.18.5 函式庫＋記憶體內合成 OOXML workbook**：匯入2題後可搜尋／顯示完整答案且寫入 localStorage；重複ID及缺題目欄位失敗保留原runtime bank；重載回到原JS129題，而 localStorage仍存2題。未使用使用者 Excel、未修改現有載入邏輯。
- 依賴僅為測試下載原站指定 CDN 版本至 repo 外，其 SHA-256 **c9506197caf809a075b6dee1da0d36fb19da7158ffe8a88e7b0c96c5d8623c99**，測試先核對hash／版本，再以route離線供應。瀏覽器全程 route fulfill／abort，外部頁面請求實際送出 **0**；入口API與遊戲iframe未接觸，未呼叫CX／GCP。單獨下載CDN依賴不代表正式站第三方服務已驗收。
- `tests/search_baseline.json` 保存已核對原貌程式的三組query結果ID／順序，瀏覽器比對通過；不是同次計算兩份結果就當作凍結基線。
- `git check-ignore` 核對 ZIP／CSV／generated／work／attachments／Excel／pycache 排除均生效。Git staged blobs 亦逐檔核對上述 SHA-256，不只檢查工作樹。

### FAQ CSV 產物與 CX 交接

- 工具版本 **1.0.0**。預設命令 `python tools/question_bank_to_faq.py`，或以 `--input`／`--output` 指定核准 workspace；唯一來源為原貌 `questionBank.js`。
- 本機已實際產生 `generated/faq.csv`：**129 data records＋1 header、2欄、73,297 bytes**。Input SHA-256：**b803a7d26df0c817bd605d5023abb4f71f8dda5280b9ad45426af60792a2c258**；Output SHA-256：**2a5220e55604e8463ef3e289841cb6d25cf81102650457cfc75097292f9712c8**。CLI與測試重跑均一致；不是尚未執行的規劃。
- `faq.csv` 已由 `.gitignore` 排除，**不在此commit、不自動上傳GCS／匯入Data Store**。CX Session 可從本輪已提交SHA取得題庫與工具，在核准空間重跑並核對題數／input／output hash。需交接實際CSV時另行確認方式；未宣稱已送達CX或完成ingestion。
- 保留完整answer、不用摘要／aliases替代，不修正原資料；CSV不是獨立真相，不手改、去重、排序、加日期或以試算表重存。二欄Data Store ingestion相容性仍由CX Framework後續實驗確認。

## 既有來源／相依性審查與限制

- Phase A與公開性技術審查已完成；本輪依NEXT不重做審查。前輪7文字檔15類模式掃描未命中確證憑證／直接識別個資，並查驗題庫／學習／fallback內容及GIF。有限掃描不構成全面保證；公開範圍以使用者此次八檔授權為準。
- **來源ZIP未缺件**；缺的是learningBank引用的 `assets/01.png`～`07.png`與各自`*_thumb.png`共**14張學習圖片**，不在ZIP或本次八檔授權範圍。文字及drawer已離線驗證，圖像呈現仍不完整，未假裝另外取得assets包。
- 外部XLSX沒有隨來源納管vendor檔；正式站仍會依原HTML從CDN取得。入口設定API response／CORS／可用性與遊戲iframe未live驗證。`../index.html`返回入口未隨ZIP提供，未來Pages相對路徑待B4決策；本輪不改連結。
- 前輪相依性試驗2/2（歷史）：題庫JS與缺少的JSON都不可用會在初始化前停止；省略learningBank仍會展示app內嵌fallback。不能藉隱藏導覽或移除單一learning檔達成資料保密。
- Public及未來Pages仍為使用者決策。沒有登入的靜態站不能用網址、前端隱藏或allowed domains辨識同仁；公開八檔不代表正式上線已核准。

## 已確認需求與架構邊界

- 保留既有 TAX AI 架構及快速搜尋、題庫瀏覽、收藏、Excel 匯入、詳情／複製與導覽；搜尋頁局部增加「快速搜尋／AI 智慧問答」切換，不重構整站。
- AI 只顯示最新問題與回答；底層同一 CX Session 保留多輪追問。模式切換與站內導覽不 reset，使用者主動「重置提問」才開始新 Session；自然逾期／結束須通知並開始新 Session。
- 新 Agent 名稱 TAX AI｜內部稅務助理、入口 Playbook TAX AI FAQ、專屬 GCS Bucket／Data Store 是既有設計決策，**不是已建立的資源**。不新增 Router，不共用或改動1999／Rental資源。
- Web repo 管網頁與題庫轉換；獨立 CX Framework repo 管 Agent／Playbook／Tool／Data Store／Bucket／Production。
- questionBank.js 為唯一正式題庫來源；faq.csv 僅為可重複產生的 question,answer 二欄產物。
- 正式網址／Messenger allowed domains 尚未提供；不可猜值。暫不登入的既有決策不能驗證同仁身分，正式上線前仍須核對實際網路存取限制。

## questionBank.js 實檔盤點

檔案是註解＋單一 window.questionBank 賦值；右側為 JSON 陣列，尾端只有分號。以 JSON parser 讀取，沒有 eval、VM 或執行題庫 JS。實際 **129 題／11 個分類**。

| 原始欄位 | 實際型別／覆蓋 | 用途 |
| --- | --- | --- |
| id | string，129/129，皆為數字字串 | 收藏／詳情／關聯；app 正規化為 number |
| category、question、answer | string，各 129/129 | 分類、問題、完整答案 |
| keywords、aliases、intent | string[]，各 129/129 | 既有搜尋排序 |
| 熱門問題、相關題號 | string，各 129/129 | 熱門標記、拆分關聯題號 |
| 重點摘要、熱門顯示名稱、版本 | string，各 128/129 | summary／popularTitle／version |

- question／answer／id／category 無缺值、null 或空白；問題／答案無首尾空白。
- 重複 ID、數字 ID 正規化碰撞、重複問題（含 trim）、重複 question＋answer pair 均為 0。
- 可選 metadata 缺漏合計影響 2 題；app 原摘要 fallback 為 answer 前 120 字，缺版本保留空字串。CSV 不用摘要替代完整答案。
- 相關題號共 385 references，其中 2 個無目標；openDetail 現有邏輯略過不存在的關聯。記錄為資料清理事項，本輪未修改。
- 47 個 answer 含換行、12 個含半形逗號、12 個含 HTTP(S) URL；未見雙引號或 HTML tag pattern。converter fixtures 仍須覆蓋雙引號等特殊字元。
- HTML 靜態 bankCount 寫 109，init 實際依 bank.length 更新成 129；不能拿靜態數字或 sidebar 版本當作題庫真相。

分類數：房屋稅24、地價稅4、契稅6、土地增值稅6、使用牌照稅5、娛樂稅12、印花稅4、納保及行政救濟6、繳稅方式／電子繳款書／繳納證明22、延分期相關11、稅務管理及其他29。

## 原網站依賴與最小整合方案

載入順序：外部 XLSX → searchDictionary.js → questionBank.js → search.js → learningBank.js → app.js。

| 接點 | 已驗證現況／必須保留 |
| --- | --- |
| loadBank／normalizeQuestion | 優先 window.questionBank；缺檔才讀 questionBank.json，ZIP 無該 JSON；保留中英欄位正規化 |
| bind／runSearch | 所有 .search-form 共用 .search-input；runSearch → TaxSearch.search(bank,q,cat) → renderResults，最多顯示50筆 |
| 首頁熱門／分類／收藏卡 | 多個入口呼叫 runSearch；不可只適配搜尋頁表單 |
| searchView／searchMeta／searchResults | 可局部加入模式切換，保留原搜尋、分類、排序、空結果 |
| renderBank／openDetail／copyItem | 保留分類工具、drawer、相關題、複製與 Escape |
| 收藏 | taxAIFavorites localStorage；AI reset 不可刪除收藏 |
| Excel 匯入 | CDN XLSX 0.18.5，成功後替換記憶體 bank 並寫 taxAIExcelBank；目前 loadBank 不讀回該 key，不能宣稱重載後沿用 |
| 學習／返回入口／遊戲 | 保留 learning JS／JSON fallback、portal settings fetch、外部 iframe、既有隱藏導覽及入口樣式 |

推薦最小方案，**尚未實作**：

1. 在 #searchView 新增模式按鈕與獨立 #tax-ai-panel；快速模式顯示原 .page-search／#searchMeta／#searchResults，AI 模式顯示獨立 form／status／單一 query＋answer card。首頁仍使用快速搜尋。
2. AI form/input 不採 .search-form／.search-input，避免原 bind handler 與欄位同步介入。新增 AI 控制器採 ES module，樣式限於 AI 面板；原 app.js 保持 classic script，避免 globals 衝突。
3. runSearch 只加一個不含題目內容的本機模式通知／等價最小 hook，讓首頁／分類／收藏再搜尋回到快速模式。模式切換只改呈現、保留輸入／結果／Session；不 dispose 或重建 Messenger。
4. 同頁僅建立一個 TAX 專用 Messenger；獨立 config 由 CX Framework 提供完整資源名稱與 binding，不複製1999 Agent／Playbook／Environment／analytics ID 或部署 workflow。
5. Excel 仍只影響本機快速搜尋，不能自動同步 CX 正式題庫。建議在資料不同時提示「本機匯入僅供快速搜尋」，實際文字待 Phase B 驗收。
6. 原站部分分類／版本／匯入欄位沿用 HTML 字串模板；本輪未擴大修正。新增 AI 的問題、答案及來源只能走安全 DOM text/node，不接入原 innerHTML 模板。

## 1999 前端重用盤點

唯讀固定 reference：[e6d1e9a116eb744dacf955b7f7a30d54de9d7e85](https://github.com/taipei-tax-lab/tpctax-1999-ai-web/tree/e6d1e9a116eb744dacf955b7f7a30d54de9d7e85)。已讀 assets/messenger-transport.js、assets/result-model.js、assets/app.js、docs/RESULT_CONTRACT.md、Node／browser tests、mock、config、HTML 及相依 assets。

| 元件 | 可重用 | TAX 所需適配 |
| --- | --- | --- |
| MessengerTransport／loadMessenger | hidden/inert SDK、storage-option none、sendQuery、首次 override、busy/timeout lock、reset/clear、expiry | 獨立 TAX config、Session invalidation UI 通知、同頁一次 mount |
| normalizeResult／safeUrl／appendAnswer | parsed text 優先、raw text fallback、安全 HTTP(S)／最小 Markdown、citation 去重 | answer 必要、sources 可選；不假設存在 universalAnswer extension |
| renderResult | 清除舊結果、安全 DOM 節點方法 | 自有 TAX 容器與文案；不帶入 official1999Faq 卡／「官方1999常見問答」 |
| app.js | IME guard、loading/empty/error、單一 in-flight 與狀態模式 | 不整份移植 selectors／頁面／analytics／回站連結 |
| tests／mock | Session、override、timeout、惡意字串等案例 | 加入模式切換、快速搜尋、來源差異等 TAX 回歸 |

必須補齊的差距：

- 1999 app 只有成功回答後顯示 reset；TAX AI 在第一題 empty/error 後也須有重置入口，busy／locked 時暫停，SDK settle 後恢復。
- 1999 transport 的 idle expiry/end 會 reset，但 app 未直接收到 UI 通知；TAX controller 須收到失效事件、清除舊卡並提示脈絡已結束。
- 1999 reset 主要隱藏 result；TAX reset 要清空 query／answer／sources DOM、輸入與當前 model，不累積完整前端 transcript。
- lock／晚到回應防護依賴單一 SDK operation 與 settle 順序；離線 mock 不能證明所有 live 行為，跨 reset／expiry 的舊結果不得落入下一題。

## 最新問答＋多輪 Session 事件序列

| 事件 | Session／transport | 呈現與防護 |
| --- | --- | --- |
| 首次進 AI | lazy mount 一個專用 Messenger，新 Session、armed | 不顯示泡泡／歷史，ready 後可送 |
| 第一題 | sendQuery → df-request-sent 注入 TAX 完整 Playbook resource name 與 Asia/Taipei；解除 defaults | 記錄當前 query、清舊卡、loading；IME／空白／超長不送；busy 期間停用送出與 reset |
| 回答 | df-response-received 可取消時 preventDefault；normalize parsed/raw text | 僅本次 query／answer／額外 sources；空答案進 empty，不合成答案 |
| 追問 | 同 Session，明確刪除 currentPlaybook | 最新卡覆蓋前次卡；不靠前端 transcript 模擬記憶 |
| 模式／站內導覽 | Session／armed／pending 不變 | 只切換面板；AI in-flight 結果只更新 AI 狀態，不寫快速搜尋容器 |
| 主動 reset（已 settle） | startNewSession({retainHistory:false})＋re-arm | 清 AI DOM／model／input、focus；下一題新 Session；保留收藏與快速搜尋 |
| expiry/end | pending 以 session error 結束；idle 立即 reset，in-flight 等 settle 後 reset | 直接通知 UI、清舊卡；不 retry，保留輸入供手動再問 |
| timeout／連續送出 | reject timeout，settle 前保持 locked，忽略晚到回答 | 無自動 retry，雙擊／連續 Enter 只有一請求；SDK 永不 settle 時提示重新載入頁面，不只解除忙碌旗標 |
| service／empty／loader error | 不自動 retry，不假設新 Session | 清楚顯示狀態；依 ready/locked 開放手動再問/reset，快速搜尋仍可用 |

1999 參考值：timeout 60 秒、TTL 1800 秒、max query 1000 字。TAX 值與 live binding 待確認，未寫入任何雲端設定。reset 表示下一題使用新會話，不宣稱刪除雲端歷史紀錄。

## questionBank.js → faq.csv 已實作規格（B1）

1. UTF-8（輸入可有BOM），只接受可選單一block comment＋`window.questionBank =`＋嚴格非空JSON array＋尾分號；不允許額外JS、動態expression、重複JSON key、非標準JSON constants。不使用eval／VM／JS runtime。
2. 每筆是object；id／question／answer須為非空string，拒絕缺值、null、錯型別與重複ID／question（比對鍵含trim）。其他metadata不匯出、不用來補缺少的answer；原JS完整保留。
3. trim只供驗證，不更動輸出文字；保留原順序、首尾空白、完整答案及欄內CR／LF／CRLF。
4. 固定header `question,answer`；UTF-8無BOM，標準CSV writer，LF記錄分隔；data二欄一律quote、雙引號加倍escape。公式樣式、HTML與URL保留為原文字，不執行或抓取。
5. 先在記憶體CSV reader round-trip逐欄核對成功，才於輸出目錄建立暫存並`os.replace`。錯誤不覆寫既有輸出、暫存清理；禁止output指向來源本身。
6. CLI只列converter版本、題數、input／output hash及output路徑，無timestamp與正文。成功exit0、失敗exit1；具體fixtures與拒絕測試已納管，可離線重跑。

## 第一輪驗證結果及後續測試矩陣（歷史記錄）

- ZIP／hash／有限 Secret scan／嚴格 JSON 題庫統計完成。
- 固定1999暫存副本執行 node tests/phase7e3a.test.mjs：**14/14 PASS**，涵蓋 normalization／URL／Markdown／去重、首次 override／followup、reset／expiry、timeout lock／late response、service error／clear。
- 原 ZIP 不改碼的 isolated Chromium：**8 組基線 PASS，page errors 0**。涵蓋129題／11分類、分類24題、drawer／Escape／收藏、首頁／搜尋頁排序一致、無結果、首頁分類捷徑、複製、XLSX 被阻擋時保留題庫。
- 瀏覽器 route 供應原檔，外部 CDN／portal API／遊戲 iframe 全部阻擋；未連 live CX、GA4、Production 或 GCP，未部署網站。
- 原站真實 XLSX／合成 workbook 路徑已由 B1 補驗，未使用真實業務 Excel。尚未執行整合後 E2E、1999 browser suite、live SDK、Production、正式網域及稅務品質驗收。

下列是後續驗收設計，**不是已通過結果**：

| 面向 | fixture／操作 | 驗收條件 |
| --- | --- | --- |
| 快速搜尋 | 固定 bank；首頁／搜尋／熱門／分類／無結果 | baseline IDs／排序／分類／50筆上限；AI 故障不影響本機搜尋 |
| 原功能 | 題庫篩選、關聯、複製、收藏、Escape、行動選單 | 原 handlers、localStorage、導覽保留 |
| Excel | 真實 workbook、無效欄位／重複編號／XLSX unavailable | 保留匯入行為；不自動替換 AI 題庫 |
| 最新卡 | A→B，B 無來源／格式 | 只剩 B 問答，舊 sources／格式清除，無泡泡 |
| 同 Session | 初問→追問，mock logs | Session 不變；只第一題注入 currentPlaybook |
| 模式切換 | AI→快速→AI、站內搜尋入口、in-flight | 不 reset／重 mount／unsolicited send；正確面板與最新狀態 |
| Reset | 成功／empty／error 後重置 | 清 DOM／model／input；新 Session、re-arm；不刪收藏 |
| Expiry/end | idle 與 in-flight | UI 提示、清舊卡、settle 後新 Session、不 retry／回填舊回答 |
| Timeout／連續送出 | 延遲／late response、雙擊／Enter | 單請求、無 retry、settle 前 lock |
| 輸入／IME | 中文組字 Enter、空白、超長、Shift+Enter | 不誤送，focus／aria 狀態正確 |
| 服務異常 | empty／malformed、SDK error／loader unavailable | 不捏造答案，快速搜尋可用 |
| 安全 DOM | HTML/script、惡意 URL、Markdown／重複 citation | 不執行 HTML、URL 許可／去重、無1999專屬卡 |
| Converter | 實際129題＋合成特殊字元／拒絕案例 | 二欄 round-trip、完整答案、逐 byte deterministic、不公開正文 |
| 行動／無障礙 | 320／390px、鍵盤、focus、aria | 原 layout 保留，AI 狀態可操作 |
| Live | 另案授權後，專屬 TAX Agent／核准網域 | 真實脈絡／reset／SDK／ingestion；不操作1999／Rental |

## 阻擋與 handoff（目前）

- **B1無來源或公開授權阻擋**：ZIP已讀取，八檔已獲核准原貌納管，converter與離線驗證已完成。等待ChatGPT驗收本輪SHA，B2尚未開始。
- **已知原資料差異**：HTML靜態109／實際129、optional metadata缺漏、2個孤立關聯、Excel runtime bank與正式JS來源不同；本輪不修正資料或同步CX。
- **B4缺件**：14張學習圖片與公開範圍、返回入口、第三方服務／相對路徑及正式存取方式待確認。這些限制不妨礙本輪B1的原貌與工具驗證，但不宣稱完整發布可用。
- **CX handoff**：獨立TAX Agent／Playbook完整resource names、Environment／Messenger binding、正式網址／allowed domains／網路限制待CX Session提供；Bucket／Data Store區域、命名、權限、CSV ingestion由Framework處理。可依上述已驗證hash離線重建FAQ；未交付或操作live雲端資源。
- **STOP**：先由ChatGPT驗收B1，再以後續明確任務授權B2最小AI UI與mock。未取得後續授權不部署Pages／CI發布、不寫CX／GCP／Messenger／IAM、不改1999／Rental，不提交額外附件或CSV。

下一輪單一任務見 NEXT_TASK.md；未建立另一份競爭性的workflow文件。

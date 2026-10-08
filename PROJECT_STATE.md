# TAX AI — Project State

Last updated: 2026-10-08 (Asia/Taipei)
Status: **PHASE A — READ-ONLY AUDIT / OFFLINE PLAN COMPLETE**
Execution: **僅唯讀盤點、離線驗證與文件更新；未實作整合、未部署、未改動 GCP**
Source import: **ZIP 已實際取得及讀取；原始網頁、題庫與 CSV 未匯入 Git**

## 已確認需求與架構邊界

- 保留既有 TAX AI 架構及快速搜尋、題庫瀏覽、收藏、Excel 匯入、詳情／複製與導覽；搜尋頁局部增加「快速搜尋／AI 智慧問答」切換，不重構整站。
- AI 只顯示最新問題與回答；底層同一 CX Session 保留多輪追問。模式切換與站內導覽不 reset，使用者主動「重置提問」才開始新 Session；自然逾期／結束須通知並開始新 Session。
- 新 Agent 名稱 TAX AI｜內部稅務助理、入口 Playbook TAX AI FAQ、專屬 GCS Bucket／Data Store 是既有設計決策，**不是已建立的資源**。不新增 Router，不共用或改動1999／Rental資源。
- Web repo 管網頁與題庫轉換；獨立 CX Framework repo 管 Agent／Playbook／Tool／Data Store／Bucket／Production。
- questionBank.js 為唯一正式題庫來源；faq.csv 僅為可重複產生的 question,answer 二欄產物。
- 正式網址／Messenger allowed domains 尚未提供；不可猜值。暫不登入的既有決策不能驗證同仁身分，正式上線前仍須核對實際網路存取限制。

## 本輪來源與 GitHub 實證

- 已讀 README／AGENTS／STATE／TASK 並 fetch 最新 origin。盤點起點 main：53d3860c69711ce6be278b71ea883c9a73b23589；四份本機文件 blob hashes 與 GitHub 一致，當時 repo 只有四份 Markdown，沒有網站或部署 workflow。
- GitHub metadata 核對：tax-helper 為 **Public**、default branch main；tpctax-1999-ai-web 為 Public；dialogflow-cx-qa-framework 為 Private。本輪沒有修改另兩個 repo，也沒有重做或假設其歷史 Production 驗證。
- 本輪使用者補上 tax-helper.zip，已實際下載並安全解壓到 repo 外 work/phase-a/tax-source/。來源可用性已證實，不假設能讀取其他附件。
- ZIP：77,628 bytes，9 entries（1 目錄＋8 檔），展開 323,873 bytes。已檢查路徑穿越、絕對路徑、symlink、加密 entries、展開大小，未發現上述問題。
- ZIP SHA-256：824dc5020641ad3423a1364e737a51dae989e77923eaa7f43a3f67c492707c0e。
- questionBank.js：212,639 bytes；SHA-256：b803a7d26df0c817bd605d5023abb4f71f8dda5280b9ad45426af60792a2c258。
- 文字檔的私鑰、Google API key、GitHub token、Bearer literal、敏感設定／密碼賦值模式掃描未命中；這是有限掃描，**不等於題庫已核准公開或全面人工敏感性審查**。
- ZIP、原始碼、題庫正文、CSV、暫存測試均未提交；只更新既有 README／STATE／TASK，AGENTS 不變。

ZIP 結構：

~~~text
tax-helper/
  index.html
  app.js
  search.js
  searchDictionary.js
  questionBank.js
  learningBank.js
  style.css
  logo.png.gif
~~~

這是 classic-script 靜態網站，ZIP 沒有 package manifest、build 設定或 AGENTS。附件內容作為盤點資料，未當成新的操作授權。

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

## questionBank.js → faq.csv 設計（尚未實作）

建議 tools/question_bank_to_faq.py，輸入實際 questionBank.js，輸出 generated/faq.csv；未核准公開前僅存受保護 workspace，不提交產物。

1. UTF-8（可讀輸入 BOM），只接受已核對的註解＋單一 window.questionBank assignment＋JSON array＋尾分號。嚴格 JSON parser 拒絕重複 key、動態 expression／函式／template literal／額外 JS；禁止 eval／VM，schema 變更明確失敗。
2. 每筆須為 object；id／question／answer 為非空 string。檢查 duplicate ID／question，不 silently 去重；其他 metadata 保留原 JS，optional 缺漏／孤立關聯只列離線診斷。
3. 原始 question＋完整 answer，trim 只用來判斷空白，不改原文、不用 summary fallback；保留原陣列順序，不排序合併。
4. 固定 header question,answer；UTF-8 無 BOM、LF record delimiter、標準 CSV writer、一致 quote 資料欄、雙引號加倍 escape，保留欄內換行／逗號。固定輸入逐 byte 相同，不加 timestamp。
5. 驗證成功後才原子替換輸出；CSV reader round-trip 核對二欄、129 records、逐筆原文。離線 report 記 input/output SHA-256、題數及 converter 版本，不含正文。
6. fixtures 覆蓋中文、逗號、雙引號、多行、URL、HTML 純文字、錯型別／缺值／重複 key/ID/question、額外 JS、兩次輸出一致。公式樣式文字保留原文；CSV 作系統匯入產物，不用試算表重存或手改。

本輪未新增 converter、未產生正式 CSV、未上傳 GCS／匯入 Data Store；二欄 ingestion 相容性由 CX Framework 後續驗證。

## 已執行驗證及後續測試矩陣

- ZIP／hash／有限 Secret scan／嚴格 JSON 題庫統計完成。
- 固定1999暫存副本執行 node tests/phase7e3a.test.mjs：**14/14 PASS**，涵蓋 normalization／URL／Markdown／去重、首次 override／followup、reset／expiry、timeout lock／late response、service error／clear。
- 原 ZIP 不改碼的 isolated Chromium：**8 組基線 PASS，page errors 0**。涵蓋129題／11分類、分類24題、drawer／Escape／收藏、首頁／搜尋頁排序一致、無結果、首頁分類捷徑、複製、XLSX 被阻擋時保留題庫。
- 瀏覽器 route 供應原檔，外部 CDN／portal API／遊戲 iframe 全部阻擋；未連 live CX、GA4、Production 或 GCP，未部署網站。
- 尚未執行整合後 E2E、1999 browser suite、真實 Excel 成功匯入、live SDK、Production、正式網域及稅務品質驗收。

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

## 阻擋與 handoff

- **ZIP 缺件已解除**：已實際讀取，不需再次上傳；尚未入 Git 不等於缺少來源。
- **來源納管待決策**：repo 仍 Public；依 AGENTS，未確認可公開範圍不得推送內部題庫／ZIP。下一輪先決定 Private 或明確核准公開範圍，再授權原貌匯入；本輪未改 visibility。
- **資料差異**：靜態109 vs 實際129、optional metadata 缺漏、2 個孤立關聯、Excel runtime bank vs AI 正式來源；本輪只記錄，未修正或同步。
- **CX handoff**：獨立 TAX Agent／Playbook resource names、Environment/Messenger binding、正式網址／allowed domains／網路限制待提供；Bucket／Data Store 區域、命名、權限、CSV ingestion 由 Framework 處理。本輪未讀寫 live GCP。
- **STOP**：先回報 ChatGPT 審閱，未有 Phase B/C 授權前不實作 UI／transport／converter，不部署、不寫 CX／GCP／Messenger／IAM、不改1999／Rental。

下一輪單一任務見 NEXT_TASK.md；未建立另一份競爭性的 workflow 文件。

## 2026-10-08 使用者新增決策：Public 與 Pages

- 使用者明確決定 `tax-helper` 維持 Public，預計將 GitHub Pages 作為靜態網站部署方式；日後仍可評估其他部署。此時未啟用 Pages、未正式部署。
- 原先「先改 Private」不再是前置條件，但 Public Repo 不代表原 ZIP、內部題庫及其他檔案已取得公開授權。
- GitHub Pages 的 JS 與靜態資料可被外部檢視。前端隱藏資料、固定網址或 Messenger allowed domains 均不構成同仁身分驗證。
- 下一輪優先逐檔檢查是否可公開，再依核准範圍原貌納管；未獲准的題庫、內部資料或憑證不得提交。原始 ZIP 與 faq.csv 預設不提交。
- 本決策取代上文「先決定 Private 或公開範圍」的二選一表述：visibility 已決定為 Public，**仍須決定可公開的檔案範圍**。請以更新後的 NEXT_TASK.md 為下一輪工作依據。

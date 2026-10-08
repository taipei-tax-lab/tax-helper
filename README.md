# TAX AI / tax-helper

本 repository 用於既有 TAX AI 網頁的版本管理，以及後續與獨立 Dialogflow CX Agent 的整合。現階段為 **Phase B1 已完成，待 ChatGPT 驗收**：已依使用者公開授權原貌納管 ZIP 八檔、驗證原功能，並建立 FAQ CSV 轉換器與離線測試。AI 整合及部署尚未開始。

## 專案原則

- 保留既有 TAX AI 網頁架構、快速搜尋、題庫瀏覽、收藏等功能，不進行不必要的重構。
- 搜尋頁面提供「快速搜尋／AI 智慧問答」切換。
- AI 智慧問答以單一問答結果卡呈現；**CX 在同一 Session 保留多輪脈絡**，使用者按「重置提問」才開始新 Session；切換搜尋模式不自行重置。
- `questionBank.js` 為原始題庫，未來透過可重複執行的轉換腳本產出 `question,answer` 二欄 `faq.csv`。
- 本 repo 僅負責 Web 與題庫轉換，CX Agent、Playbook、Tool、Data Store、GCS Bucket 與 Production 配置由獨立 CX Framework repo 管理。
- 網站正式網址、Messenger allowed domains 尚待提供；不使用登入是目前業務決策，**不代表具備使用者身分限制**。

## 工作交接

1. 先讀 `AGENTS.md`（workflow）。
2. 再讀 `PROJECT_STATE.md`（現在狀態）。
3. 最後讀 `NEXT_TASK.md`（下一輪檢查清單）。
4. 依任務明確授權範圍執行，完成後更新 State/Task、commit、push，再回報實證。

> 公開原則：使用者已決定本 repo **維持 Public**，以便未來採用 GitHub Pages；**目前尚未啟用 Pages，也未部署**。Public Repo 並不等於原始題庫／內部資料已獲准公開。匯入前須逐項確認公開範圍，不得提交帳密、Token、服務帳戶金鑰或未核准公開的內容。

## Phase A 盤點結果（2026-10-08，歷史）

- 已實際下載並唯讀檢查使用者提供的 tax-helper.zip；questionBank.js 共 **129 題、11 個分類**，問題／答案非空，無重複 ID／問題。
- 搜尋頁可局部增加獨立 AI 表單與單一結果卡；保留原 TaxSearch、題庫瀏覽、收藏、Excel 匯入與詳情／導覽。
- 1999 Messenger transport 與安全文字處理可局部重用；需 TAX 獨立 config／控制器，模式切換保留 Session，主動重置才開新 Session。
- 1999 Node 14/14、原網頁離線 Chromium 8 組基線通過；整合後 UI／真實 Excel 成功匯入／live CX 尚未驗證。
- 當時尚未提交原始碼；目前八檔已依 B1 授權原貌納管，ZIP 與 CSV 仍排除。最新證據、限制、Session 事件序列與矩陣見 [PROJECT_STATE.md](PROJECT_STATE.md)，下一步見 [NEXT_TASK.md](NEXT_TASK.md)。

## Public Repo／GitHub Pages 決策（2026-10-08）

- **保留 Public**；GitHub Pages 是預計使用的靜態網站部署方式，日後仍可重新評估其他部署方案；本次只更新規劃，未啟用 Pages 或變更網站。
- Pages 提供的 HTML、JavaScript、靜態題庫及可下載資產，均須當作**任何取得網址的人皆可讀取**。沒有登入的靜態站不能憑網址不公開、Messenger allowed domains 或前端程式來辨識內部同仁。
- 先盤點原 ZIP 全部資產的可公開性，特別確認 `questionBank.js`、`learningBank.js`、匯入資料、內部連結／端點與可能含敏感資訊的文字；確認可公開者才納管。若原題庫必須保密，**不得把原題庫放在 Public Git 或 Pages 靜態資產**；應停止該部分並提出替代承載方案。
- `faq.csv` 是可再生產物，預設不提交；CX 後端匯入與 GCS 資源仍由獨立 Session 負責。未取得部署授權不啟用 Pages、CI 發布或正式 Messenger binding。

## B1 公開授權與執行範圍（2026-10-08）

使用者已同意將原始 `tax-helper.zip` 所包含的 **8 個原始檔案全部公開**並原貌納管至本 Public repo，包含 129 題的 `questionBank.js`、學習內容與網頁程式。先前逐檔審查「待確認」是歷史狀態，公開納管授權已解除阻擋。

本輪已完成 **B1 原貌匯入、原功能基線及 deterministic FAQ CSV 轉換器與離線測試**。沒有提交原 ZIP、衍生 `faq.csv`、缺少的 14 張圖片或其他附件；未啟用 GitHub Pages、未做 CX／GCP 操作。B2 AI UI 及 B3 真實 CX 介接仍為後續階段。

## B1 重跑方式

FAQ 工具只需 Python 3.10 以上與標準函式庫，不執行輸入 JavaScript。預設讀根目錄 `questionBank.js`，產生已忽略的 `generated/faq.csv`；CLI 回報版本、題數與 input/output SHA-256，不列正文。

```bash
python tools/question_bank_to_faq.py
python -m unittest discover -s tests -p 'test_*.py' -v
```

CSV 固定二欄 `question,answer`、UTF-8 無 BOM、LF 記錄分隔；保留原陣列順序、完整答案、欄內換行及首尾空白。輸入缺值、錯型別、重複 key／ID／問題、動態或額外 JavaScript 會失敗，既有輸出不受影響。產物不可手改或以試算表重存，也不自動提交或上傳。

本輪 **20/20 Python 測試**（19 項 converter＋1 項八檔原貌 hash）及 **17/17 Chromium 基線**通過。`tests/source_baseline.json` 保存八檔 SHA-256；`.gitattributes` 保留原檔 bytes，`tests/search_baseline.json` 凍結三組搜尋 ID／排序。

瀏覽器測試需 Chromium 與 `tests/requirements-browser.txt` 的 Playwright。它以 route 供應本機原檔，不啟動 HTTP server，阻擋入口設定 API、遊戲與 CDN 的實際請求；不測 live CX 或部署。以下先執行 14 組原功能基線：

```bash
python -m pip install -r tests/requirements-browser.txt
python tests/site_baseline.py --browser /usr/bin/chromium
```

若需重跑全部 17 組，先將原站指定的 XLSX 0.18.5 依賴下載至 repo 外暫存，再由瀏覽器 route 離線提供；不是 XLSX mock，也不將第三方檔或 Excel 納入 Git。

```bash
curl --fail --location --output /tmp/tax-helper-xlsx-0.18.5.js https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js
python tests/site_baseline.py --browser /usr/bin/chromium --xlsx-script /tmp/tax-helper-xlsx-0.18.5.js
```

測試會核對依賴 hash，並以記憶體內合成的真實 OOXML workbook 驗證成功匯入、重複編號／缺題目欄位拒絕與重載行為。14 張學習圖片及返回入口未隨 ZIP 提供；外部服務可用性、Pages 路徑、live CX 與正式上線仍未驗證。

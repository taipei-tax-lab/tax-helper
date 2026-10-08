# TAX AI — Next Task

Last updated: 2026-10-08 (Asia/Taipei)
Status: **PHASE A AUDIT COMPLETE — SOURCE IMPORT DECISION PENDING**
Owner: **Web Codex**；CX 資源由 dialogflow-cx-qa-framework 工作流處理。
Authorization: **本輪僅唯讀盤點、文件與離線方案；未授權來源公開／匯入、Phase B/C 實作、部署或 GCP 寫入**。

## 本輪完成（證據見 PROJECT_STATE.md）

- [x] 讀四份文件、fetch 並核對 GitHub baseline；確認 tax-helper 仍 Public。
- [x] 實際取得使用者 ZIP、驗證 checksum／entries、安全解壓至 repo 外；未假設已取得。
- [x] 有限 Secret scan；未將原始碼／內部題庫／ZIP／CSV 推送 Public repo。
- [x] 核對八個原始檔、questionBank schema／129題／11分類、空值／重複／metadata／2個孤立關聯及功能依賴。
- [x] 核對搜尋頁最小擴充點、快速搜尋／收藏／題庫／詳情／Excel／導覽不可破壞清單。
- [x] 唯讀固定1999 commit 的 transport／result-model／app／RESULT_CONTRACT／測試；提出重用與適配差距。
- [x] 提出最新單一問答卡、同 Session 追問、切模式不 reset、主動 reset、expiry／timeout／error／連續提問事件序列。
- [x] 提出二欄 deterministic converter 與離線／E2E 矩陣；尚未實作或產生正式 CSV。
- [x] 1999 Node 14/14、原 ZIP Chromium 8 組基線通過；未連 Production；整合後 E2E／真實 Excel 成功匯入尚未執行。
- [x] 更新既有 README／STATE／TASK；文件 commit SHA 與遠端驗證於收工回報提供。

## 下一輪單一任務 — 確認來源保護與原貌納管方式

先取得來源納管決策，維持 Phase A，不開始整合實作。

- [ ] 先 fetch／讀四份文件；查驗本輪 checksum 對應原檔仍能存取。新環境若缺來源，明確要求可存取附件／路徑，不假設延續可用。
- [ ] 確認 visibility／可公開範圍：改 Private 或明確核准可公開檔案。Public 狀態本身不等於題庫公開授權；未授權停在來源匯入前。
- [ ] 決策涵蓋 ZIP 安全保存、原碼版控位置、敏感性審查及 generated CSV 排除；不連動網站或其他 repo Production。
- [ ] **只有明確授權來源匯入後**，才原貌納管核准檔案並核對 hash；不順手修正網頁／題庫，不建立 AI UI 或 converter。
- [ ] 記錄決策／未決事項，更新 STATE／TASK、commit／push、回報 branch／SHA／差異／未完成驗證。

### 驗收條件

- 可公開範圍、可納管檔案及目的地有明確記錄；未核准題庫／ZIP／CSV／Secret 不進 GitHub。
- 已授權匯入才標示「已匯入」，原貌檔案與129題 baseline 可追溯；未授權則標示等待決策。
- 原快速搜尋／收藏／Excel／導覽不變；整合／converter 方案仍見 STATE，不另立 workflow 真相。

## STOP boundary

- 未授權來源公開／匯入，不 push 內部資料，不自行改 repository visibility。
- 未取得 Phase B/C 授權，不新增 AI UI／模式切換／transport integration／converter，也不修既有網站／題庫。
- 不寫 CX Agent、Playbook、Tool、Data Store、GCS、Messenger allowed domains、Environment／Production、IAM；禁止部署或觸發部署。
- 不複製1999正式 config/binding、不修改1999／Rental、不猜網域／資源 ID／成功狀態。
- 來源／權限／live 驗證缺失記 blocker；offline fixtures 不是 live CX／稅務品質實證。

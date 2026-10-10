> **2026-10-10 後續驗收狀態（依使用者確認）**：真實瀏覽器 × CX 正式 FAQ Flow 整合驗收現已完成，狀態 **LIVE / USABLE — owner-confirmed**。下文 `PENDING`、Cloud Chromium TLS blocker 與舊 Checklist 均為 2026-10-09 的歷史交接快照；沒有追改歷史測試結果。詳 [Owner Acceptance](TAX_AI_OWNER_ACCEPTANCE_2026-10-10.md)。本輪僅更新 Markdown。

# TAX AI Web B3／CX FAQ Flow handoff

Date: 2026-10-09 (Asia/Taipei)。Backend **TAX AI INTERNAL FAQ FLOW BACKEND READY FOR WEB CUTOVER**。

此文件記 Web 消費契約；binding 唯一真相是 backend merged main `3c214fde52d17810af85bd601e05b72291df67ff` 的 [authoritative handoff](https://github.com/taipei-tax-lab/dialogflow-cx-qa-framework/blob/3c214fde52d17810af85bd601e05b72291df67ff/docs/TAX_AI_WEB_FLOW_HANDOFF_2026-10-09.md) 及 [machine config](https://github.com/taipei-tax-lab/dialogflow-cx-qa-framework/blob/3c214fde52d17810af85bd601e05b72291df67ff/config/tax_ai_internal_faq_flow_20261009.json)。逐欄一致；PR #4 已 merge。

## 正式 binding

| 欄位 | 正式值 |
| --- | --- |
| projectId | serviceagent-1150909 |
| agentId | 786d0cf9-fd1b-4eb9-af1f-16e41891a603 |
| location | global（SDK預設） |
| expectedEnvironment | e8f1496a-3e23-43b9-a75d-dc53b551e99c |
| Flow | 5bee3876-e595-413d-be3c-729227145e4d |
| languageCode／timeZone | zh-tw／Asia/Taipei |
| SDK | https://www.gstatic.com/dialogflow-console/fast/df-messenger/prod/v1/df-messenger.js |

`faqCurrentPage`：
`projects/serviceagent-1150909/locations/global/agents/786d0cf9-fd1b-4eb9-af1f-16e41891a603/flows/5bee3876-e595-413d-be3c-729227145e4d/pages/START_PAGE`

Messenger integration 已由 backend 證實 Production binding；expectedEnvironment 僅 metadata，不加 environment-id，不改 integration／Production／CX。

每題 accepted text 在 df-request-sent 設定以下 queryParams；setQueryParameters defaults 在初始化／每次send／technical recovery皆相同，使用新arrays。保留其他parameters，覆寫tax_*，刪除 stale currentPlaybook。無 first-turn／解除／re-arm。

```json
{
  "currentPage": "projects/serviceagent-1150909/locations/global/agents/786d0cf9-fd1b-4eb9-af1f-16e41891a603/flows/5bee3876-e595-413d-be3c-729227145e4d/pages/START_PAGE",
  "timeZone": "Asia/Taipei",
  "parameters": {"tax_answers": [], "tax_questions": [], "tax_answer_count": 0}
}
```

hidden＋inert SDK／單一instance、storage none、TTL1800s／timeout60s／Web上限1000。技術session可留，但每題獨立搜尋；最新結果取代舊結果，無reset／transcript。接受前拒絕保留輸入，accepted清原文；已輸入下一草稿則保留。結果heading仍顯示原問題含空白／換行。

## 0～5 FAQ renderer

完整 raw responseMessages[].text.text[] 依序合併，raw無文字才用parsed。backend header、每筆整則 N. question＋完整answer、footer；零筆專用文案。normalizeResult永遠保留完整answer；optional items只在凍結envelope／1～5整筆message成立時建立。

優先用 queryResult.parameters.tax_questions／tax_answers 和可見block exact match；native arrays超過5只取Flow已顯示的5筆。arrays不足時保守使用整則message的首行／answer邊界；不靠答案內數字切段。未知／合併格式完整text fallback。

ol／每FAQ獨立li／原question heading／完整body，細分隔線、上下留白。沒有自造title／來源URL／citation。答案內安全HTTP(S)連結、保留換行、HTML-like走text nodes，無不可信innerHTML。generic explicit citation僅接受實際提供安全來源，不由TAX Q/A合成。

service／webhook／Data Store status不當no-hit；timeout鎖至SDK settle、晚答不顯示、不自動retry。session invalidation清model／generation，settle後technical recovery；SDK recovery throw則AI unavailable，Quick Search正常。極晚SDK事件是否跨operation污染仍需真正browser驗收。

Mock僅明確 ?tax-ai-demo=1、標非正式回答，0～5stateless。production不自動切Mock。無analytics／query answer transcript。原Quick Search／分類／題庫／收藏／詳情／相關／複製／Excel／Learning／導覽保持；Excel僅本機，不同步CX。Public題庫已核准；對內不是身分驗證，未來敏感內容另案處理。

## Acceptance／rollback

[offline證據](B3_TEST_EVIDENCE_2026-10-09.json)、[deployment](PAGES_DEPLOYMENT_2026-10-09.md) 分開記。backend既有Draft36／Production36／nativeMessenger6 PASS，不是本輪Web live proof。

真實browser必驗每題currentPage／tax_*zero／無currentPlaybook、0～5canonical exact Q/A、第二題獨立、no-hit、answer URL、mobile、Quick Search、accepted clear、無reset。CloudTLS／proxy阻擋則保持PENDING；部署完成只標 DEPLOYED / LIVE ACCEPTANCE PENDING。

Launch-critical rollback：config.liveEnabled=false，重建／push／核對Pages，AI回準備中、Quick Search保留。不恢復B2 Playbook、不借其他Agent、不改backend Production。flag=false已offlinePASS；單純Cloud browser trust blocker不觸發產品rollback。

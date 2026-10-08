import {config as defaults} from './config.mjs';
import {MessengerTransport} from './messenger-transport.mjs';
import {normalizeResult, renderResult} from './result-model.mjs';

const panel = document.querySelector('#tax-ai-panel');
const form = document.querySelector('#tax-ai-form');
const input = document.querySelector('#tax-ai-query');
const submit = document.querySelector('#tax-ai-submit');
const reset = document.querySelector('#tax-ai-reset');
const status = document.querySelector('#tax-ai-status');
const result = document.querySelector('#tax-ai-result');
const buttons = [...document.querySelectorAll('[data-tax-mode]')];
const quick = [...document.querySelectorAll('#searchView .search-page-head, #searchMeta, #searchResults')];
const demo = new URL(location.href).searchParams.get('tax-ai-demo') === '1';
const options = demo ? window.__TAX_AI_MOCK_OPTIONS__ || {} : {};
const config = {...defaults};
for (const name of ['requestTimeoutMs', 'sessionTtlSeconds']) {
  if (demo && Number.isFinite(options[name]) && options[name] > 0) config[name] = options[name];
}
let transport, initialization, ready = false, busy = false, composing = false;
let generation = 0, mountCount = 0, latestModel = null;

const messages = {
  initializing: '正在準備離線模擬服務。',
  ready: '請輸入問題。追問沿用同一對話，重置提問可開始新對話。',
  idle: '已重置，可開始新的提問。',
  loading: '正在整理本次回答，請稍候。',
  empty: '尚未取得回答。您可以補充條件，再手動提問或重置。',
  error: '暫時無法取得回答。請稍後手動提問；查詢尚未結束時，按鈕暫時停用。',
  session: '對話脈絡已結束，下一題將開始新對話。請重新送出問題。',
  unavailable: 'AI 服務準備中，請先使用快速搜尋。',
  input: '請輸入問題，並將長度控制在 1000 字以內。',
};

function clearResult() {
  latestModel = null;
  result.hidden = true;
  for (const field of result.querySelectorAll('[data-ai-query], [data-ai-answer], [data-ai-sources]')) {
    field.replaceChildren();
  }
  result.querySelector('[data-ai-source-section]').hidden = true;
}

function showState(name) {
  status.dataset.state = name;
  status.hidden = false;
  status.setAttribute('role', ['error', 'timeout', 'session', 'unavailable'].includes(name) ? 'alert' : 'status');
  status.textContent = name === 'timeout'
    ? transport?.locked
      ? '查詢逾時，尚在等待查詢結束。按鈕恢復後可手動再問；若持續無法恢復，請重新載入頁面。'
      : '查詢逾時，未取得回答。您可以手動再問或重置提問。'
    : messages[name];
}

function controls() {
  const locked = busy || !!transport?.locked;
  submit.disabled = !ready || locked;
  reset.disabled = !ready || locked;
  form.setAttribute('aria-busy', String(locked));
  if (status.dataset.state === 'timeout') showState('timeout');
}

function count() {
  document.querySelector('#tax-ai-counter').textContent = `${input.value.length} / ${config.maxQueryLength}`;
}

async function initialize() {
  if (initialization) return initialization;
  initialization = (async () => {
    try {
      if (!demo) { showState('unavailable'); return; }
      showState('initializing');
      if (options.loaderError) throw new Error('unavailable');
      const {createMock} = await import('./mock-messenger.mjs');
      const {messenger, transportConfig} = createMock(config, {
        ...(Number.isFinite(options.delayMs) && options.delayMs >= 0 ? {delayMs: options.delayMs} : {}),
      });
      mountCount++;
      transport = new MessengerTransport(messenger, transportConfig);
      transport.onInvalidated = () => {
        generation++;
        clearResult();
        showState('session');
        controls();
      };
      transport.onSettled = controls;
      // Test controls exist only in the explicitly labeled offline demo.
      window.taxAiMock = {messenger, transport, get mountCount() { return mountCount; }, get latestModel() { return latestModel; }};
      ready = true;
      showState('ready');
    } catch {
      showState('unavailable');
    } finally {
      controls();
    }
  })();
  return initialization;
}

function setMode(mode) {
  const ai = mode === 'ai';
  for (const button of buttons) button.setAttribute('aria-pressed', String(button.dataset.taxMode === mode));
  for (const element of quick) element.hidden = ai;
  panel.hidden = !ai;
  if (ai) { initialize(); input.focus({preventScroll: true}); }
}

for (const button of buttons) {
  button.disabled = false;
  button.addEventListener('click', () => setMode(button.dataset.taxMode));
}
window.addEventListener('tax-quick-search', () => setMode('quick'));
input.addEventListener('input', count);
input.addEventListener('compositionstart', () => { composing = true; });
input.addEventListener('compositionend', () => { composing = false; });
input.addEventListener('keydown', event => {
  if (event.key !== 'Enter' || event.shiftKey || event.isComposing || composing || event.keyCode === 229) return;
  event.preventDefault();
  if (!submit.disabled) form.requestSubmit();
});
form.addEventListener('submit', async event => {
  event.preventDefault();
  if (!ready || busy || transport.locked || composing) return;
  const query = input.value.trim();
  if (!query || query.length > config.maxQueryLength) { showState('input'); return; }
  const acceptedGeneration = generation;
  busy = true;
  clearResult();
  controls();
  showState('loading');
  try {
    const detail = await transport.send(query);
    if (acceptedGeneration !== generation) return;
    const model = normalizeResult(detail);
    if (!model.answer.trim()) { showState('empty'); return; }
    latestModel = {query, ...model};
    renderResult(model, query, result);
    status.hidden = true;
    result.hidden = false;
    if (!panel.hidden && document.querySelector('#searchView').classList.contains('active')) {
      document.querySelector('#tax-ai-result-title').focus({preventScroll: true});
    }
  } catch (error) {
    if (acceptedGeneration !== generation) return;
    showState(['session', 'empty', 'timeout'].includes(error.message) ? error.message : 'error');
  } finally {
    busy = false;
    controls();
  }
});
reset.addEventListener('click', () => {
  if (reset.disabled) return;
  try {
    transport.reset();
    generation++;
    clearResult();
    input.value = '';
    count();
    showState('idle');
    input.focus();
  } catch {
    showState('error');
  }
  controls();
});

document.querySelector('#tax-ai-notice').textContent = demo
  ? '離線示範：所有回答為模擬資料，非正式稅務答覆。'
  : 'AI 服務準備中；目前可使用快速搜尋。';
setMode('quick');
controls();
count();
panel.dataset.initialized = 'true';

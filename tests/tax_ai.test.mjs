import test from 'node:test';
import assert from 'node:assert/strict';
import {MessengerTransport} from '../assets/tax-ai/messenger-transport.mjs';
import {normalizeResult, safeUrl, textUrls, answerParts} from '../assets/tax-ai/result-model.mjs';
import {MockMessenger, createMock, faqResponse} from '../assets/tax-ai/mock-messenger.mjs';
import {config} from '../assets/tax-ai/config.mjs';

const tick = () => new Promise(resolve => setTimeout(resolve, 0));
const raw = messages => ({raw: {queryResult: {responseMessages: messages}}});
const text = answer => ({data: {messages: [{type: 'text', text: answer}]}});

test('B3 formal binding matches authoritative global FAQ Flow; no Playbook or guessed environment', () => {
  assert.equal(config.liveEnabled, true);
  assert.equal(config.projectId, 'serviceagent-1150909');
  assert.equal(config.agentId, '786d0cf9-fd1b-4eb9-af1f-16e41891a603');
  assert.equal(config.location, 'global');
  assert.equal(config.languageCode, 'zh-tw');
  assert.equal(config.expectedEnvironment, 'e8f1496a-3e23-43b9-a75d-dc53b551e99c');
  assert.equal(config.faqCurrentPage, 'projects/serviceagent-1150909/locations/global/agents/786d0cf9-fd1b-4eb9-af1f-16e41891a603/flows/5bee3876-e595-413d-be3c-729227145e4d/pages/START_PAGE');
  assert.equal(config.messengerScript, 'https://www.gstatic.com/dialogflow-console/fast/df-messenger/prod/v1/df-messenger.js');
  assert.equal('initialPlaybook' in config, false);
});
test('complete raw text wins over partial parsed text; parsed-only fallback remains usable', () => {
  assert.deepEqual(normalizeResult({...raw([{text: {text: ['raw', 'complete second paragraph']}}]), ...text('parsed')}), {answer: 'raw\n\ncomplete second paragraph'});
  assert.deepEqual(normalizeResult(text('parsed')), {answer: 'parsed'});
  assert.deepEqual(normalizeResult(raw([{text: {text: ['第一段', '第二段']}}])), {answer: '第一段\n\n第二段'});
});
test('empty, null and malformed responses never invent an answer', () => {
  for (const detail of [null, undefined, {}, {raw: null}, {data: {messages: 'bad'}}, raw([]), raw([null])]) {
    assert.deepEqual(normalizeResult(detail), {answer: ''});
  }
});
test('1999-specific payloads and guessed FAQ metadata are not adopted', () => {
  assert.deepEqual(normalizeResult(raw([{payload: {universalAnswer: {
    schemaVersion: 1, answer: 'legacy', faqMetadata: {kind: 'official1999Faq', title: 'legacy'},
  }}}])), {answer: ''});
});
test('URL schemes and credentials are rejected', () => {
  for (const url of ['javascript:alert(1)', 'data:text/html,x', '//example.com', 'https://user:pass@example.com', 'https://[bad', null]) {
    assert.equal(safeUrl(url), null);
  }
  assert.equal(safeUrl('https://EXAMPLE.com:443/a'), 'https://example.com/a');
});
test('explicit citations are canonicalized, deduplicated and compared with inline links', () => {
  const detail = {data: {messages: [{type: 'text', text: '**[來源](https://EXAMPLE.com:443/a)**'},
    {type: 'citation', url: 'https://example.com/a'},
    {citations: [null, {url: 'https://example.com/b', title: '<img>'}, {url: 'https://example.com/b'}, {url: 'javascript:x'}]}]}};
  assert.deepEqual(normalizeResult(detail).sources, [{url: 'https://example.com/b', title: '<img>'}]);
});
test('minimal Markdown preserves balanced URL parentheses and leaves images inert', () => {
  assert.deepEqual(textUrls('**[說明](https://example.com/a_(b))**\nHTTPS://example.com/c_(d)。'),
    ['https://example.com/a_(b)', 'https://example.com/c_(d)']);
  for (const answer of ['![圖](https://example.com/image)', '[x](javascript:alert(1))', '[x](https://example.com/unclosed']) {
    assert.deepEqual(textUrls(answer), []);
  }
  assert.deepEqual(answerParts('<script>文字</script>'), [{type: 'text', text: '<script>文字</script>'}]);
});

function harness(timeout = 1000, synchronousThrow = false) {
  const root = new EventTarget();
  const requests = [];
  let parameters = {}, session = 0, resolve, reject;
  const preEventDefaults = [];
  const emit = (name, detail) => root.dispatchEvent(new CustomEvent(name, {detail, cancelable: true}));
  const messenger = {
    setQueryParameters(value) { parameters = {...parameters, ...value}; }, // Exercise stale SDK defaults.
    startNewSession(options) { assert.deepEqual(options, {retainHistory: false}); session++; },
    sendQuery(query) {
      if (synchronousThrow) throw new Error('SDK failed synchronously');
      preEventDefaults.push(structuredClone(parameters));
      const body = {queryInput: {text: {text: query}}, queryParams: structuredClone(parameters)};
      emit('df-request-sent', {data: {requestBody: body}});
      requests.push(body);
      return new Promise((success, failure) => { resolve = success; reject = failure; });
    },
  };
  const transport = new MessengerTransport(messenger, {...config, requestTimeoutMs: timeout}, root);
  return {root, messenger, transport, requests, emit, preEventDefaults, get defaults() { return parameters; }, get session() { return session; },
    answer(detail = text('回答')) { assert.equal(emit('df-response-received', detail), false); resolve(); },
    settle() { resolve(); }, fail() { reject(new Error('SDK rejection')); },
  };
}

const required = () => ({currentPage: config.faqCurrentPage, timeZone: 'Asia/Taipei',
  parameters: {tax_answers: [], tax_questions: [], tax_answer_count: 0}});
test('first/second/third queries and pre-event SDK defaults always reset FAQ parameters', async () => {
  const h = harness();let accepted = 0;h.transport.onAccepted = () => accepted++;
  assert.deepEqual(h.defaults, required());
  for (const query of ['第一完整問題', '第二完整問題', '第三完整問題']) {
    const promise = h.transport.send(query);
    assert.deepEqual(h.preEventDefaults.at(-1), required());
    assert.deepEqual(h.requests.at(-1).queryParams, required());
    h.defaults.parameters.tax_answers.push('stale answer');
    h.defaults.parameters.tax_questions.push('stale question');h.defaults.parameters.tax_answer_count = 9;
    h.answer();await promise;await tick();
  }
  assert.equal(accepted, 3);assert.equal(h.session, 0);h.transport.dispose();
});
test('internal technical recovery creates a session with identical stateless FAQ defaults', async () => {
  const h = harness();const first = h.transport.send('第一題');h.answer();await first;await tick();
  h.transport.recoverSession();assert.deepEqual(h.defaults, required());
  assert.equal(h.transport.reset, undefined);assert.equal(h.transport.armed, undefined);
  const second = h.transport.send('新獨立搜尋');assert.equal(h.session, 1);
  assert.deepEqual(h.requests[1].queryParams, required());
  h.answer();await second;await tick();h.transport.dispose();
});
test('duplicate sends and technical recovery are blocked while the SDK operation is pending', async () => {
  const h = harness();
  const first = h.transport.send('第一題');
  await assert.rejects(h.transport.send('第二題'), /busy/);
  assert.throws(() => h.transport.recoverSession(), /busy/);
  assert.throws(() => h.transport.dispose(), /busy/);
  assert.equal(h.requests.length, 1);
  h.answer(); await first; await tick(); h.transport.dispose();
});
test('unsolicited and duplicate request events never count as accepted queries', async () => {
  const h = harness();
  assert.equal(h.emit('df-request-sent', {data: {requestBody: {queryInput: {text: {text: 'unsolicited'}}}}}), false);
  assert.deepEqual(h.defaults, required());
  const promise = h.transport.send('第一題');
  assert.equal(h.emit('df-request-sent', {data: {requestBody: h.requests[0]}}), false);
  h.answer(); await promise; await tick(); h.transport.dispose();
});
test('foreign Messenger events are ignored', async () => {
  const h = harness();
  const promise = h.transport.send('第一題');
  const foreign = new EventTarget();
  const event = new CustomEvent('df-response-received', {detail: text('foreign'), cancelable: true});
  Object.defineProperty(event, 'target', {value: foreign});
  Object.defineProperty(event, 'composedPath', {value: () => [foreign, h.root]});
  h.root.dispatchEvent(event);
  assert.ok(h.transport.pending);
  h.answer(); assert.equal(normalizeResult(await promise).answer, '回答'); await tick(); h.transport.dispose();
});
test('idle expiry notifies the UI and recovers identical FAQ defaults', () => {
  const h = harness(); const notices = [];
  h.transport.onInvalidated = reason => notices.push(reason);
  h.emit('df-session-expired', {});
  assert.deepEqual(notices, ['df-session-expired']);
  assert.equal(h.session, 1);
  assert.deepEqual(h.defaults, required());
  h.transport.dispose();
});
test('in-flight end rejects immediately, ignores late response and recovers only after settle', async () => {
  const h = harness(); const notices = [];
  h.transport.onInvalidated = reason => notices.push(reason);
  const promise = h.transport.send('第一題');
  h.emit('df-session-ended', {});
  await assert.rejects(promise, /session/);
  assert.equal(h.session, 0);
  assert.equal(h.transport.locked, true);
  h.answer(text('old result')); await tick();
  assert.equal(h.session, 1);
  assert.deepEqual(notices, ['df-session-ended']);
  const next = h.transport.send('新對話');
  assert.deepEqual(h.requests[1].queryParams, required());
  h.answer(); await next; await tick(); h.transport.dispose();
});
test('timeout stays locked, late response is ignored and no automatic retry occurs', async () => {
  const h = harness(15); const promise = h.transport.send('慢查詢');
  await assert.rejects(promise, /timeout/);
  assert.equal(h.transport.locked, true);
  await assert.rejects(h.transport.send('第二題'), /busy/);
  h.answer(text('late')); await tick();
  assert.equal(h.transport.locked, false);
  assert.equal(h.requests.length, 1);
  h.transport.dispose();
});
test('expiry after timeout recovers FAQ defaults once the SDK settles', async () => {
  const h = harness(15); const promise = h.transport.send('慢查詢');
  await assert.rejects(promise, /timeout/);
  h.emit('df-session-expired', {});
  assert.equal(h.session, 0);
  h.settle(); await tick();
  assert.equal(h.session, 1);
  assert.deepEqual(h.defaults, required());
  h.transport.dispose();
});
test('SDK error rejects once, unlocks after settle and does not retry', async () => {
  const h = harness(); const promise = h.transport.send('第一題');
  h.emit('df-messenger-error', {}); h.fail();
  await assert.rejects(promise, /service/); await tick();
  assert.equal(h.transport.locked, false); assert.equal(h.requests.length, 1); h.transport.dispose();
});
test('synchronous SDK failure unlocks and reports a service error', async () => {
  const h = harness(1000, true); let settlements = 0;
  h.transport.onSettled = () => settlements++;
  await assert.rejects(h.transport.send('第一題'), /service/);
  assert.equal(h.transport.locked, false); assert.equal(settlements, 1); h.transport.dispose();
});
test('SDK settlement without a response is an empty error', async () => {
  const h = harness(); const promise = h.transport.send('第一題'); h.settle();
  await assert.rejects(promise, /empty/); await tick(); h.transport.dispose();
});
test('Mock is independent per query despite shared technical session; no transcript', async () => {
  const {messenger, transportConfig} = createMock({...config, requestTimeoutMs: 1000}, {delayMs: 0});
  const transport = new MessengerTransport(messenger, transportConfig);
  const first = normalizeResult(await transport.send('第一題'));await tick();
  const second = normalizeResult(await transport.send('不同的完整問題'));await tick();
  assert.deepEqual(first, second);assert.equal(first.items.length, 2);
  assert.equal(messenger.requests[0].session, messenger.requests[1].session);
  assert.deepEqual(messenger.requests[0].queryParams, required());
  assert.deepEqual(messenger.requests[1].queryParams, required());
  assert.equal(messenger.requests[0].query, undefined);
  messenger.dispose();transport.dispose();
});
test('Mock TTL emits expiry and uses a fresh session', async () => {
  const messenger = new MockMessenger({delayMs: 0, ttlMs: 20});
  const transport = new MessengerTransport(messenger, config);
  const before = messenger.session;
  await new Promise((resolve, reject) => {
    const watchdog = setTimeout(() => reject(new Error('Mock TTL did not expire')), 200);
    transport.onInvalidated = () => { clearTimeout(watchdog); resolve(); };
  });
  assert.equal(messenger.session, before + 1);
  messenger.dispose(); transport.dispose();
});

for (let count = 0; count <= 5; count++) test(`native ${count} results preserve complete text/Q&A/order without citations`, () => {
  const detail = faqResponse(count);
  const result = normalizeResult({...detail, ...text('only first parsed fragment')});
  assert.equal(result.answer, detail.raw.queryResult.responseMessages.flatMap(m => m.text.text).join('\n\n'));
  assert.equal(result.items?.length || 0, count);
  assert.equal(result.sources, undefined);
  if (count) {
    const params = detail.raw.queryResult.parameters;
    assert.deepEqual(result.items, params.tax_questions.map((question, i) => ({question, answer: params.tax_answers[i]})));
    assert.ok(result.items.every(x => x.answer.includes('\n1. 原有編號與換行\n2. 第二項條件')));
  } else assert.equal(result.items, undefined);
});
test('native arrays over five use only complete Flow-visible records; CRLF and multiline question intact', () => {
  const detail = faqResponse(5), qr = detail.raw.queryResult;
  qr.parameters.tax_questions.push('not visible');qr.parameters.tax_answers.push('not visible');
  qr.parameters.tax_answer_count = 6;
  qr.parameters.tax_questions[0] = '完整\r\n多行問題';qr.parameters.tax_answers[0] = '一\r\n1. 本文\n2. 仍是本文';
  qr.responseMessages[1].text.text[0] = `1. ${qr.parameters.tax_questions[0]}\n${qr.parameters.tax_answers[0]}`;
  const result = normalizeResult(detail);
  assert.equal(result.items.length, 5);assert.deepEqual(result.items[0], {question: qr.parameters.tax_questions[0], answer: qr.parameters.tax_answers[0]});
});
test('missing or truncated structured arrays fall back to whole text messages, never split internal numbering', () => {
  for (const incomplete of [false, true]) {
    const detail = faqResponse(2);
    if (incomplete) detail.raw.queryResult.parameters.tax_answers[0] = 'truncated';
    else delete detail.raw.queryResult.parameters;
    const result = normalizeResult(detail);
    assert.equal(result.items.length, 2);assert.ok(result.items[0].answer.includes('\n2. 第二項條件'));
  }
});
test('combined or unknown text remains faithful fallback; payloads never manufacture title/url', () => {
  const detail = faqResponse(2), combined = detail.raw.queryResult.responseMessages.flatMap(m => m.text.text).join('\n\n');
  assert.deepEqual(normalizeResult(raw([{text: {text: [combined]}}])), {answer: combined});
  detail.raw.queryResult.responseMessages[0].text.text[0] = 'Unknown header';
  assert.equal(normalizeResult(detail).items, undefined);
  const noTitleUrl = normalizeResult(faqResponse(1));
  assert.deepEqual(Object.keys(noTitleUrl.items[0]).sort(), ['answer', 'question']);
});
test('service errors cannot become genuine-zero fallback', () => {
  for (const mutate of [x => {x.error = {message: 'HTTP error'};},
    x => {x.queryResult.webhookStatuses = [{message: 'unavailable'}];},
    x => {x.queryResult.diagnosticInfo = {'DataStore Execution Sequence': {steps: [{status: {message: 'retrieval error'}}]}};}]) {
    const detail = faqResponse(0);mutate(detail.raw);assert.throws(() => normalizeResult(detail), /service/);
  }
});
test('accepted request discards stale page/playbook/tax values and preserves unrelated parameters', async () => {
  const h = harness();const promise = h.transport.send('  完整原問句\n第二行  ');
  // The first actual accepted request already has all defaults; duplicate cannot mutate it.
  assert.equal(h.requests[0].queryInput.text.text, '  完整原問句\n第二行  ');
  assert.deepEqual(h.requests[0].queryParams, required());
  h.answer();await promise;await tick();h.transport.dispose();
  const root = new EventTarget();let body;
  const sdk = {setQueryParameters() {}, startNewSession() {}, sendQuery(query) {
    body = {queryInput: {text: {text: query}}, queryParams: {currentPlaybook: 'stale', currentPage: 'old',
      parameters: {tax_answers: ['old'], tax_questions: ['old'], tax_answer_count: 7, keep: 'other'}}};
    root.dispatchEvent(new CustomEvent('df-request-sent', {detail: {data: {requestBody: body}}, cancelable: true}));
    root.dispatchEvent(new CustomEvent('df-response-received', {detail: text('answer'), cancelable: true}));
  }};
  const transport = new MessengerTransport(sdk, config, root);await transport.send('exact');await tick();
  assert.deepEqual(body.queryParams, {...required(), parameters: {...required().parameters, keep: 'other'}});transport.dispose();
});
test('pre-acceptance rejection never invokes accepted callback', async () => {
  const {messenger, transportConfig} = createMock(config, {delayMs: 0});const transport = new MessengerTransport(messenger, transportConfig);
  let accepted = 0;transport.onAccepted = () => accepted++;
  messenger.enqueue({beforeError: true});await assert.rejects(transport.send('keep this question'), /service/);await tick();
  assert.equal(accepted, 0);assert.equal(messenger.requests.length, 0);messenger.dispose();transport.dispose();
});
test('technical recovery SDK failure becomes unavailable without throwing or retrying', async () => {
  const h = harness();let unavailable = 0;h.transport.onUnavailable = () => unavailable++;
  h.messenger.startNewSession = () => {throw new Error('SDK recovery failed');};
  h.emit('df-session-expired', {});assert.equal(unavailable, 1);assert.equal(h.transport.unavailable, true);
  await assert.rejects(h.transport.send('retain for later'), /service/);assert.equal(h.requests.length, 0);h.transport.dispose();
});

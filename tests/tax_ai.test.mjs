import test from 'node:test';
import assert from 'node:assert/strict';
import {MessengerTransport} from '../assets/tax-ai/messenger-transport.mjs';
import {normalizeResult, safeUrl, textUrls, answerParts} from '../assets/tax-ai/result-model.mjs';
import {MockMessenger, createMock} from '../assets/tax-ai/mock-messenger.mjs';
import {config, MOCK_PLAYBOOK} from '../assets/tax-ai/config.mjs';

const tick = () => new Promise(resolve => setTimeout(resolve, 0));
const raw = messages => ({raw: {queryResult: {responseMessages: messages}}});
const text = answer => ({data: {messages: [{type: 'text', text: answer}]}});

test('B2 config has no live binding or external loader', () => {
  assert.equal(config.liveEnabled, false);
  assert.deepEqual(Object.keys(config).sort(), ['liveEnabled', 'maxQueryLength', 'requestTimeoutMs', 'sessionTtlSeconds']);
  assert.equal(MOCK_PLAYBOOK, 'mock-only-tax-faq');
});
test('parsed primary answer wins; raw text fallback preserves full paragraphs', () => {
  assert.deepEqual(normalizeResult({...raw([{text: {text: ['raw']}}]), ...text('parsed')}), {answer: 'parsed'});
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
  const emit = (name, detail) => root.dispatchEvent(new CustomEvent(name, {detail, cancelable: true}));
  const messenger = {
    setQueryParameters(value) { parameters = {...parameters, ...value}; }, // Exercise stale SDK defaults.
    startNewSession(options) { assert.deepEqual(options, {retainHistory: false}); session++; },
    sendQuery(query) {
      if (synchronousThrow) throw new Error('SDK failed synchronously');
      const body = {queryInput: {text: {text: query}}, queryParams: {...parameters}};
      emit('df-request-sent', {data: {requestBody: body}});
      requests.push(body);
      return new Promise((success, failure) => { resolve = success; reject = failure; });
    },
  };
  const transport = new MessengerTransport(messenger, {initialPlaybook: MOCK_PLAYBOOK, requestTimeoutMs: timeout}, root);
  return {root, messenger, transport, requests, emit, get session() { return session; },
    answer(detail = text('回答')) { assert.equal(emit('df-response-received', detail), false); resolve(); },
    settle() { resolve(); }, fail() { reject(new Error('SDK rejection')); },
  };
}

test('first-turn override is removed on followup even with stale SDK defaults', async () => {
  const h = harness();
  let promise = h.transport.send('第一題');
  assert.equal(h.requests[0].queryParams.currentPlaybook, MOCK_PLAYBOOK);
  assert.equal(h.requests[0].queryParams.timeZone, 'Asia/Taipei');
  h.answer(); await promise; await tick();
  promise = h.transport.send('追問');
  assert.equal(h.requests[1].queryParams.currentPlaybook, undefined);
  h.answer(); await promise; await tick();
  assert.equal(h.session, 0);
  h.transport.dispose();
});
test('manual reset creates a new session and re-arms first-turn override', async () => {
  const h = harness();
  const first = h.transport.send('第一題'); h.answer(); await first; await tick();
  h.transport.reset();
  const second = h.transport.send('新對話');
  assert.equal(h.session, 1);
  assert.equal(h.requests[1].queryParams.currentPlaybook, MOCK_PLAYBOOK);
  h.answer(); await second; await tick(); h.transport.dispose();
});
test('duplicate sends and reset are blocked while the SDK operation is pending', async () => {
  const h = harness();
  const first = h.transport.send('第一題');
  await assert.rejects(h.transport.send('第二題'), /busy/);
  assert.throws(() => h.transport.reset(), /busy/);
  assert.throws(() => h.transport.dispose(), /busy/);
  assert.equal(h.requests.length, 1);
  h.answer(); await first; await tick(); h.transport.dispose();
});
test('unsolicited and duplicate request events cannot consume the override', async () => {
  const h = harness();
  assert.equal(h.emit('df-request-sent', {data: {requestBody: {queryInput: {text: {text: 'unsolicited'}}}}}), false);
  assert.equal(h.transport.armed, true);
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
test('idle expiry notifies the UI and starts a new armed session', () => {
  const h = harness(); const notices = [];
  h.transport.onInvalidated = reason => notices.push(reason);
  h.emit('df-session-expired', {});
  assert.deepEqual(notices, ['df-session-expired']);
  assert.equal(h.session, 1);
  assert.equal(h.transport.armed, true);
  h.transport.dispose();
});
test('in-flight end rejects immediately, ignores late response and resets only after settle', async () => {
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
  assert.equal(h.requests[1].queryParams.currentPlaybook, MOCK_PLAYBOOK);
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
test('expiry after timeout still re-arms once the SDK settles', async () => {
  const h = harness(15); const promise = h.transport.send('慢查詢');
  await assert.rejects(promise, /timeout/);
  h.emit('df-session-expired', {});
  assert.equal(h.session, 0);
  h.settle(); await tick();
  assert.equal(h.session, 1);
  assert.equal(h.transport.armed, true);
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
test('Mock keeps session/turn context without storing a frontend transcript', async () => {
  const {messenger, transportConfig} = createMock({...config, requestTimeoutMs: 1000}, {delayMs: 0});
  const transport = new MessengerTransport(messenger, transportConfig);
  await transport.send('第一題'); await tick();
  const response = await transport.send('那期限呢？'); await tick();
  assert.match(normalizeResult(response).answer, /第 2 次/);
  assert.equal(messenger.requests[0].session, messenger.requests[1].session);
  assert.equal(messenger.requests[1].queryParams.currentPlaybook, undefined);
  assert.equal(messenger.requests[0].query, undefined);
  transport.reset(); assert.equal(messenger.turn, 0);
  messenger.dispose(); transport.dispose();
});
test('Mock TTL emits expiry and uses a fresh session', async () => {
  const messenger = new MockMessenger({delayMs: 0, ttlMs: 20});
  const transport = new MessengerTransport(messenger, {...config, initialPlaybook: MOCK_PLAYBOOK});
  const before = messenger.session;
  await new Promise((resolve, reject) => {
    const watchdog = setTimeout(() => reject(new Error('Mock TTL did not expire')), 200);
    transport.onInvalidated = () => { clearTimeout(watchdog); resolve(); };
  });
  assert.equal(messenger.session, before + 1);
  messenger.dispose(); transport.dispose();
});

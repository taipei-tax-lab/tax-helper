// Explicit offline demo only. Every response is independent and synthetic.
import {FAQ_HEADER, FAQ_FOOTER, FAQ_FALLBACK} from './result-model.mjs';

export function faqResponse(count = 2) {
  const items = Array.from({length: count}, (_, i) => ({question: `合成 FAQ 問題 ${i + 1}`,
    answer: `完整合成答案 ${i + 1}，非正式稅務答覆。\n1. 原有編號與換行\n2. 第二項條件`}));
  return {raw: {queryResult: {
    parameters: {tax_questions: items.map(x => x.question), tax_answers: items.map(x => x.answer), tax_answer_count: count},
    responseMessages: (count ? [FAQ_HEADER, ...items.map((x, i) => `${i + 1}. ${x.question}\n${x.answer}`), FAQ_FOOTER]
      : [FAQ_FALLBACK]).map(text => ({text: {text: [text]}})),
  }}};
}

export class MockMessenger extends EventTarget {
  constructor({delayMs = 250, ttlMs = 1_800_000} = {}) {
    super();
    this.delayMs = delayMs;
    this.ttlMs = ttlMs;
    this.session = 0;
    this.requests = []; // Technical session/ordinal/parameters only; no query/answer transcript.
    this.queue = [];
    this.held = [];
    this.startNewSession({retainHistory: false});
  }

  emit(name, detail = {}) {
    return this.dispatchEvent(new CustomEvent(name, {detail, cancelable: true}));
  }

  setQueryParameters(value) { this.parameters = {...value}; }

  startNewSession(options) {
    this.lastResetOptions = options;
    this.session++;
    this.ordinal = 0;
    this.touch();
  }

  touch() {
    clearTimeout(this.timer);
    this.timer = setTimeout(() => this.expire(), this.ttlMs);
    this.timer?.unref?.();
  }

  expire(ended = false) {
    clearTimeout(this.timer);
    this.emit(ended ? 'df-session-ended' : 'df-session-expired');
  }

  enqueue(fixture) { this.queue.push(fixture); }
  release() { this.held.shift()?.(); }
  dispose() { clearTimeout(this.timer); }

  async sendQuery(query) {
    const fixture = this.queue.shift() || {kind: 'faq'};
    if (fixture.beforeError) throw new Error('synthetic pre-acceptance error');
    if (fixture.holdBeforeAccepted) await new Promise(resolve => this.held.push(resolve));
    const body = {queryInput: {text: {text: query}}, queryParams: {...this.parameters}};
    if (!this.emit('df-request-sent', {data: {requestBody: body}})) return;
    const acceptedSession = this.session;
    const ordinal = ++this.ordinal;
    this.requests.push({session: acceptedSession, ordinal, queryParams: structuredClone(body.queryParams)});
    this.touch();
    if (fixture.hold) await new Promise(resolve => this.held.push(resolve));
    else await new Promise(resolve => setTimeout(resolve, fixture.delayMs ?? this.delayMs));
    if (fixture.kind === 'error') {
      this.emit('df-messenger-error');
      throw new Error('synthetic service error');
    }
    if (fixture.kind !== 'silent') {
      const detail = fixture.kind === 'empty' ? {data: {messages: []}}
        : fixture.kind === 'malformed' ? null
        : fixture.detail ?? faqResponse(fixture.count ?? 2);
      this.emit('df-response-received', detail);
    }
    if (this.session === acceptedSession) this.touch();
  }
}

export function createMock(config, options = {}) {
  const messenger = new MockMessenger({ttlMs: config.sessionTtlSeconds * 1000, ...options});
  return {messenger, transportConfig: {...config}};
}

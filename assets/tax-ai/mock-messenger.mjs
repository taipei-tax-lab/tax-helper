// Local synthetic backend for B2. No SDK, HTTP client, tax answers or browser storage.
import {MOCK_PLAYBOOK} from './config.mjs';

export class MockMessenger extends EventTarget {
  constructor({delayMs = 250, ttlMs = 1_800_000} = {}) {
    super();
    this.delayMs = delayMs;
    this.ttlMs = ttlMs;
    this.session = 0;
    this.requests = []; // Diagnostics contain session/turn/parameters, never question/answer text.
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
    this.turn = 0;
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
    const body = {queryInput: {text: {text: query}}, queryParams: {...this.parameters}};
    if (!this.emit('df-request-sent', {data: {requestBody: body}})) return;
    const acceptedSession = this.session;
    const turn = ++this.turn;
    this.requests.push({session: acceptedSession, turn, queryParams: structuredClone(body.queryParams)});
    this.touch();
    const fixture = this.queue.shift() || {kind: 'text'};
    if (fixture.hold) await new Promise(resolve => this.held.push(resolve));
    else await new Promise(resolve => setTimeout(resolve, fixture.delayMs ?? this.delayMs));
    if (fixture.kind === 'error') {
      this.emit('df-messenger-error');
      throw new Error('synthetic service error');
    }
    if (fixture.kind !== 'silent') {
      const detail = fixture.kind === 'empty' ? {data: {messages: []}}
        : fixture.kind === 'malformed' ? null
        : fixture.detail ?? {data: {messages: [{type: 'text', text:
          `這是離線模擬回答，非正式稅務答覆。\n同一個模擬對話的第 ${turn} 次提問；追問保留此對話脈絡。`} ]}};
      this.emit('df-response-received', detail);
    }
    if (this.session === acceptedSession) this.touch();
  }
}

export function createMock(config, options = {}) {
  const messenger = new MockMessenger({ttlMs: config.sessionTtlSeconds * 1000, ...options});
  return {messenger, transportConfig: {...config, initialPlaybook: MOCK_PLAYBOOK}};
}

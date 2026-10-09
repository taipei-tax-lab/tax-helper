// Messenger is the sole live transport; every accepted text is independent FAQ search.
export class MessengerTransport {
  constructor(messenger, config, eventRoot = messenger) {
    this.messenger = messenger;
    this.config = config;
    this.eventRoot = eventRoot;
    this.pending = null;
    this.locked = false;
    this.recoverAfterSettled = false;
    this.listeners = [];
    this.listen('df-request-sent', event => {
      const body = event.detail?.data?.requestBody;
      // Reject unsolicited, duplicate and foreign queries; never consume a draft.
      if (!this.pending || this.pending.sent || body?.queryInput?.text?.text !== this.pending.query) {
        if (event.cancelable) event.preventDefault();
        return;
      }
      body.queryParams ||= {};
      delete body.queryParams.currentPlaybook;
      body.queryParams.currentPage = this.config.faqCurrentPage;
      body.queryParams.timeZone = 'Asia/Taipei';
      if (!body.queryParams.parameters || typeof body.queryParams.parameters !== 'object'
        || Array.isArray(body.queryParams.parameters)) body.queryParams.parameters = {};
      Object.assign(body.queryParams.parameters, {tax_answers: [], tax_questions: [], tax_answer_count: 0});
      this.pending.sent = true;
      this.onAccepted?.({query: this.pending.query});
    });
    this.listen('df-response-received', event => {
      if (event.cancelable) event.preventDefault();
      if (!this.pending?.sent) return;
      this.finish(null, event.detail);
    });
    this.listen('df-messenger-error', () => this.finish(new Error('service')));
    for (const name of ['df-session-expired', 'df-session-ended']) {
      this.listen(name, () => {
        this.finish(new Error('session'));
        this.recoverAfterSettled = this.locked;
        this.onInvalidated?.(name);
        if (!this.locked) this.recoverSession();
      });
    }
    this.setDefaults();
  }

  listen(name, action) {
    const listener = event => {
      const path = event.composedPath?.() || [];
      if (event.target !== this.eventRoot && !path.includes(this.messenger)) return;
      action(event);
    };
    this.eventRoot.addEventListener(name, listener);
    this.listeners.push([name, listener]);
  }

  setDefaults() {
    this.messenger.setQueryParameters({
      timeZone: 'Asia/Taipei', currentPage: this.config.faqCurrentPage,
      parameters: {tax_answers: [], tax_questions: [], tax_answer_count: 0},
    });
  }

  recoverSession() {
    if (this.locked) throw new Error('busy');
    try {
      this.messenger.startNewSession({retainHistory: false});
      this.setDefaults();
    } catch {
      this.unavailable = true;
      this.onUnavailable?.();
    }
  }

  finish(error, detail) {
    if (!this.pending) return;
    const pending = this.pending;
    this.pending = null;
    clearTimeout(pending.timer);
    if (error) pending.reject(error);
    else pending.resolve(detail);
  }

  send(query) {
    if (this.unavailable) return Promise.reject(new Error('service'));
    if (this.locked || this.pending) return Promise.reject(new Error('busy'));
    this.locked = true;
    return new Promise((resolve, reject) => {
      const pending = {query, resolve, reject, sent: false};
      this.pending = pending;
      pending.timer = setTimeout(() => {
        this.finish(new Error('timeout'));
        // Keep locked until the SDK operation settles, even after rejecting our promise.
      }, this.config.requestTimeoutMs);
      const settled = () => {
        this.locked = false;
        if (this.recoverAfterSettled) {
          this.recoverAfterSettled = false;
          this.recoverSession();
        }
        this.onSettled?.();
      };
      let operation;
      try {
        this.setDefaults();
        operation = this.messenger.sendQuery(query);
      } catch {
        this.finish(new Error('service'));
        settled();
        return;
      }
      Promise.resolve(operation).then(() => {
        if (this.pending === pending) this.finish(new Error('empty'));
      }, () => {
        if (this.pending === pending) this.finish(new Error('service'));
      }).then(settled);
    });
  }

  dispose() {
    if (this.locked) throw new Error('busy');
    for (const [name, listener] of this.listeners) this.eventRoot.removeEventListener(name, listener);
  }
}

/** One hidden SDK instance; global Agent and Production binding come from handoff. */
export function loadMessenger(config) {
  return new Promise((resolve, reject) => {
    const messenger = document.createElement('df-messenger');
    messenger.hidden = true;messenger.inert = true;
    for (const [name, value] of Object.entries({
      'project-id': config.projectId, 'agent-id': config.agentId,
      'language-code': config.languageCode, 'storage-option': 'none',
      'session-ttl': String(config.sessionTtlSeconds), 'max-query-length': '-1',
    })) messenger.setAttribute(name, value);
    // Global is SDK's default. Environment is integration-side, never a guessed attribute.
    messenger.append(document.createElement('df-messenger-chat'));
    const cleanup = () => { clearTimeout(timer);window.removeEventListener('df-messenger-loaded', loaded); };
    const fail = () => { cleanup();messenger.remove();reject(new Error('unavailable')); };
    const loaded = () => {
      if (typeof messenger.sendQuery !== 'function' || typeof messenger.setQueryParameters !== 'function') return;
      cleanup();
      try { messenger.startNewSession({retainHistory: false});resolve(messenger); }
      catch { messenger.remove();reject(new Error('unavailable')); }
    };
    const timer = setTimeout(fail, 20_000);
    window.addEventListener('df-messenger-loaded', loaded);
    document.body.append(messenger);
    const script = document.createElement('script');script.src = config.messengerScript;
    script.onerror = fail;
    document.body.append(script);
  });
}

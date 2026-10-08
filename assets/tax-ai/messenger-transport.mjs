// Adapted from the pinned 1999 Messenger transport; no loader or live binding in B2.
export class MessengerTransport {
  constructor(messenger, config, eventRoot = messenger) {
    this.messenger = messenger;
    this.config = config;
    this.eventRoot = eventRoot;
    this.armed = true;
    this.pending = null;
    this.locked = false;
    this.rearmAfterSettled = false;
    this.listeners = [];
    this.listen('df-request-sent', event => {
      const body = event.detail?.data?.requestBody;
      // Only the accepted user operation can consume the first-turn override.
      if (!this.pending || this.pending.sent || body?.queryInput?.text?.text !== this.pending.query) {
        if (event.cancelable) event.preventDefault();
        return;
      }
      body.queryParams ||= {};
      if (this.armed) body.queryParams.currentPlaybook = this.config.initialPlaybook;
      else delete body.queryParams.currentPlaybook;
      body.queryParams.timeZone = 'Asia/Taipei';
      this.pending.sent = true;
      this.armed = false;
      this.messenger.setQueryParameters({timeZone: 'Asia/Taipei'});
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
        this.rearmAfterSettled = this.locked;
        this.onInvalidated?.(name);
        if (!this.locked) this.reset();
      });
    }
    this.arm();
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

  arm() {
    this.armed = true;
    this.messenger.setQueryParameters({
      timeZone: 'Asia/Taipei', currentPlaybook: this.config.initialPlaybook,
    });
  }

  reset() {
    if (this.locked) throw new Error('busy');
    this.messenger.startNewSession({retainHistory: false});
    this.arm();
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
        if (this.rearmAfterSettled) {
          this.rearmAfterSettled = false;
          this.reset();
        }
        this.onSettled?.();
      };
      let operation;
      try {
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

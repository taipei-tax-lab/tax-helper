// B2 has no live binding, project/agent IDs, SDK URL or credentials.
export const config = Object.freeze({
  liveEnabled: false,
  requestTimeoutMs: 60_000,
  sessionTtlSeconds: 1800,
  maxQueryLength: 1000,
});

// A synthetic marker only. Never a guessed CX resource name.
export const MOCK_PLAYBOOK = 'mock-only-tax-faq';

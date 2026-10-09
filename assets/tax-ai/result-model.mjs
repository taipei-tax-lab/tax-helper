/** Complete TAX AI text baseline; optional exact question/answer presentation items. */
export function safeUrl(value) {
  if (typeof value !== 'string' || !/^https?:\/\//i.test(value)) return null;
  try {
    const u = new URL(value);
    return ['http:', 'https:'].includes(u.protocol) && !u.username && !u.password ? u.href : null;
  } catch { return null; }
}

function markdownLink(text, start) {
  const labelEnd = text.indexOf('](', start + 1);
  if (labelEnd < 0 || /[\n\r\[\]]/.test(text.slice(start + 1, labelEnd))) return null;
  let depth = 1, end = labelEnd + 2;
  for (; end < text.length && !/[\n\r]/.test(text[end]); end++) {
    if (text[end] === '(') depth++;
    if (text[end] === ')' && --depth === 0) break;
  }
  const closed = depth === 0;
  return {label: text.slice(start + 1, labelEnd),
    url: closed ? safeUrl(text.slice(labelEnd + 2, end)) : null,
    end: closed ? end + 1 : end};
}

function bareUrl(text) {
  let value = text.match(/^https?:\/\/[^\s<>"']+/i)?.[0];
  if (!value) return null;
  value = value.replace(/[.,;!?，。；！？、）]+$/, '');
  // Keep balanced URL parentheses; only sentence-closing parentheses are removed.
  while (value.endsWith(')') && (value.match(/\)/g)?.length || 0) > (value.match(/\(/g)?.length || 0)) {
    value = value.slice(0, -1);
  }
  const url = safeUrl(value);
  return url ? {text: value, url} : null;
}

/** Only strong, labeled HTTP(S) links and bare URLs. No response HTML parser. */
export function answerParts(text, {bold = true, links = true, bare = true} = {}) {
  const parts = [];
  const literal = value => {
    if (parts.at(-1)?.type === 'text') parts.at(-1).text += value;
    else parts.push({type: 'text', text: value});
  };
  for (let i = 0; i < text.length;) {
    const image = text.startsWith('![', i);
    const link = links && (image || text[i] === '[') ? markdownLink(text, i + (image ? 1 : 0)) : null;
    if (link) {
      if (link.url && link.label && !image) {
        parts.push({type: 'link', url: link.url,
          children: answerParts(link.label, {links: false, bare: false})});
      } else literal(text.slice(i, link.end));
      i = link.end;continue;
    }
    if (bold && text.startsWith('**', i)) {
      const end = text.indexOf('**', i + 2);
      if (end > i + 2) {
        parts.push({type: 'strong', children: answerParts(text.slice(i + 2, end), {bold: false, links, bare})});
        i = end + 2;continue;
      }
    }
    const url = bare ? bareUrl(text.slice(i)) : null;
    if (url) {
      parts.push({type: 'link', url: url.url, children: [{type: 'text', text: url.text}]});
      i += url.text.length;continue;
    }
    literal(text[i]);i++;
  }
  return parts;
}

export function textUrls(text) {
  const urls = [];
  const collect = parts => {
    for (const part of parts) {
      if (part.type === 'link') urls.push(part.url);
      else if (part.children) collect(part.children);
    }
  };
  collect(answerParts(text));return urls;
}

export const FAQ_HEADER = '以下是 TAX AI 題庫中與您的問題較相關的內容：';
export const FAQ_FOOTER = '若以上內容不是您要找的資訊，可以換個方式描述問題，或改用快速搜尋。';
export const FAQ_FALLBACK = '目前 TAX AI 題庫找不到相關內容，請換個方式描述問題，或改用快速搜尋／洽業務承辦確認。';

function faqPresentation(segments, parameters) {
  const text = segments.filter(x => x.trim());
  // Only frozen Flow envelope and whole message boundaries; never split answer numbers.
  if (text[0]?.trim() !== FAQ_HEADER || text.at(-1)?.trim() !== FAQ_FOOTER
    || text.length < 3 || text.length > 7) return {};
  const blocks = text.slice(1, -1);
  const questions = parameters?.tax_questions, answers = parameters?.tax_answers;
  let items;
  if (Array.isArray(questions) && Array.isArray(answers) && questions.length === answers.length
    && questions.length >= blocks.length && blocks.every((block, i) =>
      typeof questions[i] === 'string' && questions[i].trim()
      && typeof answers[i] === 'string' && answers[i].trim()
      && block === `${i + 1}. ${questions[i]}\n${answers[i]}`)) {
    // Native collections may exceed five; use exactly the records visible in Flow text.
    items = blocks.map((_, i) => ({question: questions[i], answer: answers[i]}));
  } else {
    items = blocks.map((block, i) => {
      const boundary = block.indexOf('\n'), prefix = `${i + 1}. `;
      if (boundary < 0 || !block.startsWith(prefix)) return null;
      const question = block.slice(prefix.length, boundary).replace(/\r$/, '');
      const answer = block.slice(boundary + 1);
      return question.trim() && answer.trim() ? {question, answer} : null;
    });
    if (!items.every(Boolean)) return {};
  }
  return {items, leadingText: text[0], trailingText: text.at(-1)};
}

// All raw text messages/array items first; parsed text only when raw has no text.
export function normalizeResult(detail) {
  const raw = detail?.raw || (detail?.queryResult ? detail : {});
  const qr = raw?.queryResult;
  const steps = qr?.diagnosticInfo?.['DataStore Execution Sequence']?.steps;
  if (raw?.error?.message || (Array.isArray(qr?.webhookStatuses) && qr.webhookStatuses.some(x => x?.message))
    || (Array.isArray(steps) && steps.some(x => x?.status?.message))) throw new Error('service');
  const rawMessages = Array.isArray(raw?.queryResult?.responseMessages) ? raw.queryResult.responseMessages : [];
  const parsed = Array.isArray(detail?.data?.messages) ? detail.data.messages : [];
  const text = parsed.filter(m => m?.type === 'text' && typeof m.text === 'string').map(m => m.text);
  const rawText = rawMessages.flatMap(m => Array.isArray(m?.text?.text) ? m.text.text.filter(x => typeof x === 'string') : []);
  const segments = rawText.some(x => x.trim()) ? rawText : text;
  const answer = segments.join('\n\n');
  const sources = [];
  const add = source => {
    const url = safeUrl(source?.anchor?.href || source?.actionLink || source?.url);
    if (!url || sources.some(x => x.url === url)) return;
    sources.push({url, ...(typeof source?.title === 'string' && source.title.trim() ? {title: source.title} : {})});
  };
  for (const message of parsed) {
    if (message?.type === 'citation') add(message);
    for (const source of Array.isArray(message?.citations) ? message.citations : []) add(source);
  }
  const inline = new Set(textUrls(answer));
  const additional = sources.filter(source => !inline.has(source.url));
  return {answer, ...faqPresentation(segments, qr?.parameters), ...(additional.length ? {sources: additional} : {})};
}

export function appendAnswer(container, answer) {
  const inline = new Set();
  const append = (target, parts) => {
    for (const part of parts) {
      if (part.type === 'text') {target.append(document.createTextNode(part.text));continue;}
      const node = document.createElement(part.type === 'strong' ? 'strong' : 'a');
      if (part.type === 'link') {node.href = part.url;node.target = '_blank';node.rel = 'noopener noreferrer';inline.add(part.url);}
      append(node, part.children);target.append(node);
    }
  };
  append(container, answerParts(answer));return inline;
}

export function renderResult(model, query, root) {
  const question = root.querySelector('[data-ai-query]');
  question.textContent = query;
  const answer = root.querySelector('[data-ai-answer]');
  answer.replaceChildren();
  const hasItems = Array.isArray(model.items) && model.items.length > 0;
  answer.classList.toggle('has-faq-items', hasItems);
  const inline = new Set();
  if (hasItems) {
    const intro = document.createElement('div');intro.className = 'tax-ai-faq-intro';intro.textContent = model.leadingText || '';
    const list = document.createElement('ol');list.className = 'tax-ai-faq-results';
    for (const item of model.items) {
      const block = document.createElement('li');block.className = 'tax-ai-faq-result';
      const heading = document.createElement('h5');heading.textContent = item.question;
      const body = document.createElement('div');body.className = 'tax-ai-faq-answer';
      for (const url of appendAnswer(body, item.answer)) inline.add(url);
      block.append(heading, body);list.append(block);
    }
    const footer = document.createElement('div');footer.className = 'tax-ai-faq-footer';footer.textContent = model.trailingText || '';
    answer.append(intro, list, footer);
  } else for (const url of appendAnswer(answer, model.answer)) inline.add(url);
  const sources = root.querySelector('[data-ai-sources]');
  sources.replaceChildren();
  const additional = (model.sources || []).filter(source => safeUrl(source.url) && !inline.has(safeUrl(source.url)));
  root.querySelector('[data-ai-source-section]').hidden = !additional.length;
  for (const source of additional) {
    const item = document.createElement('li');
    const link = document.createElement('a');
    link.href = safeUrl(source.url);
    link.textContent = source.title || new URL(link.href).hostname;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    item.append(link);
    sources.append(item);
  }
}

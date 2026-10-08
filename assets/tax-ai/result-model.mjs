/** Text-first normalization. No Playbook/URL/title heuristic identifies a FAQ. */
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

// Parsed Messenger text first, raw ResponseMessage fallback. No 1999 FAQ/payload contract.
export function normalizeResult(detail) {
  const raw = detail?.raw || (detail?.queryResult ? detail : {});
  const rawMessages = Array.isArray(raw?.queryResult?.responseMessages) ? raw.queryResult.responseMessages : [];
  const parsed = Array.isArray(detail?.data?.messages) ? detail.data.messages : [];
  const text = parsed.filter(m => m?.type === 'text' && typeof m.text === 'string').map(m => m.text);
  const rawText = rawMessages.flatMap(m => Array.isArray(m?.text?.text) ? m.text.text.filter(x => typeof x === 'string') : []);
  const answer = (text.some(x => x.trim()) ? text : rawText).join('\n\n');
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
  return {answer, ...(additional.length ? {sources: additional} : {})};
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
  const inline = appendAnswer(answer, model.answer);
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

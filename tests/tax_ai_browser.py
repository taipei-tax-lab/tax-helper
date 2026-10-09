"""B3 stateless FAQ UI with explicit Mock and SDK fixture; all traffic stays offline."""
import argparse
import json
import mimetypes
from pathlib import Path
import shutil
from urllib.parse import unquote, urlsplit

from playwright.sync_api import expect, sync_playwright
from b1_reference import source_files, B1_COMMIT
from site_baseline import BASE, ORIGIN, SITE_PATH, XLSX_URL, XLSX_SHA256, upload_excel, result_ids
import hashlib

SDK_FIXTURE = r"""
window.sdkRequests = [];window.sdkDefaults = [];
class TaxSdkFixture extends HTMLElement {
  connectedCallback() {
    this.parameters = {};this.session = 0;window.taxSdk = this;
    queueMicrotask(() => window.dispatchEvent(new CustomEvent('df-messenger-loaded')));
  }
  setQueryParameters(value) {this.parameters = structuredClone(value);}
  startNewSession(options) {this.session++;this.lastRecovery = options;}
  enqueue(detail) {this.nextDetail = detail;}
  async sendQuery(query) {
    window.sdkDefaults.push(structuredClone(this.parameters));
    const body = {queryInput:{text:{text:query}},queryParams:structuredClone(this.parameters)};
    if (!this.dispatchEvent(new CustomEvent('df-request-sent', {detail:{data:{requestBody:body}},bubbles:true,cancelable:true}))) return;
    window.sdkRequests.push({query,queryParams:structuredClone(body.queryParams)});
    await Promise.resolve();
    const detail = this.nextDetail || {raw:{queryResult:{responseMessages:[{text:{text:['合成 SDK 回覆，非正式答覆。']}}]}}};
    this.nextDetail = null;
    this.dispatchEvent(new CustomEvent('df-response-received',{detail,bubbles:true,cancelable:true}));
  }
}
customElements.define('df-messenger',TaxSdkFixture);
"""


def canonical_fixture(page, count):
    # Public canonical Web bank projection using observed Flow text/parameter contract.
    # Not a fresh SDK/backend receipt or retrieval-quality proof.
    records = page.evaluate('window.questionBank').copy()[:count]
    items = [{'question': x['question'], 'answer': x['answer']} for x in records]
    texts = (['以下是 TAX AI 題庫中與您的問題較相關的內容：'] +
             [f'{i + 1}. {x["question"]}\n{x["answer"]}' for i, x in enumerate(items)] +
             ['若以上內容不是您要找的資訊，可以換個方式描述問題，或改用快速搜尋。']) if count else [
             '目前 TAX AI 題庫找不到相關內容，請換個方式描述問題，或改用快速搜尋／洽業務承辦確認。']
    return {'raw': {'queryResult': {'parameters': {'tax_questions': [x['question'] for x in items],
            'tax_answers': [x['answer'] for x in items], 'tax_answer_count': count},
            'responseMessages': [{'text': {'text': [text]}} for text in texts]}}}, items


def run(browser_path, xlsx_path=None, screenshot_dir=None):
    files = source_files()
    expected_search = json.loads((Path(__file__).parent / 'search_baseline.json').read_text())
    library = xlsx_path.read_bytes() if xlsx_path else None
    if library:
        assert hashlib.sha256(library).hexdigest() == XLSX_SHA256
    checks, blocked, errors, requested = [], set(), [], set()
    binding = {'currentPage': 'projects/serviceagent-1150909/locations/global/agents/786d0cf9-fd1b-4eb9-af1f-16e41891a603/flows/5bee3876-e595-413d-be3c-729227145e4d/pages/START_PAGE',
               'timeZone': 'Asia/Taipei', 'parameters': {'tax_answers': [], 'tax_questions': [], 'tax_answer_count': 0}}
    required = binding
    sdk_url = 'https://www.gstatic.com/dialogflow-console/fast/df-messenger/prod/v1/df-messenger.js'
    sdk_requests = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=browser_path, headless=True,
            args=['--no-sandbox', '--disable-crash-reporter', '--disable-background-networking'])

        def open_page(demo=True, options=None, available=True, with_xlsx=False, sdk_fixture=False, disabled_live=False):
            context = browser.new_context(viewport={'width': 1280, 'height': 960}, service_workers='block')
            context.add_init_script('window.__TAX_AI_MOCK_OPTIONS__ = ' + json.dumps({
                'delayMs': 0, 'requestTimeoutMs': 3000, **(options or {}),
            }) + ';')

            def route(request_route):
                url = request_route.request.url
                requested.add(url)
                parsed = urlsplit(url)
                if url == sdk_url:
                    sdk_requests.append(url)
                    if sdk_fixture:
                        request_route.fulfill(status=200, content_type='application/javascript', body=SDK_FIXTURE)
                    else: request_route.abort()
                elif with_xlsx and url == XLSX_URL:
                    request_route.fulfill(status=200, content_type='application/javascript', body=library)
                elif f'{parsed.scheme}://{parsed.netloc}' == ORIGIN:
                    path = unquote(parsed.path)
                    name = path[len(SITE_PATH):] if path.startswith(SITE_PATH) else ''
                    if path == SITE_PATH:
                        name = 'index.html'
                    if name in files:
                        content = files[name]
                        if disabled_live and name == 'assets/tax-ai/config.mjs':
                            content = content.replace(b'liveEnabled: true', b'liveEnabled: false')
                        request_route.fulfill(status=200, content_type=mimetypes.guess_type(name)[0] or 'application/octet-stream', body=content)
                    else:
                        request_route.fulfill(status=404, body='Source asset absent')
                else:
                    blocked.add(parsed.hostname)
                    request_route.abort()

            context.route('**/*', route)
            page = context.new_page()
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.goto(BASE + ('?tax-ai-demo=1' if demo else ''), wait_until='networkidle')
            expect(page.locator('#tax-ai-panel')).to_have_attribute('data-initialized', 'true')
            page.locator('[data-view="search"]').click()
            page.locator('[data-tax-mode="ai"]').click()
            if available:
                expect(page.locator('#tax-ai-submit')).to_be_enabled()
            else:
                expect(page.locator('#tax-ai-status')).to_have_attribute('data-state', 'unavailable')
            return context, page

        def enqueue(page, fixture):
            page.evaluate('fixture => window.taxAiMock.messenger.enqueue(fixture)', fixture)

        def ask(page, query, success=True):
            page.locator('#tax-ai-query').fill(query)
            page.locator('#tax-ai-submit').click()
            if success:
                expect(page.locator('#tax-ai-result')).to_be_visible()
                expect(page.locator('#tax-ai-submit')).to_be_enabled()

        def mock_state(page):
            return page.evaluate('({session:taxAiMock.messenger.session, requests:taxAiMock.messenger.requests, mountCount:taxAiMock.mountCount})')

        context, page = open_page(demo=False, available=False, disabled_live=True)
        assert page.evaluate('window.taxAiMock === undefined')
        expect(page.locator('#tax-ai-submit')).to_be_disabled()
        assert page.locator('#tax-ai-reset').count() == 0
        page.locator('[data-tax-mode="quick"]').click()
        page.locator('#searchView .search-input').fill('房屋稅')
        page.locator('#searchView .search-form button').click()
        assert result_ids(page) == expected_search['房屋稅']
        checks.append('rollback disabled-live: no Mock/SDK, quick search remains usable')
        context.close()

        context, page = open_page()
        expect(page.locator('#tax-ai-notice')).to_contain_text('離線示範')
        expect(page.locator('#searchView .search-page-head')).to_be_hidden()
        assert page.locator('#tax-ai-form.search-form').count() == 0
        assert page.locator('#tax-ai-query.search-input').count() == 0
        assert page.locator('df-messenger, df-messenger-chat').count() == 0
        enqueue(page, {'detail': {'data': {'messages': [
            {'type': 'text', 'text': '**重點**\n[說明](https://example.invalid/a)'},
            {'type': 'citation', 'url': 'https://example.invalid/a'},
            {'type': 'citation', 'url': 'https://example.invalid/b', 'title': '其他來源'},
        ]}}})
        ask(page, '第一題甲')
        assert page.locator('[data-ai-answer] strong').count() == 1
        assert page.locator('[data-ai-sources] li').count() == 1
        ask(page, '第二個完整問題')
        expect(page.locator('[data-ai-query]')).to_have_text('第二個完整問題')
        expect(page.locator('[data-ai-answer]')).to_contain_text('完整合成答案')
        assert page.locator('#tax-ai-result').count() == 1
        assert '第一題甲' not in page.locator('#tax-ai-panel').text_content()
        assert page.locator('[data-ai-answer] strong, [data-ai-answer] a, [data-ai-sources] li').count() == 0
        expect(page.locator('[data-ai-source-section]')).to_be_hidden()
        state = mock_state(page)
        assert state['requests'][0]['session'] == state['requests'][1]['session']
        assert all(request['queryParams'] == required for request in state['requests'])
        expect(page.locator('#tax-ai-query')).to_have_value('')
        assert page.locator('#tax-ai-reset').count() == 0
        assert '追問沿用同一對話' not in page.locator('#tax-ai-panel').text_content()
        checks.append('latest independent results share technical session; every-query FAQ defaults; accepted clear; no reset/context copy; old query/format/sources removed')

        for count in range(6):
            detail, items = canonical_fixture(page, count)
            enqueue(page, {'detail': detail})
            ask(page, f'完整獨立搜尋 {count}')
            assert page.locator('.tax-ai-faq-result').count() == count
            expect(page.locator('#tax-ai-query')).to_have_value('')
            expect(page.locator('#tax-ai-counter')).to_have_text('0 / 1000')
            expect(page.locator('[data-ai-query]')).to_have_text(f'完整獨立搜尋 {count}')
            assert page.locator('[data-ai-sources] li').count() == 0
            for i, item in enumerate(items):
                block = page.locator('.tax-ai-faq-result').nth(i)
                assert block.locator('h5').text_content() == item['question']
                assert block.locator('h5 a').count() == 0
                assert block.locator('.tax-ai-faq-answer').text_content() == item['answer']
            if not count:
                expect(page.locator('[data-ai-answer]')).to_contain_text('目前 TAX AI 題庫找不到相關內容')
            for width in (1280, 390, 320):
                page.set_viewport_size({'width': width, 'height': 960})
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                for i in range(count):
                    styles = page.locator('.tax-ai-faq-result').nth(i).evaluate('(e)=>({padding:getComputedStyle(e).paddingTop,border:getComputedStyle(e).borderTopWidth,shadow:getComputedStyle(e).boxShadow})')
                    assert styles['padding'] == '16px' and styles['shadow'] == 'none'
                    if i: assert styles['border'] == '1px'
                if count == 5 and screenshot_dir:
                    screenshot_dir.mkdir(parents=True, exist_ok=True)
                    page.screenshot(path=str(screenshot_dir / f'faq-five-{width}.png'), full_page=True)
        page.set_viewport_size({'width': 1280, 'height': 960})
        state = mock_state(page)
        checks.append('canonical public Q/A projection 0/1/2/3/4/5: exact full fields, native order, separate DOM, no title URL/citation, 1280/390/320 clear dividers; zero replaces old results')

        for _ in range(3):
            page.locator('[data-tax-mode="quick"]').click()
            expect(page.locator('#tax-ai-panel')).to_be_hidden()
            page.locator('[data-tax-mode="ai"]').click()
        assert mock_state(page) == state
        expect(page.locator('#tax-ai-query')).to_have_value('')
        for view in ('home', 'bank', 'favorites', 'search'):
            page.locator(f'[data-view="{view}"]').click()
        expect(page.locator('#tax-ai-result')).to_be_visible()
        assert mock_state(page) == state
        checks.append('mode and site navigation: retained input/model/session, one mount, no unsolicited sends')

        page.locator('[data-view="home"]').click()
        page.locator('#homeView .search-input').fill('房屋稅')
        page.locator('#homeView .search-form button').click()
        expect(page.locator('[data-tax-mode="quick"]')).to_have_attribute('aria-pressed', 'true')
        assert result_ids(page) == expected_search['房屋稅']
        page.locator('[data-tax-mode="ai"]').click()
        expect(page.locator('#tax-ai-result')).to_be_visible()
        page.locator('[data-view="home"]').click()
        page.locator('#categoryCards [data-cat="房屋稅"]').click()
        expect(page.locator('#tax-ai-panel')).to_be_hidden()
        assert page.locator('#searchResults .result-card').count() == 24
        assert mock_state(page) == state
        checks.append('home search and category shortcut force quick mode without remounting independent AI transport')

        page.locator('[data-tax-mode="ai"]').click()
        page.locator('[data-view="bank"]').click()
        page.locator('#bankList .bank-row').first.click()
        page.locator('[data-dfav]').click()
        favorites = page.evaluate('localStorage.getItem("taxAIFavorites")')
        page.keyboard.press('Escape')
        page.locator('[data-view="search"]').click()
        assert page.locator('#tax-ai-reset').count() == 0
        ask(page, '新獨立搜尋')
        assert mock_state(page)['requests'][-1]['queryParams'] == required
        assert page.evaluate('localStorage.getItem("taxAIFavorites")') == favorites
        assert mock_state(page)['session'] == state['session']
        assert page.evaluate('Object.keys(localStorage)') == ['taxAIFavorites']
        checks.append('no reset control: next search replaces old card without session change or favorites/AI storage regression')
        context.close()

        context, page = open_page()
        enqueue(page, {'beforeError': True})
        ask(page, '接受前失敗必須保留', success=False)
        expect(page.locator('#tax-ai-status')).to_have_attribute('data-state', 'error')
        expect(page.locator('#tax-ai-query')).to_have_value('接受前失敗必須保留')
        assert mock_state(page)['requests'] == []
        enqueue(page, {'holdBeforeAccepted': True, 'hold': True})
        original = '  完整原問題\n第二行  '
        ask(page, original, success=False)
        expect(page.locator('#tax-ai-query')).to_have_value(original)
        assert mock_state(page)['requests'] == []
        page.evaluate('taxAiMock.messenger.release()')
        expect(page.locator('#tax-ai-query')).to_have_value('')
        expect(page.locator('#tax-ai-counter')).to_have_text('0 / 1000')
        page.locator('#tax-ai-query').fill('下一題草稿')
        page.evaluate('taxAiMock.messenger.release()')
        expect(page.locator('[data-ai-query]')).to_have_text(original)
        assert page.locator('[data-ai-query]').text_content() == original
        expect(page.locator('#tax-ai-query')).to_have_value('下一題草稿')
        checks.append('accepted boundary: pre-acceptance rejection/hold retains exact raw input; accepted clear precedes answer; next draft and original heading survive late response')
        context.close()

        context, page = open_page(demo=False, available=False)
        assert page.evaluate('window.taxAiMock === undefined')
        assert page.evaluate('!performance.getEntriesByType("resource").some(x=>x.name.includes("mock-messenger.mjs"))')
        expect(page.locator('#tax-ai-submit')).to_be_disabled()
        page.locator('[data-tax-mode="quick"]').click()
        page.locator('#searchView .search-input').fill('房屋稅')
        page.locator('#searchView .search-form button').click()
        assert result_ids(page) == expected_search['房屋稅']
        checks.append('production SDK load failure stays unavailable, never auto-loads Mock, Quick Search remains functional')
        context.close()

        context, page = open_page(demo=False, sdk_fixture=True)
        assert page.evaluate('window.taxAiMock === undefined')
        assert page.evaluate('!performance.getEntriesByType("resource").some(x=>x.name.includes("mock-messenger.mjs"))')
        sdk = page.locator('df-messenger')
        assert sdk.count() == 1
        assert sdk.get_attribute('project-id') == 'serviceagent-1150909'
        assert sdk.get_attribute('agent-id') == '786d0cf9-fd1b-4eb9-af1f-16e41891a603'
        assert sdk.get_attribute('language-code') == 'zh-tw'
        assert sdk.get_attribute('environment-id') is None
        assert sdk.get_attribute('location') is None  # documented global default
        assert sdk.get_attribute('storage-option') == 'none'
        assert sdk.evaluate('(e)=>e.hidden && e.inert')
        assert sdk.locator('df-messenger-chat').count() == 1
        for ordinal, count in enumerate((5, 2, 0), 1):
            detail, items = canonical_fixture(page, count)
            page.evaluate('detail=>taxSdk.enqueue(detail)', detail)
            ask(page, f'  第{ordinal}個完整原問題\n原換行  ')
            assert page.locator('.tax-ai-faq-result').count() == count
            assert page.evaluate('sdkRequests.at(-1).queryParams') == required
            assert page.evaluate('sdkDefaults.at(-1)') == required
            assert page.evaluate('sdkRequests.at(-1).query') == f'  第{ordinal}個完整原問題\n原換行  '
            expect(page.locator('#tax-ai-query')).to_have_value('')
            for i, item in enumerate(items):
                assert page.locator('.tax-ai-faq-answer').nth(i).text_content() == item['answer']
        assert page.evaluate('sdkRequests.length') == 3
        assert page.locator('#tax-ai-reset').count() == 0
        assert '重置提問' not in page.locator('#tax-ai-panel').text_content()
        page.locator('[data-tax-mode="quick"]').click();page.locator('[data-tax-mode="ai"]').click()
        assert page.locator('df-messenger').count() == 1
        assert page.evaluate('sdkRequests.length') == 3
        checks.append('formal loader through offline SDK fixture: new global Agent, hidden API, no environment attribute/Mock; first/second/third currentPage + zero tax_* defaults and bodies, exact raw query, 5→2→0 replacement, one mount')
        context.close()

        context, page = open_page()
        detail, _ = canonical_fixture(page, 1)
        qr = detail['raw']['queryResult']
        q = '<img src=x onerror="window.__faqUnsafe=1"> 官方原問題'
        a = '<script>window.__faqUnsafe=2</script>\r\n1. 答案內原編號\n2. 下一行\nhttps://tpctax.gov.taipei/\n[x](javascript:alert(1))'
        qr['parameters']['tax_questions'] = [q];qr['parameters']['tax_answers'] = [a]
        qr['responseMessages'][1]['text']['text'] = [f'1. {q}\n{a}']
        enqueue(page, {'detail': detail});ask(page, '安全原文測試')
        assert page.locator('.tax-ai-faq-result h5').text_content() == q
        assert page.locator('.tax-ai-faq-result h5 a').count() == 0
        assert page.locator('.tax-ai-faq-answer').text_content() == a
        assert page.locator('.tax-ai-faq-answer a').count() == 1
        assert page.locator('.tax-ai-faq-answer a').get_attribute('href') == 'https://tpctax.gov.taipei/'
        assert page.evaluate('window.__faqUnsafe === undefined')
        assert page.locator('#tax-ai-result img, #tax-ai-result script').count() == 0
        assert page.locator('[data-ai-sources] li').count() == 0
        text_only = json.loads(json.dumps(detail));del text_only['raw']['queryResult']['parameters']
        enqueue(page, {'detail': text_only});ask(page, '只有逐筆文字')
        assert page.locator('.tax-ai-faq-result').count() == 1
        assert page.locator('.tax-ai-faq-answer').text_content() == a
        combined = '\n\n'.join(x for m in qr['responseMessages'] for x in m['text']['text'])
        enqueue(page, {'detail': {'raw': {'queryResult': {'responseMessages': [{'text': {'text': [combined]}}]}}}})
        ask(page, '未知合併文字保留')
        assert page.locator('.tax-ai-faq-result').count() == 0
        assert page.locator('[data-ai-answer]').text_content() == combined
        assert not page.locator('[data-ai-answer]').evaluate('(e)=>e.classList.contains("has-faq-items")')
        err, _ = canonical_fixture(page, 0);err['raw']['queryResult']['webhookStatuses'] = [{'message': 'synthetic service failure'}]
        enqueue(page, {'detail': err});ask(page, '檢索服務失敗', success=False)
        expect(page.locator('#tax-ai-status')).to_have_attribute('data-state', 'error')
        expect(page.locator('#tax-ai-result')).to_be_hidden()
        checks.append('FAQ safe URL/CRLF/internal numbers/HTML-like preserved inert; per-message text-only and combined fallback; service status never rendered as zero result')
        context.close()

        context, page = open_page()
        page.evaluate('taxAiMock.messenger.startNewSession=()=>{throw new Error("synthetic recovery failure")};taxAiMock.messenger.expire()')
        expect(page.locator('#tax-ai-status')).to_have_attribute('data-state', 'unavailable')
        expect(page.locator('#tax-ai-submit')).to_be_disabled()
        page.locator('[data-tax-mode="quick"]').click()
        page.locator('#searchView .search-input').fill('房屋稅');page.locator('#searchView .search-form button').click()
        assert result_ids(page) == expected_search['房屋稅']
        assert mock_state(page)['requests'] == []
        checks.append('internal SDK recovery failure gracefully disables AI without JS errors/Mock fallback/retry; Quick Search stays functional')
        context.close()

        context, page = open_page()
        enqueue(page, {'hold': True, 'detail': {'data': {'messages': [{'type': 'text', 'text': '延遲的新回答'}]}}})
        ask(page, '慢查詢', success=False)
        expect(page.locator('#tax-ai-form')).to_have_attribute('aria-busy', 'true')
        assert page.locator('#tax-ai-reset').count() == 0
        page.locator('#tax-ai-form').dispatch_event('submit')
        page.locator('#tax-ai-query').press('Enter')
        assert len(mock_state(page)['requests']) == 1
        page.locator('[data-tax-mode="quick"]').click()
        page.locator('#searchView .search-input').fill('房屋稅')
        page.locator('#searchView .search-form button').click()
        expected_ids = result_ids(page)
        page.locator('#searchView .search-input').focus()
        page.evaluate('taxAiMock.messenger.release()')
        expect(page.locator('[data-ai-answer]')).to_have_text('延遲的新回答')
        expect(page.locator('#searchView .search-input')).to_be_focused()
        assert result_ids(page) == expected_ids
        page.locator('[data-tax-mode="ai"]').click()
        expect(page.locator('#tax-ai-result')).to_be_visible()
        assert mock_state(page)['mountCount'] == 1
        checks.append('in-flight switching: single request, late success stays in AI, quick results/focus remain intact')
        context.close()

        for kind, expected in [('empty', 'empty'), ('malformed', 'empty'), ('silent', 'empty'), ('error', 'error')]:
            context, page = open_page()
            enqueue(page, {'kind': kind})
            ask(page, '第一題失敗', success=False)
            expect(page.locator('#tax-ai-status')).to_have_attribute('data-state', expected)
            assert page.locator('#tax-ai-reset').count() == 0
            assert page.evaluate('taxAiMock.latestModel') is None
            assert len(mock_state(page)['requests']) == 1
            ask(page, '下一個獨立完整問題')
            assert mock_state(page)['requests'][-1]['queryParams'] == required
            checks.append(f'{kind}: clear empty/error state, no reset/retry, independent manual next search recovers')
            context.close()

        context, page = open_page(options={'loaderError': True}, available=False)
        assert page.evaluate('window.taxAiMock === undefined')
        page.locator('[data-tax-mode="quick"]').click()
        page.locator('#searchView .search-input').fill('車子報廢')
        page.locator('#searchView .search-form button').click()
        assert result_ids(page) == expected_search['車子報廢']
        checks.append('Mock loader unavailable: clear service state and working quick search; no SDK fallback')
        context.close()

        context, page = open_page()
        ask(page, '逾期前的問題')
        session = mock_state(page)['session']
        page.locator('[data-tax-mode="quick"]').click()
        page.evaluate('taxAiMock.messenger.expire()')
        assert page.evaluate('taxAiMock.latestModel') is None
        assert mock_state(page)['session'] == session + 1
        page.locator('[data-tax-mode="ai"]').click()
        expect(page.locator('#tax-ai-status')).to_have_attribute('data-state', 'session')
        expect(page.locator('#tax-ai-query')).to_have_value('')
        expect(page.locator('#tax-ai-result')).to_be_hidden()
        ask(page, '新對話的問題')
        assert mock_state(page)['requests'][-1]['queryParams'] == required
        checks.append('idle expiry while hidden: clear result, retain next draft, notify and recover technical session with FAQ defaults')
        context.close()

        for ended in (False, True):
            context, page = open_page()
            enqueue(page, {'hold': True})
            session = mock_state(page)['session']
            ask(page, '逾期中的問題', success=False)
            page.evaluate('ended => taxAiMock.messenger.expire(ended)', ended)
            expect(page.locator('#tax-ai-status')).to_have_attribute('data-state', 'session')
            assert page.locator('#tax-ai-reset').count() == 0
            assert mock_state(page)['session'] == session
            page.evaluate('taxAiMock.messenger.release()')
            expect(page.locator('#tax-ai-submit')).to_be_enabled()
            expect(page.locator('#tax-ai-result')).to_be_hidden()
            assert page.locator('[data-ai-answer]').text_content() == ''
            assert mock_state(page)['session'] == session + 1
            ask(page, '逾期後的第一題')
            assert mock_state(page)['requests'][-1]['queryParams'] == required
            checks.append(f'in-flight {"end" if ended else "expiry"}: reject, ignore old answer, new session only after settle')
            context.close()

        context, page = open_page(options={'sessionTtlSeconds': 0.15})
        ask(page, '短 TTL 提問')
        expect(page.locator('#tax-ai-status')).to_have_attribute('data-state', 'session')
        expect(page.locator('#tax-ai-result')).to_be_hidden()
        assert mock_state(page)['session'] > 1
        checks.append('automatic Mock TTL expiration clears the card and notifies UI')
        context.close()

        context, page = open_page(options={'requestTimeoutMs': 60})
        enqueue(page, {'hold': True, 'detail': {'data': {'messages': [{'type': 'text', 'text': '不得回填的舊回答'}]}}})
        ask(page, '逾時問題', success=False)
        expect(page.locator('#tax-ai-status')).to_have_attribute('data-state', 'timeout')
        expect(page.locator('#tax-ai-status')).to_contain_text('重新載入')
        expect(page.locator('#tax-ai-submit')).to_be_disabled()
        assert page.locator('#tax-ai-reset').count() == 0
        page.locator('#tax-ai-form').dispatch_event('submit')
        assert len(mock_state(page)['requests']) == 1
        assert page.evaluate('taxAiMock.latestModel') is None
        page.evaluate('taxAiMock.messenger.release()')
        expect(page.locator('#tax-ai-submit')).to_be_enabled()
        expect(page.locator('#tax-ai-form')).to_have_attribute('aria-busy', 'false')
        expect(page.locator('#tax-ai-result')).to_be_hidden()
        assert page.locator('[data-ai-answer]').text_content() == ''
        ask(page, '手動再提問')
        assert '不得回填' not in page.locator('#tax-ai-panel').text_content()
        assert len(mock_state(page)['requests']) == 2
        checks.append('timeout/never-settled warning: lock until settle, no retry, discard late answer, manual next query')
        context.close()

        context, page = open_page()
        input_box = page.locator('#tax-ai-query')
        ask(page, '   ', success=False)
        expect(page.locator('#tax-ai-status')).to_have_attribute('data-state', 'input')
        ask(page, '字' * 1001, success=False)
        assert len(mock_state(page)['requests']) == 0
        input_box.fill('中文組字')
        input_box.dispatch_event('compositionstart')
        input_box.press('Enter')
        page.locator('#tax-ai-form').dispatch_event('submit')
        assert len(mock_state(page)['requests']) == 0
        input_box.dispatch_event('compositionend')
        input_box.dispatch_event('keydown', {'key': 'Enter', 'isComposing': True})
        input_box.evaluate("e => e.dispatchEvent(new KeyboardEvent('keydown', {key:'Enter', keyCode:229, bubbles:true}))")
        assert len(mock_state(page)['requests']) == 0
        input_box.fill('兩行')
        input_box.press('Shift+Enter')
        assert '\n' in input_box.input_value()
        assert len(mock_state(page)['requests']) == 0
        input_box.press('Enter')
        expect(page.locator('#tax-ai-result')).to_be_visible()
        expect(page.locator('#tax-ai-result-title')).to_be_focused()
        assert len(mock_state(page)['requests']) == 1
        checks.append('input/IME: blank and overlength rejected, composition/isComposing/229 guarded, Shift+Enter newline, Enter sends')
        context.close()

        context, page = open_page()
        malicious_query = '<img src=x onerror="window.__unsafe=1">'
        answer = '<img src=x onerror="window.__unsafe=1">\n<script>window.__unsafe=2</script>\n**安全粗體**\n[安全說明](https://example.invalid/a)\n[x](javascript:alert(1))\n![圖](https://example.invalid/image)'
        enqueue(page, {'detail': {'data': {'messages': [{'type': 'text', 'text': answer},
            {'citations': [{'url': 'javascript:alert(1)'}, {'url': 'data:text/html,x'}, {'url': 'https://user:pass@example.invalid/'},
                {'url': 'https://example.invalid/a'}, {'url': 'https://example.invalid/b', 'title': '<script>來源</script>'}, {'url': 'https://example.invalid/b'}]}]}}})
        ask(page, malicious_query)
        expect(page.locator('[data-ai-query]')).to_have_text(malicious_query)
        assert page.locator('#tax-ai-panel script, #tax-ai-panel img, #tax-ai-panel iframe, #tax-ai-panel object').count() == 0
        assert page.evaluate('window.__unsafe === undefined')
        assert page.locator('[data-ai-answer] strong').count() == 1
        assert page.locator('[data-ai-answer] a').count() == 1
        assert page.locator('[data-ai-sources] li').count() == 1
        links = page.locator('#tax-ai-result a').evaluate_all('els => els.map(e => ({href:e.href, rel:e.rel, target:e.target}))')
        assert {link['href'] for link in links} == {'https://example.invalid/a', 'https://example.invalid/b'}
        assert all(link['rel'] == 'noopener noreferrer' and link['target'] == '_blank' for link in links)
        checks.append('safe rendering: HTML stays text, unsafe URLs/images inert, minimal Markdown, explicit citations deduplicated')

        for width in (320, 390):
            page.set_viewport_size({'width': width, 'height': 900})
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            for selector in ('#tax-ai-query', '#tax-ai-submit'):
                box = page.locator(selector).bounding_box()
                assert box and box['x'] >= 0 and box['x'] + box['width'] <= width
            input_box = page.locator('#tax-ai-query')
            assert page.locator('#tax-ai-reset').count() == 0
            page.locator('[data-tax-mode="quick"]').focus()
            page.locator('[data-tax-mode="quick"]').press('Enter')
            expect(page.locator('#tax-ai-panel')).to_be_hidden()
            page.locator('[data-tax-mode="ai"]').focus()
            page.locator('[data-tax-mode="ai"]').press('Enter')
            expect(input_box).to_be_focused()
            ask(page, '行動版問題')
            expect(page.locator('#tax-ai-result-title')).to_be_focused()
            if screenshot_dir:
                screenshot_dir.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(screenshot_dir / f'ai-{width}.png'), full_page=True)
        checks.append('320/390px: no horizontal overflow, usable controls, keyboard mode switch, result focus/no reset')
        context.close()

        context, page = open_page()
        enqueue(page, {'detail': {'raw': {'queryResult': {'responseMessages': [{'text': {'text': ['原始第一段', '完整第二段']}}]}}}})
        ask(page, 'raw 回覆')
        assert page.locator('[data-ai-answer]').text_content() == '原始第一段\n\n完整第二段'
        enqueue(page, {'kind': 'error'})
        ask(page, '接續失敗', success=False)
        expect(page.locator('#tax-ai-status')).to_have_attribute('data-state', 'error')
        assert page.locator('[data-ai-answer]').text_content() == ''
        assert page.evaluate('taxAiMock.latestModel') is None
        ask(page, '手動恢復')
        assert {request['session'] for request in mock_state(page)['requests']} == {1}
        checks.append('raw fallback and later service error: old card removed, manual recovery keeps same session')
        context.close()

        if library:
            context, page = open_page(with_xlsx=True)
            ask(page, '匯入前 AI 問題')
            state = mock_state(page)
            model = page.evaluate('taxAiMock.latestModel')
            upload_excel(page, [['編號', '分類', '問題', '完整答案'], [1001, '合成分類', '合成題庫問題', '合成答案']])
            expect(page.locator('#toast')).to_have_text('已成功匯入 1 題')
            page.locator('[data-view="search"]').click()
            expect(page.locator('#tax-ai-result')).to_be_visible()
            assert mock_state(page) == state
            assert page.evaluate('taxAiMock.latestModel') == model
            expect(page.locator('#tax-ai-bank-note')).to_contain_text('不會更新 AI 問答來源')
            page.locator('[data-tax-mode="quick"]').click()
            page.locator('#searchView .search-input').fill('合成題庫問題')
            page.locator('#searchView .search-form button').click()
            assert result_ids(page) == ['1001']
            checks.append('Excel runtime data stays local to quick search; AI session/model unchanged and source difference explained')
            context.close()

        assert not errors, errors
        assert blocked <= {'cdn.jsdelivr.net', '113604.github.io', 'tax-status-api.ddy88000000.workers.dev'}, blocked
        assert not any('dialogflow.cloud.google.com/' in url for url in requested)
        version = browser.version
        browser.close()

    return {'status': 'PASS', 'check_count': len(checks), 'checks': checks, 'b1_commit': B1_COMMIT,
            'chromium_version': version, 'page_errors': errors, 'blocked_external_origins': sorted(blocked),
            'external_page_requests_sent': 0, 'production_requests': 0,
            'messenger_sdk_requests_forwarded': 0, 'offline_sdk_bootstrap_requests': len(sdk_requests),
            'limitations': [] if library else ['Excel/AI source isolation requires --xlsx-script']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--browser', default=shutil.which('chromium'))
    parser.add_argument('--xlsx-script', type=Path)
    parser.add_argument('--report', type=Path)
    parser.add_argument('--screenshots', type=Path)
    args = parser.parse_args()
    result = run(args.browser, args.xlsx_script, args.screenshots)
    text = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.report:
        args.report.write_text(text, encoding='utf-8')
    print(text, end='')


if __name__ == '__main__':
    main()

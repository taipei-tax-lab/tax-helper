"""B2 UI and Mock integration only; every browser request is fulfilled locally or aborted."""
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


def run(browser_path, xlsx_path=None, screenshot_dir=None):
    files = source_files()
    expected_search = json.loads((Path(__file__).parent / 'search_baseline.json').read_text())
    library = xlsx_path.read_bytes() if xlsx_path else None
    if library:
        assert hashlib.sha256(library).hexdigest() == XLSX_SHA256
    checks, blocked, errors, requested = [], set(), [], set()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=browser_path, headless=True,
            args=['--no-sandbox', '--disable-crash-reporter', '--disable-background-networking'])

        def open_page(demo=True, options=None, available=True, with_xlsx=False):
            context = browser.new_context(viewport={'width': 1280, 'height': 960}, service_workers='block')
            context.add_init_script('window.__TAX_AI_MOCK_OPTIONS__ = ' + json.dumps({
                'delayMs': 0, 'requestTimeoutMs': 3000, **(options or {}),
            }) + ';')

            def route(request_route):
                url = request_route.request.url
                requested.add(url)
                parsed = urlsplit(url)
                if with_xlsx and url == XLSX_URL:
                    request_route.fulfill(status=200, content_type='application/javascript', body=library)
                elif f'{parsed.scheme}://{parsed.netloc}' == ORIGIN:
                    path = unquote(parsed.path)
                    name = path[len(SITE_PATH):] if path.startswith(SITE_PATH) else ''
                    if path == SITE_PATH:
                        name = 'index.html'
                    if name in files:
                        request_route.fulfill(status=200, content_type=mimetypes.guess_type(name)[0] or 'application/octet-stream', body=files[name])
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

        context, page = open_page(demo=False, available=False)
        assert page.evaluate('window.taxAiMock === undefined')
        expect(page.locator('#tax-ai-submit')).to_be_disabled()
        expect(page.locator('#tax-ai-reset')).to_be_disabled()
        page.locator('[data-tax-mode="quick"]').click()
        page.locator('#searchView .search-input').fill('房屋稅')
        page.locator('#searchView .search-form button').click()
        assert result_ids(page) == expected_search['房屋稅']
        checks.append('default unavailable: no Mock/SDK, quick search remains usable')
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
        ask(page, '那期限呢？')
        expect(page.locator('[data-ai-query]')).to_have_text('那期限呢？')
        expect(page.locator('[data-ai-answer]')).to_contain_text('第 2 次')
        assert page.locator('#tax-ai-result').count() == 1
        assert '第一題甲' not in page.locator('#tax-ai-panel').text_content()
        assert page.locator('[data-ai-answer] strong, [data-ai-answer] a, [data-ai-sources] li').count() == 0
        expect(page.locator('[data-ai-source-section]')).to_be_hidden()
        state = mock_state(page)
        assert state['requests'][0]['session'] == state['requests'][1]['session']
        assert state['requests'][0]['queryParams']['currentPlaybook'] == 'mock-only-tax-faq'
        assert 'currentPlaybook' not in state['requests'][1]['queryParams']
        assert all(request['queryParams']['timeZone'] == 'Asia/Taipei' for request in state['requests'])
        checks.append('latest card: two turns share a session; first-only override; old query/format/sources removed')

        for _ in range(3):
            page.locator('[data-tax-mode="quick"]').click()
            expect(page.locator('#tax-ai-panel')).to_be_hidden()
            page.locator('[data-tax-mode="ai"]').click()
        assert mock_state(page) == state
        expect(page.locator('#tax-ai-query')).to_have_value('那期限呢？')
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
        checks.append('home search and category shortcut force quick mode without resetting AI context')

        page.locator('[data-tax-mode="ai"]').click()
        page.locator('[data-view="bank"]').click()
        page.locator('#bankList .bank-row').first.click()
        page.locator('[data-dfav]').click()
        favorites = page.evaluate('localStorage.getItem("taxAIFavorites")')
        page.keyboard.press('Escape')
        page.locator('[data-view="search"]').click()
        page.locator('#tax-ai-reset').click()
        assert page.evaluate('taxAiMock.latestModel') is None
        expect(page.locator('#tax-ai-query')).to_have_value('')
        assert page.locator('[data-ai-query]').text_content() == ''
        assert page.locator('[data-ai-answer]').text_content() == ''
        assert page.locator('[data-ai-sources]').text_content() == ''
        expect(page.locator('#tax-ai-result')).to_be_hidden()
        expect(page.locator('#tax-ai-query')).to_be_focused()
        assert page.evaluate('localStorage.getItem("taxAIFavorites")') == favorites
        assert mock_state(page)['session'] == state['session'] + 1
        ask(page, '新的第一題')
        assert mock_state(page)['requests'][-1]['queryParams']['currentPlaybook'] == 'mock-only-tax-faq'
        assert page.evaluate('Object.keys(localStorage)') == ['taxAIFavorites']
        checks.append('manual reset: clears model/DOM/input, focuses input, new armed session, favorites retained, no AI storage')
        context.close()

        context, page = open_page()
        enqueue(page, {'hold': True, 'detail': {'data': {'messages': [{'type': 'text', 'text': '延遲的新回答'}]}}})
        ask(page, '慢查詢', success=False)
        expect(page.locator('#tax-ai-form')).to_have_attribute('aria-busy', 'true')
        expect(page.locator('#tax-ai-reset')).to_be_disabled()
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
            expect(page.locator('#tax-ai-reset')).to_be_enabled()
            assert page.evaluate('taxAiMock.latestModel') is None
            assert len(mock_state(page)['requests']) == 1
            page.locator('#tax-ai-reset').click()
            ask(page, '重置後提問')
            assert mock_state(page)['requests'][-1]['queryParams']['currentPlaybook'] == 'mock-only-tax-faq'
            checks.append(f'{kind}: clear empty/error state, reset available after first failure, no retry, recovery')
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
        expect(page.locator('#tax-ai-query')).to_have_value('逾期前的問題')
        expect(page.locator('#tax-ai-result')).to_be_hidden()
        ask(page, '新對話的問題')
        assert mock_state(page)['requests'][-1]['queryParams']['currentPlaybook'] == 'mock-only-tax-faq'
        checks.append('idle expiry while hidden: clear result, retain input, notify and re-arm new session')
        context.close()

        for ended in (False, True):
            context, page = open_page()
            enqueue(page, {'hold': True})
            session = mock_state(page)['session']
            ask(page, '逾期中的問題', success=False)
            page.evaluate('ended => taxAiMock.messenger.expire(ended)', ended)
            expect(page.locator('#tax-ai-status')).to_have_attribute('data-state', 'session')
            expect(page.locator('#tax-ai-reset')).to_be_disabled()
            assert mock_state(page)['session'] == session
            page.evaluate('taxAiMock.messenger.release()')
            expect(page.locator('#tax-ai-submit')).to_be_enabled()
            expect(page.locator('#tax-ai-result')).to_be_hidden()
            assert page.locator('[data-ai-answer]').text_content() == ''
            assert mock_state(page)['session'] == session + 1
            ask(page, '逾期後的第一題')
            assert mock_state(page)['requests'][-1]['queryParams']['currentPlaybook'] == 'mock-only-tax-faq'
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
        expect(page.locator('#tax-ai-reset')).to_be_disabled()
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
            for selector in ('#tax-ai-query', '#tax-ai-submit', '#tax-ai-reset'):
                box = page.locator(selector).bounding_box()
                assert box and box['x'] >= 0 and box['x'] + box['width'] <= width
            page.locator('#tax-ai-reset').click()
            expect(input_box := page.locator('#tax-ai-query')).to_be_focused()
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
        checks.append('320/390px: no horizontal overflow, usable controls, keyboard mode switch, result/reset focus')
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
        assert not any('gstatic' in url or 'dialogflow' in url for url in requested)
        version = browser.version
        browser.close()

    return {'status': 'PASS', 'check_count': len(checks), 'checks': checks, 'b1_commit': B1_COMMIT,
            'chromium_version': version, 'page_errors': errors, 'blocked_external_origins': sorted(blocked),
            'external_page_requests_sent': 0, 'messenger_sdk_requests': 0,
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

"""Exercise the pristine site through local routes; never contact its external services."""

import argparse
import hashlib
import io
import json
import mimetypes
from pathlib import Path
import shutil
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree as ET
import zipfile

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "http://127.0.0.1:8876"
SITE_PATH = "/tax-helper/"
BASE = ORIGIN + SITE_PATH
XLSX_URL = "https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"
XLSX_SHA256 = "c9506197caf809a075b6dee1da0d36fb19da7158ffe8a88e7b0c96c5d8623c99"


def workbook(rows):
    """Build a synthetic, real OOXML workbook in memory; no user Excel is used."""
    namespace = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    worksheet = ET.Element("worksheet", xmlns=namespace)
    sheet_data = ET.SubElement(worksheet, "sheetData")
    for number, values in enumerate(rows, 1):
        sheet_row = ET.SubElement(sheet_data, "row", r=str(number))
        for column, value in enumerate(values):
            cell = ET.SubElement(sheet_row, "c", r=f"{chr(65 + column)}{number}", t="inlineStr")
            text = ET.SubElement(ET.SubElement(cell, "is"), "t")
            text.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
            text.text = str(value)
    entries = {
        "[Content_Types].xml": '''<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>''',
        "_rels/.rels": '''<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>''',
        "xl/workbook.xml": '''<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="題庫" sheetId="1" r:id="rId1"/></sheets></workbook>''',
        "xl/_rels/workbook.xml.rels": '''<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>''',
        "xl/worksheets/sheet1.xml": ET.tostring(worksheet, encoding="utf-8", xml_declaration=True),
    }
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, content in entries.items():
            archive.writestr(name, content)
    return output.getvalue()


def upload_excel(page, rows):
    page.locator("#excelFileInput").set_input_files({
        "name": "synthetic.xlsx",
        "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "buffer": workbook(rows),
    })


def result_ids(page):
    return page.locator("#searchResults .result-card").evaluate_all("els => els.map(e => e.dataset.id)")


def run(browser_path, xlsx_path=None):
    manifest = json.loads((ROOT / "tests" / "source_baseline.json").read_text())
    for name, expected in manifest["file_sha256"].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name
    expected_search = json.loads((ROOT / "tests" / "search_baseline.json").read_text())
    library = xlsx_path.read_bytes() if xlsx_path else None
    if library is not None:
        assert hashlib.sha256(library).hexdigest() == XLSX_SHA256, "Cached XLSX differs from baseline"

    checks, blocked, errors, missing = [], set(), [], set()
    cached_requests = 0
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path=browser_path, headless=True,
            args=["--no-sandbox", "--disable-crash-reporter", "--disable-background-networking"],
        )

        def new_context(with_xlsx=False):
            context = browser.new_context(viewport={"width": 1280, "height": 960}, service_workers="block")
            context.grant_permissions(["clipboard-read", "clipboard-write"], origin=ORIGIN)

            def route(request_route):
                nonlocal cached_requests
                url = request_route.request.url
                parsed = urlsplit(url)
                if with_xlsx and url == XLSX_URL:
                    cached_requests += 1
                    request_route.fulfill(status=200, content_type="application/javascript", body=library)
                elif f"{parsed.scheme}://{parsed.netloc}" == ORIGIN:
                    path = unquote(parsed.path)
                    name = path[len(SITE_PATH):] if path.startswith(SITE_PATH) else ""
                    if path == SITE_PATH:
                        name = "index.html"
                    if name in manifest["file_sha256"]:
                        file = ROOT / name
                        request_route.fulfill(status=200, body=file.read_bytes(),
                                              content_type=mimetypes.guess_type(name)[0] or "application/octet-stream")
                    else:
                        missing.add(path)
                        request_route.fulfill(status=404, body="Original ZIP did not include this asset")
                else:
                    blocked.add(parsed.hostname)
                    request_route.abort()

            context.route("**/*", route)
            page = context.new_page()
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(BASE, wait_until="networkidle")
            return context, page

        context, page = new_context()
        expect(page.locator("#bankCount")).to_have_text("129")
        assert page.locator("#bankList .bank-row").count() == 129
        assert page.locator("#categoryCards .category-card").count() == 11
        checks.append("init: 129 questions, 11 categories, 129 browse rows")

        page.locator('[data-view="bank"]').click()
        page.locator("#categorySelect").select_option("房屋稅")
        assert page.locator("#bankList .bank-row").count() == 24
        page.locator("#categorySelect").select_option("全部")
        page.locator("#bankFilter").fill("房屋稅")
        assert page.locator("#bankList .bank-row").evaluate_all("els=>els.map(e=>e.dataset.id)") == expected_search["房屋稅"]
        page.locator("#bankFilter").fill("")
        assert page.locator("#bankList .bank-row").count() == 129
        checks.append("browse: category filter, query ordering and restore")

        page.locator("#bankList .bank-row").first.click()
        expect(page.locator("#detailDrawer")).to_have_attribute("aria-hidden", "false")
        assert page.locator("#drawerContent .detail-card").count() == 3
        answer = page.evaluate(r"bank[0].answer.replace(/\r\n?/g, '\n')")
        assert page.locator("#drawerContent .detail-card").nth(1).locator("p").text_content() == answer
        page.keyboard.press("Escape")
        expect(page.locator("#detailDrawer")).to_have_attribute("aria-hidden", "true")
        checks.append("detail: complete answer and Escape")

        page.locator("#bankList .bank-row").first.click()
        related = page.locator("[data-related]").first
        related_title = related.text_content()
        related.click()
        expect(page.locator("#drawerContent h2")).to_have_text(related_title)
        checks.append("related question opens its own detail")

        page.locator("[data-dfav]").click()
        favorites = page.evaluate("JSON.parse(localStorage.getItem('taxAIFavorites'))")
        assert len(favorites) == 1
        page.keyboard.press("Escape")
        page.reload(wait_until="networkidle")
        assert page.evaluate("JSON.parse(localStorage.getItem('taxAIFavorites'))") == favorites
        page.locator('[data-view="favorites"]').click()
        assert page.locator("#favoriteList .result-card").count() == 1
        page.locator("#favoriteList [data-fav]").click()
        assert page.evaluate("JSON.parse(localStorage.getItem('taxAIFavorites'))") == []
        assert page.locator("#favoriteList .empty").count() == 1
        checks.append("favorites: add, reload persistence, remove and empty state")

        page.locator('[data-view="home"]').click()
        page.locator("#homeView .search-input").fill("房屋稅")
        page.locator("#homeView .search-form button").click()
        assert result_ids(page) == expected_search["房屋稅"]
        for query, ids in expected_search.items():
            page.locator("#searchView .search-input").fill(query)
            page.locator("#searchView .search-form button").click()
            assert result_ids(page) == ids, query
        checks.append("quick search: home/search matching order and three frozen query results")

        page.locator("#searchView .search-input").fill("ZZZ_NO_MATCH_20261008")
        page.locator("#searchView .search-form button").click()
        assert page.locator("#searchResults .empty").count() == 1
        checks.append("quick search: original no-match state")

        page.locator('[data-view="home"]').click()
        page.locator('#categoryCards [data-cat="房屋稅"]').click()
        assert page.locator("#searchResults .result-card").count() == 24
        expect(page.locator("#searchMeta b")).to_have_text("共 24 筆")
        checks.append("home category shortcut: 24 housing questions")

        page.locator('[data-view="home"]').click()
        popular = page.locator("#popularSearches [data-popular-id]").first
        title = popular.get_attribute("title")
        popular.click()
        expect(page.locator("#drawerContent h2")).to_have_text(title)
        page.keyboard.press("Escape")
        checks.append("popular chip: opens the original question detail")

        page.locator("#homeView .search-input").fill("")
        page.locator("#homeView .search-form button").click()
        expect(page.locator("#searchMeta b")).to_have_text("共 129 筆")
        assert result_ids(page) == [str(number) for number in range(1, 51)]
        checks.append("empty query: original order and 50-result display limit")

        page.locator('[data-view="bank"]').click()
        page.locator("#bankList .bank-row").first.click()
        page.locator("[data-copy]").click()
        expect(page.locator("#toast")).to_have_text("已複製完整答詢")
        copied = page.evaluate("navigator.clipboard.readText()")
        assert page.evaluate("bank[0].answer") in copied
        assert page.evaluate("bank[0].question") in copied
        page.keyboard.press("Escape")
        checks.append("copy: clipboard contains complete original question and answer")

        upload_excel(page, [["問題", "完整答案"], ["合成問題", "合成答案"]])
        expect(page.locator("#toast")).to_have_text("Excel 元件載入失敗，請確認網路連線")
        expect(page.locator("#bankCount")).to_have_text("129")
        checks.append("Excel dependency unavailable: failure leaves the original bank intact")

        # The original learning navigation is hidden. Invoke its existing handler without changing UI.
        page.locator('[data-view="learning"]').evaluate("element => element.click()")
        assert page.locator("#learningNews .learning-news-item").count() == 6
        page.locator(".learning-start-btn").click()
        expect(page.locator("#drawerContent h2")).to_have_text(page.evaluate("window.LEARNING_BANK.featured.title"))
        page.keyboard.press("Escape")
        missing_images = page.evaluate("[window.LEARNING_BANK.featured, ...window.LEARNING_BANK.news].flatMap(x=>[x.image,x.thumbnail]).filter(Boolean)")
        assert len(set(missing_images)) == 14
        assert all(not (ROOT / name).exists() for name in missing_images)
        checks.append("learning: seven article records and drawer; 14 images remain absent")

        page.set_viewport_size({"width": 390, "height": 844})
        page.locator("#menuBtn").click()
        expect(page.locator(".sidebar")).to_have_class("sidebar open")
        page.locator('[data-view="home"]').click()
        expect(page.locator(".sidebar")).to_have_class("sidebar")
        expect(page.locator("#homeView")).to_have_class("view active")
        checks.append("mobile: menu opens and navigation closes it at 390px")
        context.close()

        if library is not None:
            context, page = new_context(with_xlsx=True)
            assert page.evaluate("XLSX.version") == "0.18.5"
            header = ["編號", "分類", "問題", "重點摘要", "完整答案", "關鍵字"]
            rows = [header, [1001, "合成分類", "離線測試甲", "短摘要", "完整答覆甲\n第二行", "離線測試"],
                    [1002, "合成分類", "離線測試乙", "短摘要", "完整答覆乙", "離線測試"]]
            upload_excel(page, rows)
            expect(page.locator("#toast")).to_have_text("已成功匯入 2 題")
            expect(page.locator("#bankCount")).to_have_text("2")
            assert page.locator("#bankList .bank-row").count() == 2
            assert len(page.evaluate("JSON.parse(localStorage.getItem('taxAIExcelBank'))")) == 2
            page.locator('[data-view="search"]').click()
            page.locator("#searchView .search-input").fill("離線測試")
            page.locator("#searchView .search-form button").click()
            assert result_ids(page) == ["1001", "1002"]
            page.locator("#searchResults [data-open]").first.click()
            assert page.locator("#drawerContent .detail-card").nth(1).locator("p").text_content() == "完整答覆甲\n第二行"
            page.keyboard.press("Escape")
            checks.append("real XLSX 0.18.5: two synthetic OOXML rows replace runtime bank and remain searchable")

            dialogs = []
            page.on("dialog", lambda dialog: (dialogs.append(dialog.message), dialog.accept()))
            upload_excel(page, [header, rows[1], [1001, "合成分類", "另一題", "摘要", "另一答案", ""]])
            page.wait_for_function("document.querySelector('#excelFileInput').value === ''")
            assert len(dialogs) == 1 and "重複" in dialogs[0]
            expect(page.locator("#bankCount")).to_have_text("2")
            assert page.evaluate("bank.map(x=>x.id)") == [1001, 1002]
            upload_excel(page, [["不相符欄位"], ["合成資料"]])
            page.wait_for_function("document.querySelector('#excelFileInput').value === ''")
            assert len(dialogs) == 2 and "找不到可匯入的題目" in dialogs[1]
            assert page.evaluate("bank.map(x=>x.id)") == [1001, 1002]
            checks.append("real XLSX errors: duplicate IDs and absent question columns leave the runtime bank intact")

            page.reload(wait_until="networkidle")
            expect(page.locator("#bankCount")).to_have_text("129")
            assert len(page.evaluate("JSON.parse(localStorage.getItem('taxAIExcelBank'))")) == 2
            checks.append("reload: original JS bank wins over saved Excel, matching existing behavior")
            context.close()
        assert not errors, errors
        browser_version = browser.version
        browser.close()

    return {
        "status": "PASS", "checks": checks, "check_count": len(checks),
        "chromium_version": browser_version, "page_errors": errors,
        "blocked_external_origins": sorted(blocked), "missing_requested_assets": sorted(missing),
        "known_missing_learning_images": sorted(set(missing_images)),
        "cached_xlsx_sha256": XLSX_SHA256 if library else None,
        "cached_xlsx_route_responses": cached_requests,
        "external_page_requests_sent": 0,
        "limitations": [] if library else ["Real XLSX success/error paths not run; supply --xlsx-script"],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--browser", default=shutil.which("chromium"))
    parser.add_argument("--xlsx-script", type=Path, help="Optional offline copy of the pinned CDN dependency")
    parser.add_argument("--report", type=Path, help="Local report path; keep it outside Git")
    args = parser.parse_args()
    result = run(args.browser, args.xlsx_script)
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        args.report.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()

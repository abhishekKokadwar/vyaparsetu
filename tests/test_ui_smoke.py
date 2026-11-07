import pytest
from playwright.sync_api import sync_playwright

BASE_URL = "http://127.0.0.1:8000"

def get_browser(p):
    """Launches headless Chrome or Edge browser installed on Windows"""
    for channel in ["chrome", "msedge"]:
        try:
            return p.chromium.launch(headless=True, channel=channel)
        except Exception:
            continue
    return p.chromium.launch(headless=True)

def test_ui_smoke_navigation_and_zero_console_errors():
    """
    Playwright Smoke Test:
    1. Validates end-to-end journey across all 5 prototype tabs:
       Advisor -> Quote -> Smart KYC -> Order Tracker -> Partner Portal.
    2. Enforces ZERO unhandled JavaScript runtime console errors or page exceptions.
    3. Verifies zero 'undefined' or 'NaN' rendering bugs in DOM.
    4. Confirms pricing synchronization between Advisor recommendation and Quote bill.
    """
    with sync_playwright() as p:
        browser = get_browser(p)
        page = browser.new_page()

        console_errors = []
        page_errors = []

        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda err: page_errors.append(str(err)))

        # 1. Load Homepage
        page.goto(BASE_URL, wait_until="networkidle")
        assert "VyaparSetu" in page.title()

        # 2. Tab 1: Advisor Journey
        # Select Kirana preset button
        kirana_btn = page.locator("button:has-text('Kirana')").first
        assert kirana_btn.is_visible()
        kirana_btn.click()
        page.wait_for_timeout(600)

        advisor_content = page.locator("#advisor-content")
        assert advisor_content.is_visible()
        rec_text = advisor_content.inner_text()
        assert "undefined" not in rec_text.lower()
        assert "nan" not in rec_text.lower()
        assert "₹" in page.locator("#rec-price").inner_text()

        # 3. Tab 2: Quote & Catalogue
        page.click("#tab-btn-quote")
        page.wait_for_timeout(600)

        quote_total_elem = page.locator("#bill-monthly-total")
        assert quote_total_elem.is_visible()
        quote_text = quote_total_elem.inner_text()
        assert "₹" in quote_text
        assert "undefined" not in quote_text
        assert "nan" not in quote_text

        # 4. Tab 3: Smart KYC Verification
        page.click("#tab-btn-kyc")
        page.wait_for_timeout(600)

        verdict_title = page.locator("#kyc-verdict-title")
        assert verdict_title.is_visible()

        # Test K02 (Clean Pass)
        page.select_option("#kyc-applicant-select", "K02")
        page.wait_for_timeout(700)
        k02_status = page.locator("#kyc-verdict-title").inner_text()
        assert "VERIFIED" in k02_status or "PASS" in k02_status

        # Test K06 (Planted Fake GSTIN)
        page.select_option("#kyc-applicant-select", "K06")
        page.wait_for_timeout(700)
        k06_status = page.locator("#kyc-verdict-title").inner_text()
        assert "REJECTED" in k06_status

        # Test K07 (Legal Entity Mismatch)
        page.select_option("#kyc-applicant-select", "K07")
        page.wait_for_timeout(700)
        k07_status = page.locator("#kyc-verdict-title").inner_text()
        assert "REJECTED" in k07_status

        # 5. Tab 4: Order Tracker
        page.click("#tab-btn-tracker")
        page.wait_for_timeout(600)

        assert page.locator("#trk-order-num").is_visible()
        order_num = page.locator("#trk-order-num").inner_text()
        assert "VS-2026" in order_num
        assert page.locator("#trk-tech-pin").is_visible()

        # 6. Tab 5: Partner Portal
        page.click("#tab-btn-partner")
        page.wait_for_timeout(800)

        dropped_stat = page.locator("#ptnr-dropped-leads").inner_text()
        assert "4,632" in dropped_stat

        salvageable_stat = page.locator("#ptnr-salvageable").inner_text()
        assert "1,463" in salvageable_stat

        arr_stat = page.locator("#ptnr-arr").inner_text()
        assert "2.24" in arr_stat

        # Table rows check
        table_body = page.locator("#ptnr-leads-table")
        assert table_body.is_visible()
        table_text = table_body.inner_text()
        assert "undefined" not in table_text.lower()

        # Filter un-actionable console errors (e.g. 404 on non-critical favicon)
        fatal_console_errors = [e for e in console_errors if "favicon" not in e.lower() and "404" not in e.lower()]
        assert len(fatal_console_errors) == 0, f"Encountered JS console errors: {fatal_console_errors}"
        assert len(page_errors) == 0, f"Encountered page errors: {page_errors}"

        browser.close()

def test_diagrams_page_smoke():
    """Verify SVG Architecture & Journey Diagrams page renders cleanly"""
    with sync_playwright() as p:
        browser = get_browser(p)
        page = browser.new_page()

        page.goto(f"{BASE_URL}/diagrams", wait_until="networkidle")
        assert "Diagrams" in page.title()
        assert page.locator("#active-diagram-img").is_visible()

        # Switch to Journey tab
        page.click("#tab-journey")
        page.wait_for_timeout(400)
        assert "Customer Journey" in page.locator("#diag-caption").inner_text()

        browser.close()

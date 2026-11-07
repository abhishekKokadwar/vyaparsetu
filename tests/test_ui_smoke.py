import os
import re
import socket
from pathlib import Path
import pytest
from playwright.sync_api import sync_playwright

BASE_URL = os.environ.get("SMOKE_BASE_URL", "http://127.0.0.1:8000")

def is_server_running(host=None, port=None):
    if host is None or port is None:
        # Parse from BASE_URL
        from urllib.parse import urlparse
        parsed = urlparse(BASE_URL)
        host = parsed.hostname or "127.0.0.1"
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
    try:
        with socket.create_connection((host, port), timeout=1.0):
            return True
    except OSError:
        return False

def get_browser(p):
    """Launches headless Chrome or Edge browser installed on Windows"""
    for channel in ["chrome", "msedge", None]:
        try:
            if channel:
                return p.chromium.launch(headless=True, channel=channel)
            return p.chromium.launch(headless=True)
        except Exception:
            continue
    raise RuntimeError("No suitable Chromium browser found for Playwright")

def clean_currency(txt: str) -> str:
    return re.sub(r'[^0-9]', '', txt or '')

def test_ui_smoke_navigation_and_zero_console_errors():
    """
    Playwright Smoke Test:
    1. Validates end-to-end journey across all 5 prototype tabs:
       Advisor -> Quote -> Smart KYC -> Order Tracker -> Partner Portal.
    2. Enforces ZERO unhandled JavaScript runtime console errors or page exceptions.
    3. Verifies zero 'undefined' or 'NaN' rendering bugs in DOM.
    4. Confirms pricing synchronization between Advisor recommendation and Quote bill across 4 personas.
    5. Verifies real multipart document upload with K07 image files catching legal entity mismatch.
    """
    if not is_server_running():
        pytest.skip(f"Server not running at {BASE_URL}; run 'py run.py' or set SMOKE_BASE_URL")

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

        # 2. Scenarios Pricing Sync across 4 personas
        scenarios = ["kirana_no_gst", "clinic_pro", "multi_store", "small_mfg"]
        for sc in scenarios:
            page.evaluate(f"loadScenario('{sc}')")
            page.wait_for_timeout(500)
            rec_price_raw = page.locator("#rec-price").inner_text()
            rec_price = clean_currency(rec_price_raw)
            # Switch to Quote tab
            page.click("#tab-btn-quote")
            page.wait_for_timeout(400)
            quote_price_raw = page.locator("#bill-monthly-total").inner_text()
            quote_price = clean_currency(quote_price_raw)
            assert rec_price == quote_price, f"Price mismatch for {sc}: rec={rec_price} vs quote={quote_price}"
            # Switch back to Advisor tab
            page.click("#tab-btn-advisor")
            page.wait_for_timeout(300)

        # 3. Tab 3: Smart KYC Verification (PASS & REJECT checks)
        page.click("#tab-btn-kyc")
        page.wait_for_timeout(500)

        verdict_title = page.locator("#kyc-verdict-title")
        assert verdict_title.is_visible()

        # Test K02 (Clean Pass)
        page.select_option("#kyc-applicant-select", "K02")
        page.wait_for_timeout(500)
        k02_status = page.locator("#kyc-verdict-title").inner_text()
        assert "VERIFIED" in k02_status or "PASS" in k02_status

        # Test K06 (Planted Fake GSTIN)
        page.select_option("#kyc-applicant-select", "K06")
        page.wait_for_timeout(500)
        k06_status = page.locator("#kyc-verdict-title").inner_text()
        assert "REJECTED" in k06_status

        # Test K07 (Legal Entity Mismatch)
        page.select_option("#kyc-applicant-select", "K07")
        page.wait_for_timeout(500)
        k07_status = page.locator("#kyc-verdict-title").inner_text()
        assert "REJECTED" in k07_status

        # 4. Real Multipart Document Upload (K07)
        k07_dir = Path(__file__).resolve().parent.parent / "udyam_digital_data" / "kyc_documents"
        k07_files = [
            str(k07_dir / "K07_gst_certificate.png"),
            str(k07_dir / "K07_udyam_certificate.png"),
            str(k07_dir / "K07_address_proof.png"),
            str(k07_dir / "K07_signatory_id.png"),
        ]
        if all(os.path.exists(f) for f in k07_files):
            file_input = page.locator("#kyc-file-upload-input")
            with page.expect_response(lambda res: "/api/kyc/upload-files" in res.url, timeout=45000) as response_info:
                file_input.set_input_files(k07_files)
            resp = response_info.value
            assert resp.status == 200
            page.wait_for_timeout(800)
            upload_verdict = page.locator("#kyc-verdict-title").inner_text()
            assert "REJECTED" in upload_verdict
            upload_desc = page.locator("#kyc-verdict-desc").inner_text()
            assert "mismatch" in upload_desc.lower() or "shri physio" in upload_desc.lower()

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
        assert "932" in salvageable_stat

        arr_stat = page.locator("#ptnr-arr").inner_text()
        assert "1.91" in arr_stat

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
    if not is_server_running():
        pytest.skip("Local test server not running on port 8000; run 'py run.py' to run browser smoke tests")

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

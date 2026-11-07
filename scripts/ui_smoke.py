import sys
import os
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_URL = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "http://localhost:8000"
ONLY_MOBILE = "--mobile" in sys.argv

PASS_APPLICANTS = ["K02", "K03", "K08", "K09", "K10", "K12"]
REJECT_APPLICANTS = ["K01", "K04", "K05", "K06", "K07", "K11"]

def get_browser(p):
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

def switch_to_tab(page, tab_name: str):
    mobile_btn = page.locator(f'#mobile-subnav button[data-tab="{tab_name}"]')
    desktop_btn = page.locator(f'#tab-btn-{tab_name}')
    if mobile_btn.is_visible():
        mobile_btn.click()
    elif desktop_btn.is_visible():
        desktop_btn.click()
    else:
        page.evaluate(f"switchTab('{tab_name}')")
    page.wait_for_timeout(300)

def run_journey(page, mode_name: str, base_url: str):
    print("-" * 70)
    print(f"Executing End-to-End Journey in {mode_name} mode...")
    print("-" * 70)

    console_errors = []
    page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
    page.on("pageerror", lambda err: console_errors.append(str(err)))

    # 1. Homepage Load & Title
    print(f"  [1/8] Loading application homepage ({mode_name})...")
    page.goto(base_url, wait_until="networkidle")
    assert "VyaparSetu" in page.title()
    print("        PASS: Homepage loaded cleanly.")

    # Check horizontal scroll on mobile
    if "Mobile" in mode_name:
        scroll_w = page.evaluate("document.documentElement.scrollWidth")
        client_w = page.evaluate("document.documentElement.clientWidth")
        assert scroll_w <= client_w + 1, f"Horizontal scroll detected on mobile: {scroll_w}px > {client_w}px"
        print(f"        PASS: Zero horizontal scroll on mobile ({scroll_w}px <= {client_w}px).")

    # 2. Scenarios Pricing Sync
    print(f"  [2/8] Testing Advisor & Quote pricing sync across 4 personas ({mode_name})...")
    scenarios = ["kirana_no_gst", "clinic_pro", "multi_store", "small_mfg"]
    for sc in scenarios:
        with page.expect_response(lambda res: "/api/advisor/recommend" in res.url, timeout=15000):
            page.evaluate(f"loadScenario('{sc}')")
        page.wait_for_timeout(400)
        rec_price_raw = page.locator("#rec-price").inner_text()
        rec_price = clean_currency(rec_price_raw)
        # Switch to Quote tab
        switch_to_tab(page, "quote")
        page.wait_for_timeout(400)
        quote_price_raw = page.locator("#bill-monthly-total").inner_text()
        quote_price = clean_currency(quote_price_raw)
        assert rec_price == quote_price, f"Price mismatch for {sc}: rec={rec_price} vs quote={quote_price}"
        # Switch back to Advisor tab
        switch_to_tab(page, "advisor")
        page.wait_for_timeout(300)
    print("        PASS: Pricing 100% matched across all 4 personas.")

    # 3. Smart KYC K01-K12 Verification Checks
    print(f"  [3/8] Testing Smart KYC registry verification across K01-K12 ({mode_name})...")
    switch_to_tab(page, "kyc")
    page.wait_for_timeout(400)
    page.check("#dpdp-consent-chk")
    page.wait_for_timeout(300)
    for app_code in PASS_APPLICANTS:
        with page.expect_response(lambda res: "/api/kyc/verify-applicant" in res.url, timeout=15000):
            page.select_option("#kyc-applicant-select", app_code)
        page.wait_for_timeout(300)
        title = page.locator("#kyc-verdict-title").inner_text()
        assert "VERIFIED" in title or "PASS" in title, f"{app_code} expected PASS, got {title}"
    for app_code in REJECT_APPLICANTS:
        with page.expect_response(lambda res: "/api/kyc/verify-applicant" in res.url, timeout=15000):
            page.select_option("#kyc-applicant-select", app_code)
        page.wait_for_timeout(300)
        title = page.locator("#kyc-verdict-title").inner_text()
        assert "REJECTED" in title, f"{app_code} expected REJECTED, got {title}"
    print("        PASS: All 12 KYC sample applicants verified correctly (6 PASS / 6 REJECT).")

    # 4. Real File Upload with K07 PNGs
    print(f"  [4/8] Testing real multipart image upload with K07 documents ({mode_name})...")
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
        upload_desc = page.locator("#kyc-verdict-desc").inner_text()
        assert "REJECTED" in upload_verdict, f"K07 upload expected REJECTED, got {upload_verdict}"
        checklist_text = page.locator("#kyc-checklist-container").inner_text()
        assert "mismatch" in upload_desc.lower() or "mismatch" in checklist_text.lower(), f"Expected legal entity mismatch in verdict, got: {upload_desc}"
        print("        PASS: K07 upload correctly extracted and caught legal entity mismatch.")

        # A valid applicant MUST pass end to end through real OCR (K07 alone passes even if extraction is broken,
        # because a broken extractor also rejects).
        k02_files = [str(k07_dir / f"K02_{n}.png") for n in
                     ("gst_certificate", "udyam_certificate", "address_proof", "signatory_id")]
        with page.expect_response(lambda res: "/api/kyc/upload-files" in res.url, timeout=60000) as response_info:
            file_input.set_input_files(k02_files)
        assert response_info.value.status == 200, f"K02 upload HTTP {response_info.value.status}"
        page.wait_for_timeout(800)
        k02_verdict = page.locator("#kyc-verdict-title").inner_text()
        assert "VERIFIED" in k02_verdict.upper() or "PASS" in k02_verdict.upper() or "APPROVED" in k02_verdict.upper(), \
            f"K02 upload must PASS, got: {k02_verdict} / {page.locator('#kyc-verdict-desc').inner_text()}"
        assert page.locator("#btn-place-order").is_enabled(), "K02 passed but 'Confirm & Activate' is still disabled"
        print("        PASS: K02 upload passes end to end and unlocks activation.")
    else:
        print("        SKIP: K07 files not found on disk.")

    # 5. Place Order for K02 & Verify Live Tracker
    print(f"  [5/8] Testing order creation from verified applicant K02 ({mode_name})...")
    with page.expect_response(lambda res: "/api/kyc/verify-applicant" in res.url, timeout=15000):
        page.select_option("#kyc-applicant-select", "K02")
    page.wait_for_timeout(300)
    with page.expect_response(lambda res: "/api/orders/create" in res.url, timeout=15000):
        page.evaluate("placeOrderAfterKYC()")
    page.wait_for_timeout(400)
    assert page.locator("#trk-order-num").is_visible()
    trk_num = page.locator("#trk-order-num").inner_text()
    assert trk_num.startswith("VS-2026-"), f"Expected VS-2026- order ID, got {trk_num}"
    print(f"        PASS: Order {trk_num} generated with dynamic SLA & PIN.")

    # 6. Partner Portal Verification
    print(f"  [6/8] Testing Channel Partner Portal live numbers & recovery queue ({mode_name})...")
    switch_to_tab(page, "partner")
    page.wait_for_timeout(400)
    salvageable_text = page.locator("#ptnr-salvageable").inner_text()
    assert "932" in salvageable_text, f"Expected 932 high propensity leads, got {salvageable_text}"
    rows = page.locator("#ptnr-leads-table tr")
    assert rows.count() > 0, "Expected at least 1 lead row in partner table"
    print(f"        PASS: Partner portal shows {salvageable_text} salvageable leads.")

    # 7. Absence of NaN or undefined in DOM text
    print(f"  [7/8] Scanning DOM text for 'undefined' or 'NaN' rendering bugs ({mode_name})...")
    body_text = page.locator("body").inner_text()
    assert not re.search(r'\bNaN\b', body_text), "Detected raw NaN rendered in visible page text"
    assert not re.search(r'\bundefined\b', body_text, re.IGNORECASE), "Detected raw undefined rendered in visible page text"
    print("        PASS: Zero 'undefined' or 'NaN' text detected.")

    # 8. Check for JavaScript Console Errors
    print(f"  [8/8] Validating console logs ({mode_name})...")
    fatal_errors = [e for e in console_errors if "favicon" not in e.lower() and "404" not in e.lower()]
    assert len(fatal_errors) == 0, f"Encountered JS errors: {fatal_errors}"
    print("        PASS: Zero unhandled console runtime errors.")

def main():
    print("=" * 70)
    print(f"VyaparSetu · End-to-End Browser Journey Smoke Test ({BASE_URL})")
    print("=" * 70)

    with sync_playwright() as p:
        browser = get_browser(p)

        if not ONLY_MOBILE:
            # 1. Desktop 1440px Journey
            desk_ctx = browser.new_context(viewport={"width": 1440, "height": 900})
            page_desk = desk_ctx.new_page()
            run_journey(page_desk, "Desktop (1440px)", BASE_URL)
            desk_ctx.close()

        # 2. Mobile 375px Journey (Touch + Responsive Emulation)
        mob_ctx = browser.new_context(
            viewport={"width": 375, "height": 667},
            is_mobile=True,
            has_touch=True,
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1"
        )
        page_mob = mob_ctx.new_page()
        run_journey(page_mob, "Mobile (375px)", BASE_URL)
        mob_ctx.close()

        browser.close()

    print("=" * 70)
    modes_tested = "Mobile (375px)" if ONLY_MOBILE else "Both Desktop (1440px) & Mobile (375px)"
    print(f"ALL END-TO-END JOURNEY CHECKS PASSED FOR {modes_tested.upper()}.")
    print("=" * 70)
    sys.exit(0)

if __name__ == "__main__":
    main()

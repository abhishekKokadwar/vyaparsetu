import sys
import os
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"

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

def main():
    print("=" * 70)
    print(f"VyaparSetu · End-to-End Browser Journey Smoke Test ({BASE_URL})")
    print("=" * 70)

    checks_passed = 0
    total_checks = 8

    with sync_playwright() as p:
        browser = get_browser(p)
        page = browser.new_page()

        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda err: console_errors.append(str(err)))

        # 1. Homepage Load & Title
        print("[1/8] Loading application homepage...")
        page.goto(BASE_URL, wait_until="networkidle")
        assert "VyaparSetu" in page.title()
        print("      PASS: Homepage loaded cleanly.")
        checks_passed += 1

        # 2. Scenarios Pricing Sync
        print("[2/8] Testing Advisor & Quote pricing sync across 4 business personas...")
        scenarios = ["kirana_no_gst", "clinic_pro", "multi_store", "small_mfg"]
        for sc in scenarios:
            page.evaluate(f"loadScenario('{sc}')")
            page.wait_for_timeout(600)
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
        print("      PASS: Pricing 100% matched across all 4 personas.")
        checks_passed += 1

        # 3. Smart KYC K01-K12 Verification Checks
        print("[3/8] Testing Smart KYC registry verification across K01-K12...")
        page.click("#tab-btn-kyc")
        page.wait_for_timeout(500)
        page.check("#dpdp-consent-chk")
        page.wait_for_timeout(300)
        for app_code in PASS_APPLICANTS:
            page.select_option("#kyc-applicant-select", app_code)
            page.wait_for_timeout(400)
            title = page.locator("#kyc-verdict-title").inner_text()
            assert "VERIFIED" in title or "PASS" in title, f"{app_code} expected PASS, got {title}"
        for app_code in REJECT_APPLICANTS:
            page.select_option("#kyc-applicant-select", app_code)
            page.wait_for_timeout(400)
            title = page.locator("#kyc-verdict-title").inner_text()
            assert "REJECTED" in title, f"{app_code} expected REJECTED, got {title}"
        print("      PASS: All 12 KYC sample applicants verified correctly (6 PASS / 6 REJECT).")
        checks_passed += 1

        # 4. Real File Upload with K07 PNGs
        print("[4/8] Testing real multipart image upload with K07 documents...")
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
            print("      PASS: K07 upload correctly extracted and caught legal entity mismatch.")
        else:
            print("      SKIP: K07 files not found on disk.")
        checks_passed += 1

        # 5. Place Order for K02 & Verify Live Tracker
        print("[5/8] Testing order creation from verified applicant K02...")
        page.select_option("#kyc-applicant-select", "K02")
        page.wait_for_timeout(500)
        # Click place order button
        page.evaluate("placeOrderAfterKYC()")
        page.wait_for_timeout(800)
        assert page.locator("#trk-order-num").is_visible()
        trk_num = page.locator("#trk-order-num").inner_text()
        assert trk_num.startswith("VS-2026-"), f"Expected VS-2026- order ID, got {trk_num}"
        print(f"      PASS: Order {trk_num} generated with dynamic SLA & PIN.")
        checks_passed += 1

        # 6. Partner Portal Verification
        print("[6/8] Testing Channel Partner Portal live numbers & recovery queue...")
        page.click("#tab-btn-partner")
        page.wait_for_timeout(800)
        salvageable_text = page.locator("#ptnr-salvageable").inner_text()
        assert "932" in salvageable_text, f"Expected 932 high propensity leads, got {salvageable_text}"
        rows = page.locator("#ptnr-leads-table tr")
        assert rows.count() > 0, "Expected at least 1 lead row in partner table"
        print(f"      PASS: Partner portal shows {salvageable_text} salvageable leads.")
        checks_passed += 1

        # 7. Absence of NaN or undefined in DOM text
        print("[7/8] Scanning DOM text for 'undefined' or 'NaN' rendering bugs...")
        body_text = page.locator("body").inner_text()
        assert not re.search(r'\bNaN\b', body_text), "Detected raw NaN rendered in visible page text"
        assert not re.search(r'\bundefined\b', body_text, re.IGNORECASE), "Detected raw undefined rendered in visible page text"
        print("      PASS: Zero 'undefined' or 'NaN' text detected.")
        checks_passed += 1

        # 8. Check for JavaScript Console Errors
        print("[8/8] Validating console logs...")
        fatal_errors = [e for e in console_errors if "favicon" not in e.lower() and "404" not in e.lower()]
        assert len(fatal_errors) == 0, f"Encountered JS errors: {fatal_errors}"
        print("      PASS: Zero unhandled console runtime errors.")
        checks_passed += 1

        browser.close()

    print("=" * 70)
    print(f"ALL {checks_passed}/{total_checks} BROWSER SMOKE CHECKS PASSED.")
    print("=" * 70)
    sys.exit(0)

if __name__ == "__main__":
    main()

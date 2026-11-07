# VyaparSetu · Fix Plan v2 (re-audit, 7 Nov 2026)

**Goal:** a deployed prototype (Vercel) that holds up when Airtel judges upload documents, type their own advisor scenarios, and read the repo, and documents that agree with the deck.

**How to use this plan**
1. Do the items **in order**. Each one has: *Why*, *Files*, *Steps*, *Verify* (exact command and expected result), and *Don't* (common mistakes).
2. An item is done only when its **Verify** passes. Don't tick an item because the tests pass: several bugs below passed every test.
3. **Never edit an expected value in a test just to make it pass.** If a test disagrees with the code, decide which one is wrong and write down why in the commit message.
4. Commit after each item, using the commit message given.
5. Run everything from the repo root: `D:\CODES\hackathons_and_activities\airtel`.

---

## Part A · Already fixed and verified (don't redo)

| Item from v1 | Verified how | Result |
|---|---|---|
| Slide 2: 49% / 2,290 leads | Clusters recomputed from `smb_leads.csv`: 1,632 + 385 + 273 = 2,290 | ✅ |
| Slide 3: "baseline configurations" note | Exported PPTX checked | ✅ |
| Partner screen shows live API numbers | Playwright: 1,808 / ₹2.60 Cr / ₹39.0 L, 12 lead rows | ✅ |
| KYC verdicts come from the documents, not hardcoded labels | All hardcoded fields deleted at runtime → same 12 verdicts | ✅ |
| K06 (fake GSTIN) and K07 (name mismatch) rejected | `verify_applicant_by_code` | ✅ |
| GSTIN normaliser false rejects | All 3,534 registry GSTINs → normalise → lookup: **0 not found** (was 120) | ✅ |
| Install estimate from catalogue | Leased-line order with caller value 3 → **21 days** | ✅ |
| GSTIN masked in partner leads API | `/api/partner/leads` | ✅ |
| LLM advisor (OpenRouter) | 8/8 on previously failed messages (Tamil, Punjabi, Marathi, Hinglish), ~2.4 s each | ✅ (uncommitted) |
| Offline UI (no CDN) | `app/static/vendor/tailwind.js`, `lucide.min.js` | ✅ (uncommitted) |
| Filename-based fake upload removed | No `fn.includes('K..')` left in `app.js` | ✅ (uncommitted) |
| DPDP retention: 30 days in code and note | `kyc_engine.py` line ~247, `DPDP_COMPLIANCE_NOTE.md` | ✅ (uncommitted) |

**Reference values used in Verify steps below** (don't change these):
- KYC sample verdicts: **PASS** = K02, K03, K08, K09, K10, K12. **REJECT** = K01, K04, K05, K06, K07, K11.
- Endpoint count today: **31** (`grep -c "^@app\." app/main.py`).
- Deck KPIs: conversion **7.4% → 15%**, time **17.6 d → ≤ 5 d**, chase calls **3.0 → < 0.5**, CAC **₹15,053 → ≤ ₹7,500**, churn **15.2% → < 10%**, NPS baseline **6.9**.

---

## Part B · Fixes, in order

| # | Fix | Priority | Est. |
|---|---|---|---|
| B0 | Save current work safely | 🔴 | 10 min |
| B1 | Tests must not call the LLM | 🔴 | 45 min |
| B2 | Upload: document classification overwrites the GST certificate | 🔴 | 45 min |
| B3 | Upload: path traversal and limits | 🔴 | 20 min |
| B4 | Upload: OCR that works on Vercel (Linux) | 🔴 | 1.5 h |
| B5 | LLM output validation and prompt fixes | 🟠 | 45 min |
| B6 | Order tracker must not depend on server memory | 🟠 | 1 h |
| B7 | Deployment files and Vercel deploy | 🔴 | 1 h |
| B8 | Partner portal: masking and propensity | 🟡 | 45 min |
| B9 | Documents agree with the deck | 🟡 | 30 min |
| B10 | Browser smoke test | 🟠 | 1 h |
| B11 | Demo readiness | 🟠 | 2 h |

---

### B0 · Save current work safely 🔴
**Why:** the LLM client, vendor files and upload code are uncommitted, and the suite currently shows **2 failed, 62 passed** because the tests hit the live LLM (fixed in B1).

**Steps**
1. `git status` and confirm `.env` is **not** listed (it is gitignored; keep it that way).
2. `git add app/ tests/ && git commit -m "wip: LLM advisor, real file upload, offline vendor assets"`
   Commit even with 2 failing tests; B1 fixes them. Don't push yet.

**Verify:** `git status --short` shows nothing under `app/` or `tests/`. `git log -1 --stat` does **not** include `.env`.

**Don't:** use `git add .` (it would pick up scratch files). Don't push before B1 passes.

---

### B1 · Tests must not call the LLM 🔴
**Why:** the suite calls OpenRouter. Results vary between runs (8 failures on one run, 2 on the next), it takes ~50 s, costs money, and fails without internet. Unit tests must be deterministic.

**Files:** `app/llm_client.py`, new `tests/conftest.py`, new `scripts/eval_advisor_llm.py`, `tests/test_phase3_advisor_engine.py`, `tests/test_phase7_end_to_end_journey.py`

**Steps**
1. In `app/llm_client.py`, make the client report disabled when `os.environ.get("VYAPAR_LLM_DISABLED") == "1"`: `extract_profile()` and any other network method return `None` immediately, before building the request.
2. Create `tests/conftest.py`:
   ```python
   import os
   os.environ["VYAPAR_LLM_DISABLED"] = "1"   # unit tests use the rule parser only
   ```
   It must run before `app` is imported. pytest loads `conftest.py` first, so a module-level assignment is enough.
3. The two failing tests now run on the rule parser. Re-run them:
   - `test_audit_colloquial_and_regional_queries` expects Marathi → `'mr'`. If the rule parser returns `'mr'`, it passes. If not, fix the rule parser's Marathi detection (Devanagari plus Marathi words: `आहे`, `माझे`, `मध्ये`), **not** the test.
   - `test_end_to_end_single_sitting_customer_lifecycle` ("2-counter किराना") expects `micro`. Same rule.
4. Create `scripts/eval_advisor_llm.py`, a **manual** evaluation that uses the real LLM. It contains the 18-message set below and prints OK/MISS, latency, and a total. It exits non-zero if fewer than 17/18 are correct. It's not part of pytest.

   | Message | Expected segment | Also check |
   |---|---|---|
   | I run a dental clinic in Pune with 6 staff, we have GST | prof | employees 6, GST true |
   | मेरी किराना दुकान है, 2 लोग काम करते हैं, GST नहीं है | micro | GST false |
   | we have 4 restaurants in bangalore, need cctv and one bill | multi | sites 4 |
   | small garment factory in Surat, 40 workers, machines need monitoring | mfg | employees 40 |
   | I'm a chartered accountant, 3 people, need email and backup | prof | employees 3 |
   | beauty parlour hai, wifi chahiye customers ke liye | micro | |
   | माझे मेडिकल स्टोअर आहे नाशिक मध्ये | micro | language mr |
   | We are a coaching institute with 2 branches and 15 teachers | multi | sites 2, employees 15 |
   | hardware shop chalata hoon Indore mein, akela hi hoon | micro | employees 1 |
   | Our law firm has 12 lawyers in one office in Delhi, GST registered | prof | employees 12, GST true |
   | chain of 6 pharmacies across Hyderabad | multi | sites 6 |
   | எனக்கு ஒரு மளிகை கடை இருக்கிறது, சென்னை | micro | language ta |
   | we make auto parts, 25 machines, plant in Pune, have GSTIN | mfg | GST true |
   | Mobile repair shop, 1 helper, no GST | micro | GST false |
   | 3 branches of our gym in Jaipur | multi | sites 3 |
   | eye hospital with 30 staff | prof | employees 30 |
   | ਮੇਰੀ ਬੇਕਰੀ ਹੈ ਲੁਧਿਆਣਾ ਵਿੱਚ | micro | language pa |
   | मेरी जयपुर में 2-counter किराना दुकान है 2 लोग काम करते हैं | micro | sites 1 (counters are not sites) |

**Verify**
- `set OPENROUTER_API_KEY=` (blank), then `py -m pytest -q` → **all passed, 0 failed, under 20 s**. Run it twice: same result both times.
- Turn off Wi-Fi and run `py -m pytest -q` → still all passed.
- `py scripts/eval_advisor_llm.py` (with the key, online) → **≥ 17/18**, average latency < 4 s.

**Don't:** mock by deleting the LLM code path. Don't put the 18-message eval inside pytest. Don't change `'mr'` to `'hi'` in the test.

**Commit:** `test: isolate unit tests from live LLM; add manual LLM eval set (18 msgs)`

---

### B2 · Upload: classification overwrites the GST certificate 🔴
**Why:** the Udyam certificate's text contains "Registration Certificate", which matches the GST rule first. It's stored as `gst_certificate` and **replaces the real GST certificate**. Result today: uploading the 4 genuine documents of **every** applicant (including the valid K02) gives **REJECT** "Missing Udyam + GSTIN UDYA… not found".

**Files:** `app/main.py` (`upload_kyc_files`)

**Steps**
1. Classify with **specific markers, most specific first**, on the uppercase OCR text:
   1. `UDYAM REG` or `UDYAM-` → `udyam_certificate`
   2. `GSTIN` or `GST REGISTRATION` → `gst_certificate`
   3. `ELECTRICITY BILL` or `BILL DATE` or `CONSUMER NO` → `address_proof`
   4. `SIGNATORY` or `VALID TILL` → `signatory_id`
   5. Otherwise use the filename keywords as now, else `unclassified`. **Never** default to `gst_certificate`.
2. **Never overwrite.** If a slot is already filled, put the file under `unclassified` and add a warning to the response: `"Two files look like <type>: <a>, <b>"`.
3. Return the chosen type per file in `extracted_snippets` (already there) so the UI can show "GST certificate ✓ / Udyam ✓ / …".
4. If any of the 4 slots is empty after classification, the verdict reasons must say which one ("Missing Udyam certificate"), which the engine already does.

**Verify** (server running on any port, e.g. 8765). This loop must print the reference verdicts for **all 12**:
```bash
cd udyam_digital_data/kyc_documents
for k in K01 K02 K03 K04 K05 K06 K07 K08 K09 K10 K11 K12; do
  files=""; for t in gst_certificate udyam_certificate address_proof signatory_id; do [ -f ${k}_$t.png ] && files="$files -F files=@${k}_$t.png"; done
  printf "%s " $k; curl -s -X POST localhost:8765/api/kyc/upload-files -F consent_granted=true $files | py -c "import json,sys;v=json.load(sys.stdin)['verification'];print(v['verdict'],v['reject_reasons'][:1])"
done
```
Expected: K02, K03, K08, K09, K10, K12 → **PASS**. K01, K04, K05, K06, K07, K11 → **REJECT**. K07's first reason must mention the **legal name mismatch**, and K06's the **GSTIN not found**. (K05 has no Udyam file; K04's GST image is blank.)

Also add `tests/test_upload_classification.py`. It feeds the **text** of the 4 K02 documents from `kyc_extracted.json` to the classification function (factor it out as `classify_document(text, filename)`) and asserts each lands in the right slot. Pure Python, no OCR, no network.

**Don't:** check "GST" before "UDYAM". Don't let the last file silently win.

**Commit:** `fix(kyc-upload): specific doc classification, no overwrite; 12/12 uploads match sample verdicts`

---

### B3 · Upload: path traversal and limits 🔴
**Why:** `os.path.join(temp_dir, file.filename)` with a filename like `../../app/main.py` writes outside the temp folder. On a public URL this is a security hole.

**Files:** `app/main.py`

**Steps**
1. Never use the client's filename as a path. Save as `os.path.join(temp_dir, f"{uuid.uuid4().hex}{ext}")`, where `ext = os.path.splitext(file.filename or "")[1].lower()`.
2. Allow only `.png .jpg .jpeg .webp .pdf .txt`. Anything else → HTTP 400.
3. Limits: at most **8 files** per request and **5 MB** per file (read in chunks and stop at 5 MB + 1 → HTTP 413).
4. Delete the temp folder in a `finally:` block (`shutil.rmtree(temp_dir, ignore_errors=True)`). Check that it already does; if not, add it.
5. Keep using `file.filename` only for **display** in the response.

**Verify**
- `curl -s -o /dev/null -w "%{http_code}" -X POST localhost:8765/api/kyc/upload-files -F "files=@README.md;filename=../../evil.txt"` → **200 or 400**, and `ls ../evil.txt ../../evil.txt` finds **nothing**.
- Upload a `.exe` → **400**. Upload a 6 MB file → **413**.
- After an upload, no `vyaparsetu_ocr_*` folders remain in `%TEMP%`.

**Commit:** `fix(security): sanitize upload paths, type/size limits, temp cleanup`

---

### B4 · Upload: OCR that works on Vercel 🔴
**Why:** OCR runs `powershell … scripts/ocr_test.ps1` (Windows only). Vercel runs Linux, so on the deployed site **every image upload extracts nothing** and is rejected.

**Decision:** use the LLM's vision input for OCR in the cloud and keep Windows OCR locally. (Tesseract isn't available on Vercel.)

**Files:** `app/llm_client.py`, `app/main.py`

**Steps**
1. In `llm_client.py`, add `ocr_image(image_bytes: bytes, mime: str) -> Optional[str]`. Send one user message with an `image_url` part (`data:<mime>;base64,<…>`) and the instruction: *"Transcribe all text in this document exactly as printed, in reading order. Output only the text, no commentary."* Use timeout 15 s and `temperature: 0`. It must respect `VYAPAR_LLM_DISABLED`.
2. In `main.py`, add `extract_text(path, ext)`:
   - `.txt/.json` → read the file.
   - Image and `os.name == "nt"` and env `OCR_BACKEND != "llm"` → PowerShell OCR (current code).
   - Otherwise → `llm_client.ocr_image(...)`.
   - If the result is empty or None → put the file under `unclassified` with the warning `"Could not read text from <file>"`. **Never** treat empty text as a valid document.
3. `.pdf`: return a clear 400, "PDF not supported yet, upload a PNG/JPG". Don't fake it.
4. Add `"ocr_backend": "windows" | "llm"` to the response so you can see which one ran.

**Verify**
- Locally with `set OCR_BACKEND=llm`, re-run the **B2 loop** → same 12 verdicts as the reference. Note the time per applicant (target < 20 s for 4 files).
- Locally without `OCR_BACKEND` → same 12 verdicts (Windows OCR).
- After B7 deploy: run the B2 loop against the **production URL** → same 12 verdicts.

**Don't:** fall back to the pre-extracted `kyc_extracted.json` for uploads. That would be the fake upload again.

**Commit:** `feat(kyc-upload): LLM vision OCR backend for Linux/Vercel, explicit unreadable-file handling`

---

### B5 · LLM output validation and prompt fixes 🟠
**Why:** the LLM read "2-counter kirana" as a multi-site chain, and Marathi as Hindi. LLM output is untrusted and must be checked before it reaches the rules engine.

**Files:** `app/llm_client.py` (prompt), `app/advisor_engine.py` (validation)

**Steps**
1. Prompt: add explicit rules.
   - "Counters, tills, desks, chairs, machines, looms are NOT sites. `num_sites` counts separate physical locations/branches/outlets."
   - "`preferred_language` must be one of: en, hi, mr, ta, te, pa, gu, bn, kn, ml. Detect it from the script **and** the words; Marathi uses Devanagari but words like आहे, माझे, मध्ये."
2. Validate in `advisor_engine.parse_conversational_query` after the LLM returns:
   - `segment` ∈ {micro, prof, multi, mfg}, else discard the LLM result and use the rule parser.
   - `employee_count`, `num_sites`: int, 1 ≤ value ≤ 10,000, else `None`.
   - `num_sites >= 2` is required for `segment == "multi"`. If the LLM says multi with 1 or no sites, set segment from the business type via the rule parser.
   - `preferred_language` not in the allowed list → `"en"`.
   - Record `profile["_source"] = "llm" | "rules"` so the UI and logs show which one ran.
3. The UI should still ask a clarifying question when segment or business type is missing, instead of defaulting to the kirana pack.

**Verify:** `py scripts/eval_advisor_llm.py` → **≥ 17/18**, including the "2-counter" and Marathi rows. `py -m pytest -q` still all pass (LLM disabled).

**Commit:** `fix(advisor): validate LLM profile; counters≠sites; language allow-list`

---

### B6 · Order tracker must not depend on server memory 🟠
**Why:** orders live in `OrderService.orders` (memory). On Vercel, creating an order and fetching it can hit different instances, giving "Order not found". `app.js` line ~720 then shows `alert("Order not found. Showing sample order VS-2026-90412.")`, which shows a judge **someone else's order**.

**Files:** `app/static/app.js`, optionally `app/order_service.py`

**Steps (minimum, enough for the demo)**
1. `placeOrderAfterKYC`: render the tracker **directly from the create response** (`renderOrderTracker(order)`, already at line ~705). Make sure no second fetch is needed for the happy path.
2. Store the created order in `localStorage` (`vs_last_order`). When "Track" is used and the server says 404 for that ID, render the stored copy and show the note "Showing your saved order".
3. **Remove** the `alert(...)` and the fallback to sample order `VS-2026-90412`. Show an inline "Order not found" message instead.

**Optional (proper fix):** Upstash Redis from the Vercel Marketplace. Store orders as JSON under `order:<id>` with a 7-day expiry. Use memory when the env var is absent (local dev).

**Verify**
- Locally: create an order → tracker shows it. Restart the server → click Track with that ID → it still shows (from `localStorage`), with no alert.
- `grep -n "alert(" app/static/app.js` → **no results**.

**Commit:** `fix(tracker): render from create response, local fallback, remove sample-order alert`

---

### B7 · Deployment files and Vercel deploy 🔴
**Why:** there's no `requirements.txt`, and `.env` (your OpenRouter key) is ignored by git but **not guaranteed to be ignored by the Vercel CLI**.

**Files:** new `requirements.txt`, new `.vercelignore`, new `vercel.json`

**Steps**
1. `requirements.txt` (pin to the versions that pass locally):
   ```text
   fastapi==0.139.0
   pydantic==2.13.4
   pandas==3.0.3
   numpy==2.4.6
   scipy==1.17.1
   python-multipart==0.0.32
   python-dotenv
   ```
   Run `py -m pip show python-dotenv` and pin its version too.
2. `.vercelignore`:
   ```text
   .env
   .env.*
   .git
   .playwright-mcp
   __pycache__
   *.pptx
   *.pdf
   *.zip
   6ae1873397bc1_digital
   airtel_sync_case
   deck
   tests
   scripts
   template1.pptx
   template2.pptx
   ```
   Keep `udyam_digital_data/` (the app reads its CSVs and `kyc_extracted.json`). `scripts/ocr_test.ps1` isn't needed in the cloud (B4).
3. `vercel.json`:
   ```json
   {
     "$schema": "https://openapi.vercel.sh/vercel.json",
     "functions": { "app/main.py": { "maxDuration": 60 } }
   }
   ```
   60 s covers cold start plus 4-file LLM OCR.
4. Link and set secrets (key values are typed by you; never commit them):
   ```bash
   vercel link
   vercel env add OPENROUTER_API_KEY production
   vercel env add OPENROUTER_API_KEY preview
   vercel env add OPENROUTER_MODEL production     # e.g. openai/gpt-4o-mini
   vercel env add OCR_BACKEND production          # value: llm
   ```
5. Preview deploy: `vercel`. Open the preview URL logged in as yourself (previews are protected).
6. Run the checks below on the **preview**. Only then: `vercel --prod`.

**Verify (on the deployed URL)**
- `curl -s <url>/openapi.json | py -c "import json,sys;print(len(json.load(sys.stdin)['paths']))"` → the same count as locally (31 routes, minus any non-API).
- `curl -s -X POST <url>/api/advisor/chat -H "content-type: application/json" -d "{\"query\":\"chain of 6 pharmacies across Hyderabad\"}"` → `segment: multi`, `num_sites: 6`, `_source: llm`.
- B2 loop against `<url>` → the 12 reference verdicts.
- Download the deployment source list (`vercel inspect <url>`, or the Source tab in the dashboard) and confirm **`.env` is not in it**.
- Open the **production** URL in a private window → loads with no login page.
- First load after idle may take several seconds (cold start). Open it once before presenting.

**Don't:** deploy before B2–B4. A broken upload on a public URL is worse than none. Don't paste the API key into any file.

**Commit:** `chore(deploy): requirements, vercelignore, vercel.json`

---

### B8 · Partner portal: masking and propensity 🟡
**Files:** `app/partner_service.py`, `app/static/index.html`, `app/static/app.js`

**Steps**
1. Mask `contact_name` in `/api/partner/leads`: first name plus initial ("Gurpreet J."). Keep the full name only inside the generated WhatsApp pitch text if you must. Better: use "Namaste ji".
2. Propensity:
   - The code checks `'out of service area'`, which never occurs in the data. Use the real reason `'site not feasible for fibre'`. Either apply a penalty (`score = min(score, 40)`) **or** keep the score and make that lead's playbook a **5G AirFiber** pitch. Pick one and write it in the commit message.
   - Replace the fixed `>= 70` "high" threshold with the **80th percentile** of scores, so "high" means the top 20%.
3. Rename "AI Propensity" to "Propensity score" in the UI. It's hand-weighted rules, not a trained model.

**Verify**
- `curl -s localhost:8765/api/partner/leads?limit=3` → no full contact names.
- `curl -s localhost:8765/api/partner/stats` → `high_propensity_pct` between **18 and 22**.
- Top 5 leads: none with "Site not feasible for fibre" (if you chose the penalty), or each has an AirFiber pitch (if you chose the pitch).
- Note the new high-propensity count, ARR and commission numbers. B9 needs them.

**Commit:** `fix(partner): mask contacts, top-20% propensity, handle site-not-feasible`

---

### B9 · Documents agree with the deck 🟡
**Files:** `PLAN.md`, `ROADMAP.md`, `README.md`, `DEMO_SCRIPT.md`, `DPDP_COMPLIANCE_NOTE.md`

**Steps**
1. `PLAN.md` line ~123 (slide list) and §5 KPI table: replace 24.5% / ₹2,800 / < 48 hours / < 0.3 calls / NPS 8.5+ with the **deck KPIs** from Part A. Make the slide list match the real deck order: Cover, Problem, Segments & bundles, Journey, Architecture & privacy, Competition, Impact.
2. `ROADMAP.md`:
   - "✅ PRODUCTION READY" → "Prototype v1.0 · demo-ready".
   - "28 REST endpoints" (lines ~125 and ~182) → the real count from `grep -c "^@app\." app/main.py`.
   - Test counts → the real count after B1/B2 (`py -m pytest -q`).
   - Partner numbers → the new values from B8.
   - Phase 3: say "LLM extraction (OpenRouter) with rule-based fallback; rules engine sets all prices".
3. `README.md`: add a "Run locally" block (`py -m pip install -r requirements.txt`, set `OPENROUTER_API_KEY` in `.env`, `py run.py`) and the production URL after B7.
4. `DEMO_SCRIPT.md`: update scene 2 (chat with the LLM), scene 3 (real upload), and the partner numbers from B8.
5. `DPDP_COMPLIANCE_NOTE.md`: mention that uploaded images go to the LLM provider for OCR in the cloud (B4). That's a disclosure the DPDP purpose clause expects. Name the provider and that only OCR text is kept.

**Verify:** each command must print **nothing**:
```bash
grep -n "24\.5%\|₹2,800\|< *48 hours\|< 0\.3\|8\.5+\|PRODUCTION READY\|28 REST\|1,420\|₹4\.26\|out of service area" PLAN.md ROADMAP.md README.md DEMO_SCRIPT.md
grep -n "AI Propensity" app/static/index.html app/static/app.js
```

**Commit:** `docs: align PLAN/ROADMAP/README/DEMO/DPDP with deck, API and deployment`

---

### B10 · Browser smoke test 🟠
**Why:** two UI breakages this week came from renamed API fields and failed silently. A browser test catches that class of bug.

**Files:** new `scripts/ui_smoke.py` (Playwright for Python is already installed). It's a script, not part of pytest, because it needs a running server and a browser.

**Steps.** The script takes a base URL (`py scripts/ui_smoke.py http://localhost:8765` or the prod URL) and:
1. Collects console errors and fails on any (ignore `favicon.ico` 404).
2. For each scenario `kirana_no_gst, clinic_pro, multi_store, small_mfg`: calls `loadScenario`, waits, and asserts `#rec-price` text equals `#bill-monthly-total` text, ignoring whitespace and "/mo".
3. KYC: for every K01–K12 option, selects it, runs verification, and asserts `#kyc-verdict-title` starts with VERIFIED for the PASS list and REJECTED for the REJECT list.
4. Uploads the 4 real K07 PNGs through the file input (`set_input_files`) and asserts REJECTED with "mismatch" in the text.
5. Places an order for K02 and asserts the tracker view is active and shows an order ID matching `VS-2026-`.
6. Partner tab: asserts `#ptnr-salvageable` equals the API's `high_propensity_count` and that the leads table has ≥ 1 row.
7. Asserts the page text contains no `undefined` or `NaN`.
8. Prints PASS/FAIL per check and exits non-zero on any failure.

**Verify:** `py scripts/ui_smoke.py http://localhost:8765` → all PASS. Then break something on purpose (rename `high_propensity_count` in `app.js`) → the script must FAIL. Revert.

**Commit:** `test: Playwright UI smoke script for full journey`

---

### B11 · Demo readiness 🟠
1. **Final gate:** run in order and keep the output:
   - `py -m pytest -q` → all pass.
   - `py scripts/eval_advisor_llm.py` → ≥ 17/18.
   - `py scripts/ui_smoke.py <prod-url>` → all PASS.
   - B2 loop against `<prod-url>` → 12/12.
2. **Judge sheet:** one page listing the 18 advisor messages and the 12 KYC applicants with expected results, to run live if asked.
3. **Record the 3-minute video** from `DEMO_SCRIPT.md` on the **production URL**. Show one Hindi message and one real upload (K07 → name mismatch).
4. **Backups:** the video file, plus the local version (`py run.py`) on a second laptop, which works offline because the vendor files are local and Windows OCR runs. The advisor falls back to rules offline.
5. **Before presenting:** open the prod URL once (warm the cold start), and run one advisor message and one sample KYC.
6. **Q&A answers, written down:**
   - Registries are mock CSVs from the case pack.
   - OCR is Windows OCR locally and the LLM's vision model in the cloud.
   - DigiLocker and e-sign are planned, not built.
   - The LLM never sets prices; the rules engine does.
   - The propensity score is weighted rules, not a trained model.

---

## Part C · Final checklist (all must be ✅ before sending the link)

- [ ] B0 committed, `.env` not in git history
- [ ] `py -m pytest -q`: all pass, offline, < 20 s, same result twice
- [ ] LLM eval ≥ 17/18
- [ ] Upload loop: 12/12 reference verdicts, locally **and** on prod
- [ ] Path-traversal upload creates no file outside temp; `.exe` → 400; 6 MB → 413
- [ ] No `alert(` in `app.js`; tracker survives a server restart
- [ ] `.env` not in the Vercel deployment source
- [ ] Prod URL opens in a private window without login
- [ ] `ui_smoke.py <prod-url>`: all PASS
- [ ] B9 grep commands print nothing
- [ ] Video recorded on the prod URL

# VyaparSetu · Fix Plan (from the 7 Nov audit)

Goal: a prototype that holds up when Airtel judges run their own KYC answer key and 15 advisor scenarios live, and documents that agree with each other and with the deck.

**Deadlines**
- **8 Nov, 11:59 PM IST:** 7-slide PPT + PDF on Unstop (P0 only).
- **Virtual presentation (date TBC):** working prototype + 3-minute demo video (P1 must be done, P2 should be).

**Priority key**
- **P0:** blocks tomorrow's submission.
- **P1:** a judge will see it fail in the live demo.
- **P2:** inconsistency or overclaim a judge could catch by reading the repo.
- **P3:** demo preparation.

---

## P0 · Before submitting (today, ~1 hour)

| # | Task | Files | Done when |
|---|---|---|---|
| 0.1 | Slide 2: replace "75% of drops are process friction" with **~49% (2,290 leads)**. Count only reasons a self-serve journey removes: unreachable, no time for visit, visit not scheduled, quote too complex, quote too slow, paperwork (4 reasons). | `deck/index.html` | Slide 2 says 49%; the number is recomputed from `smb_leads.csv`, not typed |
| 0.2 | Slide 3 bundle prices vs app (clinic ₹3,517 vs ₹3,097, multi-site ₹8,985 vs ₹11,188, factory ₹12,541 vs ₹11,243). **Decide:** either add "example setup; the advisor sizes it to the business" under the prices, or change the advisor bundles to match (P1 1.4). | `deck/index.html` | No unexplained price gap between deck and app |
| 0.3 | Rebuild deck and check every slide in the PowerPoint export. | `scripts/build_svg_deck.py` | New PPTX + PDF, 7 slides, nothing clipped |
| 0.4 | Commit the partner-screen fix (live stats instead of hardcoded 1,420 / ₹4.26 Cr; label 12% → 15%). | `app/static/app.js`, `app/static/index.html` | Pushed; partner tab shows API numbers |
| 0.5 | Upload `Hacker_247_ABVIIITMGwalior.pptx` + `.pdf` on Unstop. | — | Unstop shows the submission |

---

## P1 · Make the prototype correct (before the virtual round)

Order matters: 1.1 and 1.2 are what judges test directly.

### 1.1 Smart KYC that actually reads the documents (~4 h)
**Problem:** the engine uses hardcoded names and verdicts, searches the registry by name instead of by the GSTIN on the certificate, never checks the Udyam registry, and passes any signatory ID. It misses **K06** (GSTIN on the certificate doesn't exist in the registry) and **K07** (legal name on the certificate doesn't match the registry). Its "100% agreement" is measured against its own labels.

**Fix (`app/kyc_engine.py`, `app/registry_service.py`):**
1. Parse fields from each document's OCR text: GSTIN, legal and trade name, address and PIN (GST certificate); Udyam number, enterprise name, state (Udyam); name, business, designation, valid-till date (signatory ID); name, PIN, bill date (address proof).
2. Normalise common OCR confusions (I/l→1, O→0 in digit positions) and validate the **GSTIN checksum**. A valid checksum that's missing from the registry means a fake GSTIN, not an OCR slip.
3. Look up the GSTIN from the certificate. Not found → REJECT. Cancelled or suspended → REJECT.
4. Look up the Udyam number in the Udyam registry; check name and state.
5. Cross-check the business name across GST certificate, registry, Udyam, signatory ID and bill (normalised, fuzzy ≥ 0.9). Mismatch → REJECT.
6. Signatory ID expired as of 2026-07-15 → REJECT. Designation that doesn't fit the constitution (e.g. "Owner" of an LLP or Pvt Ltd) → WARNING only.
7. Keep: consent gate, missing-document check, unreadable-document check, 90-day bill rule.
8. Delete the hardcoded `ground_truth` names, verdicts and reasons from the engine. Build the summary from the failed checks.

**Tests (`tests/test_phase4_smart_kyc.py`):** expected verdicts live in the test file, labelled "team's own reading, not the official key". Assert K01, K04, K05, **K06**, **K07**, K11 = REJECT, each with the specific reason, and the other 6 = PASS. Add an assertion that no business name string appears in `kyc_engine.py`.

### 1.2 GenAI advisor: an LLM understands the owner, the rules engine decides (~4 h)
**Problem:** a keyword parser. 4 of 8 realistic messages were misread ("4 restaurants in bangalore", "beauty parlour hai", Marathi "medical store", "we have GST"), and the fallback recommends a kirana pack. The deck and case both say GenAI.

**Fix (`app/advisor_engine.py`, new `app/llm_client.py`, `app/main.py`):**
1. The LLM turns free text in any Indian language into a fixed JSON profile: business type, segment, staff, sites, city, tier, has_gstin, needs, language. Use tool/structured output and validate the result.
2. If a field is missing, ask one clarifying question instead of defaulting to kirana.
3. Bundle, prices and eligibility come **only** from the existing rules engine. The LLM never outputs a price.
4. The LLM writes the "why this bundle" text in the owner's language, using only the rules engine's output.
5. Fallback: no API key, timeout (5 s) or invalid JSON → current rule parser. The demo must never hang.
6. Cache by normalised message.

**UI (`app/static/`):** add a chat box to the advisor tab, keeping the form as "quick mode".

**Tests:** a 20-message set (English, Hindi, Hinglish, Marathi, Tamil, typos, the 4 current failures). Need ≥ 18/20 correct segment and 0 rule violations. Keep the 2,000-profile fuzz test (currently 0 violations).

**Decision needed:** LLM provider and API key (suggest Claude Haiku for speed and cost).

### 1.3 Document upload in KYC (~2 h)
**Problem:** the case asks for "document upload with extraction and validation". Today the app only reads text that was extracted once in advance.

**Fix:** an upload control per document type → OCR (the LLM's vision model if 1.2 lands, otherwise Windows OCR from `scripts/extract_kyc_data.py`) → the same 1.1 pipeline. K01–K12 stay as one-click samples.

**Done when:** uploading `K07_gst_certificate.png` with the other K07 files gives REJECT with the name-mismatch reason.

### 1.4 Small correctness fixes (~1.5 h)
| Fix | File | Done when |
|---|---|---|
| Install estimate always from the catalogue; ignore the client value (the API default of 3 days can promise a leased line in 3 days instead of 21) | `app/order_service.py`, `app/main.py` | Order with P05 → 21 days |
| Mask GSTIN, phone and contact name in the partner-leads API (DPDP) | `app/partner_service.py` | No full GSTIN in `/api/partner/leads` |
| Propensity: "Site not feasible for fibre" either gets a penalty or a 5G AirFiber win-back pitch; set "high" to the top ~20% instead of a fixed 70 | `app/partner_service.py` | Top-ranked lead is plausibly recoverable |
| Rename "AI propensity" to "propensity score" (it's hand-weighted rules) | UI, docs | — |
| If 0.2 chose "match the deck": align advisor bundles to slide 3 | `app/advisor_engine.py` | Same 4 prices in deck and app |

### 1.5 Stop frontend/backend drift from breaking the UI again (~1 h)
Both UI bugs this week came from renamed API fields, and the screen failed silently.
- Add `tests/test_ui_smoke.py` (Playwright). It loads the app, runs advisor → quote → KYC → order → tracker → partner, and fails on any console error, any visible "undefined", or advisor ≠ quote price.
- Run it with the pytest suite.

### 1.6 Demo works offline (~30 min)
Download Tailwind and the lucide icons into `app/static/vendor/`, and stop using the CDN.

---

## P2 · Make the documents agree (~2 h)

One rule: every number comes from `phase1_intelligence_report.json`, the live API, or the deck. Nothing is typed from memory.

| Fix | Files |
|---|---|
| KPIs → 7.4%→15%, ≤5 days, <0.5 calls, ≤₹7,500, churn <10%; NPS baseline **6.9** (not 4.8) | `PLAN.md` |
| Bundle prices → match the app (or deck, per 0.2) | `PLAN.md`, `ROADMAP.md` |
| Drop clusters → the counts in the report (2,102 / 1,113 / 605 / 539 / 273), plus the 49% "fixable" figure | `PLAN.md`, `ROADMAP.md` |
| Fix phase numbering (diagram vs table); remove "Ready for Prod" / "Architecture Ready" from unbuilt phases → "Planned" | `ROADMAP.md` |
| Partner numbers → live API values, 15% commission | `ROADMAP.md`, `DEMO_SCRIPT.md` |
| Phase 7: 29 endpoints, not 18 | `ROADMAP.md` |
| KYC claim → "6 of 12 rejected by our own reading", not "100% agreement" | `ROADMAP.md`, `README.md` |
| Savings → compare with each lead's stated current spend (`monthly_telecom_spend_inr`), or label the 1.40× as an assumption | `app/catalog_engine.py`, docs |
| Check the DPDP note matches what the code does (30-day purge, masking, consent ledger) | `DPDP_COMPLIANCE_NOTE.md` |

---

## P3 · Demo preparation (after P1)

1. **Our own judge sheet:** 15 advisor scenarios + all 12 KYC applicants with the expected result. Run it the morning of the presentation.
2. **Record the 3-minute video** from `DEMO_SCRIPT.md` (update scenes 2 and 3 for chat and upload). Show one Hindi message.
3. **Backup plan:** the recorded video plus the offline build (1.6) on a second laptop.
4. **Rehearse Q&A:** what is real and what is mocked (registries, OCR, DigiLocker, e-sign).

---

## Summary of effort

| Priority | Items | Estimate |
|---|---|---|
| P0 | 0.1–0.5 | ~1 h |
| P1 | 1.1–1.6 | ~13 h |
| P2 | doc alignment | ~2 h |
| P3 | demo prep | ~3 h |

## Decisions needed from the team
1. **0.2:** deck prices — add a note, or change the app to match?
2. **1.2:** LLM provider and API key for the advisor.
3. Date of the virtual round, to schedule P1–P3.

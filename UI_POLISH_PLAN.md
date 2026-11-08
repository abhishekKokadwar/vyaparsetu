# VyaparSetu: UI polish plan (8 Nov 2026)

Goal: a calm, premium, professional dashboard. One visual system across all five tabs, no fake data, no leaked test metadata.
Evidence below comes from an audit of the running app at 1440x800 and 375x740 (screenshots plus a style census per tab).


## STATUS (8 Nov, evening, measured, not estimated)

| Package | State | Evidence / what is left |
|---|---|---|
| WP1 Shared components and tokens | **Done** | Audit now fails on off-token button heights (only 36 compact or 44+) and corner radii (8 / 12 / pill). Nested cards 0 on every tab (was 27 / 13 / 3 / 1). Inputs uniform. |
| WP2 Quote tab | **Done** | Rows not cards, pinned bill, mobile total bar, GST-gated rows, Recommended badge, empty state, computed savings. |
| WP3 KYC tab | **Done** | 3-step flow, locked until consent, no pre-filled IDs, no verdict hints, specimens in a labelled section. |
| WP4 Tracker | **Partly** | Done: lookup, history, labelled sample, flat page. **Left:** two-column layout and the notification log. |
| WP5 Partner | **Partly** | Done: tie-break ranking, reasons, 40 rows, shared controls. **Left:** search, sort, detail drawer, feedback when "Assist" is clicked. Scores still cap at 98 (kept so the deck's 932 / 1.91 Cr stay true). |
| WP6 Shell | **Done** | Sidebar progress ticks, header button jumps to the next incomplete step, mobile bottom tab bar, language toggle relabelled "Advisor language", skeletons on partner table, drawer and message log. |
| WP7 QA gate | **Done** | `ui_audit.py` enforces tokens, contrast, sizes; `AUDIT_THEME=dark` audits dark mode; HTML tag-balance test; 114 tests. |

New features: voice input done, chat view done. **Not started:** D notification log, E Good/Better/Best, F metrics view, G printable quote, H upload progress.

---

## 1. What is wrong today (findings)

### 1.1 The five tabs do not look like one product
Only the Advisor was rebuilt. The other four still use the old styling.

| Property | Advisor (new) | Quote / KYC / Tracker / Partner (old) |
|---|---|---|
| Corner radius | 8 px controls | 4, 8, 12, 16 px mixed (Quote has 4 radii) |
| Input background | white | grey `#F8FAFC` (KYC) |
| Input font size | 16 px | 12 to 14 px (iOS zooms below 16) |
| Button heights | 44 px | 30, 36, 38, 44, 48 px (five sizes) |
| Primary button colour | navy | navy **and** near-black (`Run Smart Verification`, `Track`, chips) |
| Nested cards (card inside card) | 0 | Quote 27, KYC 13, Tracker 3 |
| Shadows | none | up to 17 per screen (Partner) |
| Body text | 14 to 16 px | Quote and Partner use 12 px for ~100 elements |

### 1.2 Fake or misleading content (credibility risks)
1. **KYC select shows the answer key.** Options read `[K07] Neelgiri Physio Clinic (UNKNOWN) - reason...`, and the code prints `expected_verdict` into the label. A judge sees test metadata in the product.
2. **KYC pre-fills a GSTIN and Udyam number** (`19EOGXH4115Y1ZL`, `UDYAM-WB-00-5053330`) that nobody entered. Same flaw we removed from the Advisor.
3. **Language toggle (EN / हिंदी) translates 5 strings.** It implies a Hindi app and delivers a Hindi title and one button. Either translate properly or relabel it.
4. **Partner propensity score has only 4 distinct values** (85, 90, 95, 98). The top 141 leads are all 98%, so the "ranking" is arbitrary. Needs a continuous score with visible reasons.
5. **Partner portal has no sign-in** and shows "1-Click Assist" buttons that do nothing visible.
6. **Quote tab opens with no business context.** Without an Advisor recommendation it shows 25 products and no hint what to pick.

### 1.3 Layout and flow problems
- **Quote:** category filter chips wrap into two rows; the price summary card floats with dead space above and below and does not stay in view; every product is a bordered card (long, heavy list).
- **KYC:** one very long form (consent, specimen picker, GSTIN, Udyam, date, upload, samples). The result panel is empty until you run something and shows two stacked empty states. "Step 1 of 3" is a label with no steps. Sample buttons are three different colours.
- **Tracker:** single wide column; the order summary, six stages and the technician card stack vertically and waste the right half at 1440 px.
- **Partner:** table is fine, but no search, no sort, no row detail, no empty state.
- **Global:** sidebar does not show progress (which steps are done); no loading skeletons (panels are blank for ~1 s); no toasts for actions such as "Order placed"; mobile has no bottom navigation (sub-nav scrolls sideways); desktop has a duplicate "Start KYC" button that skips the quote.

---

## 2. Design system (one page, applied everywhere)

| Token | Value |
|---|---|
| Primary | navy `#1E3A8A` (hover `#14285F`). **The only filled button colour.** |
| Secondary button | white, 1 px `#CBD5E1` border |
| Danger / success / warning | red `#B91C1C`, green `#047857`, amber `#B45309` (text plus icon, never colour alone) |
| Surface | white panels on `#EDF0F5` page, 1 px `#DCE2EC` border, **no shadows** (shadow only on overlays) |
| Radius | 8 px controls, 12 px panels, 999 px chips and badges. Nothing else. |
| Type scale | 12 meta, 14 secondary, 16 body and inputs, 20 section title, 24 page title |
| Controls | height 44 px everywhere (36 px only for table row actions on desktop) |
| Spacing | 4 / 8 / 12 / 16 / 24 grid |
| Structure rule | **One panel per screen region. Group with headings and dividers, not boxes. Lists are rows, not cards.** |
| Shared parts | `.btn-primary`, `.btn-secondary`, `.field`, `.chip`, `.seg` (segmented), `.badge`, `.panel`, `.row`, `.empty`, `.skeleton`, `.toast` |

Already built for the Advisor and reusable: `.field`, `.field-label`, `.btn-primary`, `.btn-secondary`, `.chip`, `.seg`, `.kpi-strip`, `.section-h`, `.eyebrow`.

---

## 3. Work packages (in build order)

Time is for one person. **P0 = must ship, P1 = should, P2 = if time.**

### WP1 · Shared components and tokens (P0, 40 min) · DONE
Add `.badge`, `.panel`, `.row`, `.empty`, `.skeleton`, `.toast` to `style.css`; delete the old per-tab button and input classes.
Done when: the census shows one input style, button heights only {44, 36}, radii only {8, 12, 999}.

### WP2 · Quote tab (P0, 45 min) · DONE
- Two columns: product list left, **sticky** price summary right (full height, pinned).
- Products become rows in one bordered list (checkbox, name, tag, price), not one card each. Setup fee as a second line in muted text.
- Category filter becomes one scrollable chip row (no wrap).
- "Requires GST" shown as an inline badge plus a reason when the item is disabled.
- Empty state when nothing is selected: "Pick a bundle from the Advisor or choose products."
- Show a "Recommended by Advisor" badge on items the Advisor chose.
Done when: zero nested cards, summary stays visible while the list scrolls.

### WP3 · KYC tab (P0, 60 min)
- Real three-step layout: **1 Consent, 2 Documents, 3 Result**, each with a done state; step 2 unlocks after consent.
- Remove pre-filled GSTIN/Udyam. Manual GSTIN/Udyam lookup moves into a "Check a number" disclosure.
- Upload drop zone is the main control. Demo specimens go under a clearly labelled **"Demo specimens (hackathon data)"** disclosure, one neutral chip style, **no expected verdict in any label**.
- Result panel: verdict banner, then a checklist (icon plus text per check), then the "Confirm & activate" button. Skeleton while verifying.
- One empty state, not two.
Done when: no `expected_verdict` text anywhere in the DOM before a run; inputs are 16 px.

### WP4 · Tracker (P0, 40 min)
- Summary strip (order, business, bundle, live date) across the top.
- Two columns: timeline left; right column holds technician card and **notification log** (the messages the system would send, from the existing endpoint).
- Keep the lookup, history and sample-order behaviour already built.
Done when: no vertical dead space at 1440 px; timeline and technician visible together.

### WP5 · Partner portal (P1, 45 min)
- Fix the score: add continuous tie-breakers (staff size, days since drop, bundle value) so scores spread; show the top 3 reasons per lead ("KYC complete", "21-day install delay", "high-value segment").
- Add search, sort, and a side drawer with lead detail plus a visible result when "Assist" is clicked (toast and status change).
- State clearly on the page that it is demo data; add a "Partner sign-in required in production" note.
Done when: top 25 leads show more than 4 distinct scores, each with reasons.

### WP6 · Global shell (P1, 60 min)
- Sidebar **progress**: check marks on completed steps (Advisor, Quote, KYC, Order).
- Mobile **bottom tab bar** (5 items) replacing the sideways sub-nav; keep skip link and focus rings.
- **Language toggle**: either translate nav, headings, buttons and empty states (about 40 strings, EN and HI) or rename it "Advisor language". Pick one.
- Loading skeletons for every async panel; toast for "Order placed", "Consent recorded", "Copied".
- Remove the duplicate header "Start KYC" (or make it jump to the first incomplete step).
Done when: no blank panel while loading; mobile has bottom navigation; toggle behaviour matches its label.

### WP7 · QA gate (P0, 30 min, runs after each package)
Extend `scripts/ui_audit.py` so it **fails** on: button heights outside {44, 36}; radii outside {8, 12, 999}; inputs under 16 px; more than 2 nested cards on any tab; any text under 12 px; contrast under 4.5:1; horizontal scroll at 375 px. Then run `ui_smoke.py` (desktop and mobile), `pytest`, and look at screenshots of all five tabs.

---

## 4. What to add (new features), ranked

| # | Feature | Brief link | Effort | Impact |
|---|---|---|---|---|
| A | **Journey progress in the sidebar** (in WP6) | UX polish | incl. | High, cheap |
| B | **Hindi voice input** on the Advisor (browser speech recognition, `hi-IN`) | stretch goal: voice front end | 45 min | High |
| C | **WhatsApp-style chat view** of the Advisor | stretch goal: WhatsApp front end | 1-1.5 h | High |
| D | **Tracker notification log** (in WP4) | "3 status chases per customer" | incl. | Medium |
| E | **Good / Better / Best** options on the recommendation (3 bundles at 3 prices) | key question 1: bundle and price fit | 1 h | High, shows judgement |
| F | **Success metrics view**: lead-to-activation, time to activate, cost per acquisition, 6-month churn, with targets, computed from `smb_leads.csv` | key question 5 | 1.5 h | Medium |
| G | **Printable quote** (print stylesheet and "Download quote") | quote and checkout | 30 min | Medium |
| H | **Specimen upload progress** (per-document tick as each is read) | smart KYC | 30 min | Medium |

Do not add tonight: Clerk or any login, real DigiLocker, e-sign, a third language.

---

## 5. Cut lines (be strict)

- **Tier 1, must have before the video:** WP1, WP2, WP3, WP4, WP7, plus content fixes 1.2 items 1 to 3. About 3.5 h.
- **Tier 2, strong upgrade:** WP5, WP6, then features B and C. About 3.5 h.
- **Tier 3, only if time remains:** E, F, G, H.
- **Freeze rule:** stop building at least 3 hours before the deadline, run the full check, then record the video and submit.

---

## 6. Known risks to manage

- Gemini free-tier quota is shared with production. Test on the specimen path and avoid cloud OCR loops.
- Production aliases do not follow deploys automatically (`vyaparsetu-airtel.vercel.app` does; the others need `vercel alias set`).
- Every change must pass: `ui_audit.py`, `ui_smoke.py` (desktop and mobile), `pytest`, then a production spot check.

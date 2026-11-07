# VyaparSetu · UI/UX Improvement Guide

**For:** whoever is implementing the UI fixes (you).
**Scope:** `app/static/index.html`, `app/static/app.js`, `app/static/style.css`, plus 1 small backend fix.
**Method:** Measured with `scripts/ui_audit.py` (Playwright, 1440 px desktop + 375 px phone) and screenshots of all 5 tabs, then checked against the *ui-ux-pro-max* rule set (accessibility → touch → layout → type/colour → feedback → navigation).

---

## 0. How to use this guide

1. Work **in order**: §1 Foundations first (everything else uses its tokens), then P0 → P1 → P2.
2. Each item has **Why / Where / Do / Done when / Don't**. Do not move on until *Done when* passes.
3. After each item, run:
   ```
   py -m uvicorn app.main:app --port 8000        (terminal 1)
   py scripts/ui_audit.py http://127.0.0.1:8000  (terminal 2)
   py scripts/ui_smoke.py http://127.0.0.1:8000  (must stay 8/8)
   py -m pytest -q                               (must stay all-pass)
   ```
   `ui_audit.py` prints the remaining misses and exits 1 until every hard target is met.
4. Commit after each item (`git commit -m "ui(G5): ..."`), so any regression is easy to find.
5. **Do not change** element IDs that `app.js`, `tests/test_ui_smoke.py` or `scripts/ui_smoke.py` use (`#rec-price`, `#bill-monthly-total`, `#kyc-verdict-desc`, `#kyc-applicant-select`, `#btn-place-order`, `#tracker-order-id`, `#ptnr-*`, `#tab-btn-*`, `#view-*`). Add new IDs; don't rename old ones.

### Baseline (measured, current `main`)

| Check | Desktop | Phone 375 px | Target |
|---|---|---|---|
| Horizontal scroll | none | **every tab** (page is 448–552 px wide) | none |
| Text under 12 px (Quote tab) | **146** | **146** | 0 |
| Low-contrast text (Quote tab) | **87** | **87** | 0 |
| Low-contrast text (other tabs) | 6–19 | 6–19 | 0 |
| Tap targets under 44 px | 7–18 | 10–23 | 0 on phone |
| Inputs under 16 px (iOS zooms) | 6–7 | 6–7 | 0 on phone |
| `:focus-visible` styles | none | none | present |
| ARIA tab roles | none | none | `role=tablist/tab/tabpanel` |
| Phone menu highlights current tab | — | **stuck on "Advisor"** | follows tab |
| Emoji used as icons | 1 in HTML, 5 in JS, 56 in advisor text | same | 0 |
| AI chat visible in UI | **no** (`/api/advisor/chat` never called) | no | yes |

---

## 1. Foundations (do first, ~30 min)

The `ui-ux-pro-max` design-system query for *"B2B telecom onboarding, MSME India, trustworthy"* gave: **flat, touch-first, navy + one accent, Plus Jakarta Sans, status colours green/amber/red, no decorative motion**. You already use Plus Jakarta Sans and a slate/navy base, so **keep the look**; what's missing is a *rule* for each colour and size. Add these tokens and use only them.

### 1.1 Colour roles

Airtel red stays the brand, but right now it means four things at once: brand, primary button, "in progress" and "rejected". Give each meaning its own colour:

| Role | Token | Hex | Use for | Never use for |
|---|---|---|---|---|
| Brand / primary action | `--brand` | `#E40000` | Logo, **one** primary button per screen | status, small text on tinted bg |
| Brand hover / red text on tint | `--brand-strong` | `#B80000` | hover, active nav text on `#FFF1F1` | — |
| Ink (headings) | `--ink` | `#0F172A` (slate-900) | headings, key numbers | — |
| Body text | `--text` | `#334155` (slate-700) | paragraphs, table cells | — |
| Secondary text | `--muted` | `#64748B` (slate-500) | captions on **white or slate-50 only** | text on slate-100 or tinted cards (use slate-600) |
| Info / in progress / focus | `--info` | `#0369A1` (sky-700) | "In progress", focus ring, links | errors |
| Success | `--ok` | `#047857` (emerald-700) | PASS, completed, savings | — |
| Warning | `--warn` | `#B45309` (amber-700) | consent box, near-expiry, rule hints | — |
| Error | `--err` | `#B91C1C` (red-700) | REJECT, failed checks — **always with an icon + word** | primary buttons |
| Lines | `--line` | `#E2E8F0` | borders, dividers | text |

**Where:** add to the top of `app/static/style.css`:

```css
:root {
  --brand: #E40000; --brand-strong: #B80000; --brand-soft: #FFF1F1;
  --ink: #0F172A; --text: #334155; --muted: #64748B; --line: #E2E8F0;
  --info: #0369A1; --info-soft: #F0F9FF;
  --ok: #047857;   --ok-soft: #ECFDF5;
  --warn: #B45309; --warn-soft: #FFFBEB;
  --err: #B91C1C;  --err-soft: #FEF2F2;
}
html { touch-action: manipulation; }           /* removes 300 ms tap delay */
.tabular { font-variant-numeric: tabular-nums; } /* prices, PINs, dates */
```

and extend the Tailwind config in `index.html` (lines 12–30) so you can write `text-info`, `bg-ok-soft`, etc.:

```js
colors: {
  airtel: { red: '#E40000', darkred: '#B80000', lightred: '#FFF1F1', dark: '#111827', gray: '#4B5563', border: '#E5E7EB' },
  info: { DEFAULT: '#0369A1', soft: '#F0F9FF' },
  ok:   { DEFAULT: '#047857', soft: '#ECFDF5' },
  warn: { DEFAULT: '#B45309', soft: '#FFFBEB' },
  err:  { DEFAULT: '#B91C1C', soft: '#FEF2F2' }
},
```

### 1.2 Type scale (minimum 12 px)

| Role | Tailwind | Size | Where |
|---|---|---|---|
| Caption / badge / meta | `text-xs` | 12 px | lead IDs, timestamps, badges |
| Body, table cells, buttons | `text-sm` | 14 px | descriptions, table rows, all buttons |
| Inputs on phone | `text-base md:text-sm` | 16 → 14 px | every `input`, `select`, `textarea` |
| Card title | `text-lg font-bold` | 18 px | card headers |
| Page/section title | `text-xl font-bold` | 20 px | tab titles |
| Key number | `text-2xl font-extrabold tabular` | 24 px | prices, KPIs |

**Rules:** `text-[10px]` and `text-[11px]` are banned (there are 14 + 25 in `index.html` and 20 + 6 in `app.js`). Sentences use `leading-relaxed`. Prices, PINs, order IDs and dates get `tabular`.

### 1.3 Spacing, radius, elevation

- Spacing: only 4/8 px steps (Tailwind `1, 2, 3, 4, 6, 8`). Card padding `p-5 sm:p-6`; gap between cards `gap-6`.
- Radius: cards `rounded-2xl` (16 px), controls `rounded-xl` (12 px), badges `rounded-full`. Don't mix `rounded-lg` and `rounded-xl` for buttons.
- Elevation: cards `border + shadow-sm` only. Remove the coloured shadows (`shadow-red-200`), which read as glow, not depth.

**Done when:** tokens exist in `style.css`, the Tailwind config has `info/ok/warn/err`, and nothing else has changed yet (the audit numbers are the same).

---

## 2. P0: fix before the demo (correctness and honesty)

### G1 · Put the real AI advisor on screen

**Why:** The tab is called "GenAI Advisor", but the UI only has a form. `/api/advisor/chat` (multilingual LLM, Gemini) is never called, so judges never see the AI.

**Prerequisite (backend, 10 min):** In this audit, `"मेरी जयपुर में किराना दुकान है, 2 लोग, GST नहीं है"` came back as `num_sites: 2, segment: multi, has_gstin: true`. That's wrong: "2 लोग" means 2 *people*, and "GST नहीं है" means *no* GST.
1. In `app/llm_client.py` `SYSTEM_EXTRACTION_PROMPT`, add two rules under `Rules:`:
   ```
   - People words (लोग, कर्मचारी, staff, workers, employees, helpers, lawyers) -> employee_count, NEVER num_sites.
   - Negations (नहीं, nahi, no, without, not registered) next to GST -> has_gstin false.
   ```
2. Add that exact sentence as test case 19 in `scripts/eval_advisor_llm.py`, expecting `segment: micro, employee_count: 2, num_sites: 1, has_gstin: False`.
3. **Done when:** `py scripts/eval_advisor_llm.py` passes 18/19 or better with `llm` as the source.

**Where (UI):** `index.html`, inside the left advisor card, directly **above** `<form id="advisor-form" …>` (line 140).

**Do: HTML**

```html
<!-- G1: Talk to the AI advisor -->
<div class="mb-5">
  <label for="adv-chat-input" class="block text-sm font-semibold text-slate-900 mb-1">
    Tell us about your business, in your own words
  </label>
  <p id="adv-chat-help" class="text-xs text-slate-500 mb-2">
    English, हिंदी, मराठी, தமிழ், ਪੰਜਾਬੀ… e.g. “मेरी जयपुर में किराना दुकान है, 2 लोग, GST नहीं है”
  </p>
  <div class="flex gap-2">
    <textarea id="adv-chat-input" rows="2" aria-describedby="adv-chat-help"
      class="flex-1 min-w-0 bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-base md:text-sm focus:bg-white outline-none"
      onkeydown="if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();sendAdvisorChat();}"></textarea>
    <button id="adv-chat-send" type="button" onclick="sendAdvisorChat()" aria-label="Ask the AI advisor"
      class="shrink-0 min-h-[44px] min-w-[44px] px-4 bg-airtel-red hover:bg-airtel-darkred text-white rounded-xl flex items-center justify-center gap-2 text-sm font-semibold">
      <i data-lucide="send" class="w-4 h-4" aria-hidden="true"></i><span class="hidden sm:inline">Ask</span>
    </button>
  </div>
  <div id="adv-chat-understood" class="mt-3 hidden" aria-live="polite"></div>
  <div id="adv-chat-clarify" class="mt-2 hidden"></div>
  <div class="flex items-center gap-3 my-5 text-xs text-slate-500">
    <span class="flex-1 border-t border-slate-200"></span>or answer 4 quick questions<span class="flex-1 border-t border-slate-200"></span>
  </div>
</div>
```

**Do: JS** (add to `app.js`; `escapeHtml` and `setBusy` are also used by later items):

```js
// Shared helpers
function escapeHtml(s) {
  return String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}
function setBusy(btn, busy, busyText = 'Working…') {
  if (!btn) return;
  btn.disabled = busy;
  btn.setAttribute('aria-busy', String(busy));
  if (busy) {
    btn.dataset.label = btn.innerHTML;
    btn.innerHTML = `<span class="inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" aria-hidden="true"></span><span>${busyText}</span>`;
  } else if (btn.dataset.label) {
    btn.innerHTML = btn.dataset.label;
    if (window.lucide) lucide.createIcons();
  }
}

const SEGMENT_TO_BIZ = {
  micro: 'Kirana & Retail Store', prof: 'Clinic & Healthcare',
  multi: 'Restaurant & Food Chain', mfg: 'Small Manufacturing & Workshop'
};
let chatProfile = null;

async function sendAdvisorChat(text) {
  const input = document.getElementById('adv-chat-input');
  const query = (text ?? input.value).trim();
  if (!query) { input.focus(); return; }
  const btn = document.getElementById('adv-chat-send');
  setBusy(btn, true, 'Thinking…');
  try {
    const res = await fetch('/api/advisor/chat', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, current_profile: chatProfile })
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    chatProfile = data.profile;
    currentRecommendation = data.recommendation;
    renderAdvisorRecommendation(data.recommendation);
    renderUnderstood(data.profile);
    renderClarifications(data.clarifications || []);
    syncFormFromProfile(data.profile);
  } catch (e) {
    const box = document.getElementById('adv-chat-understood');
    box.classList.remove('hidden');
    box.innerHTML = `<p role="alert" class="text-sm text-err">Couldn't reach the advisor. Try again, or use the form below.</p>`;
  } finally {
    setBusy(btn, false);
  }
}

function renderUnderstood(p) {
  const chips = [
    p.business_type,
    p.employee_count && `${p.employee_count} staff`,
    p.num_sites && `${p.num_sites} site${p.num_sites > 1 ? 's' : ''}`,
    p.city,
    p.has_gstin === true ? 'GST registered' : p.has_gstin === false ? 'No GST' : null
  ].filter(Boolean);
  const src = p._source === 'llm'
    ? `<span class="inline-flex items-center gap-1 text-xs font-semibold text-info bg-info-soft px-2 py-0.5 rounded-full"><i data-lucide="sparkles" class="w-3 h-3" aria-hidden="true"></i>Understood by AI</span>`
    : `<span class="text-xs font-semibold text-slate-600 bg-slate-100 px-2 py-0.5 rounded-full">Rule-based (AI unavailable)</span>`;
  const box = document.getElementById('adv-chat-understood');
  box.classList.remove('hidden');
  box.innerHTML = `<div class="flex flex-wrap items-center gap-1.5">${src}${chips.map(c =>
    `<span class="text-xs text-slate-700 bg-white border border-slate-200 px-2 py-0.5 rounded-full">${escapeHtml(c)}</span>`).join('')}</div>`;
  if (window.lucide) lucide.createIcons();
}

function renderClarifications(list) {
  const box = document.getElementById('adv-chat-clarify');
  if (!list.length) { box.classList.add('hidden'); box.innerHTML = ''; return; }
  const q = list[0];   // one question at a time
  const question = currentLanguage === 'hi' ? (q.question_hi || q.question) : (q.question_en || q.question);
  box.classList.remove('hidden');
  box.innerHTML = `<p class="text-sm text-slate-800 mb-2">${escapeHtml(question)}</p>
    <div class="flex flex-wrap gap-2">${(q.options || []).map(o =>
      `<button type="button" class="min-h-[44px] px-3 text-sm border border-slate-300 rounded-xl hover:border-airtel-red"
         onclick="sendAdvisorChat(${escapeHtml(JSON.stringify(o))})">${escapeHtml(o)}</button>`).join('')}</div>`;
}

function syncFormFromProfile(p) {
  if (SEGMENT_TO_BIZ[p.segment]) document.getElementById('adv-biz-type').value = SEGMENT_TO_BIZ[p.segment];
  if (p.city_tier) document.getElementById('adv-city-tier').value = String(p.city_tier);
  if (p.city) document.getElementById('adv-city-name').value = p.city;
  if (p.employee_count) document.getElementById('adv-employees').value = p.employee_count;
  if (p.num_sites) document.getElementById('adv-sites').value = p.num_sites;
  if (p.has_gstin != null)
    document.querySelector(`input[name="adv-has-gst"][value="${p.has_gstin ? 'yes' : 'no'}"]`).checked = true;
}
```

> If `submitAdvisorProfile()` does anything after `renderAdvisorRecommendation(data)` (for example, syncing the Quote tab), do the same after it in `sendAdvisorChat`, so the Quote tab and the advisor price stay equal. `ui_smoke.py` checks this.

**Done when:**
- Typing the Hindi kirana sentence → *Understood by AI · Grocery/Kirana · 2 staff · 1 site · Jaipur · No GST*; the result card shows a micro bundle; the form fields update.
- Clicking a clarification option sends it and updates the result.
- With `VYAPAR_LLM_DISABLED=1` the chip says *Rule-based* and it still works.
- `ui_smoke.py` stays 8/8.

**Don't:** insert `p.business_type` or LLM text with `innerHTML` without `escapeHtml` (LLM output is untrusted). Don't remove the form; it's the fallback and the judge scenarios use it.

---

### G2 · DPDP consent must be opt-in, not pre-ticked

**Why:** DPDP Act 2023 requires a *clear affirmative action*. A pre-ticked box (`index.html` line 410, `checked`) is the opposite, and a judge who knows DPDP will spot it. Also, `loadDocSpecimen()` (`app.js` ~line 393) **hard-codes `consent_granted: true`**, and `handleFileUpload` defaults to `?? true`.

**Do:**
1. `index.html` line 410: remove `checked`; add `aria-describedby="dpdp-consent-help"`.
2. Under the consent paragraph, add the hint:
   ```html
   <p id="dpdp-consent-help" class="hidden mt-2 text-xs font-semibold text-err" role="alert">
     Tick the consent box to continue. We can't verify documents without it.
   </p>
   ```
3. Add the `data-needs-consent` attribute to these buttons: *Run Smart Verification* (line 436), *Verify GST* (450), *Verify Udyam* (460), the 4 sample buttons (487–490), *Extract OCR & Verify* (526), and the upload `<label for="kyc-file-upload-input">` (496).
4. In `app.js` add one gate and call it at the **top** of `runSmartKYCVerification`, `uploadAndVerifyKYCDocuments`, `handleFileUpload`, `loadDocSpecimen`, `lookupGSTINManually` and `lookupUdyamManually`:
   ```js
   function requireConsent() {
     const chk = document.getElementById('dpdp-consent-chk');
     const help = document.getElementById('dpdp-consent-help');
     if (chk.checked) { help.classList.add('hidden'); return true; }
     help.classList.remove('hidden');
     chk.focus();
     return false;
   }
   // usage:  if (!requireConsent()) return;
   ```
5. Replace `consent_granted: true` in `loadDocSpecimen` and `?? true` in `handleFileUpload` with `document.getElementById('dpdp-consent-chk').checked`.
6. Make consent the visual **step 1** of the KYC card: put a small "Step 1 of 3" label above the consent box. When it's ticked, change the box to `bg-ok-soft border-emerald-200` with a check icon.
7. In `onApplicantSelected` (it runs verification when the dropdown changes), apply the same gate. If consent isn't ticked, show the hint and don't call the API.

**Done when:** Fresh page load → KYC tab → box unticked → any verify/upload/sample button shows the red hint and focuses the checkbox, with **no** network request (check the DevTools Network tab). Tick → everything works as before.
**Update the smoke tests:** `scripts/ui_smoke.py` and `tests/test_ui_smoke.py` must tick `#dpdp-consent-chk` before step 3. Add `page.check('#dpdp-consent-chk')`.

**Don't:** auto-tick it on page load "for the demo". Ticking it on stage *is* the demo of DPDP.

---

### G3 · The upload box must tell the truth, and drag-and-drop must work

**Why:** The box says *"PNG, JPG, PDF, TXT supported (Max 10MB)"* and *"Drag & Drop"*. The server rejects PDF (400), caps files at 4 MB and 8 files, and there is **no** drop handler, so dropping a file makes the browser open it and leave the app.

**Do:**
1. `index.html` line 495: `accept=".png,.jpg,.jpeg,.webp,.txt"`.
2. Line 499: `PNG, JPG or WEBP · up to 4 MB each · up to 8 files` (class `text-xs text-slate-500`).
3. Line 481: delete the `Drag & Drop / Select Files` chip (the box itself says it).
4. Give the dashed box an id and drop handling. Line 494: add `id="kyc-dropzone"`. Then in `app.js` (inside `DOMContentLoaded`):
   ```js
   const dz = document.getElementById('kyc-dropzone');
   const on = e => { e.preventDefault(); dz.classList.add('ring-2', 'ring-info', 'bg-info-soft'); };
   const off = e => { e.preventDefault(); dz.classList.remove('ring-2', 'ring-info', 'bg-info-soft'); };
   ['dragenter', 'dragover'].forEach(t => dz.addEventListener(t, on));
   ['dragleave', 'drop'].forEach(t => dz.addEventListener(t, off));
   dz.addEventListener('drop', e => handleFileUpload({ target: { files: e.dataTransfer.files } }));
   ```
5. Validate files in the browser **before** uploading (top of `handleFileUpload`, after `requireConsent()`):
   ```js
   const OK_EXT = ['png', 'jpg', 'jpeg', 'webp', 'txt'];
   const problems = [];
   if (files.length > 8) problems.push(`You chose ${files.length} files. The maximum is 8.`);
   for (const f of files) {
     const ext = f.name.split('.').pop().toLowerCase();
     if (!OK_EXT.includes(ext)) problems.push(`${f.name}: ${ext.toUpperCase()} isn't supported. Use PNG, JPG or WEBP.`);
     else if (f.size > 4 * 1024 * 1024) problems.push(`${f.name}: ${(f.size / 1048576).toFixed(1)} MB is over the 4 MB limit.`);
   }
   if (problems.length) { showUploadErrors(problems); return; }
   ```
   `showUploadErrors` renders a `role="alert"` list under the drop zone in `text-sm text-err`.
6. While OCR runs, show the time honestly: *"Reading 4 documents… this takes about 10–20 seconds"*. Cloud OCR is about 3–5 s per image. Replace `📄` with `<i data-lucide="file-text" class="w-4 h-4" aria-hidden="true"></i>` and the `animate-pulse` red text with a spinner in `text-info`.
7. After the response, show **what each file was recognised as**, from `extracted_snippets[*].assigned_type`, plus any `warnings`:
   `GST certificate ✓ · Udyam ✓ · Address proof ✓ · Signatory ID ✓` or `scan3.png · not recognised ⚠`. Use lucide `check-circle-2` (`text-ok`) and `alert-triangle` (`text-warn`), each with words, not colour alone.
8. Map server errors to plain language: 400 → the server's `detail` message; 413 → "One file is over 4 MB."; network/other → "Upload failed. Check your connection and try again." Show these in the same alert area.

**Done when:** Dropping the 4 K07 PNGs onto the box runs verification and shows *Legal entity mismatch*. Dropping a `.pdf` shows the PDF message with no network call. The box text matches the server limits.

---

### G4 · Remove claims you can't show

**Why:** The *"256-bit Encrypted"* badge (`index.html` lines 401–404) isn't something the app does or can prove. One unprovable claim makes judges doubt the true ones.

**Do:** Replace it with what the code really does:
```html
<span class="bg-ok-soft text-ok font-semibold text-xs px-2.5 py-1 rounded-full border border-emerald-200 flex items-center gap-1">
  <i data-lucide="eye-off" class="w-3.5 h-3.5" aria-hidden="true"></i><span>IDs masked · purged in 30 days</span>
</span>
```
Also review the footer line *"Zero Paperwork · Instant Activation"*. Activation takes 3–21 days in your own tracker, so change it to *"Paperless KYC · Live order tracking"*.

**Done when:** every badge or claim on screen maps to a feature you can demo.

---

### G5 · No sideways scrolling on phones

**Why:** At 375 px every tab is 448–552 px wide, so the page wobbles sideways. The culprits are the announcement bar (line 38), the header CTA (line 104), the brand subtitle (line 69) and the Quote filter chips (lines 323–330).

**Do:**
1. **Announcement bar** (line 38): on phones show only the badge and the GitHub link.
   - Line 41 text: add `hidden md:inline`.
   - Line 44 "Team" span: `hidden sm:inline`.
   - Line 45 "SVG Diagrams" link: `hidden sm:flex`.
   - Container: add `gap-3`, and change the `GitHub Repo` link colour to `text-red-300 hover:text-white`, which also fixes its contrast (3.63 → OK).
2. **Header**:
   - Line 69 subtitle: `hidden sm:block`.
   - Line 104 "Instant Checkout" button: `hidden sm:flex`. On phones, the per-step "Next" CTA (G16) replaces it.
   - Line 67 Devanagari pill: `hidden sm:inline` (keeps the logo row to one line).
3. **Quote card header** (line 318): `flex flex-col gap-3 sm:flex-row sm:justify-between sm:items-center`; filter row (line 323): `flex flex-wrap gap-1.5` (remove `space-x-1`).
4. **Tracker search** (line 578): add `min-w-0 flex-1` to the input.
5. Add a global safety net in `style.css`: `img, svg, table { max-width: 100%; }`. Keep `overflow-x-auto` **only** around the partner table (G21 replaces it on phones anyway).

**Done when:** `ui_audit.py` reports no `horizontal scroll` on any mobile tab. Check by hand at 375, 390 and 768 px in DevTools.

**Don't:** "fix" it with `overflow-x: hidden` on `body`. That hides content instead of fitting it.

---

### G6 · Navigation: one state, both menus, real tabs

**Why:**
- The phone menu (lines 113–119) has the active style hard-coded on "1. Advisor", and `switchTab()` never updates it.
- Partner is always purple.
- There are no ARIA roles, so screen readers announce 10 unrelated buttons.
- The URL never changes, so you can't refresh into or share a step.

**Do:**
1. Desktop `<nav>` (line 74): `<nav role="tablist" aria-label="Onboarding steps" class="hidden md:flex gap-1">`.
   Each button gets: `type="button" role="tab" data-tab="advisor" aria-controls="view-advisor" aria-selected="false"`. Keep the existing `id="tab-btn-advisor"`.
2. Phone menu (line 113): `<nav id="mobile-subnav" role="tablist" aria-label="Onboarding steps" class="md:hidden …">`. Each button gets `type="button" role="tab" data-tab="…" aria-controls="view-…"` and the class `sub-tab` (delete the hard-coded colour classes).
3. Each `<section class="tab-view">`: add `role="tabpanel" aria-labelledby="tab-btn-advisor" tabindex="-1"`.
4. CSS (`style.css`):
   ```css
   .sub-tab { min-height: 44px; padding: 0 .9rem; border-radius: .75rem; font-weight: 600; color: #475569; white-space: nowrap; }
   .sub-tab.active, .nav-tab.active { background: var(--brand-soft); color: var(--brand-strong); }
   ```
   (`brand-strong` on `brand-soft` is 6.6:1. The current `#E40000` on `#FFF1F1` is 4.44:1, which fails.)
5. Replace `switchTab` in `app.js`:
   ```js
   const TABS = ['advisor', 'quote', 'kyc', 'tracker', 'partner'];
   function switchTab(tabName) {
     if (!TABS.includes(tabName)) tabName = 'advisor';
     document.querySelectorAll('.tab-view').forEach(v => v.classList.toggle('active', v.id === `view-${tabName}`));
     document.querySelectorAll('[data-tab]').forEach(b => {
       const on = b.dataset.tab === tabName;
       b.classList.toggle('active', on);
       b.setAttribute('aria-selected', String(on));
     });
     if (location.hash !== `#${tabName}`) history.replaceState(null, '', `#${tabName}`);
     document.querySelector('main').scrollIntoView({ block: 'start' });
     if (window.lucide) lucide.createIcons();
   }
   ```
   In `DOMContentLoaded`, call `switchTab(location.hash.slice(1))` so `/#kyc` opens KYC directly. That's handy for the demo video.
6. Remove the purple from the Partner tab (line 91, and line 118 in the phone menu). Instead, separate it as a different **persona**: add a thin divider `<span class="w-px h-6 bg-slate-200 mx-1" aria-hidden="true"></span>` before it and label it "Partner Portal" without a step number. It isn't step 5 of the customer journey.

**Done when:** `ui_audit.py` stops reporting `mobile sub-nav` and `role=tablist`; `/#tracker` opens the tracker; screen-reader smoke test (Windows Narrator, Ctrl+Win+Enter) reads "Onboarding steps, tab, 1 of 5, selected".

---

### G7 · Partner portal: wrong mapping, a score that tells nothing, and a quoting bug

**Why:**
1. `assistDroppedLead` (`app.js` ~line 887) maps **every** non-retail lead to *Clinic*, so a 139-staff polymer manufacturer gets a clinic bundle on stage.
2. The top 50 leads **all** show `98%`, so the score column carries no information.
3. `onclick="assistDroppedLead('${l.business_name}', …)"` breaks on any name with an apostrophe (`Raju's Store`) and is an HTML-injection path.

**Do:**
1. Keep the rows in memory and pass only the id:
   ```js
   let partnerLeads = [];
   // in loadPartnerLeads, after fetching:
   partnerLeads = data.leads;
   // button:
   `<button type="button" onclick="assistDroppedLead('${escapeHtml(l.lead_id)}')" …>`
   ```
2. Fix the mapping:
   ```js
   const LEAD_SEGMENT_TO_BIZ = {
     'Micro retail & services': 'Kirana & Retail Store',
     'Professional offices': 'CA / Legal / Consulting Office',
     'Small multi-site businesses': 'Restaurant & Food Chain',
     'Small manufacturers': 'Small Manufacturing & Workshop'
   };
   function assistDroppedLead(leadId) {
     const l = partnerLeads.find(x => x.lead_id === leadId);
     if (!l) return;
     switchTab('advisor');
     document.getElementById('adv-biz-type').value = LEAD_SEGMENT_TO_BIZ[l.segment] || 'Kirana & Retail Store';
     document.getElementById('adv-city-tier').value = String(l.city_tier);
     document.getElementById('adv-city-name').value = l.city || '';
     document.getElementById('adv-employees').value = l.employee_count;
     document.getElementById('adv-sites').value = l.segment === 'Small multi-site businesses' ? Math.max(2, l.num_sites || 2) : 1;
     document.querySelector(`input[name="adv-has-gst"][value="${l.has_gstin ? 'yes' : 'no'}"]`).checked = true;
     submitAdvisorProfile();
   }
   ```
3. Escape every lead field rendered with `innerHTML` (`business_name`, `city`, `drop_reason`, `segment`, `stage_reached`) using `escapeHtml`.
4. Replace the flat score column with **"Priority"**: the row's rank (`#1`, `#2`, …) plus a small 0–100 bar (`<div class="h-1.5 rounded bg-slate-100"><div class="h-1.5 rounded bg-ok" style="width:${score}%"></div></div>`) and the number. Sort the visible rows by `employee_count` (a bigger business is a bigger bundle) as the tie-breaker when scores are equal. Add the header tooltip *"Likelihood to convert with partner help (0–100)"*.
   *(Root cause, separate backend task: the propensity score saturates at 98. If you have time, widen it in the partner engine so the top 20% spread out.)*

**Done when:**
- *1-Click Assist* on **Moonlight Polymers** opens the advisor with *Small Manufacturing*, 139 staff and a manufacturing bundle.
- A lead with an apostrophe in its name still works (test it by editing a row's `business_name` in DevTools).
- The Priority column shows distinct ranks.

---

## 3. P1: readability and accessibility

### G8 · Minimum 12 px text; 16 px inputs on phones

**Why:** The Quote tab has **146 text elements under 12 px**; overall there are 39 `text-[10px]/[11px]` in HTML and 26 in JS. iOS zooms the page when a focused input is under 16 px.

**Do (find and replace, then check by eye):**

| Find | Replace with | Where |
|---|---|---|
| `text-[10px]` | `text-xs` | `index.html`, `app.js` |
| `text-[11px]` | `text-xs` | `index.html`, `app.js` |
| `text-xs` on **sentences/descriptions** (card subtitles, reasoning list, product descriptions, timeline descriptions, drop reasons) | `text-sm leading-relaxed` | review each |
| `text-xs` on **table bodies** (`rec-products-table` wrapper line 272, partner table line 685) | `text-sm` | 2 places |
| every `input`/`select`/`textarea` `text-sm` or `text-xs` | `text-base md:text-sm` | ~12 controls, including the generated product checkboxes |
| `text-[10px] font-mono` OCR textareas (513–521) | `text-xs font-mono` | 3 |

**Done when:** `ui_audit.py` shows `textUnder12px: 0` and `inputsUnder16px: 0` on mobile for all tabs. Check that the Quote list still looks good on desktop. If it looks too loose, reduce **padding**, not font size.

---

### G9 · Contrast: every text at least 4.5:1

**Why:** The audit flags 87 low-contrast texts on Quote and 6–19 on other tabs.

**Do:**
1. `text-slate-400` → `text-slate-500` everywhere text sits on white/slate-50 (12 in HTML, 8 in JS). On `slate-100` or any tinted card, use `text-slate-600`.
2. Tinted labels: `text-emerald-600` → `text-emerald-700`, `text-amber-600` → `text-amber-700`, `text-purple-600` → gone after G6/G14.
3. *AI Recommended Bundle* pill (line 245): `text-airtel-darkred bg-white border border-red-200` (red on `red-100/70` is 4.0:1).
4. Disabled *Confirm & Activate* (line 556): fine as-is (disabled controls are exempt), but add a one-line reason under it while disabled: *"Available after a PASS verdict"* in `text-xs text-slate-500`.
5. The **VS logo tile** is white on a gradient; the audit skips gradients, and it's fine.

**Known measured failures to re-check:**
- `⚡ 1-Click Judge Test Scenarios` (2.56)
- `(P01)` / `/mo` / `Setup: ₹0` (2.56)
- tracker timestamps (2.56)
- `From 5,000 baseline leads` (2.56)
- lead IDs (2.56)
- `At ₹2.5k avg bundle/mo` (3.77)
- `15% revenue share…` (3.19)
- `In Progress` badge (4.00)
- active nav tab (4.44)
- `GitHub Repo` (3.63)
- `व्यापारसेतु` pill (4.34)

**Done when:** `ui_audit.py` reports `lowContrast: 0` on all tabs.

---

### G10 · Keyboard focus and reduced motion

**Do:** append to `style.css`:
```css
:where(button, a, input, select, textarea, summary, [tabindex]):focus-visible {
  outline: 3px solid var(--info);
  outline-offset: 2px;
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: .01ms !important; animation-iteration-count: 1 !important;
    transition-duration: .01ms !important; scroll-behavior: auto !important;
  }
}
```
Blue rings are used on purpose so a keyboard focus never looks like an error or the brand.

Also add a skip link as the first thing in `<body>`:
```html
<a href="#main" class="sr-only focus:not-sr-only focus:fixed focus:top-2 focus:left-2 focus:z-[100] bg-white px-3 py-2 rounded-lg">Skip to content</a>
```
and give `<main>` the attribute `id="main"`.

**Done when:** Pressing Tab from page load shows the skip link, then a visible blue ring on every stop. In Windows *Settings → Accessibility → Visual effects → Animation effects: Off*, the spinners stop spinning but the page still works.

---

### G11 · Tap targets at least 44 px on phones

**Do:** one global rule in `style.css` covers almost all of them:
```css
@media (max-width: 767px) {
  button, select, summary, a.btn,
  input:not([type=checkbox]):not([type=radio]):not([type=file]) { min-height: 44px; }
  input[type=checkbox], input[type=radio] { width: 20px; height: 20px; }
}
```
Then check the stragglers:
- language toggle `EN/हिंदी`: `px-3 py-2`
- product checkboxes in the Quote list: make the **whole card** a `<label>` so tapping anywhere toggles it
- radio cards (lines 185–192): already labels, so add `min-h-[44px]`

**Done when:** `ui_audit.py` reports `tapTargetsUnder44px: 0` on mobile.

---

### G12 · No emoji as icons

**Why:** 1 in `index.html` (line 210 `⚡`), 5 `📄` in `app.js` (~lines 404–476), and 56 in `app/advisor_engine.py` reasoning strings (lines 269+). They look different on every phone and can't be coloured.

**Do:**
- `index.html` line 210: `<i data-lucide="zap" class="w-3.5 h-3.5 inline" aria-hidden="true"></i> Try a sample business`. Also rename the label; "Judge Test Scenarios" breaks the fourth wall in a customer UI.
- `app.js` `📄` → `<i data-lucide="file-text" class="w-4 h-4" aria-hidden="true"></i>`, and call `lucide.createIcons()` after inserting.
- Reasoning list: strip the emoji where it's rendered (one line in `renderAdvisorRecommendation`), and use one consistent icon per bullet:
  ```js
  listEl.innerHTML = data.reasoning.map(pt => `
    <li class="flex items-start gap-2">
      <i data-lucide="check-circle-2" class="w-4 h-4 mt-0.5 text-ok shrink-0" aria-hidden="true"></i>
      <span class="text-sm text-slate-700 leading-relaxed">${escapeHtml(pt.replace(/^\p{Extended_Pictographic}️?\s*/u, ''))}</span>
    </li>`).join('');
  ```
  and change `#rec-reasoning-list` to a `<ul>`. (Cleaning the strings in `advisor_engine.py` itself is nicer, but this one line is enough.)

**Done when:** `py -c "import re;print(len(re.findall(r'[\U0001F300-\U0001FAFF☀-➿]', open('app/static/index.html',encoding='utf-8').read()+open('app/static/app.js',encoding='utf-8').read())))"` prints `0`, and no emoji is visible in the advisor card.

---

### G13 · Every action shows progress and every failure says what to do

**Why:**
- Most `catch` blocks only `console.error`, so the user sees nothing when something fails.
- Only the advisor has a loading state.
- Cloud OCR and AI calls take 2–20 s, and silent buttons get double-clicked.

**Do:**
1. Wrap every API-calling button with `setBusy(btn, true, '…')` / `setBusy(btn, false)` (helper from G1). Busy texts:
   - Generate → `Building your bundle…`
   - Run Smart Verification → `Verifying…`
   - Verify GST / Verify Udyam → `Checking registry…`
   - Extract OCR & Verify → `Reading documents…`
   - Confirm & Activate → `Placing order…`
   - Track → `Looking up…`
2. Replace each bare `console.error` with an inline message in the card where the action happened (`role="alert"`, `text-sm text-err`, and a **Retry** button that calls the same function). Wording pattern: *what happened + what to do*, for example *"Couldn't load the catalogue. Check your connection and retry."*
3. Live regions so screen readers hear results:
   - `#kyc-verdict-banner` → `role="status" aria-live="polite"`
   - `#advisor-loading` → `role="status"`
   - `#bill-validation-alerts` → `aria-live="polite"`
4. Advisor loading: keep the result card's height while loading (it's already dimmed with `opacity-40`, good) instead of collapsing it, so nothing jumps.

**Done when:** With the server stopped, every button shows a readable error with Retry; with it running, every button shows a spinner and can't be double-submitted.

---

### G14 · Status colours mean one thing each

**Do:**
1. **Tracker "in progress"**: `style.css` `.timeline-dot.in-progress` → `background: var(--info); box-shadow: 0 0 0 4px #E0F2FE;`. The `IN PROGRESS` badge → `bg-info-soft text-info`. Red in a tracker reads as "something broke".
2. **KYC verdict banner** (`renderKYCDiagnostics`):
   - REJECT → `bg-err-soft border-red-200`, icon `x-circle` in `text-err`, title *"Rejected: <business>"*, and the reasons as a `<ul>` (one per line, not run-on text)
   - PASS → `bg-ok-soft border-emerald-200`, icon `check-circle-2`
   - idle → neutral `shield`

   The icon currently stays a grey shield on a red banner.
3. **Checklist order**: render `FAILED` items first, then `PASSED`, so the reason is the first thing read. Each status badge keeps its word (*PASSED/FAILED*), not just colour.
4. **Partner portal**:
   - KPI cards: one neutral style (`text-slate-500` label, `text-slate-900` number), with only the *Recoverable ARR* number in `text-ok`.
   - The per-row **1-Click Assist** becomes a secondary button (`border border-slate-300 text-slate-800 hover:border-airtel-red bg-white`), because 12 bright purple primaries in one table compete with each other.
5. Brand red is now used only for: logo, the single primary CTA per screen, and the active tab.

**Done when:** `grep -c "purple-" app/static/index.html app/static/app.js` → `0`; each screen has exactly **one** red filled button (not counting the header CTA, which G5 hides on phones).

---

## 4. P2: polish (do if time allows, in this order)

### G15 · Header that fits on one line at 1440 px
At 1440 px, the nav labels and *Instant Checkout* wrap to two lines.
- Shorten the labels: `Advisor · Quote · KYC · Track` plus the separated `Partner Portal` (G6).
- Show the step number as a 20 px circle before each label (`<span class="w-5 h-5 rounded-full bg-slate-100 text-xs grid place-items-center">1</span>`) instead of `1.` text.
- Rename the header CTA from *Instant Checkout* to *Start KYC*, since that's where it goes.
- Add `whitespace-nowrap` to nav buttons.

### G16 · Show progress through the journey
- Mark a step **done** when its work happens (bundle generated → Advisor done; quote total exists → Quote done; PASS verdict → KYC done; order placed → Track done). Show a check icon in that step's circle (`bg-ok text-white`).
- Each customer step ends with one primary **Next** button at the bottom right:
  - Advisor → *Continue to quote*
  - Quote → *Continue to KYC*
  - KYC (after PASS) → *Confirm & activate*

  On phones, make this button a sticky bottom bar: `fixed bottom-0 inset-x-0 p-3 bg-white border-t` plus `pb-24` on `<main>`, so content isn't hidden behind it.
- Add a **Back** text link next to it.

### G17 · Advisor result: clear empty state, clear price
- On first load the card shows a full kirana bundle that nobody asked for. Either keep it and add a small `Sample` badge until the user generates their own, or show an empty state: an icon plus *"Describe your business or pick a sample to see your bundle"*.
- Put the price on its own line under the title on phones (`flex-col sm:flex-row`); add `tabular` to the price and to the table's Monthly column.
- Move *Single Unified Invoicing* out of the price corner into a small benefit row: `One bill · No visit needed · Live tracking`.

### G18 · KYC card layout
- Order the card as 3 numbered steps: **1 Consent** → **2 Load documents** (sample applicants *or* upload) → **3 Verify**. Put the manual GSTIN/Udyam/date fields inside a `<details>` called *"Enter numbers manually instead"*, collapsed by default (progressive disclosure).
- Rename *"Load Live Judge Test Applicant (K01 – K12)"* to *"Try a sample applicant"*, and the dropdown entries to `K07 · Neelgiri Physio Clinic` (drop `(UNKNOWN) -`).
- The "View / Edit Extracted OCR Text" panel: rename to *"Show what we read from your documents"*; textareas get visible labels (they have them) at `text-xs`.

### G19 · Quote tab
- Remove the inner scroll (`max-h-[580px] overflow-y-auto` on line 334) on phones: `lg:max-h-[580px] lg:overflow-y-auto`. Nested scrolling on touch traps the thumb.
- Make each product card a `<label>` (G11) with the checkbox at left, name + description in the middle, and price at right in `tabular`.
- On phones, the bill summary becomes the sticky bottom bar from G16: `₹2,796/mo · 4 products · Continue`.
- Rule-validation alerts (`#bill-validation-alerts`): `bg-warn-soft text-warn` with an `alert-triangle` icon and a **fix action** button where possible (for example *"Add Biz Fibre 100"* when a dependency is missing).

### G20 · Tracker
- A copy button next to the order number and the PIN (`navigator.clipboard.writeText(...)`), followed by a 2 s "Copied" text.
- Timestamps `text-xs text-slate-500 tabular`.
- Don't pre-fill `VS-2026-90412` as the input **value**: keep it as the placeholder, and load the user's **last order** from `localStorage` (`vs_last_order`) if there is one.
- *Call Technician*: `min-h-[44px]`; add `aria-label="Call technician Ramesh Kumar"`.

### G21 · Partner table on phones
Below `md`, render each lead as a card instead of a 6-column table:
```
Moonlight Polymers Pvt Ltd            #11
Small manufacturer · Indore (Tier 2) · 139 staff
Dropped at: Quote accepted — Missing GST or Udyam document
[Priority bar ████████░░ 98]          [ Assist ]
```
Implementation: render both a `<table class="hidden md:table">` and a `<div class="md:hidden space-y-3">` from the same `partnerLeads` array.

### G22 · Hindi toggle: make it honest
The toggle translates **4 strings**. Either:
- (a) extend `i18n` to cover the tab labels, card titles, primary buttons, verdict titles and the consent text (about 40 strings), **and** set `document.documentElement.lang = lang` in `setLanguage`; or
- (b) relabel it `हिंदी (beta)` and keep the scope small.

Option (a) is a strong demo moment combined with G1 (the AI already answers in Hindi).

### G23 · Fonts that work offline
`index.html` line 9 loads Plus Jakarta Sans and Noto Sans Devanagari from Google Fonts. If the demo Wi-Fi is bad, the page falls back to the default font, and any Devanagari text might fall back too.
- Download the `woff2` files (weights 400/600/700/800 Latin; 400/600 Devanagari) into `app/static/vendor/fonts/`.
- Declare them with `@font-face { font-display: swap; }` in `style.css`.
- Delete the Google Fonts `<link>`s (lines 7–9).

---

## 5. Final checklist (all must be true)

**Measured, from `scripts/ui_audit.py`:**
- [ ] No horizontal scroll at 375 px on any tab
- [ ] 0 text under 12 px; 0 inputs under 16 px on phone
- [ ] 0 low-contrast texts
- [ ] 0 tap targets under 44 px on phone
- [ ] `:focus-visible` CSS present; `role=tablist` present; phone menu highlights the current tab
- [ ] The script ends with `ALL UI/UX TARGETS MET`

**Functional (by hand):**
- [ ] Hindi kirana sentence → correct chips + micro bundle (G1)
- [ ] Unticked consent blocks every KYC action with no network call (G2)
- [ ] Dropping 4 K07 PNGs → *Legal entity mismatch*; dropping a PDF → clear message (G3)
- [ ] Moonlight Polymers *Assist* → manufacturing bundle (G7)
- [ ] `/#kyc` opens KYC; refresh keeps the tab (G6)
- [ ] With the server stopped, every button shows an error with Retry (G13)

**Regression:**
- [ ] `py scripts/ui_smoke.py` → 8/8 (after adding the consent tick from G2)
- [ ] `py -m pytest -q` → all pass
- [ ] `py scripts/eval_advisor_llm.py` → passes, including the new Hindi case (G1 prerequisite)

## 6. Suggested commit order and time

| # | Items | Time | Why this order |
|---|---|---|---|
| 1 | §1 tokens + G10 focus/motion | 30 min | Everything else uses them |
| 2 | G2 consent, G4 claims | 30 min | Smallest, most visible to judges |
| 3 | G5 mobile overflow, G6 nav | 1 h | Unblocks phone testing for the rest |
| 4 | G1 AI chat (+ backend prompt fix) | 1.5 h | Biggest demo win |
| 5 | G3 upload, G13 feedback | 1.5 h | Upload is what judges try |
| 6 | G7 partner, G14 colours | 1 h | |
| 7 | G8 type, G9 contrast, G11 targets, G12 emoji | 1.5 h | Mostly find-and-replace, then the audit |
| 8 | P2 items as time allows | — | |

Each P0 item is independent of the others except that **G1 and G3 use the helpers (`escapeHtml`, `setBusy`) defined in G1**. If you do G3 first, copy those two helpers then.

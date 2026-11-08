"""
UI/UX audit for VyaparSetu - measures the numbers that UI_UX_GUIDE.md asks you to bring down.

Usage (server must be running):
    py scripts/ui_audit.py                       # http://127.0.0.1:8000
    py scripts/ui_audit.py http://127.0.0.1:8766
    py scripts/ui_audit.py http://127.0.0.1:8000 shots   # also save screenshots to ./shots/

Exit code 1 if any hard target in the guide's "Done when" checklist is missed.
"""
import json
import os
import sys

from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("SMOKE_BASE_URL", "http://127.0.0.1:8000")
SHOTS = sys.argv[2] if len(sys.argv) > 2 else None
TABS = ["advisor", "quote", "kyc", "tracker", "partner"]

TOKENS = r"""() => {
  const vis = e => { const r = e.getBoundingClientRect(), s = getComputedStyle(e);
    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'
           && e.closest('.tab-view:not(.active)') === null && !e.closest('#app-sidebar'); };
  const bad = { buttonHeights: [], radii: [] };
  document.querySelectorAll('button, a[role=button]').forEach(b => {
    if (!vis(b) || b.classList.contains('link-btn') || b.classList.contains('splitter') || b.closest('.stepper')) return;
    const h = Math.round(b.getBoundingClientRect().height);
    if (h !== 36 && h < 44) bad.buttonHeights.push((b.textContent || b.getAttribute('aria-label') || '').trim().slice(0, 24) + ' ' + h);
  });
  document.querySelectorAll('.btn-primary, .btn-secondary, .btn-confirm, .field, .seg, .kpi-strip, .disc, .consent-box, .empty, .dropzone, .notice').forEach(e => {
    if (!vis(e)) return;
    const r = parseFloat(getComputedStyle(e).borderTopLeftRadius);
    if (![8, 12].includes(Math.round(r))) bad.radii.push(e.className.toString().split(' ')[0] + ' ' + r);
  });
  return bad;
}"""

METRICS = r"""() => {
  const vis = e => { const r = e.getBoundingClientRect(), s = getComputedStyle(e);
    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'
           && e.closest('.tab-view:not(.active)') === null; };
  const texts = [...document.querySelectorAll('body *')].filter(e => vis(e) &&
    [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim().length > 1));
  const lum = c => { const m = c.match(/[\d.]+/g); if (!m) return null;
    const [r, g, b] = m.slice(0, 3).map(v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); });
    return 0.2126 * r + 0.7152 * g + 0.0722 * b; };
  const bgOf = e => { while (e) { const s = getComputedStyle(e);
      if (s.backgroundImage !== 'none') return null;          // gradient: skip, can't measure
      const a = s.backgroundColor.match(/[\d.]+/g);
      if (a && (a.length < 4 || +a[3] > 0.5)) return s.backgroundColor; e = e.parentElement; }
    return 'rgb(255,255,255)'; };
  const lowContrast = [];
  texts.forEach(e => {
    if (e.closest('button:disabled')) return;               // disabled controls are exempt (WCAG)
    const bg = bgOf(e); if (!bg) return;
    const f = lum(getComputedStyle(e).color), b = lum(bg); if (f == null || b == null) return;
    const ratio = (Math.max(f, b) + 0.05) / (Math.min(f, b) + 0.05);
    const s = getComputedStyle(e), big = parseFloat(s.fontSize) >= 24 || (parseFloat(s.fontSize) >= 18.66 && +s.fontWeight >= 700);
    if (ratio < (big ? 3 : 4.5)) lowContrast.push(e.textContent.trim().slice(0, 40) + ' [' + ratio.toFixed(2) + ']');
  });
  const ctrls = [...document.querySelectorAll('button, a[href], input:not([type=hidden]), select, textarea, summary')].filter(vis);
  const small = ctrls.filter(e => { const r = e.getBoundingClientRect();
    return r.height < 44 && !['checkbox', 'radio', 'file'].includes(e.type); });
  return {
    horizontalScroll: document.documentElement.scrollWidth > innerWidth,
    pageWidth: document.documentElement.scrollWidth,
    textUnder12px: texts.filter(e => parseFloat(getComputedStyle(e).fontSize) < 12).length,
    lowContrast: lowContrast.length,
    lowContrastSamples: lowContrast.slice(0, 6),
    tapTargetsUnder44px: small.length,
    inputsUnder16px: [...document.querySelectorAll('input:not([type=checkbox]):not([type=radio]):not([type=file]), select, textarea')]
      .filter(vis).filter(e => parseFloat(getComputedStyle(e).fontSize) < 16).length,
    hasFocusVisibleCss: [...document.styleSheets].some(s => { try { return [...s.cssRules].some(r => r.cssText.includes('focus-visible')); } catch (e) { return false; } }),
    tablistRole: !!document.querySelector('[role=tablist]'),
  };
}"""

results, failures = {}, []
with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome")
    for device, vp in [("desktop", {"width": 1440, "height": 900}), ("mobile", {"width": 375, "height": 812})]:
        ctx = browser.new_context(viewport=vp)
        if os.environ.get("AUDIT_THEME") in ("dark", "light"):   # AUDIT_THEME=dark py scripts/ui_audit.py ...
            ctx.add_init_script(f"localStorage.setItem('vyapar_theme', '{os.environ['AUDIT_THEME']}')")
        page = ctx.new_page()
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(BASE)
        page.wait_for_timeout(2500)
        for tab in TABS:
            page.evaluate(f"switchTab('{tab}')")
            page.wait_for_timeout(700)
            m = page.evaluate(METRICS)
            results[f"{device}/{tab}"] = m
            if SHOTS:
                os.makedirs(SHOTS, exist_ok=True)
                page.screenshot(path=os.path.join(SHOTS, f"{device}_{tab}.png"), full_page=True)
            # Hard targets (see UI_UX_GUIDE.md -> "Done when")
            if m["horizontalScroll"]:
                failures.append(f"{device}/{tab}: horizontal scroll (page {m['pageWidth']}px wide)")
            if m["textUnder12px"]:
                failures.append(f"{device}/{tab}: {m['textUnder12px']} text elements under 12px")
            if m["lowContrast"]:
                failures.append(f"{device}/{tab}: {m['lowContrast']} low-contrast texts e.g. {m['lowContrastSamples'][:2]}")
            tk = page.evaluate(TOKENS)   # design tokens: button heights 36/44, radii 8/12
            if tk["buttonHeights"]:
                failures.append(f"{device}/{tab}: button heights off-token {tk['buttonHeights'][:3]}")
            if tk["radii"]:
                failures.append(f"{device}/{tab}: corner radius off-token {tk['radii'][:3]}")
            if device == "mobile" and m["inputsUnder16px"]:
                failures.append(f"mobile/{tab}: {m['inputsUnder16px']} inputs under 16px (iOS will zoom)")
            if device == "mobile" and m["tapTargetsUnder44px"]:
                failures.append(f"mobile/{tab}: {m['tapTargetsUnder44px']} tap targets under 44px tall")
        if device == "mobile":
            # Mobile sub-nav must highlight the current tab (exactly one active pill)
            page.evaluate("switchTab('kyc')")
            active = page.evaluate("[...document.querySelectorAll('#mobile-subnav [aria-selected=true]')].map(b => b.dataset.tab)")
            if active != ["kyc"]:
                failures.append(f"mobile sub-nav: active tabs after switchTab('kyc') = {active}, expected ['kyc']")
        first = results[f"{device}/advisor"]
        if not first["hasFocusVisibleCss"]:
            failures.append(f"{device}: no :focus-visible styles in any stylesheet")
        if not first["tablistRole"]:
            failures.append(f"{device}: navigation has no role=tablist")
        if errors:
            failures.append(f"{device}: JS errors {errors[:2]}")
        page.close()
    browser.close()

print(json.dumps(results, indent=1, ensure_ascii=False))
print("\n" + "=" * 70)
if failures:
    print(f"{len(failures)} target(s) missed:")
    for f in failures:
        print("  - " + f)
    sys.exit(1)
print("ALL UI/UX TARGETS MET")

// VyaparSetu Frontend Client Logic

let currentLanguage = 'en';
let allProducts = [];
let selectedProductIds = new Set(); // empty until the customer or the Advisor picks products
let recommendedProductIds = new Set();
let productQuantities = {}; // advisor-chosen quantities, so the quote matches the advisor price
let activeCategoryFilter = 'all';
let currentRecommendation = null;
let currentApplicant = null;
let lastCreatedOrderId = null;
const SAMPLE_ORDER_ID = 'VS-2026-90412';
let partnerLeads = [];
let chatProfile = null;
let currentTheme = 'light';

// ---------- Theme toggle ----------
function applyTheme(theme) {
  currentTheme = theme;
  const html = document.documentElement;
  const body = document.body;
  const icon = document.getElementById('theme-icon');
  const btn = document.getElementById('theme-toggle');

  if (theme === 'dark') {
    html.setAttribute('data-theme', 'dark');
    body.setAttribute('data-theme', 'dark');
    if (icon) { icon.setAttribute('data-lucide', 'sun'); icon.classList.remove('text-slate-600'); icon.classList.add('text-amber-500'); }
    if (btn) { btn.classList.remove('bg-slate-50', 'text-slate-600', 'border-slate-200'); btn.classList.add('bg-slate-800', 'text-amber-500', 'border-slate-700'); }
  } else {
    html.removeAttribute('data-theme');
    body.removeAttribute('data-theme');
    if (icon) { icon.setAttribute('data-lucide', 'moon'); icon.classList.remove('text-amber-500'); icon.classList.add('text-slate-600'); }
    if (btn) { btn.classList.remove('bg-slate-800', 'text-amber-500', 'border-slate-700'); btn.classList.add('bg-slate-50', 'text-slate-600', 'border-slate-200'); }
  }
  if (btn) {
    btn.setAttribute('aria-pressed', String(theme === 'dark'));
    const label = theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme';
    btn.setAttribute('aria-label', label); btn.setAttribute('title', label);
  }
  if (window.lucide) lucide.createIcons();
  try { localStorage.setItem('vyapar_theme', theme); } catch (e) { /* storage may be blocked */ }
}

function toggleTheme() {
  applyTheme(currentTheme === 'light' ? 'dark' : 'light');
}

function initTheme() {
  let theme = 'light';
  try { theme = localStorage.getItem('vyapar_theme'); } catch (e) { /* ignore */ }
  if (!theme || (theme !== 'light' && theme !== 'dark')) {
    theme = 'light';   // light is the default; dark is an explicit choice (it is remembered)
  }
  applyTheme(theme);
}

// Multi-language text dictionary
const i18n = {
  en: {
    advisorTitle: "Conversational Business Discovery",
    advisorSubtitle: "Answer 4 quick questions for an optimized enterprise bundle",
    whyBundle: "Why this bundle fits your daily business",
    btnRec: "Generate Tailored Bundle",
    lblBizType: "Business Type / Category"
  },
  hi: {
    advisorTitle: "व्यापारिक आवश्यकता विश्लेषण (AI सलाहकार)",
    advisorSubtitle: "मात्र 4 सरल प्रश्नों के उत्तर दें — पाएं सबसे किफ़ायती बिज़नेस पैक",
    whyBundle: "यह बंडल आपके दैनिक व्यापार के लिए क्यों सबसे उपयुक्त है",
    btnRec: "कस्टमाइज़्ड बंडल तैयार करें",
    lblBizType: "व्यवसाय का प्रकार / श्रेणी"
  }
};

const SEGMENT_TO_BIZ = {
  micro: 'Kirana & Retail Store',
  prof: 'Clinic & Healthcare',
  multi: 'Restaurant & Food Chain',
  mfg: 'Small Manufacturing & Workshop'
};

const LEAD_SEGMENT_TO_BIZ = {
  'Micro retail & services': 'Kirana & Retail Store',
  'Professional offices': 'CA / Legal / Consulting Office',
  'Small multi-site businesses': 'Restaurant & Food Chain',
  'Small manufacturers': 'Small Manufacturing & Workshop'
};

// Shared UI Helpers
function escapeHtml(s) {
  return String(s ?? '').replace(/[&<>"']/g, c => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
  }[c]));
}

function setBusy(btn, busy, busyText = 'Working…') {
  if (!btn) return;
  btn.disabled = busy;
  btn.setAttribute('aria-busy', String(busy));
  if (busy) {
    btn.dataset.label = btn.innerHTML;
    btn.innerHTML = `<span class="inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" aria-hidden="true"></span><span>${escapeHtml(busyText)}</span>`;
  } else if (btn.dataset.label) {
    btn.innerHTML = btn.dataset.label;
    if (window.lucide) lucide.createIcons();
  }
}

function requireConsent() {
  const chk = document.getElementById('dpdp-consent-chk');
  const help = document.getElementById('dpdp-consent-help');
  if (chk && chk.checked) {
    if (help) help.classList.add('hidden');
    return true;
  }
  if (help) help.classList.remove('hidden');
  if (chk) chk.focus();
  return false;
}

document.addEventListener('DOMContentLoaded', async () => {
  if (window.lucide) {
    lucide.createIcons();
  }

  initTheme();
  const consentChk = document.getElementById('dpdp-consent-chk');
  const consentBox = document.getElementById('dpdp-consent-box');
  const consentHelp = document.getElementById('dpdp-consent-help');
  if (consentChk && consentBox) {
    consentChk.addEventListener('change', () => {
      if (consentChk.checked) {
        if (consentHelp) consentHelp.classList.add('hidden');
        consentBox.classList.add('is-ok');
      } else {
        consentBox.classList.remove('is-ok');
      }
    });
  }

  // Setup Drag & Drop Zone for KYC
  const dz = document.getElementById('kyc-dropzone');
  if (dz) {
    const on = e => { e.preventDefault(); dz.classList.add('ring-2', 'ring-info', 'bg-info-soft'); };
    const off = e => { e.preventDefault(); dz.classList.remove('ring-2', 'ring-info', 'bg-info-soft'); };
    ['dragenter', 'dragover'].forEach(t => dz.addEventListener(t, on));
    ['dragleave', 'drop'].forEach(t => dz.addEventListener(t, off));
    dz.addEventListener('drop', e => {
      off(e);
      if (e.dataTransfer && e.dataTransfer.files) {
        handleFileUpload({ target: { files: e.dataTransfer.files } });
      }
    });
  }

  await loadCatalogue();
  await loadKYCApplicants();
  await loadPartnerPortal();
  
  // No recommendation until the customer has told us about the business.
  renderOrderHistory();

  // Handle URL hash routing
  if (location.hash) {
    const hashTab = location.hash.replace('#', '').trim();
    if (['advisor', 'quote', 'kyc', 'tracker', 'partner'].includes(hashTab)) {
      switchTab(hashTab);
    }
  }
});

// Tab Switcher
const TABS = ['advisor', 'quote', 'kyc', 'tracker', 'partner'];
function switchTab(tabName) {
  if (!TABS.includes(tabName)) tabName = 'advisor';
  document.querySelectorAll('.tab-view').forEach(v => v.classList.toggle('active', v.id === `view-${tabName}`));
  document.querySelectorAll('[data-tab]').forEach(b => {
    const on = b.dataset.tab === tabName;
    b.classList.toggle('active', on);
    b.setAttribute('aria-selected', String(on));
  });
  if (location.hash !== `#${tabName}`) {
    history.replaceState(null, '', `#${tabName}`);
  }
  if (window.innerWidth < 1024) toggleSidebar(false);
  const mainEl = document.querySelector('main');
  if (mainEl) { mainEl.scrollTop = 0; mainEl.scrollIntoView({ block: 'start' }); }
  if (window.lucide) lucide.createIcons();
}

// Language Switcher
function setLanguage(lang) {
  currentLanguage = lang;
  document.documentElement.lang = lang;
  document.getElementById('lang-en').className = lang === 'en' 
    ? 'px-3 py-2 min-h-[44px] text-xs font-bold rounded-lg bg-white shadow-sm text-slate-800 flex items-center justify-center'
    : 'px-3 py-2 min-h-[44px] text-xs font-bold rounded-lg text-slate-600 hover:text-slate-800 flex items-center justify-center';
  document.getElementById('lang-hi').className = lang === 'hi' 
    ? 'px-3 py-2 min-h-[44px] text-xs font-bold rounded-lg bg-white shadow-sm text-slate-800 flex items-center justify-center'
    : 'px-3 py-2 min-h-[44px] text-xs font-bold rounded-lg text-slate-600 hover:text-slate-800 flex items-center justify-center';

  document.getElementById('txt-advisor-title').textContent = i18n[lang].advisorTitle;
  document.getElementById('txt-advisor-subtitle').textContent = i18n[lang].advisorSubtitle;
  document.getElementById('txt-why-bundle').textContent = i18n[lang].whyBundle;
  document.getElementById('btn-generate-rec').textContent = i18n[lang].btnRec;

  // Re-run recommendation with new language
  if (currentRecommendation) {
    submitAdvisorProfile();
  }
}

// GenAI Advisor Conversational Chat
async function sendAdvisorChat(text) {
  const input = document.getElementById('adv-chat-input');
  const query = (text ?? input?.value ?? '').trim();
  if (!query) {
    if (input) input.focus();
    return;
  }
  const btn = document.getElementById('adv-chat-send');
  setBusy(btn, true, 'Thinking…');
  try {
    const res = await fetch('/api/advisor/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
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
    if (box) {
      box.classList.remove('hidden');
      box.innerHTML = `<p role="alert" class="text-sm text-err">Couldn't reach the advisor. Try again, or use the form below.</p>`;
    }
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
    : `<span class="text-xs font-semibold text-slate-700 bg-slate-100 px-2 py-0.5 rounded-full">Rule-based (AI fallback)</span>`;

  const box = document.getElementById('adv-chat-understood');
  if (box) {
    box.classList.remove('hidden');
    box.innerHTML = `<div class="flex flex-wrap items-center gap-1.5">${src}${chips.map(c =>
      `<span class="text-xs text-slate-700 bg-white border border-slate-200 px-2 py-0.5 rounded-full">${escapeHtml(c)}</span>`).join('')}</div>`;
    if (window.lucide) lucide.createIcons();
  }
}

function renderClarifications(list) {
  const box = document.getElementById('adv-chat-clarify');
  if (!box) return;
  if (!list.length) {
    box.classList.add('hidden');
    box.innerHTML = '';
    return;
  }
  const q = list[0]; // one question at a time
  const question = currentLanguage === 'hi' ? (q.question_hi || q.question) : (q.question_en || q.question);
  box.classList.remove('hidden');
  box.innerHTML = `
    <p class="text-sm text-slate-800 mb-2 font-medium">${escapeHtml(question)}</p>
    <div class="flex flex-wrap gap-2">
      ${(q.options || []).map(o => `
        <button type="button" class="min-h-[44px] px-3.5 text-sm font-medium border border-slate-300 rounded-xl hover:border-airtel-red bg-white text-slate-800 shadow-sm transition"
          onclick="sendAdvisorChat(${escapeHtml(JSON.stringify(o))})">
          ${escapeHtml(o)}
        </button>
      `).join('')}
    </div>
  `;
}

function syncFormFromProfile(p) {
  if (p.segment && SEGMENT_TO_BIZ[p.segment]) {
    const el = document.getElementById('adv-biz-type');
    if (el) el.value = SEGMENT_TO_BIZ[p.segment];
  }
  if (p.city_tier) {
    const el = document.getElementById('adv-city-tier');
    if (el) el.value = String(p.city_tier);
  }
  if (p.city) {
    const el = document.getElementById('adv-city-name');
    if (el) el.value = p.city;
  }
  if (p.employee_count) {
    const el = document.getElementById('adv-employees');
    if (el) el.value = p.employee_count;
  }
  if (p.num_sites) {
    const el = document.getElementById('adv-sites');
    if (el) el.value = p.num_sites;
  }
  if (p.has_gstin != null) {
    const radio = document.querySelector(`input[name="adv-has-gst"][value="${p.has_gstin ? 'yes' : 'no'}"]`);
    if (radio) radio.checked = true;
  }
}

// Load Catalogue from Backend API
async function loadCatalogue() {
  try {
    const res = await fetch('/api/catalogue');
    const data = await res.json();
    allProducts = data.products;
    renderCatalogList();
    recalculateQuotePricing();
  } catch (err) {
    console.error("Failed to load catalogue:", err);
  }
}

// ---- Quote tab -------------------------------------------------------------------------------------------
function toast(message, kind = 'info') {
  let host = document.getElementById('toast-host');
  if (!host) {
    host = document.createElement('div');
    host.id = 'toast-host';
    host.setAttribute('aria-live', 'polite');
    document.body.appendChild(host);
  }
  const t = document.createElement('div');
  t.className = `toast toast-${kind}`;
  t.textContent = message;
  host.appendChild(t);
  setTimeout(() => t.remove(), 4000);
}

const inr = n => '₹' + Number(n || 0).toLocaleString('en-IN');
const customerHasGst = () => document.querySelector('input[name="adv-has-gst"]:checked')?.value !== 'no';

function renderCatalogList() {
  const container = document.getElementById('catalog-products-list');
  if (!container) return;
  const nameOf = id => (allProducts.find(x => x.product_id === id) || {}).product_name || id;
  const hasGst = customerHasGst();

  const filtered = activeCategoryFilter === 'all' ? allProducts : allProducts.filter(p => p.category === activeCategoryFilter);
  container.innerHTML = filtered.map(p => {
    const on = selectedProductIds.has(p.product_id);
    const locked = p.requires_gstin && !hasGst && !on;
    const recommended = recommendedProductIds.has(p.product_id);
    const dep = (p.requires_one_of || []).length
      ? `<p class="prow-note">Needs a base connection: ${escapeHtml(p.requires_one_of.slice(0, 2).map(nameOf).join(' or '))}${p.requires_one_of.length > 2 ? ' …' : ''}</p>` : '';
    const lockNote = locked ? `<p class="prow-note">Available once a GSTIN is registered.</p>` : '';
    return `
      <label class="prow${on ? ' is-on' : ''}${locked ? ' is-locked' : ''}">
        <input type="checkbox" class="chk" ${on ? 'checked' : ''} ${locked ? 'disabled' : ''}
               aria-label="${escapeHtml(p.product_name)}" onchange="toggleProductSelection('${p.product_id}', this.checked)">
        <div class="min-w-0 flex-1">
          <div class="flex items-center flex-wrap gap-x-2 gap-y-1">
            <span class="prow-name">${escapeHtml(p.product_name)}</span>
            <span class="badge">${escapeHtml(p.category)}</span>
            ${recommended ? '<span class="badge badge-info">Recommended</span>' : ''}
            ${p.requires_gstin ? '<span class="badge badge-warn">Needs GSTIN</span>' : ''}
          </div>
          <p class="prow-desc">${escapeHtml(p.description)}</p>
          ${dep}${lockNote}
        </div>
        <div class="prow-price">
          <span class="tabular"><b>${inr(p.price_min_inr_per_month)}</b>/mo</span>
          <span class="prow-setup tabular">Setup ${inr(p.one_time_setup_inr)}</span>
        </div>
      </label>`;
  }).join('');
}

function filterCatalogCategory(cat) {
  activeCategoryFilter = cat;
  document.querySelectorAll('.chips-scroll .chip').forEach(btn => btn.classList.toggle('is-on', btn.dataset.cat === cat));
  renderCatalogList();
}

function toggleProductSelection(pid, checked) {
  if (checked) selectedProductIds.add(pid); else selectedProductIds.delete(pid);
  recalculateQuotePricing();
  renderCatalogList();
}

function showBill(hasItems) {
  document.getElementById('bill-empty')?.classList.toggle('hidden', hasItems);
  document.getElementById('bill-body')?.classList.toggle('hidden', !hasItems);
  const btn = document.getElementById('btn-continue-kyc');
  if (btn) btn.disabled = !hasItems;
  document.getElementById('q-mobilebar')?.classList.toggle('hidden', !hasItems);
}

// Recalculate live quote pricing and dependency/eligibility notices
async function recalculateQuotePricing() {
  const items = Array.from(selectedProductIds).map(pid => ({ product_id: pid, quantity: productQuantities[pid] || 1 }));
  if (items.length === 0) {
    showBill(false);
    const box = document.getElementById('bill-validation-alerts');
    if (box) box.innerHTML = '';
    return;
  }

  try {
    const res = await fetch('/api/catalogue/pricing', {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ items })
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const pricing = await res.json();
    showBill(true);

    document.getElementById('bill-item-count').textContent = `${pricing.items.length} product${pricing.items.length === 1 ? '' : 's'}`;
    document.getElementById('bill-setup-fee').textContent = inr(pricing.setup_total_inr);
    document.getElementById('bill-contract').textContent = `${pricing.contract_lock_months} Months`;
    document.getElementById('bill-install-days').textContent = `${pricing.estimated_install_sla_days} Days`;
    document.getElementById('bill-monthly-total').innerHTML = `${inr(pricing.monthly_total_inr)}<span class="text-sm text-slate-500 font-normal">/mo</span>`;
    const qm = document.getElementById('qm-total'); if (qm) qm.textContent = inr(pricing.monthly_total_inr) + '/mo';

    const saveEl = document.getElementById('bill-savings');
    const yearly = pricing.vendor_savings_benchmark?.annual_savings_inr;
    if (saveEl) {
      saveEl.classList.toggle('hidden', !yearly);
      if (yearly) saveEl.innerHTML = `<i data-lucide="trending-down" class="w-4 h-4" aria-hidden="true"></i><span><b>${inr(yearly)} a year</b> saved compared with buying these from separate local vendors.</span>`;
    }

    const valRes = await fetch('/api/catalogue/validate', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        selected_product_ids: Array.from(selectedProductIds),
        city_tier: parseInt(document.getElementById('adv-city-tier')?.value || '1'),
        employee_count: parseInt(document.getElementById('adv-employees')?.value) || 2,
        num_sites: parseInt(document.getElementById('adv-sites')?.value) || 1,
        has_gstin: customerHasGst()
      })
    });
    const val = await valRes.json();
    const alertBox = document.getElementById('bill-validation-alerts');
    if (alertBox) {
      alertBox.innerHTML = (!val.is_valid && val.errors.length)
        ? `<div class="notice notice-warn" role="alert"><i data-lucide="alert-triangle" class="w-4 h-4 shrink-0 mt-0.5" aria-hidden="true"></i>
             <div><b>Check this bundle</b>${val.errors.map(e => `<div>${escapeHtml(e)}</div>`).join('')}</div></div>`
        : '';
    }
    if (window.lucide) lucide.createIcons();
  } catch (err) {
    console.error('Pricing calculation error:', err);
    toast("Couldn't update the price. Please try again.", 'error');
  }
}

// Submit Advisor Form
async function submitAdvisorProfile() {
  const bizType = document.getElementById('adv-biz-type').value;
  const tier = parseInt(document.getElementById('adv-city-tier').value);
  const employees = parseInt(document.getElementById('adv-employees').value);
  const sites = parseInt(document.getElementById('adv-sites').value);
  const hasGst = document.querySelector('input[name="adv-has-gst"]:checked').value === 'yes';
  const spend = parseInt(document.getElementById('adv-current-spend').value) || 0;

  // Don't recommend anything until we actually know the business.
  const errEl = document.getElementById('adv-form-error');
  const problems = [];
  if (!bizType) problems.push('business type');
  if (!employees || employees < 1) problems.push('number of staff');
  if (!sites || sites < 1) problems.push('number of sites');
  if (errEl) {
    errEl.classList.toggle('hidden', problems.length === 0);
    errEl.textContent = problems.length ? `Please add the ${problems.join(' and ')} so we can recommend the right bundle.` : '';
  }
  if (problems.length) return;

  const payload = {
    business_type: bizType,
    city_tier: tier,
    employee_count: employees,
    num_sites: sites,
    has_gstin: hasGst,
    current_spend: spend,
    preferred_language: currentLanguage
  };

  const loadingEl = document.getElementById('advisor-loading');
  const contentEl = document.getElementById('advisor-content');
  if (loadingEl) loadingEl.classList.remove('hidden');
  if (contentEl) contentEl.classList.add('opacity-40');

  try {
    const res = await fetch('/api/advisor/recommend', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    currentRecommendation = data;
    renderAdvisorRecommendation(data);
  } catch (err) {
    console.error("Advisor error:", err);
  } finally {
    if (loadingEl) loadingEl.classList.add('hidden');
    if (contentEl) contentEl.classList.remove('opacity-40');
  }
}

// Render Advisor Recommendation Result Card
function renderAdvisorRecommendation(data) {
  const emptyEl = document.getElementById('advisor-empty');
  if (emptyEl) emptyEl.classList.add('hidden');
  const contentEl0 = document.getElementById('advisor-content');
  if (contentEl0) contentEl0.classList.remove('hidden');
  document.getElementById('rec-bundle-title').textContent = data.bundle_name;
  document.getElementById('rec-price').innerHTML = `₹${data.pricing.monthly_total_inr.toLocaleString('en-IN')}<span class="text-xs text-slate-500 font-normal"> /mo</span>`;
  document.getElementById('rec-contract').textContent = `${data.pricing.contract_lock_months} Months`;
  document.getElementById('rec-install').textContent = `${data.pricing.estimated_install_sla_days} Days`;
  const vb = data.pricing.vendor_savings_benchmark || {};
  document.getElementById('kpi-monthly').textContent = inr(data.pricing.monthly_total_inr);
  document.getElementById('kpi-setup').textContent = inr(data.pricing.one_time_setup_total_inr);
  document.getElementById('kpi-save').textContent = vb.annual_savings_inr ? `${inr(vb.annual_savings_inr)} / yr` : '—';
  document.getElementById('kpi-sla').textContent = `${data.pricing.estimated_install_sla_days} days`;

  // Reasoning points - strip emoji, use check-circle-2 icon
  const listEl = document.getElementById('rec-reasoning-list');
  if (listEl && data.reasoning) {
    listEl.innerHTML = data.reasoning.map(pt => `
      <div class="flex items-start gap-2">
        <i data-lucide="check-circle-2" class="w-4 h-4 mt-0.5 text-ok shrink-0" aria-hidden="true"></i>
        <span class="text-sm text-slate-700 leading-relaxed">${escapeHtml(pt.replace(/^\p{Extended_Pictographic}️?\s*/u, ''))}</span>
      </div>
    `).join('');
  }

  // Products table
  const tbody = document.getElementById('rec-products-table');
  if (tbody && data.pricing?.items) {
    tbody.innerHTML = data.pricing.items.map(it => `
      <tr class="hover:bg-slate-50/50">
        <td class="py-2.5 px-3 font-semibold text-slate-800 text-sm">${escapeHtml(it.product_name)}</td>
        <td class="py-2.5 px-3 text-slate-600 text-xs">${escapeHtml(it.category)}</td>
        <td class="py-2.5 px-3 text-center font-mono text-sm text-slate-800 tabular">${it.quantity}</td>
        <td class="py-2.5 px-3 text-right font-bold text-slate-900 text-sm tabular">₹${it.total_monthly_inr.toLocaleString('en-IN')}</td>
      </tr>
    `).join('');
  }

  // Sync selected products to Quote tab
  selectedProductIds = new Set(data.selected_product_ids);
  recommendedProductIds = new Set(data.selected_product_ids);
  productQuantities = Object.fromEntries((data.pricing?.items || []).map(it => [it.product_id, it.quantity]));
  renderCatalogList();
  recalculateQuotePricing();

  if (window.lucide) lucide.createIcons();
}

// Pre-canned Quick Scenarios for Live Testing
function loadScenario(type) {
  if (type === 'kirana_no_gst') {
    document.getElementById('adv-biz-type').value = 'Kirana & Retail Store';
    document.getElementById('adv-city-tier').value = '2';
    document.getElementById('adv-city-name').value = 'Ludhiana';
    document.getElementById('adv-employees').value = '2';
    document.getElementById('adv-sites').value = '1';
    document.querySelector('input[name="adv-has-gst"][value="no"]').checked = true;
    document.getElementById('adv-current-spend').value = '1500';
  } else if (type === 'clinic_pro') {
    document.getElementById('adv-biz-type').value = 'Clinic & Healthcare';
    document.getElementById('adv-city-tier').value = '1';
    document.getElementById('adv-city-name').value = 'Bengaluru';
    document.getElementById('adv-employees').value = '4';
    document.getElementById('adv-sites').value = '1';
    document.querySelector('input[name="adv-has-gst"][value="yes"]').checked = true;
    document.getElementById('adv-current-spend').value = '3500';
  } else if (type === 'multi_store') {
    document.getElementById('adv-biz-type').value = 'Restaurant & Food Chain';
    document.getElementById('adv-city-tier').value = '1';
    document.getElementById('adv-city-name').value = 'Mumbai';
    document.getElementById('adv-employees').value = '15';
    document.getElementById('adv-sites').value = '3';
    document.querySelector('input[name="adv-has-gst"][value="yes"]').checked = true;
    document.getElementById('adv-current-spend').value = '8000';
  } else if (type === 'small_mfg') {
    document.getElementById('adv-biz-type').value = 'Small Manufacturing & Workshop';
    document.getElementById('adv-city-tier').value = '1';
    document.getElementById('adv-city-name').value = 'Pune';
    document.getElementById('adv-employees').value = '12';
    document.getElementById('adv-sites').value = '1';
    document.querySelector('input[name="adv-has-gst"][value="yes"]').checked = true;
    document.getElementById('adv-current-spend').value = '12000';
  }
  submitAdvisorProfile();
}

function proceedToKYCFromAdvisor() {
  switchTab('kyc');
}

// Load KYC Test Applicants (K01-K12)
async function loadKYCApplicants() {
  try {
    const res = await fetch('/api/kyc/applicants');
    const data = await res.json();
    const select = document.getElementById('kyc-applicant-select');
    select.innerHTML = `<option value="">Select an applicant…</option>` + 
      data.applicants.map(a => `
        <option value="${a.code}">
          ${a.code} · ${a.business_name}
        </option>
      `).join('');
  } catch (err) {
    console.error("Failed to load KYC applicants:", err);
  }
}

// On Test Applicant Selected in Dropdown
async function onApplicantSelected(code) {
  if (!code) return;
  if (!requireConsent()) {
    document.getElementById('kyc-applicant-select').value = '';
    return;
  }
  try {
    const res = await fetch('/api/kyc/applicants');
    const data = await res.json();
    const applicant = data.applicants.find(a => a.code === code);
    if (!applicant) return;

    currentApplicant = applicant;

    // Prefill fields based on applicant
    if (code === 'K01') {
      document.getElementById('kyc-input-gstin').value = '37IHKXV5167L1ZS';
      document.getElementById('kyc-input-udyam').value = 'UDYAM-TS-00-8751054';
      document.getElementById('kyc-input-date').value = '2026-06-26';
    } else if (code === 'K02') {
      document.getElementById('kyc-input-gstin').value = '19EOGXH4115Y1ZL';
      document.getElementById('kyc-input-udyam').value = 'UDYAM-WB-00-5053330';
      document.getElementById('kyc-input-date').value = '2026-05-22';
    } else if (code === 'K04') {
      document.getElementById('kyc-input-gstin').value = '27PZSXS1936O1ZH';
      document.getElementById('kyc-input-udyam').value = 'UDYAM-MH-00-6131836';
      document.getElementById('kyc-input-date').value = '2026-05-28';
    } else if (code === 'K05') {
      document.getElementById('kyc-input-gstin').value = '27RXYXB9017K1ZY';
      document.getElementById('kyc-input-udyam').value = '';
      document.getElementById('kyc-input-date').value = '2026-06-11';
    } else if (code === 'K11') {
      document.getElementById('kyc-input-gstin').value = '29NFXXT0330H1Z7';
      document.getElementById('kyc-input-udyam').value = 'UDYAM-KR-00-6326107';
      document.getElementById('kyc-input-date').value = '2025-10-31';
    } else {
      document.getElementById('kyc-input-date').value = '2026-06-15';
    }

    // Run verification automatically
    runSmartKYCVerification();
  } catch (err) {
    console.error("Applicant selection error:", err);
  }
}

// Load Specimen Documents for Sandbox Upload testing
async function loadDocSpecimen(code) {
  if (!requireConsent()) return;
  const consent = document.getElementById('dpdp-consent-chk').checked;
  try {
    const res = await fetch('/api/kyc/verify-applicant', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ applicant_code: code, consent_granted: consent })
    });
    const data = await res.json();
    renderKYCDiagnostics(data);
    
    // Set file upload preview
    const filesList = document.getElementById('uploaded-files-list');
    if (filesList) {
      filesList.classList.remove('hidden');
      filesList.innerHTML = `
        <div class="flex items-center justify-between text-slate-700 bg-white p-2 rounded-lg border border-slate-200">
          <span class="flex items-center gap-1.5"><i data-lucide="file-text" class="w-4 h-4 text-slate-500"></i>${code}_gst_certificate.png (${data.extracted_fields?.gstin ? 'Extracted GSTIN: ' + data.extracted_fields.gstin : 'Unreadable/Corrupt'})</span>
          <span class="text-ok font-bold text-xs flex items-center gap-1"><i data-lucide="check-circle-2" class="w-3.5 h-3.5"></i>Loaded</span>
        </div>
        <div class="flex items-center justify-between text-slate-700 bg-white p-2 rounded-lg border border-slate-200">
          <span class="flex items-center gap-1.5"><i data-lucide="file-text" class="w-4 h-4 text-slate-500"></i>${code}_udyam_certificate.png (${data.extracted_fields?.udyam_number || 'Missing'})</span>
          <span class="text-ok font-bold text-xs flex items-center gap-1"><i data-lucide="check-circle-2" class="w-3.5 h-3.5"></i>Loaded</span>
        </div>
        <div class="flex items-center justify-between text-slate-700 bg-white p-2 rounded-lg border border-slate-200">
          <span class="flex items-center gap-1.5"><i data-lucide="file-text" class="w-4 h-4 text-slate-500"></i>${code}_address_proof.png (Date: ${data.extracted_fields?.bill_date || 'Missing'})</span>
          <span class="text-ok font-bold text-xs flex items-center gap-1"><i data-lucide="check-circle-2" class="w-3.5 h-3.5"></i>Loaded</span>
        </div>
      `;
      if (window.lucide) lucide.createIcons();
    }

    if (data.extracted_fields?.gstin) {
      document.getElementById('kyc-input-gstin').value = data.extracted_fields.gstin;
      const gstTa = document.getElementById('ocr-gst-text');
      if (gstTa) gstTa.value = `Specimen GST Registration Certificate Format for testing\nGSTIN: ${data.extracted_fields.gstin}\nLegal name: ${data.extracted_fields.legal_name || ''}\nTrade name: ${data.extracted_fields.trade_name || ''}\nType of registration ${data.extracted_fields.gstin}`;
    } else {
      const gstTa = document.getElementById('ocr-gst-text');
      if (gstTa) gstTa.value = "GST Registration Certificate";
    }
    if (data.extracted_fields?.udyam_number) {
      document.getElementById('kyc-input-udyam').value = data.extracted_fields.udyam_number;
      const udyamTa = document.getElementById('ocr-udyam-text');
      if (udyamTa) udyamTa.value = `Specimen Udyam Registration Certificate\nUdyam reg. number ${data.extracted_fields.udyam_number}\nEnterprise name ${data.business_name}\nMajor activity Services Date of registration 2024-01-01`;
    } else {
      const udyamTa = document.getElementById('ocr-udyam-text');
      if (udyamTa) udyamTa.value = "";
    }
    if (data.extracted_fields?.bill_date) {
      document.getElementById('kyc-input-date').value = data.extracted_fields.bill_date;
      const addrTa = document.getElementById('ocr-addr-text');
      if (addrTa) addrTa.value = `Electricity Bill Specimen\nBilled to Supply address Bill date Units Amount\n12345 ${data.business_name} Shop 1, City ${data.extracted_fields.bill_date} 500 2500`;
    }
  } catch (err) {
    console.error("Error loading specimen:", err);
  }
}

// Handle Real File Upload via FormData with OCR
async function handleFileUpload(event) {
  if (!requireConsent()) return;
  const files = event?.target?.files || event?.dataTransfer?.files;
  if (!files || files.length === 0) return;

  const OK_EXT = ['png', 'jpg', 'jpeg', 'webp', 'txt'];
  const problems = [];
  if (files.length > 8) problems.push(`You chose ${files.length} files. The maximum is 8.`);
  for (const f of files) {
    const ext = f.name.split('.').pop().toLowerCase();
    if (!OK_EXT.includes(ext)) problems.push(`${f.name}: ${ext.toUpperCase()} isn't supported. Use PNG, JPG or WEBP.`);
    else if (f.size > 4 * 1024 * 1024) problems.push(`${f.name}: ${(f.size / 1048576).toFixed(1)} MB is over the 4 MB limit.`);
  }

  const errBox = document.getElementById('upload-errors-list');
  if (problems.length) {
    if (errBox) {
      errBox.classList.remove('hidden');
      errBox.innerHTML = problems.map(p => `<div><i data-lucide="alert-triangle" class="w-3.5 h-3.5 inline mr-1 text-err"></i>${escapeHtml(p)}</div>`).join('');
      if (window.lucide) lucide.createIcons();
    }
    return;
  }
  if (errBox) {
    errBox.classList.add('hidden');
    errBox.innerHTML = '';
  }

  const filesList = document.getElementById('uploaded-files-list');
  if (filesList) {
    filesList.classList.remove('hidden');
    filesList.innerHTML = `
      <div class="p-2.5 bg-info-soft border border-sky-200 rounded-lg text-info flex items-center gap-2 mb-2">
        <span class="inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"></span>
        <span class="font-semibold text-xs">Reading ${files.length} document${files.length > 1 ? 's' : ''}… this takes about 10–20 seconds</span>
      </div>
      ` + Array.from(files).map(f => `
      <div class="flex items-center justify-between text-slate-700 bg-white p-2 rounded-lg border border-slate-200">
        <span class="flex items-center gap-1.5"><i data-lucide="file-text" class="w-4 h-4 text-slate-500"></i>${escapeHtml(f.name)} (${Math.round(f.size/1024)} KB)</span>
        <span class="text-info font-bold text-xs flex items-center gap-1"><span class="inline-block w-3 h-3 border border-current border-t-transparent rounded-full animate-spin"></span>OCR...</span>
      </div>
    `).join('');
    if (window.lucide) lucide.createIcons();
  }

  const consent = document.getElementById('dpdp-consent-chk')?.checked;
  const formData = new FormData();
  for (const f of files) {
    formData.append('files', f);
  }
  formData.append('consent_granted', consent);

  try {
    const res = await fetch('/api/kyc/upload-files', {
      method: 'POST',
      body: formData
    });
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      let msg = errData.detail || `Upload failed with status ${res.status}`;
      if (res.status === 413) msg = "One file is over 4 MB.";
      throw new Error(msg);
    }
    const data = await res.json();

    if (filesList) {
      filesList.innerHTML = Array.from(files).map(f => {
        let typeLabel = "Document read";
        if (data.extracted_snippets) {
          for (const [docKey, info] of Object.entries(data.extracted_snippets)) {
            if (info && (info.filename === f.name || f.name.toLowerCase().includes(docKey.replace('_', '')))) {
              typeLabel = docKey.replace(/_/g, ' ');
            }
          }
        }
        return `
          <div class="flex items-center justify-between text-slate-700 bg-white p-2 rounded-lg border border-slate-200">
            <span class="flex items-center gap-1.5"><i data-lucide="file-text" class="w-4 h-4 text-slate-500"></i>${escapeHtml(f.name)} (${Math.round(f.size/1024)} KB)</span>
            <span class="text-ok font-bold text-xs flex items-center gap-1"><i data-lucide="check-circle-2" class="w-3.5 h-3.5"></i>${escapeHtml(typeLabel)} ✓</span>
          </div>
        `;
      }).join('');
      if (window.lucide) lucide.createIcons();
    }

    if (data.extracted_snippets) {
      if (data.extracted_snippets.gst_certificate) {
        const gstTa = document.getElementById('ocr-gst-text');
        if (gstTa) gstTa.value = data.extracted_snippets.gst_certificate.preview;
      }
      if (data.extracted_snippets.udyam_certificate) {
        const udyamTa = document.getElementById('ocr-udyam-text');
        if (udyamTa) udyamTa.value = data.extracted_snippets.udyam_certificate.preview;
      }
      if (data.extracted_snippets.address_proof) {
        const addrTa = document.getElementById('ocr-addr-text');
        if (addrTa) addrTa.value = data.extracted_snippets.address_proof.preview;
      }
    }

    if (data.verification) {
      renderKYCDiagnostics(data.verification);
    }
  } catch (err) {
    console.error("File upload OCR error:", err);
    if (errBox) {
      errBox.classList.remove('hidden');
      errBox.innerHTML = `<div><i data-lucide="alert-triangle" class="w-3.5 h-3.5 inline mr-1 text-err"></i>${escapeHtml(err.message)}</div>`;
      if (window.lucide) lucide.createIcons();
    }
  }
}

// Upload & Verify KYC Documents
async function uploadAndVerifyKYCDocuments() {
  if (!requireConsent()) return;
  const consent = document.getElementById('dpdp-consent-chk').checked;
  const gstText = document.getElementById('ocr-gst-text')?.value || document.getElementById('kyc-input-gstin')?.value || "";
  const udyamText = document.getElementById('ocr-udyam-text')?.value || document.getElementById('kyc-input-udyam')?.value || "";
  const addrDate = document.getElementById('kyc-input-date')?.value || "2026-06-15";
  const addrText = document.getElementById('ocr-addr-text')?.value || `Bill date ${addrDate} Electricity Bill`;

  try {
    const res = await fetch('/api/kyc/upload-and-verify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        applicant_code: 'CUSTOM_UPLOAD',
        business_name: 'Uploaded Business Entity',
        gst_certificate_text: gstText,
        udyam_certificate_text: udyamText,
        address_proof_text: addrText,
        signatory_id_text: "Name: Authorized Signatory Designation: Owner Valid till 2029-01-01",
        consent_granted: consent
      })
    });
    const result = await res.json();
    renderKYCDiagnostics(result);
  } catch (err) {
    console.error("Upload and verify error:", err);
  }
}

// Run Smart KYC Verification on selected applicant
async function runSmartKYCVerification() {
  if (!requireConsent()) return;
  const code = document.getElementById('kyc-applicant-select').value || 'K02';
  const consent = document.getElementById('dpdp-consent-chk').checked;

  try {
    const res = await fetch('/api/kyc/verify-applicant', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ applicant_code: code, consent_granted: consent })
    });
    const result = await res.json();
    renderKYCDiagnostics(result);
  } catch (err) {
    console.error("KYC verification error:", err);
  }
}

// Render KYC Diagnostics & Checklist
function renderKYCDiagnostics(res) {
  updateKycStepper(res.verdict);
  const banner = document.getElementById('kyc-verdict-banner');
  const orderBtn = document.getElementById('btn-place-order');
  const orderHint = document.getElementById('btn-place-order-hint');

  if (banner) {
    if (res.verdict === 'PASS') {
      banner.className = 'rounded-xl p-4 mb-4 border flex items-center space-x-3 bg-ok-soft border-emerald-200 text-slate-900';
      banner.innerHTML = `
        <i data-lucide="check-circle-2" class="w-6 h-6 text-ok shrink-0"></i>
        <div>
          <span class="text-sm font-bold block text-slate-900" id="kyc-verdict-title">VERIFIED: ${escapeHtml(res.business_name)} (Signatory: ${escapeHtml(res.signatory)})</span>
          <span class="text-xs text-slate-600" id="kyc-verdict-desc">${escapeHtml(res.summary)}</span>
        </div>
      `;
      if (orderBtn) orderBtn.disabled = false;
      if (orderHint) orderHint.classList.add('hidden');
    } else {
      banner.className = 'rounded-xl p-4 mb-4 border flex items-center space-x-3 bg-err-soft border-red-200 text-slate-900';
      banner.innerHTML = `
        <i data-lucide="x-circle" class="w-6 h-6 text-err shrink-0"></i>
        <div>
          <span class="text-sm font-bold block text-slate-900" id="kyc-verdict-title">REJECTED: ${escapeHtml(res.business_name || 'Verification Failed')}</span>
          <span class="text-xs text-slate-600" id="kyc-verdict-desc">${escapeHtml(res.summary)}</span>
        </div>
      `;
      if (orderBtn) orderBtn.disabled = true;
      if (orderHint) orderHint.classList.remove('hidden');
    }
  }

  // Update extracted fields in input boxes
  if (res.extracted_fields) {
    if (res.extracted_fields.gstin) {
      document.getElementById('kyc-input-gstin').value = res.extracted_fields.gstin;
    }
    if (res.extracted_fields.udyam_number) {
      document.getElementById('kyc-input-udyam').value = res.extracted_fields.udyam_number;
    }
    if (res.extracted_fields.bill_date) {
      document.getElementById('kyc-input-date').value = res.extracted_fields.bill_date;
    }
  }

  // Checklist - sort FAILED first, then WARNING, then PASSED (G14 requirement)
  const checklistEl = document.getElementById('kyc-checklist-container');
  if (checklistEl && res.checklist) {
    const items = [...res.checklist].sort((a, b) => {
      const order = { 'FAILED': 0, 'WARNING': 1, 'PASSED': 2 };
      return (order[a.status] ?? 3) - (order[b.status] ?? 3);
    });

    checklistEl.innerHTML = items.map(item => {
      let icon = 'check-circle-2';
      let iconClass = 'text-ok';
      let badgeClass = 'text-ok bg-ok-soft border-emerald-200';
      if (item.status === 'FAILED') {
        icon = 'x-circle';
        iconClass = 'text-err';
        badgeClass = 'text-err bg-err-soft border-red-200';
      } else if (item.status === 'WARNING') {
        icon = 'alert-triangle';
        iconClass = 'text-warn';
        badgeClass = 'text-warn bg-warn-soft border-amber-200';
      }

      return `
        <div class="p-3 rounded-xl border border-slate-200 bg-white flex items-start justify-between gap-3 text-sm">
          <div class="flex items-start gap-2.5">
            <i data-lucide="${icon}" class="w-5 h-5 ${iconClass} shrink-0 mt-0.5"></i>
            <div>
              <span class="font-bold text-slate-900 block">${escapeHtml(item.name)}</span>
              <p class="text-xs text-slate-600 mt-0.5 leading-relaxed">${escapeHtml(item.detail)}</p>
            </div>
          </div>
          <span class="text-xs font-bold px-2 py-0.5 rounded-full border ${badgeClass} uppercase shrink-0">
            ${escapeHtml(item.status)}
          </span>
        </div>
      `;
    }).join('');
  }

  if (window.lucide) lucide.createIcons();
}

// Manual GST Lookup
async function lookupGSTINManually() {
  if (!requireConsent()) return;
  const gstin = document.getElementById('kyc-input-gstin').value.trim();
  const box = document.getElementById('gst-lookup-result');
  box.classList.remove('hidden');

  try {
    const res = await fetch(`/api/registry/gstin/${gstin}`);
    const data = await res.json();
    if (data.found) {
      box.innerHTML = `
        <div class="p-3 bg-ok-soft border border-emerald-200 rounded-xl text-slate-900 text-xs">
          <div class="flex justify-between items-center">
            <strong class="font-bold text-slate-900">${escapeHtml(data.legal_name)}</strong>
            <span class="text-xs bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded uppercase">${escapeHtml(data.status)}</span>
          </div>
          <p class="text-xs mt-1 text-slate-600 leading-relaxed">${escapeHtml(data.trade_name)} · ${escapeHtml(data.principal_place_of_business)}, ${escapeHtml(data.state)}</p>
        </div>
      `;
    } else {
      box.innerHTML = `
        <div class="p-3 bg-err-soft border border-red-200 rounded-xl text-slate-900 text-xs">
          <strong class="text-err">Not Verified:</strong> ${escapeHtml(data.message)}
        </div>
      `;
    }
  } catch (err) {
    box.innerHTML = `<div class="p-2 text-err text-xs">Error connecting to registry.</div>`;
  }
}

// Manual Udyam Lookup
async function lookupUdyamManually() {
  if (!requireConsent()) return;
  const udyam = document.getElementById('kyc-input-udyam').value.trim();
  const box = document.getElementById('udyam-lookup-result');
  box.classList.remove('hidden');

  try {
    const res = await fetch(`/api/registry/udyam/${udyam}`);
    const data = await res.json();
    if (data.found) {
      box.innerHTML = `
        <div class="p-3 bg-ok-soft border border-emerald-200 rounded-xl text-slate-900 text-xs">
          <div class="flex justify-between items-center">
            <strong class="font-bold text-slate-900">${escapeHtml(data.enterprise_name)}</strong>
            <span class="text-xs bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded uppercase">${escapeHtml(data.enterprise_type)}</span>
          </div>
          <p class="text-xs mt-1 text-slate-600 leading-relaxed">${escapeHtml(data.major_activity)} · ${escapeHtml(data.city)}, ${escapeHtml(data.state)}</p>
        </div>
      `;
    } else {
      box.innerHTML = `
        <div class="p-3 bg-err-soft border border-red-200 rounded-xl text-slate-900 text-xs">
          <strong class="text-err">Not Verified:</strong> ${escapeHtml(data.message)}
        </div>
      `;
    }
  } catch (err) {
    box.innerHTML = `<div class="p-2 text-err text-xs">Error connecting to registry.</div>`;
  }
}

// Place Order after KYC Pass
async function placeOrderAfterKYC() {
  const bizName = currentApplicant?.business_name || document.getElementById('adv-biz-type').value;
  const bundle = currentRecommendation?.bundle_name_en || 'Vyapar Booster Pack';
  const price = currentRecommendation?.pricing?.monthly_total_inr || 2597;
  const installDays = currentRecommendation?.pricing?.estimated_install_sla_days || 3;

  const payload = {
    business_name: bizName,
    contact_name: currentApplicant?.signatory || 'Business Owner',
    contact_phone: '+91 98450 12345',
    city: document.getElementById('adv-city-name')?.value || 'Visakhapatnam',
    bundle_name: bundle,
    monthly_amount_inr: price,
    estimated_install_days: installDays,
    selected_products: Array.from(selectedProductIds)
  };

  const btn = document.getElementById('btn-place-order');
  setBusy(btn, true, 'Placing order…');
  try {
    const res = await fetch('/api/orders/create', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const order = await res.json();
    lastCreatedOrderId = order.order_id;
    try {
      localStorage.setItem('vs_last_order', JSON.stringify(order));
      localStorage.setItem(`vs_order_${order.order_id}`, JSON.stringify(order));
    } catch (e) {}
    document.getElementById('tracker-order-id').value = order.order_id;
    renderOrderTracker(order);
    switchTab('tracker');
  } catch (err) {
    console.error("Order creation error:", err);
  } finally {
    setBusy(btn, false);
  }
}

// Fetch Order Status for Live Order Tracker
const digits10 = v => String(v || '').replace(/\D/g, '').slice(-10);

function trackerMessage(msg) {
  const el = document.getElementById('tracker-not-found-msg');
  if (!el) return;
  el.textContent = msg || '';
  el.classList.toggle('hidden', !msg);
}

function openSampleOrder() {
  document.getElementById('tracker-order-id').value = SAMPLE_ORDER_ID;
  document.getElementById('tracker-phone').value = '';
  fetchOrderStatus(SAMPLE_ORDER_ID, '');
}

function showTrackerHome() {
  document.getElementById('tracker-lookup').classList.remove('hidden');
  document.getElementById('tracker-order-view').classList.add('hidden');
  document.getElementById('tracker-empty').classList.remove('hidden');
  trackerMessage('');
  renderOrderHistory();
}

function savedOrders() {
  const out = [];
  try {
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith('vs_order_')) out.push(JSON.parse(localStorage.getItem(key)));
    }
  } catch (e) {}
  return out.filter(o => o && o.order_id && o.order_id !== SAMPLE_ORDER_ID)
            .sort((a, b) => String(b.created_at).localeCompare(String(a.created_at)));
}

function renderOrderHistory() {
  const box = document.getElementById('tracker-history');
  if (!box) return;
  const orders = savedOrders();
  if (!orders.length) {
    box.innerHTML = `<div class="px-4 py-8 text-center">
      <p class="text-sm font-semibold text-slate-800">No orders yet</p>
      <p class="text-sm text-slate-600 mt-1">Orders you place appear here. Start with the Advisor, then complete KYC.</p>
      <button type="button" onclick="switchTab('advisor')" class="btn-secondary mt-3">Go to Advisor</button>
    </div>`;
    return;
  }
  box.innerHTML = orders.map(o => `
    <button type="button" data-oid="${escapeHtml(o.order_id)}" class="w-full text-left px-4 py-3 min-h-[44px] hover:bg-slate-50 flex items-center justify-between gap-3">
      <span class="min-w-0">
        <span class="block text-sm font-semibold text-slate-900 truncate">${escapeHtml(o.business_name || 'Order')}</span>
        <span class="block text-sm text-slate-600 font-mono">${escapeHtml(o.order_id)} · ${escapeHtml(o.bundle_name || '')}</span>
      </span>
      <span class="text-sm font-semibold text-slate-700 shrink-0">${escapeHtml((o.current_stage_code || '').replace(/_/g, ' ').toLowerCase())}</span>
    </button>`).join('');
  box.querySelectorAll('button[data-oid]').forEach(b => b.addEventListener('click', () => {
    const o = orders.find(x => x.order_id === b.dataset.oid);
    document.getElementById('tracker-order-id').value = o.order_id;
    document.getElementById('tracker-phone').value = digits10(o.contact_phone);
    fetchOrderStatus(o.order_id, o.contact_phone);
  }));
}

async function fetchOrderStatus(orderId, phone) {
  const oid = (orderId || document.getElementById('tracker-order-id').value).trim().toUpperCase();
  const ph = phone !== undefined ? phone : document.getElementById('tracker-phone').value;
  if (!oid) { trackerMessage('Enter your order number.'); return; }
  const isSample = oid === SAMPLE_ORDER_ID;
  if (!isSample && digits10(ph).length < 10) {
    trackerMessage('Enter the 10-digit mobile number registered on this order.');
    return;
  }
  trackerMessage('');

  try {
    const res = await fetch(`/api/orders/${encodeURIComponent(oid)}?phone=${encodeURIComponent(digits10(ph))}`);
    if (res.ok) {
      const order = await res.json();
      if (!isSample) {
        try { localStorage.setItem(`vs_order_${order.order_id}`, JSON.stringify(order)); } catch (e) {}
      }
      renderOrderTracker(order);
      return;
    }
  } catch (err) {
    console.error('Tracking error:', err);
  }

  // Serverless cold start: fall back to a copy saved on this device, only if the mobile number matches too.
  try {
    const saved = JSON.parse(localStorage.getItem(`vs_order_${oid}`) || 'null');
    if (saved && digits10(saved.contact_phone) === digits10(ph)) {
      renderOrderTracker(saved, 'Showing the copy saved on this device.');
      return;
    }
  } catch (e) {}
  trackerMessage('No order found for that order number and mobile number. Check both and try again.');
}

function renderOrderTracker(order, note = null) {
  document.getElementById('tracker-lookup').classList.add('hidden');
  document.getElementById('tracker-order-view').classList.remove('hidden');
  document.getElementById('tracker-empty').classList.add('hidden');
  const sampleBadge = document.getElementById('tracker-sample-badge');
  if (sampleBadge) sampleBadge.classList.toggle('hidden', order.order_id !== SAMPLE_ORDER_ID);
  const notFoundEl = document.getElementById('tracker-not-found-msg');
  if (notFoundEl) {
    if (note) {
      notFoundEl.textContent = note;
      notFoundEl.classList.remove('hidden');
    } else {
      notFoundEl.classList.add('hidden');
    }
  }

  document.getElementById('trk-order-num').textContent = order.order_id;
  document.getElementById('trk-biz-name').textContent = order.business_name;
  document.getElementById('trk-bundle').textContent = order.bundle_name;
  document.getElementById('trk-est-date').textContent = order.estimated_activation_date || order.estimated_live_date || 'Within 2 Days';

  // Timeline stages
  const stages = order.stages || order.timeline || [];
  const timelineEl = document.getElementById('tracker-timeline');
  timelineEl.innerHTML = stages.map((st, idx) => {
    let dotClass = 'completed';
    let statusBadge = 'bg-ok-soft text-ok border-emerald-200';
    let statusText = 'Completed';

    if (st.status === 'IN_PROGRESS') {
      dotClass = 'in-progress';
      statusBadge = 'bg-info-soft text-info border-sky-200';
      statusText = 'In Progress';
    } else if (st.status === 'PENDING') {
      dotClass = 'pending';
      statusBadge = 'bg-slate-100 text-slate-600 border-slate-200';
      statusText = 'Pending';
    }

    return `
      <div class="flex items-start space-x-4 relative">
        <div class="timeline-dot ${dotClass}">
          ${idx + 1}
        </div>
        <div class="flex-1 pt-1">
          <div class="flex justify-between items-baseline">
            <h4 class="text-sm font-bold text-slate-900">${escapeHtml(st.name || st.stage_name)}</h4>
            <span class="text-xs font-bold px-2 py-0.5 rounded-full border ${statusBadge} uppercase">${statusText}</span>
          </div>
          <p class="text-xs text-slate-600 mt-0.5 leading-relaxed">${escapeHtml(st.detail || '')}</p>
          <span class="text-xs text-slate-500 tabular block mt-1">${escapeHtml(st.timestamp || st.updated_at || '')}</span>
        </div>
      </div>
    `;
  }).join('');

  // Technician Card
  if (order.technician) {
    document.getElementById('trk-tech-name').textContent = order.technician.name;
    document.getElementById('trk-tech-slot').textContent = `Slot: ${order.technician.slot}`;
    document.getElementById('trk-tech-pin').textContent = order.technician.installation_pin || order.technician.pin || '8492';
    document.getElementById('trk-tech-call').href = `tel:${order.technician.phone}`;
  }

  loadOrderNotifications(order);
  if (window.lucide) lucide.createIcons();
}

async function loadOrderNotifications(order) {
  const box = document.getElementById('tracker-notifs');
  if (!box) return;
  box.innerHTML = '<li class="skeleton" style="height:4.5rem"></li>';
  try {
    const ph = digits10(document.getElementById('tracker-phone').value || order.contact_phone);
    const res = await fetch(`/api/orders/${encodeURIComponent(order.order_id)}/notifications?phone=${ph}`);
    if (!res.ok) throw new Error(res.status);
    const hi = currentLanguage === 'hi';
    const items = (await res.json()).notifications || [];
    box.innerHTML = items.length ? items.slice().reverse().map(n => `
      <li class="trk-notif">
        <div class="flex items-baseline justify-between gap-2">
          <strong class="text-sm text-slate-900">${escapeHtml(n.title)}</strong>
          <span class="text-xs text-slate-500 shrink-0">${escapeHtml(n.channel)}</span>
        </div>
        <p class="text-sm text-slate-700 mt-1">${escapeHtml(hi ? n.message_hi : n.message_en)}</p>
        <span class="text-xs text-slate-500 tabular">${escapeHtml(n.timestamp || '')}</span>
      </li>`).join('') : '<li class="help">No messages yet.</li>';
  } catch (e) {
    box.innerHTML = '<li class="help">Messages are unavailable right now.</li>';
  }
}

// Load Partner Dropped Leads Portal
async function loadPartnerPortal() {
  try {
    const statsRes = await fetch('/api/partner/stats');
    const stats = await statsRes.json();
    document.getElementById('ptnr-dropped-leads').textContent = stats.total_dropped_leads.toLocaleString('en-IN');
    document.getElementById('ptnr-salvageable').textContent = stats.high_propensity_count.toLocaleString('en-IN');
    document.getElementById('ptnr-arr').textContent = `₹${(stats.projected_recoverable_arr_inr / 10000000).toFixed(2)} Cr`;
    document.getElementById('ptnr-comm').textContent = `₹${(stats.partner_commission_pool_inr / 100000).toFixed(1)} Lakh`;

    await loadPartnerLeads();
  } catch (err) {
    console.error("Partner portal error:", err);
  }
}

async function loadPartnerLeads() {
  const seg = document.getElementById('ptnr-filter-segment').value;
  const url = seg ? `/api/partner/leads?limit=12&segment=${encodeURIComponent(seg)}` : '/api/partner/leads?limit=40';
  try {
    const res = await fetch(url);
    const data = await res.json();
    partnerLeads = data.leads || [];
    const tbody = document.getElementById('ptnr-leads-table');
    tbody.innerHTML = partnerLeads.map((l, idx) => {
      return `
        <tr class="hover:bg-slate-50 text-sm">
          <td class="py-2.5 px-3">
            <span class="font-bold text-slate-800 block">${escapeHtml(l.business_name)}</span>
            <span class="text-xs font-mono text-slate-500">${escapeHtml(l.lead_id)} · ${l.employee_count} Staff</span>
            ${(l.reasons || []).length ? `<span class="flex flex-wrap gap-1 mt-1">${l.reasons.map(r => `<span class="badge">${escapeHtml(r)}</span>`).join('')}</span>` : ''}
          </td>
          <td class="py-2.5 px-3">
            <span class="text-slate-700 block">${escapeHtml(l.segment)}</span>
            <span class="text-xs text-slate-500">${escapeHtml(l.city)} (Tier ${l.city_tier})</span>
          </td>
          <td class="py-2.5 px-3">
            <span class="bg-slate-100 text-slate-700 text-xs font-semibold px-2 py-0.5 rounded">${escapeHtml(l.stage_reached)}</span>
          </td>
          <td class="py-2.5 px-3 text-slate-600 max-w-xs text-xs truncate" title="${escapeHtml(l.drop_reason)}">
            ${escapeHtml(l.drop_reason)}
          </td>
          <td class="py-2.5 px-3 text-center">
            <div class="flex items-center justify-center gap-1.5">
              <span class="text-xs font-bold text-slate-500">#${idx + 1}</span>
              <div class="w-12 h-1.5 rounded-full bg-slate-100 overflow-hidden inline-block">
                <div class="h-full rounded-full bg-ok" style="width:${l.propensity_score}%"></div>
              </div>
              <span class="text-xs font-bold text-slate-700 tabular" title="Rule-based propensity score out of 100. Ties are ranked by spend, team size and recency.">${l.propensity_score}</span>
            </div>
          </td>
          <td class="py-2.5 px-3 text-right">
            <button type="button" onclick="assistDroppedLead('${escapeHtml(l.lead_id)}')" class="btn-secondary btn-compact">
              1-Click Assist
            </button>
          </td>
        </tr>
      `;
    }).join('');
  } catch (err) {
    console.error("Failed to load partner leads:", err);
  }
}

// 1-Click Assist Dropped Lead
function assistDroppedLead(leadId) {
  const l = partnerLeads.find(x => x.lead_id === leadId);
  if (!l) return;
  switchTab('advisor');
  document.getElementById('adv-biz-type').value = LEAD_SEGMENT_TO_BIZ[l.segment] || 'Kirana & Retail Store';
  document.getElementById('adv-city-tier').value = String(l.city_tier);
  document.getElementById('adv-city-name').value = l.city || '';
  document.getElementById('adv-employees').value = l.employee_count;
  document.getElementById('adv-sites').value = l.segment === 'Small multi-site businesses' ? Math.max(2, l.num_sites || 2) : 1;
  const radio = document.querySelector(`input[name="adv-has-gst"][value="${l.has_gstin ? 'yes' : 'no'}"]`);
  if (radio) radio.checked = true;
  submitAdvisorProfile();
}


// ---- App shell: collapsible sidebar (drawer on small screens) ------------------------------------------------
const SIDEBAR_KEY = 'vs_sidebar_collapsed';
function toggleSidebar(force) {
  const small = window.innerWidth < 1024;
  const cls = small ? 'sidebar-open' : 'sidebar-collapsed';
  const current = document.body.classList.contains(cls);
  // force === true means "show": open the drawer, or un-collapse the rail. false means "hide".
  const next = force === undefined ? !current : (small ? force : !force);
  document.body.classList.toggle(cls, next);
  const shown = small ? next : !next;
  document.getElementById('sidebar-toggle')?.setAttribute('aria-expanded', String(shown));
  if (!small) { try { localStorage.setItem(SIDEBAR_KEY, next ? '1' : '0'); } catch (e) {} }
}
document.addEventListener('keydown', e => { if (e.key === 'Escape' && document.body.classList.contains('sidebar-open')) toggleSidebar(false); });
window.addEventListener('resize', () => { if (window.innerWidth >= 1024) document.body.classList.remove('sidebar-open'); });
try { if (localStorage.getItem(SIDEBAR_KEY) === '1' && window.innerWidth >= 1024) {
  document.body.classList.add('sidebar-collapsed');
  document.getElementById('sidebar-toggle')?.setAttribute('aria-expanded', 'false');
} } catch (e) {}

// ---- Resizable panels: <div class="splitter" data-var data-mode data-min data-max data-key> ------------------
function initSplitter(el) {
  const box = el.parentElement;
  const cssVar = el.dataset.var, mode = el.dataset.mode;
  const min = +el.dataset.min, max = +el.dataset.max, key = el.dataset.key;
  const OTHER_MIN = 340;   // the panel on the other side never gets narrower than this
  const apply = px => {
    const ceiling = Math.min(max, box.clientWidth - OTHER_MIN - el.offsetWidth);
    box.style.setProperty(cssVar, Math.max(min, Math.min(ceiling, Math.round(px))) + 'px');
  };
  const current = () => parseFloat(getComputedStyle(box).getPropertyValue(cssVar)) || (mode === 'left' ? el.previousElementSibling : el.nextElementSibling).getBoundingClientRect().width;
  try { const saved = localStorage.getItem(key); if (saved) apply(+saved); } catch (e) {}
  const save = () => { try { localStorage.setItem(key, String(parseFloat(box.style.getPropertyValue(cssVar)))); } catch (e) {} };

  el.addEventListener('pointerdown', ev => {
    ev.preventDefault();
    el.setPointerCapture(ev.pointerId);
    el.classList.add('is-dragging');
    document.body.classList.add('is-resizing');
  });
  el.addEventListener('pointermove', ev => {
    if (!el.classList.contains('is-dragging')) return;
    const r = box.getBoundingClientRect();
    apply(mode === 'left' ? ev.clientX - r.left : r.right - ev.clientX);
  });
  const stop = () => { el.classList.remove('is-dragging'); document.body.classList.remove('is-resizing'); save(); };
  el.addEventListener('pointerup', stop);
  el.addEventListener('pointercancel', stop);
  el.addEventListener('keydown', ev => {
    const step = ev.shiftKey ? 48 : 16;
    if (ev.key === 'ArrowLeft' || ev.key === 'ArrowRight') {
      ev.preventDefault();
      const grow = (ev.key === 'ArrowRight') === (mode === 'left');
      apply(current() + (grow ? step : -step));
      save();
    }
  });
  el.addEventListener('dblclick', () => { box.style.removeProperty(cssVar); try { localStorage.removeItem(key); } catch (e) {} });
}
document.addEventListener('DOMContentLoaded', () => document.querySelectorAll('.splitter').forEach(initSplitter));


// ---- KYC stepper ------------------------------------------------------------------------------------------
function updateKycStepper(verdict) {
  const stepper = document.getElementById('kyc-stepper');
  if (!stepper) return;
  const consent = !!document.getElementById('dpdp-consent-chk')?.checked;
  const set = (n, cls, text) => {
    const li = stepper.querySelector(`li[data-step="${n}"]`);
    if (!li) return;
    li.className = cls;
    li.querySelector('.stepper-dot').textContent = text;
  };
  document.getElementById('kstep-2')?.classList.toggle('is-locked', !consent);
  set(1, consent ? 'is-done' : 'is-active', consent ? '✓' : '1');
  if (verdict === 'PASS') { set(2, 'is-done', '✓'); set(3, 'is-done', '✓'); }
  else if (verdict) { set(2, 'is-done', '✓'); set(3, 'is-fail', '!'); }
  else { set(2, consent ? 'is-active' : '', '2'); set(3, '', '3'); }
}
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('dpdp-consent-chk')?.addEventListener('change', () => updateKycStepper());
  updateKycStepper();
});


// ---- Advisor: Chat / Form modes ---------------------------------------------------------------------------
const MODE_KEY = 'vs_adv_mode';
const STARTERS = [
  'Kirana store in Jaipur, 2 staff, no GST',
  'Dental clinic in Pune, 6 staff, we have GST',
  '3 restaurants in Bengaluru, 15 staff',
  'मेरी किराना दुकान है, 2 लोग, GST नहीं है'
];
let advisorMode = 'chat';

function setAdvisorMode(mode) {
  advisorMode = mode === 'form' ? 'form' : 'chat';
  try { localStorage.setItem(MODE_KEY, advisorMode); } catch (e) {}
  document.getElementById('adv-chat-mode')?.classList.toggle('hidden', advisorMode !== 'chat');
  document.getElementById('adv-form-mode')?.classList.toggle('hidden', advisorMode !== 'form');
  document.getElementById('adv-rail')?.classList.toggle('is-chat', advisorMode === 'chat');
  document.getElementById('mode-chat')?.setAttribute('aria-pressed', String(advisorMode === 'chat'));
  document.getElementById('mode-form')?.setAttribute('aria-pressed', String(advisorMode === 'form'));
  if (advisorMode === 'chat' && !document.getElementById('adv-thread').children.length) greetInThread();
  if (window.lucide) lucide.createIcons();
}

function threadScroll() {
  const t = document.getElementById('adv-thread');
  if (t) t.scrollTop = t.scrollHeight;
}

function addBubble(role, html) {
  const t = document.getElementById('adv-thread');
  const el = document.createElement('div');
  el.className = `bubble bubble-${role}`;
  el.innerHTML = html;
  t.appendChild(el);
  if (window.lucide) lucide.createIcons();
  threadScroll();
  return el;
}

function greetInThread() {
  addBubble('bot', `
    <p>Namaste! Tell me about your business: what you do, how many people work with you, where you are, and whether you have a GSTIN.</p>
    <p class="mt-1 text-slate-600">You can type or speak, in English, हिंदी, मराठी, தமிழ் and more.</p>
    <div class="flex flex-wrap gap-2 mt-3">
      ${STARTERS.map(q => `<button type="button" class="chip" data-starter="${escapeHtml(q)}">${escapeHtml(q)}</button>`).join('')}
    </div>`);
  document.querySelectorAll('#adv-thread [data-starter]').forEach(b => b.addEventListener('click', () => sendThreadMessage(b.dataset.starter)));
}

async function sendThreadMessage(text) {
  const input = document.getElementById('thread-input');
  const query = (text ?? input.value).trim();
  if (!query) { input.focus(); return; }
  input.value = '';
  addBubble('user', escapeHtml(query));
  const typing = addBubble('bot', '<span class="typing" role="status" aria-label="The advisor is typing"><i></i><i></i><i></i></span>');
  const sendBtn = document.getElementById('thread-send');
  sendBtn.disabled = true;

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
    syncFormFromProfile(data.profile);
    typing.remove();

    const p = data.profile || {};
    const chips = [p.business_type, p.employee_count && `${p.employee_count} staff`, p.num_sites && `${p.num_sites} site${p.num_sites > 1 ? 's' : ''}`,
                   p.city, p.has_gstin === true ? 'GST registered' : p.has_gstin === false ? 'No GST' : null].filter(Boolean);
    const rec = data.recommendation || {};
    const monthly = rec.pricing?.monthly_total_inr;
    const yearly = rec.pricing?.vendor_savings_benchmark?.annual_savings_inr;
    const clar = (data.clarifications || [])[0];

    let html = '';
    if (chips.length) html += `<div class="flex flex-wrap gap-1.5 mb-2">${chips.map(c => `<span class="badge">${escapeHtml(c)}</span>`).join('')}</div>`;
    if (clar) {
      const q = currentLanguage === 'hi' ? (clar.question_hi || clar.question) : (clar.question_en || clar.question);
      html += `<p>${escapeHtml(q)}</p><div class="flex flex-wrap gap-2 mt-2">${(clar.options || []).map(o =>
        `<button type="button" class="chip" data-reply="${escapeHtml(o)}">${escapeHtml(o)}</button>`).join('')}</div>`;
    } else {
      if (rec.pitch_narrative) html += `<p>${escapeHtml(rec.pitch_narrative)}</p>`;
      if (monthly) html += `<p class="mt-2"><b>${escapeHtml(rec.bundle_name || 'Recommended bundle')}</b><br><span class="tabular">${inr(monthly)}/month</span>${yearly ? ` · saves ${inr(yearly)} a year` : ''}</p>`;
      html += `<button type="button" class="btn-secondary mt-3 lg:hidden" onclick="document.getElementById('advisor-result-card').scrollIntoView({behavior:'smooth',block:'start'})">See the full bundle</button>`;
    }
    const bubble = addBubble('bot', html || '<p>Thanks. Tell me a little more about your business.</p>');
    bubble.querySelectorAll('[data-reply]').forEach(b => b.addEventListener('click', () => sendThreadMessage(b.dataset.reply)));
  } catch (err) {
    typing.remove();
    addBubble('bot', `<p>Sorry, I couldn't reach the advisor just now. Please try again, or switch to the <b>Form</b>.</p>`);
  } finally {
    sendBtn.disabled = false;
    input.focus();
  }
}

// ---- Voice input (browser speech recognition; hidden where unsupported) -----------------------------------
const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
let activeRecognition = null;
const VOICE_KEY = 'vs_voice_lang';

function initVoice() {
  if (!SpeechRec) return;   // Firefox and some browsers: leave the mic hidden, typing still works
  const sel = document.getElementById('voice-lang');
  document.getElementById('voice-lang-wrap')?.classList.remove('hidden');
  try { sel.value = localStorage.getItem(VOICE_KEY) || (currentLanguage === 'hi' ? 'hi-IN' : 'en-IN'); } catch (e) {}
  sel.addEventListener('change', () => { try { localStorage.setItem(VOICE_KEY, sel.value); } catch (e) {} });
  document.querySelectorAll('[data-mic]').forEach(btn => {
    btn.classList.remove('hidden');
    btn.addEventListener('click', () => toggleMic(btn));
  });
}

function toggleMic(btn) {
  if (activeRecognition) { activeRecognition.stop(); return; }
  const target = document.getElementById(btn.dataset.target);
  const rec = new SpeechRec();
  rec.lang = document.getElementById('voice-lang').value;
  rec.interimResults = true;
  rec.maxAlternatives = 1;
  let finalText = '';
  rec.onresult = e => {
    let interim = '';
    for (let i = e.resultIndex; i < e.results.length; i++) {
      const t = e.results[i][0].transcript;
      if (e.results[i].isFinal) finalText += t; else interim += t;
    }
    target.value = (finalText + interim).trim();
  };
  rec.onerror = e => {
    toast(e.error === 'not-allowed' || e.error === 'service-not-allowed'
      ? 'The microphone is blocked. Allow it in the address bar and try again.'
      : "Couldn't hear that. Please try again.", 'error');
  };
  rec.onend = () => {
    btn.classList.remove('is-listening');
    btn.setAttribute('aria-pressed', 'false');
    activeRecognition = null;
    if (btn.dataset.target === 'thread-input' && target.value.trim()) sendThreadMessage();   // chat: send what was said
  };
  btn.classList.add('is-listening');
  btn.setAttribute('aria-pressed', 'true');
  activeRecognition = rec;
  rec.start();
}

document.addEventListener('DOMContentLoaded', () => {
  let saved = 'chat';
  try { saved = localStorage.getItem(MODE_KEY) || 'chat'; } catch (e) {}
  setAdvisorMode(saved);
  initVoice();
});

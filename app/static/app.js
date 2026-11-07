// VyaparSetu Frontend Client Logic

let currentLanguage = 'en';
let allProducts = [];
let selectedProductIds = new Set(['P01', 'P19', 'P07', 'P23']); // Default Kirana bundle
let productQuantities = {}; // advisor-chosen quantities, so the quote matches the advisor price
let activeCategoryFilter = 'all';
let currentRecommendation = null;
let currentApplicant = null;
let lastCreatedOrderId = 'VS-2026-90412';
let partnerLeads = [];
let chatProfile = null;

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

  // Setup DPDP Consent Box visual changes
  const consentChk = document.getElementById('dpdp-consent-chk');
  const consentBox = document.getElementById('dpdp-consent-box');
  const consentHelp = document.getElementById('dpdp-consent-help');
  if (consentChk && consentBox) {
    consentChk.addEventListener('change', () => {
      if (consentChk.checked) {
        if (consentHelp) consentHelp.classList.add('hidden');
        consentBox.classList.remove('bg-amber-50/70', 'border-amber-200');
        consentBox.classList.add('bg-ok-soft', 'border-emerald-200');
      } else {
        consentBox.classList.remove('bg-ok-soft', 'border-emerald-200');
        consentBox.classList.add('bg-amber-50/70', 'border-amber-200');
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
  fetchOrderStatus('VS-2026-90412');

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

// Render Catalogue with Toggles
function renderCatalogList() {
  const container = document.getElementById('catalog-products-list');
  if (!container) return;

  const filtered = activeCategoryFilter === 'all' 
    ? allProducts 
    : allProducts.filter(p => p.category === activeCategoryFilter);

  container.innerHTML = filtered.map(p => {
    const isChecked = selectedProductIds.has(p.product_id);
    const requiresGstBadge = p.requires_gstin 
      ? `<span class="bg-amber-50 text-amber-800 border border-amber-200 text-xs px-2 py-0.5 rounded font-semibold ml-2">Requires GST</span>` 
      : '';
    const depNotice = p.requires_one_of && p.requires_one_of.length > 0
      ? `<span class="text-xs text-slate-600 block mt-1">Needs base connection: ${escapeHtml(p.requires_one_of.join(' | '))}</span>`
      : '';

    return `
      <label class="p-3.5 border rounded-xl flex items-start justify-between cursor-pointer transition min-h-[44px] ${isChecked ? 'bg-indigo-50/60 border-indigo-200' : 'bg-white border-slate-200 hover:border-slate-300'}">
        <div class="flex items-start space-x-3">
          <input type="checkbox" onchange="toggleProductSelection('${p.product_id}', this.checked)" ${isChecked ? 'checked' : ''} class="mt-1 w-5 h-5 rounded text-airtel-red focus:ring-airtel-red shrink-0">
          <div>
            <div class="flex items-center flex-wrap gap-1">
              <span class="font-bold text-sm text-slate-900">${escapeHtml(p.product_name)}</span>
              <span class="text-xs font-mono text-slate-600">(${escapeHtml(p.product_id)})</span>
              <span class="text-xs bg-slate-100 text-slate-700 px-2 py-0.5 rounded font-medium">${escapeHtml(p.category)}</span>
              ${requiresGstBadge}
            </div>
            <p class="text-sm text-slate-600 mt-1 leading-relaxed">${escapeHtml(p.description)}</p>
            ${depNotice}
          </div>
        </div>
        <div class="text-right whitespace-nowrap ml-3 shrink-0">
          <div class="font-bold text-sm text-slate-900 tabular">₹${p.price_min_inr_per_month.toLocaleString('en-IN')}<span class="text-xs text-slate-600 font-normal"> /mo</span></div>
          <span class="text-xs text-slate-600 tabular block">Setup: ₹${p.one_time_setup_inr.toLocaleString('en-IN')}</span>
        </div>
      </label>
    `;
  }).join('');
}

function filterCatalogCategory(cat) {
  activeCategoryFilter = cat;
  document.querySelectorAll('.cat-filter').forEach(btn => {
    btn.classList.toggle('active', btn.textContent.includes(cat) || (cat === 'all' && btn.textContent.includes('All')));
  });
  renderCatalogList();
}

function toggleProductSelection(pid, checked) {
  if (checked) {
    selectedProductIds.add(pid);
  } else {
    selectedProductIds.delete(pid);
  }
  recalculateQuotePricing();
  renderCatalogList();
}

// Recalculate Live Quote Pricing & Dependencies
async function recalculateQuotePricing() {
  const items = Array.from(selectedProductIds).map(pid => ({ product_id: pid, quantity: productQuantities[pid] || 1 }));
  
  if (items.length === 0) {
    const countEl = document.getElementById('bill-item-count');
    if (countEl) countEl.textContent = '0 products';
    const totalEl = document.getElementById('bill-monthly-total');
    if (totalEl) totalEl.innerHTML = `₹0<span class="text-xs text-slate-500 font-normal">/mo</span>`;
    return;
  }

  try {
    const res = await fetch('/api/catalogue/pricing', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ items })
    });
    const pricing = await res.json();

    document.getElementById('bill-item-count').textContent = `${pricing.items.length} products`;
    document.getElementById('bill-setup-fee').textContent = `₹${pricing.setup_total_inr.toLocaleString('en-IN')}`;
    document.getElementById('bill-contract').textContent = `${pricing.contract_lock_months} Months`;
    document.getElementById('bill-install-days').textContent = `${pricing.estimated_install_sla_days} Days`;
    document.getElementById('bill-monthly-total').innerHTML = `₹${pricing.monthly_total_inr.toLocaleString('en-IN')}<span class="text-xs text-slate-500 font-normal">/mo</span>`;

    // Validate
    const valRes = await fetch('/api/catalogue/validate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        selected_product_ids: Array.from(selectedProductIds),
        city_tier: parseInt(document.getElementById('adv-city-tier')?.value || '1'),
        employee_count: parseInt(document.getElementById('adv-employees')?.value || '2'),
        num_sites: parseInt(document.getElementById('adv-sites')?.value || '1'),
        has_gstin: document.querySelector('input[name="adv-has-gst"]:checked')?.value === 'yes'
      })
    });
    const val = await valRes.json();
    const alertBox = document.getElementById('bill-validation-alerts');
    if (alertBox) {
      if (!val.is_valid && val.errors.length > 0) {
        alertBox.innerHTML = `
          <div class="bg-amber-50 border border-amber-200 text-amber-900 p-3 rounded-xl text-xs space-y-1">
            <strong class="font-bold flex items-center space-x-1 text-warn">
              <i data-lucide="alert-triangle" class="w-4 h-4"></i>
              <span>Catalogue Configuration Notice</span>
            </strong>
            ${val.errors.map(e => `<div>• ${escapeHtml(e)}</div>`).join('')}
          </div>
        `;
      } else {
        alertBox.innerHTML = '';
      }
    }
    if (window.lucide) lucide.createIcons();
  } catch (err) {
    console.error("Pricing calculation error:", err);
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
  const inr = n => '₹' + Number(n || 0).toLocaleString('en-IN');
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
    select.innerHTML = `<option value="">-- Select an Applicant Specimen (K01 – K12) --</option>` + 
      data.applicants.map(a => `
        <option value="${a.code}">
          [${a.code}] ${a.business_name} (${a.expected_verdict}) - ${a.reason}
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
async function fetchOrderStatus(orderId) {
  const oid = orderId || document.getElementById('tracker-order-id').value.trim();
  if (!oid) return;

  const notFoundEl = document.getElementById('tracker-not-found-msg');
  if (notFoundEl) notFoundEl.classList.add('hidden');

  try {
    const res = await fetch(`/api/orders/${oid}`);
    if (res.ok) {
      const order = await res.json();
      try {
        localStorage.setItem('vs_last_order', JSON.stringify(order));
        localStorage.setItem(`vs_order_${order.order_id}`, JSON.stringify(order));
      } catch (e) {}
      renderOrderTracker(order);
      return;
    }
  } catch (err) {
    console.error("Tracking error:", err);
  }

  // Fallback to locally saved order if server restarted or on serverless cold instance
  try {
    const saved = localStorage.getItem(`vs_order_${oid}`) || localStorage.getItem('vs_last_order');
    if (saved) {
      const savedOrder = JSON.parse(saved);
      if (savedOrder.order_id === oid || !orderId) {
        renderOrderTracker(savedOrder, "Showing your saved order (synced locally)");
        return;
      }
    }
  } catch (e) {}

  // Inline non-intrusive error notice (no popup alert)
  if (notFoundEl) {
    notFoundEl.textContent = `Order '${oid}' not found. Please verify the ID or create a new order via the KYC tab.`;
    notFoundEl.classList.remove('hidden');
  }
}

// Render Live Order Tracker UI
function renderOrderTracker(order, note = null) {
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

  if (window.lucide) lucide.createIcons();
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
  const url = seg ? `/api/partner/leads?limit=12&segment=${encodeURIComponent(seg)}` : '/api/partner/leads?limit=12';
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
              <span class="text-xs font-bold text-slate-700 tabular">${l.propensity_score}%</span>
            </div>
          </td>
          <td class="py-2.5 px-3 text-right">
            <button type="button" onclick="assistDroppedLead('${escapeHtml(l.lead_id)}')" class="px-3 py-1.5 border border-slate-300 text-slate-800 hover:border-airtel-red bg-white rounded-lg text-xs font-semibold shadow-sm transition min-h-[44px]">
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

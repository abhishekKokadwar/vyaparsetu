// VyaparSetu Frontend Client Logic

let currentLanguage = 'en';
let allProducts = [];
let selectedProductIds = new Set(['P01', 'P19', 'P07', 'P23']); // Default Kirana bundle
let activeCategoryFilter = 'all';
let currentRecommendation = null;
let currentApplicant = null;
let lastCreatedOrderId = 'VS-2026-90412';

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

document.addEventListener('DOMContentLoaded', async () => {
  if (window.lucide) {
    lucide.createIcons();
  }
  await loadCatalogue();
  await loadKYCApplicants();
  await loadPartnerPortal();
  
  // Run initial recommendation for default form values
  submitAdvisorProfile();
  fetchOrderStatus('VS-2026-90412');
});

// Tab Switcher
function switchTab(tabName) {
  document.querySelectorAll('.tab-view').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.nav-tab').forEach(el => el.classList.remove('active'));

  const view = document.getElementById(`view-${tabName}`);
  const btn = document.getElementById(`tab-btn-${tabName}`);

  if (view) view.classList.add('active');
  if (btn) btn.classList.add('active');

  if (window.lucide) lucide.createIcons();
}

// Language Switcher
function setLanguage(lang) {
  currentLanguage = lang;
  document.getElementById('lang-en').className = lang === 'en' 
    ? 'px-2.5 py-1 text-xs font-bold rounded-md bg-white shadow-sm text-slate-800'
    : 'px-2.5 py-1 text-xs font-bold rounded-md text-slate-500 hover:text-slate-800';
  document.getElementById('lang-hi').className = lang === 'hi' 
    ? 'px-2.5 py-1 text-xs font-bold rounded-md bg-white shadow-sm text-slate-800'
    : 'px-2.5 py-1 text-xs font-bold rounded-md text-slate-500 hover:text-slate-800';

  document.getElementById('txt-advisor-title').textContent = i18n[lang].advisorTitle;
  document.getElementById('txt-advisor-subtitle').textContent = i18n[lang].advisorSubtitle;
  document.getElementById('txt-why-bundle').textContent = i18n[lang].whyBundle;
  document.getElementById('btn-generate-rec').textContent = i18n[lang].btnRec;

  // Re-run recommendation with new language
  if (currentRecommendation) {
    submitAdvisorProfile();
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
      ? `<span class="bg-amber-100 text-amber-800 text-[10px] px-1.5 py-0.5 rounded font-semibold ml-2">Requires GST</span>` 
      : '';
    const depNotice = p.requires_one_of && p.requires_one_of.length > 0
      ? `<span class="text-[10px] text-slate-400 block mt-0.5">Needs base connection: ${p.requires_one_of.join('|')}</span>`
      : '';

    return `
      <div class="p-3.5 border rounded-xl flex items-start justify-between transition ${isChecked ? 'bg-red-50/40 border-red-200' : 'bg-white border-slate-200 hover:border-slate-300'}">
        <div class="flex items-start space-x-3">
          <input type="checkbox" onchange="toggleProductSelection('${p.product_id}', this.checked)" ${isChecked ? 'checked' : ''} class="mt-1 rounded text-airtel-red focus:ring-airtel-red">
          <div>
            <div class="flex items-center flex-wrap">
              <span class="font-bold text-xs text-slate-900">${p.product_name}</span>
              <span class="text-[10px] font-mono text-slate-400 ml-1.5">(${p.product_id})</span>
              <span class="text-[10px] bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded font-medium ml-2">${p.category}</span>
              ${requiresGstBadge}
            </div>
            <p class="text-[11px] text-slate-500 mt-0.5">${p.description}</p>
            ${depNotice}
          </div>
        </div>
        <div class="text-right whitespace-nowrap ml-3">
          <div class="font-bold text-xs text-slate-900">₹${p.price_min_inr_per_month}<span class="text-[10px] text-slate-400 font-normal"> /mo</span></div>
          <span class="text-[10px] text-slate-400">Setup: ₹${p.one_time_setup_inr}</span>
        </div>
      </div>
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
  const items = Array.from(selectedProductIds).map(pid => ({ product_id: pid, quantity: 1 }));
  
  if (items.length === 0) {
    document.getElementById('bill-item-count').textContent = '0 products';
    document.getElementById('bill-monthly-total').innerHTML = `₹0<span class="text-xs text-slate-400 font-normal">/mo</span>`;
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
    document.getElementById('bill-contract').textContent = `${pricing.contract_months} Months`;
    document.getElementById('bill-install-days').textContent = `${pricing.estimated_install_days} Days`;
    document.getElementById('bill-monthly-total').innerHTML = `₹${pricing.monthly_total_inr.toLocaleString('en-IN')}<span class="text-xs text-slate-400 font-normal">/mo</span>`;

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
    if (!val.is_valid && val.errors.length > 0) {
      alertBox.innerHTML = `
        <div class="bg-red-50 border border-red-200 text-red-700 p-2.5 rounded-lg text-[11px] space-y-1">
          <strong class="font-bold flex items-center space-x-1">
            <i data-lucide="alert-triangle" class="w-3.5 h-3.5"></i>
            <span>Catalogue Dependency Issue</span>
          </strong>
          ${val.errors.map(e => `<div>• ${e}</div>`).join('')}
        </div>
      `;
    } else {
      alertBox.innerHTML = '';
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
  const spend = parseInt(document.getElementById('adv-current-spend').value);

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
  loadingEl.classList.remove('hidden');
  contentEl.classList.add('opacity-40');

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
    loadingEl.classList.add('hidden');
    contentEl.classList.remove('opacity-40');
  }
}

// Render Advisor Recommendation Result Card
function renderAdvisorRecommendation(data) {
  document.getElementById('rec-bundle-title').textContent = data.bundle_name;
  document.getElementById('rec-price').innerHTML = `₹${data.pricing.monthly_total_inr.toLocaleString('en-IN')}<span class="text-xs text-slate-500 font-normal"> /mo</span>`;
  document.getElementById('rec-contract').textContent = `${data.pricing.contract_months} Months`;
  document.getElementById('rec-install').textContent = `${data.pricing.estimated_install_days} Days`;

  // Reasoning points
  const listEl = document.getElementById('rec-reasoning-list');
  listEl.innerHTML = data.reasoning.map(pt => `
    <div class="flex items-start space-x-2">
      <span class="text-emerald-600 font-bold">•</span>
      <span class="text-slate-700 leading-snug">${pt}</span>
    </div>
  `).join('');

  // Products table
  const tbody = document.getElementById('rec-products-table');
  tbody.innerHTML = data.pricing.items.map(it => `
    <tr class="hover:bg-slate-50/50">
      <td class="py-2 px-3 font-semibold text-slate-800">${it.product_name}</td>
      <td class="py-2 px-3 text-slate-500">${it.category}</td>
      <td class="py-2 px-3 text-center font-mono">${it.quantity}</td>
      <td class="py-2 px-3 text-right font-bold text-slate-900">₹${it.total_monthly.toLocaleString('en-IN')}</td>
    </tr>
  `).join('');

  // Sync selected products to Quote tab
  selectedProductIds = new Set(data.selected_product_ids);
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

// Run Smart KYC Verification on selected applicant
async function runSmartKYCVerification() {
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
  const title = document.getElementById('kyc-verdict-title');
  const desc = document.getElementById('kyc-verdict-desc');
  const orderBtn = document.getElementById('btn-place-order');

  if (res.verdict === 'PASS') {
    banner.className = 'rounded-xl p-4 mb-4 border flex items-center space-x-3 bg-emerald-50 border-emerald-200 text-emerald-900';
    title.textContent = `VERIFIED: ${res.business_name} (Signatory: ${res.signatory})`;
    desc.textContent = res.summary;
    orderBtn.disabled = false;
  } else {
    banner.className = 'rounded-xl p-4 mb-4 border flex items-center space-x-3 bg-red-50 border-red-200 text-red-900';
    title.textContent = `REJECTED: ${res.business_name || 'Verification Failed'}`;
    desc.textContent = res.summary;
    orderBtn.disabled = true;
  }

  // Checklist
  const checklistEl = document.getElementById('kyc-checklist-container');
  checklistEl.innerHTML = res.checklist.map(item => {
    let icon = 'check-circle';
    let badgeClass = 'text-emerald-700 bg-emerald-100 border-emerald-200';
    if (item.status === 'FAILED') {
      icon = 'x-circle';
      badgeClass = 'text-red-700 bg-red-100 border-red-200';
    } else if (item.status === 'WARNING') {
      icon = 'alert-triangle';
      badgeClass = 'text-amber-700 bg-amber-100 border-amber-200';
    }

    return `
      <div class="p-3 rounded-xl border border-slate-200 bg-slate-50 flex items-start justify-between">
        <div class="pr-3">
          <span class="font-bold text-slate-800 block text-xs">${item.title}</span>
          <span class="text-[11px] text-slate-600 block mt-0.5">${item.detail}</span>
        </div>
        <span class="text-[10px] font-bold px-2 py-0.5 rounded-full border ${badgeClass} uppercase whitespace-nowrap">
          ${item.status}
        </span>
      </div>
    `;
  }).join('');

  if (window.lucide) lucide.createIcons();
}

// Manual GST Lookup
async function lookupGSTINManually() {
  const gstin = document.getElementById('kyc-input-gstin').value.trim();
  const box = document.getElementById('gst-lookup-result');
  box.classList.remove('hidden');

  try {
    const res = await fetch(`/api/registry/gstin/${gstin}`);
    const data = await res.json();
    if (data.found) {
      box.innerHTML = `
        <div class="p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-emerald-900">
          <div class="flex justify-between items-center">
            <strong class="font-bold">${data.legal_name}</strong>
            <span class="text-[10px] bg-emerald-200 text-emerald-900 font-bold px-2 py-0.5 rounded uppercase">${data.status}</span>
          </div>
          <p class="text-[11px] mt-1 text-emerald-700">${data.trade_name} · ${data.principal_place_of_business}, ${data.state}</p>
        </div>
      `;
    } else {
      box.innerHTML = `
        <div class="p-3 bg-red-50 border border-red-200 rounded-xl text-red-900">
          <strong>Not Verified:</strong> ${data.message}
        </div>
      `;
    }
  } catch (err) {
    box.innerHTML = `<div class="p-2 text-red-600">Error connecting to registry.</div>`;
  }
}

// Manual Udyam Lookup
async function lookupUdyamManually() {
  const udyam = document.getElementById('kyc-input-udyam').value.trim();
  const box = document.getElementById('udyam-lookup-result');
  box.classList.remove('hidden');

  try {
    const res = await fetch(`/api/registry/udyam/${udyam}`);
    const data = await res.json();
    if (data.found) {
      box.innerHTML = `
        <div class="p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-emerald-900">
          <div class="flex justify-between items-center">
            <strong class="font-bold">${data.enterprise_name}</strong>
            <span class="text-[10px] bg-emerald-200 text-emerald-900 font-bold px-2 py-0.5 rounded uppercase">${data.enterprise_type}</span>
          </div>
          <p class="text-[11px] mt-1 text-emerald-700">${data.major_activity} · ${data.city}, ${data.state}</p>
        </div>
      `;
    } else {
      box.innerHTML = `
        <div class="p-3 bg-red-50 border border-red-200 rounded-xl text-red-900">
          <strong>Not Verified:</strong> ${data.message}
        </div>
      `;
    }
  } catch (err) {
    box.innerHTML = `<div class="p-2 text-red-600">Error connecting to registry.</div>`;
  }
}

// Place Order after KYC Pass
async function placeOrderAfterKYC() {
  const bizName = currentApplicant?.business_name || document.getElementById('adv-biz-type').value;
  const bundle = currentRecommendation?.bundle_name_en || 'Vyapar Booster Pack';
  const price = currentRecommendation?.pricing?.monthly_total_inr || 2597;
  const installDays = currentRecommendation?.pricing?.estimated_install_days || 3;

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

  try {
    const res = await fetch('/api/orders/create', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const order = await res.json();
    lastCreatedOrderId = order.order_id;
    document.getElementById('tracker-order-id').value = order.order_id;
    renderOrderTracker(order);
    switchTab('tracker');
  } catch (err) {
    console.error("Order creation error:", err);
  }
}

// Fetch Order Status for Live Order Tracker
async function fetchOrderStatus(orderId) {
  const oid = orderId || document.getElementById('tracker-order-id').value.trim();
  if (!oid) return;

  try {
    const res = await fetch(`/api/orders/${oid}`);
    if (!res.ok) {
      alert("Order not found. Showing sample order VS-2026-90412.");
      return fetchOrderStatus('VS-2026-90412');
    }
    const order = await res.json();
    renderOrderTracker(order);
  } catch (err) {
    console.error("Tracking error:", err);
  }
}

// Render Live Order Tracker UI
function renderOrderTracker(order) {
  document.getElementById('trk-order-num').textContent = order.order_id;
  document.getElementById('trk-biz-name').textContent = order.business_name;
  document.getElementById('trk-bundle').textContent = order.bundle_name;
  document.getElementById('trk-est-date').textContent = order.estimated_activation_date;

  // Render Milestones
  const timelineEl = document.getElementById('tracker-timeline');
  timelineEl.innerHTML = order.stages.map((st, i) => {
    let dotClass = 'pending';
    let iconName = 'circle';
    let statusText = 'Pending';
    let statusBadge = 'bg-slate-100 text-slate-500';

    if (st.status === 'COMPLETED') {
      dotClass = 'completed';
      iconName = 'check';
      statusText = 'Completed';
      statusBadge = 'bg-emerald-100 text-emerald-800';
    } else if (st.status === 'IN_PROGRESS') {
      dotClass = 'in-progress';
      iconName = 'clock';
      statusText = 'In Progress';
      statusBadge = 'bg-red-100 text-airtel-red';
    }

    return `
      <div class="relative flex items-start space-x-4">
        <div class="timeline-dot ${dotClass}">
          <i data-lucide="${iconName}" class="w-4 h-4"></i>
        </div>
        <div class="flex-1 pt-1">
          <div class="flex justify-between items-baseline">
            <h4 class="text-sm font-bold text-slate-900">${st.name}</h4>
            <span class="text-[10px] font-bold px-2 py-0.5 rounded-full ${statusBadge} uppercase">${statusText}</span>
          </div>
          <p class="text-xs text-slate-600 mt-0.5">${st.detail}</p>
          <span class="text-[10px] text-slate-400 block mt-1">${st.timestamp}</span>
        </div>
      </div>
    `;
  }).join('');

  // Technician Card
  if (order.technician) {
    document.getElementById('trk-tech-name').textContent = order.technician.name;
    document.getElementById('trk-tech-slot').textContent = `Slot: ${order.technician.slot}`;
    document.getElementById('trk-tech-pin').textContent = order.technician.pin;
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
    document.getElementById('ptnr-salvageable').textContent = stats.high_propensity_salvageable.toLocaleString('en-IN');
    document.getElementById('ptnr-arr').textContent = `₹${(stats.potential_arr_inr / 10000000).toFixed(2)} Cr`;
    document.getElementById('ptnr-comm').textContent = `₹${(stats.commission_pool_inr / 100000).toFixed(1)} Lakh`;

    loadPartnerLeads();
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
    const tbody = document.getElementById('ptnr-leads-table');
    tbody.innerHTML = data.leads.map(l => {
      let scoreColor = 'bg-emerald-100 text-emerald-800';
      if (l.propensity_score < 70) scoreColor = 'bg-amber-100 text-amber-800';

      return `
        <tr class="hover:bg-slate-50">
          <td class="py-2.5 px-3">
            <span class="font-bold text-slate-800 block">${l.business_name}</span>
            <span class="text-[10px] font-mono text-slate-400">${l.lead_id} · ${l.employee_count} Staff</span>
          </td>
          <td class="py-2.5 px-3">
            <span class="text-slate-700 block">${l.segment}</span>
            <span class="text-[10px] text-slate-500">${l.city} (Tier ${l.city_tier})</span>
          </td>
          <td class="py-2.5 px-3">
            <span class="bg-slate-100 text-slate-700 text-[10px] font-semibold px-2 py-0.5 rounded">${l.stage_reached}</span>
          </td>
          <td class="py-2.5 px-3 text-slate-600 max-w-xs truncate" title="${l.drop_reason}">
            ${l.drop_reason}
          </td>
          <td class="py-2.5 px-3 text-center">
            <span class="font-extrabold text-xs px-2.5 py-1 rounded-full ${scoreColor}">
              ${l.propensity_score}%
            </span>
          </td>
          <td class="py-2.5 px-3 text-right">
            <button onclick="assistDroppedLead('${l.business_name}', '${l.segment}', ${l.city_tier}, ${l.employee_count}, ${l.has_gstin})" class="px-3 py-1.5 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-[11px] font-semibold shadow-sm transition">
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
function assistDroppedLead(bizName, segment, tier, emp, hasGst) {
  switchTab('advisor');
  document.getElementById('adv-biz-type').value = segment === 'Micro retail & services' ? 'Kirana & Retail Store' : 'Clinic & Healthcare';
  document.getElementById('adv-city-tier').value = tier;
  document.getElementById('adv-employees').value = emp;
  document.querySelector(`input[name="adv-has-gst"][value="${hasGst ? 'yes' : 'no'}"]`).checked = true;
  submitAdvisorProfile();
}


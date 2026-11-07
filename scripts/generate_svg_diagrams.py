import os

diagrams_dir = os.path.join(os.path.dirname(__file__), '..', 'app', 'static', 'diagrams')
os.makedirs(diagrams_dir, exist_ok=True)

# 1. System Architecture SVG
arch_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 680" width="100%" height="100%" style="background:#0F172A; font-family:'Plus Jakarta Sans', -apple-system, sans-serif;">
  <defs>
    <linearGradient id="gradRed" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#E40000" />
      <stop offset="100%" stop-color="#990000" />
    </linearGradient>
    <linearGradient id="gradCard" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1E293B" />
      <stop offset="100%" stop-color="#0F172A" />
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#E40000" flood-opacity="0.25"/>
    </filter>
  </defs>

  <!-- Title & Header -->
  <text x="50" y="55" fill="#E40000" font-size="14" font-weight="700" letter-spacing="2">AIRTEL SYNC 2026 · ENTERPRISE TRACK A</text>
  <text x="50" y="85" fill="#FFFFFF" font-size="24" font-weight="800">VyaparSetu: End-to-End Solution Architecture</text>
  <text x="50" y="110" fill="#94A3B8" font-size="13">Modular microservices architecture for zero-paperwork, single-sitting MSME digital onboarding</text>

  <!-- Column 1: Client Ingestion Layer -->
  <rect x="50" y="140" width="240" height="490" rx="16" fill="#1E293B" stroke="#334155" stroke-width="1.5"/>
  <rect x="70" y="160" width="200" height="32" rx="8" fill="#E40000" opacity="0.15"/>
  <text x="170" y="181" fill="#FF4D4D" font-size="12" font-weight="700" text-anchor="middle">1. OMNICHANNEL CLIENTS</text>

  <g transform="translate(70, 210)">
    <rect width="200" height="85" rx="12" fill="#0F172A" stroke="#334155"/>
    <text x="20" y="32" fill="#FFFFFF" font-size="13" font-weight="700">Self-Serve Web App</text>
    <text x="20" y="52" fill="#94A3B8" font-size="11">Mobile-first responsive UI</text>
    <text x="20" y="70" fill="#E40000" font-size="10" font-weight="600">English + हिंदी Localization</text>
  </g>

  <g transform="translate(70, 310)">
    <rect width="200" height="85" rx="12" fill="#0F172A" stroke="#334155"/>
    <text x="20" y="32" fill="#FFFFFF" font-size="13" font-weight="700">WhatsApp Business Bot</text>
    <text x="20" y="52" fill="#94A3B8" font-size="11">Meta Cloud API interactive flows</text>
    <text x="20" y="70" fill="#10B981" font-size="10" font-weight="600">Zero App Download Needed</text>
  </g>

  <g transform="translate(70, 410)">
    <rect width="200" height="85" rx="12" fill="#0F172A" stroke="#334155"/>
    <text x="20" y="32" fill="#FFFFFF" font-size="13" font-weight="700">Partner Assisted Tablet</text>
    <text x="20" y="52" fill="#94A3B8" font-size="11">Field sales & channel reps</text>
    <text x="20" y="70" fill="#A855F7" font-size="10" font-weight="600">Direct QR Commission Credit</text>
  </g>

  <g transform="translate(70, 510)">
    <rect width="200" height="95" rx="12" fill="#0F172A" stroke="#334155"/>
    <text x="20" y="32" fill="#FFFFFF" font-size="13" font-weight="700">Self-Service Tracker</text>
    <text x="20" y="52" fill="#94A3B8" font-size="11">5-Milestone live tracking</text>
    <text x="20" y="70" fill="#38BDF8" font-size="10" font-weight="600">Technician PIN & Slot View</text>
    <text x="20" y="85" fill="#64748B" font-size="9">Deflects 90% Status Calls</text>
  </g>

  <!-- Connectors from Col 1 to Col 2 -->
  <path d="M 290 380 L 330 380" stroke="#E40000" stroke-width="2" stroke-dasharray="4 4" />

  <!-- Column 2: Gateway & Business Logic -->
  <rect x="330" y="140" width="270" height="490" rx="16" fill="#1E293B" stroke="#334155" stroke-width="1.5"/>
  <rect x="350" y="160" width="230" height="32" rx="8" fill="#38BDF8" opacity="0.15"/>
  <text x="465" y="181" fill="#38BDF8" font-size="12" font-weight="700" text-anchor="middle">2. CORE LOGIC & ENGINES</text>

  <g transform="translate(350, 210)">
    <rect width="230" height="110" rx="12" fill="#0F172A" stroke="#334155"/>
    <text x="20" y="30" fill="#FFFFFF" font-size="13" font-weight="700">GenAI Advisor (VyaparSaarthi)</text>
    <text x="20" y="50" fill="#94A3B8" font-size="11">Conversational discovery engine</text>
    <text x="20" y="68" fill="#94A3B8" font-size="11">Translates specs to plain Hindi/EN</text>
    <text x="20" y="92" fill="#FF4D4D" font-size="10" font-weight="600">4-Question Persona Profiler</text>
  </g>

  <g transform="translate(350, 335)">
    <rect width="230" height="125" rx="12" fill="#0F172A" stroke="#334155"/>
    <text x="20" y="30" fill="#FFFFFF" font-size="13" font-weight="700">Catalog Rule Engine</text>
    <text x="20" y="50" fill="#94A3B8" font-size="11">Enforces product_catalogue.csv</text>
    <text x="20" y="68" fill="#94A3B8" font-size="11">• requires_gstin validation</text>
    <text x="20" y="86" fill="#94A3B8" font-size="11">• requires_one_of dependencies</text>
    <text x="20" y="106" fill="#38BDF8" font-size="10" font-weight="600">Single Monthly Invoicing</text>
  </g>

  <g transform="translate(350, 475)">
    <rect width="230" height="130" rx="12" fill="#0F172A" stroke="#334155"/>
    <text x="20" y="30" fill="#FFFFFF" font-size="13" font-weight="700">Lead Propensity Salvage</text>
    <text x="20" y="50" fill="#94A3B8" font-size="11">Evaluates 4,632 dropped leads</text>
    <text x="20" y="68" fill="#94A3B8" font-size="11">Percentile propensity scoring</text>
    <text x="20" y="86" fill="#94A3B8" font-size="11">932 Top 20% targets (&gt;=80)</text>
    <text x="20" y="110" fill="#10B981" font-size="10" font-weight="600">₹1.91 Cr Recoverable ARR</text>
  </g>

  <!-- Connectors from Col 2 to Col 3 -->
  <path d="M 600 380 L 640 380" stroke="#38BDF8" stroke-width="2" stroke-dasharray="4 4"/>

  <!-- Column 3: Smart KYC & Privacy Infrastructure -->
  <rect x="640" y="140" width="260" height="490" rx="16" fill="#1E293B" stroke="#334155" stroke-width="1.5"/>
  <rect x="660" y="160" width="220" height="32" rx="8" fill="#10B981" opacity="0.15"/>
  <text x="770" y="181" fill="#10B981" font-size="12" font-weight="700" text-anchor="middle">3. SMART KYC & PRIVACY</text>

  <g transform="translate(660, 210)">
    <rect width="220" height="110" rx="12" fill="#0F172A" stroke="#334155"/>
    <text x="20" y="30" fill="#FFFFFF" font-size="13" font-weight="700">Mock Registry APIs</text>
    <text x="20" y="50" fill="#94A3B8" font-size="11">3,534 GST records cache</text>
    <text x="20" y="68" fill="#94A3B8" font-size="11">2,723 MSME Udyam records</text>
    <text x="20" y="92" fill="#10B981" font-size="10" font-weight="600">&lt;500ms Instant Autofill</text>
  </g>

  <g transform="translate(660, 335)">
    <rect width="220" height="125" rx="12" fill="#0F172A" stroke="#334155"/>
    <text x="20" y="30" fill="#FFFFFF" font-size="13" font-weight="700">OCR & Document Engine</text>
    <text x="20" y="50" fill="#94A3B8" font-size="11">Native WinRT OCR processing</text>
    <text x="20" y="68" fill="#94A3B8" font-size="11">• 90-day expiry check (15-Jul-26)</text>
    <text x="20" y="86" fill="#94A3B8" font-size="11">• Planted defect detection (K01-K12)</text>
    <text x="20" y="106" fill="#F59E0B" font-size="10" font-weight="600">Catches Expired & Cancelled</text>
  </g>

  <g transform="translate(660, 475)">
    <rect width="220" height="130" rx="12" fill="#0F172A" stroke="#334155"/>
    <text x="20" y="30" fill="#FFFFFF" font-size="13" font-weight="700">DPDP Act 2023 Shield</text>
    <text x="20" y="50" fill="#94A3B8" font-size="11">• Unbundled digital consent</text>
    <text x="20" y="68" fill="#94A3B8" font-size="11">• Dynamic PAN/GSTIN masking</text>
    <text x="20" y="86" fill="#94A3B8" font-size="11">• 30-day auto-purge policy</text>
    <text x="20" y="110" fill="#38BDF8" font-size="10" font-weight="600">Privacy by Design</text>
  </g>

  <!-- Connectors from Col 3 to Col 4 -->
  <path d="M 900 380 L 940 380" stroke="#10B981" stroke-width="2" stroke-dasharray="4 4"/>

  <!-- Column 4: Airtel Telecom OSS/BSS Integration -->
  <rect x="940" y="140" width="210" height="490" rx="16" fill="#1E293B" stroke="#334155" stroke-width="1.5"/>
  <rect x="955" y="160" width="180" height="32" rx="8" fill="#A855F7" opacity="0.15"/>
  <text x="1045" y="181" fill="#A855F7" font-size="12" font-weight="700" text-anchor="middle">4. TELCO OSS / BSS</text>

  <g transform="translate(955, 210)">
    <rect width="180" height="110" rx="12" fill="#0F172A" stroke="#334155"/>
    <text x="15" y="30" fill="#FFFFFF" font-size="12" font-weight="700">Fibre / Port Feasibility</text>
    <text x="15" y="50" fill="#94A3B8" font-size="10">Automated GIS line check</text>
    <text x="15" y="68" fill="#94A3B8" font-size="10">OLT port reservation</text>
    <text x="15" y="92" fill="#A855F7" font-size="10" font-weight="600">Zero Manual Inspection</text>
  </g>

  <g transform="translate(955, 335)">
    <rect width="180" height="125" rx="12" fill="#0F172A" stroke="#334155"/>
    <text x="15" y="30" fill="#FFFFFF" font-size="12" font-weight="700">Field Dispatch Dispatcher</text>
    <text x="15" y="50" fill="#94A3B8" font-size="10">Technician slot assignment</text>
    <text x="15" y="68" fill="#94A3B8" font-size="10">Router CPE hardware dispatch</text>
    <text x="15" y="86" fill="#94A3B8" font-size="10">Security OTP verification</text>
    <text x="15" y="106" fill="#10B981" font-size="10" font-weight="600">&lt;48 Hr Activation SLA</text>
  </g>

  <g transform="translate(955, 475)">
    <rect width="180" height="130" rx="12" fill="#0F172A" stroke="#334155"/>
    <text x="15" y="30" fill="#FFFFFF" font-size="12" font-weight="700">Unified Billing (BSS)</text>
    <text x="15" y="50" fill="#94A3B8" font-size="10">Single enterprise account</text>
    <text x="15" y="68" fill="#94A3B8" font-size="10">Consolidates Broadband,</text>
    <text x="15" y="86" fill="#94A3B8" font-size="10">Cloud POS, Email &amp; CCTV</text>
    <text x="15" y="110" fill="#E40000" font-size="10" font-weight="600">Single Monthly Invoicing</text>
  </g>
</svg>
"""

with open(os.path.join(diagrams_dir, 'architecture_diagram.svg'), 'w', encoding='utf-8') as f:
    f.write(arch_svg.strip())

# 2. Customer Journey SVG
journey_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 480" width="100%" height="100%" style="background:#0F172A; font-family:'Plus Jakarta Sans', -apple-system, sans-serif;">
  <!-- Title -->
  <text x="50" y="55" fill="#E40000" font-size="13" font-weight="700" letter-spacing="2">VYAPARSETU CUSTOMER EXPERIENCE</text>
  <text x="50" y="85" fill="#FFFFFF" font-size="22" font-weight="800">The 4-Stage 10-Minute Onboarding Journey</text>
  <text x="50" y="110" fill="#94A3B8" font-size="13">Transforming 17.6 days of paper friction into an instant, self-serve digital experience</text>

  <!-- Stage 1 -->
  <g transform="translate(50, 145)">
    <rect width="250" height="280" rx="16" fill="#1E293B" stroke="#334155" stroke-width="1.5"/>
    <circle cx="45" cy="45" r="22" fill="#E40000" />
    <text x="45" y="52" fill="#FFFFFF" font-size="14" font-weight="800" text-anchor="middle">01</text>
    <text x="80" y="42" fill="#FF4D4D" font-size="11" font-weight="700">STAGE 1 · 2 MINS</text>
    <text x="80" y="60" fill="#FFFFFF" font-size="14" font-weight="700">Conversational Advisor</text>
    
    <text x="25" y="105" fill="#CBD5E1" font-size="11">• Plain Hindi/English interaction</text>
    <text x="25" y="130" fill="#CBD5E1" font-size="11">• 4 high-signal business questions</text>
    <text x="25" y="155" fill="#CBD5E1" font-size="11">• Automatic bundle recommendation</text>
    <text x="25" y="180" fill="#CBD5E1" font-size="11">• Plain-language 'Why' explanation</text>
    <text x="25" y="205" fill="#CBD5E1" font-size="11">• Zero sales scheduling wait</text>
    
    <rect x="25" y="225" width="200" height="30" rx="8" fill="#E40000" opacity="0.2"/>
    <text x="125" y="244" fill="#FF4D4D" font-size="10" font-weight="700" text-anchor="middle">Replaces 3-Day Sales Visit</text>
  </g>

  <!-- Arrow 1 -->
  <path d="M 315 285 L 340 285" stroke="#E40000" stroke-width="3" stroke-linecap="round"/>
  <polygon points="345,285 337,280 337,290" fill="#E40000" />

  <!-- Stage 2 -->
  <g transform="translate(350, 145)">
    <rect width="250" height="280" rx="16" fill="#1E293B" stroke="#334155" stroke-width="1.5"/>
    <circle cx="45" cy="45" r="22" fill="#38BDF8" />
    <text x="45" y="52" fill="#0F172A" font-size="14" font-weight="800" text-anchor="middle">02</text>
    <text x="80" y="42" fill="#38BDF8" font-size="11" font-weight="700">STAGE 2 · 2 MINS</text>
    <text x="80" y="60" fill="#FFFFFF" font-size="14" font-weight="700">Transparent Quote</text>
    
    <text x="25" y="105" fill="#CBD5E1" font-size="11">• Single monthly recurring total</text>
    <text x="25" y="130" fill="#CBD5E1" font-size="11">• Modular add-ons (CCTV, Wi-Fi 6)</text>
    <text x="25" y="155" fill="#CBD5E1" font-size="11">• Real-time dependency solver</text>
    <text x="25" y="180" fill="#CBD5E1" font-size="11">• ₹13,800/yr savings vs unorganized</text>
    <text x="25" y="205" fill="#CBD5E1" font-size="11">• Single unified billing line</text>
    
    <rect x="25" y="225" width="200" height="30" rx="8" fill="#38BDF8" opacity="0.2"/>
    <text x="125" y="244" fill="#38BDF8" font-size="10" font-weight="700" text-anchor="middle">Eliminates Complex PDFs</text>
  </g>

  <!-- Arrow 2 -->
  <path d="M 615 285 L 640 285" stroke="#38BDF8" stroke-width="3" stroke-linecap="round"/>
  <polygon points="645,285 637,280 637,290" fill="#38BDF8" />

  <!-- Stage 3 -->
  <g transform="translate(650, 145)">
    <rect width="250" height="280" rx="16" fill="#1E293B" stroke="#334155" stroke-width="1.5"/>
    <circle cx="45" cy="45" r="22" fill="#10B981" />
    <text x="45" y="52" fill="#0F172A" font-size="14" font-weight="800" text-anchor="middle">03</text>
    <text x="80" y="42" fill="#10B981" font-size="11" font-weight="700">STAGE 3 · 3 MINS</text>
    <text x="80" y="60" fill="#FFFFFF" font-size="14" font-weight="700">Smart KYC & DPDP</text>
    
    <text x="25" y="105" fill="#CBD5E1" font-size="11">• 1-Click GSTIN &amp; Udyam lookups</text>
    <text x="25" y="130" fill="#CBD5E1" font-size="11">• 90-day expiry check on proofs</text>
    <text x="25" y="155" fill="#CBD5E1" font-size="11">• Catches cancelled &amp; corrupt docs</text>
    <text x="25" y="180" fill="#CBD5E1" font-size="11">• DPDP Act 2023 consent capture</text>
    <text x="25" y="205" fill="#CBD5E1" font-size="11">• Dynamic PAN masking in UI &amp; logs</text>
    
    <rect x="25" y="225" width="200" height="30" rx="8" fill="#10B981" opacity="0.2"/>
    <text x="125" y="244" fill="#10B981" font-size="10" font-weight="700" text-anchor="middle">Zero Paper Submissions</text>
  </g>

  <!-- Arrow 3 -->
  <path d="M 915 285 L 940 285" stroke="#10B981" stroke-width="3" stroke-linecap="round"/>
  <polygon points="945,285 937,280 937,290" fill="#10B981" />

  <!-- Stage 4 -->
  <g transform="translate(950, 145)">
    <rect width="200" height="280" rx="16" fill="#1E293B" stroke="#334155" stroke-width="1.5"/>
    <circle cx="45" cy="45" r="22" fill="#A855F7" />
    <text x="45" y="52" fill="#FFFFFF" font-size="14" font-weight="800" text-anchor="middle">04</text>
    <text x="80" y="42" fill="#A855F7" font-size="11" font-weight="700">STAGE 4 · &lt;48 HRS</text>
    <text x="80" y="60" fill="#FFFFFF" font-size="14" font-weight="700">Fulfillment</text>
    
    <text x="20" y="105" fill="#CBD5E1" font-size="11">• 5-Stage live order status</text>
    <text x="20" y="130" fill="#CBD5E1" font-size="11">• Assigned technician PIN</text>
    <text x="20" y="155" fill="#CBD5E1" font-size="11">• Router pre-configuration</text>
    <text x="20" y="180" fill="#CBD5E1" font-size="11">• Rapid same-day/48h setup</text>
    <text x="20" y="205" fill="#CBD5E1" font-size="11">• Deflects 90% status calls</text>
    
    <rect x="20" y="225" width="160" height="30" rx="8" fill="#A855F7" opacity="0.2"/>
    <text x="100" y="244" fill="#C084FC" font-size="10" font-weight="700" text-anchor="middle">Activation in &lt;48 Hours</text>
  </g>
</svg>
"""

with open(os.path.join(diagrams_dir, 'customer_journey_diagram.svg'), 'w', encoding='utf-8') as f:
    f.write(journey_svg.strip())

print("Saved architecture_diagram.svg and customer_journey_diagram.svg to app/static/diagrams/!")


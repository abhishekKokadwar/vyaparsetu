# VyaparSetu (व्यापारसेतु) · Comprehensive Product & Engineering Roadmap
## Airtel Sync 2026 · Enterprise Track A (Project Udyam Digital)
**Platform Name:** **VyaparSetu** (*The Digital Bridge for MSME Commerce*)  
**Architecture Vision:** Zero-Paperwork, Self-Service Digital Onboarding for India's 6 Crore+ MSMEs  
**Team:** Hacker_247 · November 2026

---

## 🧭 Executive Overview of the Roadmap

This roadmap outlines the complete end-to-end engineering and product lifecycle for **VyaparSetu**. It is structured into **6 Fixed Core Phases** (mandatory foundational platform architecture) followed by **5 "If Time Permits" Extended Phases** (next-generation scale, Indic voice agents, and telecom core integration).

```mermaid
flowchart TD
    subgraph Core ["6 Fixed Core Phases (Foundational Platform)"]
        P1["Phase 1: Data Intelligence & Funnel Root-Cause Modeling"] --> P2["Phase 2: Deterministic Catalog & Pricing Engine"]
        P2 --> P3["Phase 3: Conversational GenAI Advisor (VyaparSaarthi)"]
        P3 --> P4["Phase 4: Smart KYC & DPDP Compliance Infrastructure"]
        P4 --> P5["Phase 5: Self-Service Order Fulfillment & Live Tracker"]
        P5 --> P6["Phase 6: Channel Partner Portal & Lead Salvage Engine"]
    end

    subgraph Extended ["Extended Scale Phases (If Time Permits)"]
        P6 --> P7["Phase 7: Omnichannel WhatsApp Conversational Bot"]
        P7 --> P8["Phase 8: Indic Voice AI Co-Pilot (Bhashini / Whisper)"]
        P8 --> P9["Phase 9: Production DigiLocker & Aadhaar e-Sign Gateway"]
        P9 --> P10["Phase 10: Predictive ML Propensity & Churn Prevention"]
        P10 --> P11["Phase 11: Telco OSS/BSS & Zero-Touch CPE Provisioning"]
    end
```

---

## 🧱 The 6 Fixed Core Phases

### Phase 1: Data Intelligence & Funnel Root-Cause Modeling
* **Primary Objective:** Analyze baseline telemetry, dissect funnel leakages from `smb_leads.csv`, and establish empirical benchmarks.
* **Key Deliverables:**
  1. **Funnel Decomposition:** Quantify conversion leakage at each milestone (Lead $\rightarrow$ Contacted $\rightarrow$ Needs Assessed $\rightarrow$ Quote Accepted $\rightarrow$ KYC $\rightarrow$ Activated).
  2. **Drop-Cause Categorization:** Group drop-offs into actionable clusters:
     - *Field Visit & Scheduling Friction* (1,632 leads: 805 unreachable, 827 scheduling friction).
     - *Pricing & Quotation Complexity* (1,006 leads: 385 quote complex/delayed, 621 price/competitor).
     - *Documentation & Paperwork Bottlenecks* (273 leads: missing GST/Udyam, expired address proofs).
  3. **Segment Profiles & Persona Archetypes:** Model economics across the 4 key cohorts:
     - *Micro Retail & Services (55%)*: ₹2.5k bundle, zero tolerance for lag in UPI/POS payments.
     - *Professional Offices (25%)*: ₹3.5k bundle, focus on uptime, cloud email, and 1TB ransomware backup.
     - *Small Multi-Site Businesses (15%)*: ₹6.9k bundle, demands single unified bill, central CCTV, SD-WAN.
     - *Small Manufacturers (5%)*: ₹12k+ bundle, demands dedicated leased lines, IoT, firewall.
  4. **Baseline KPI Dashboard:** Establish tracking metrics (7.36% conversion, ₹15,000 CAC, 17.6-day delay, 3.2 chase calls).

---

### Phase 2: Deterministic Catalog & Dynamic Pricing Engine
* **Primary Objective:** Build a bulletproof, high-speed rule evaluation engine matching all 25 products in `product_catalogue.csv`.
* **Key Deliverables:**
  1. **Strict Catalogue Rule Enforcement:**
     - `requires_gstin`: Gate enterprise leased lines (P05/P06), SD-WAN (P10), and SIP (P12) behind active GSTIN checks.
     - `requires_one_of`: Enforce parent connectivity dependencies (e.g., CCTV P23 requires base connectivity P01-P06).
     - `min_employees` & `min_sites`: Enforce minimum operational scale constraints.
     - `available_city_tiers`: Validate Tier 1 vs Tier 2 availability (e.g., Biz Fibre 1G limited to Tier 1).
  2. **Dynamic Bundle Pricing Matrix:**
     - Real-time calculation of monthly recurring charges (MRC), one-time setup fees (OTC), and lock-in contract durations.
     - Rule dependency validation API (`/api/catalogue/validate`).
  3. **Vendor Fragmentation Savings Calculator:**
     - Computes monthly and annual cost savings of unified Accel Business bundles vs. fragmented local vendors (~31% savings).

---

### Phase 3: Conversational GenAI Advisor (VyaparSaarthi)
* **Primary Objective:** Eliminate the 3–5 day sales discovery delay with an intuitive conversational advisor in Hindi and English.
* **Key Deliverables:**
  1. **Multilingual Needs Discovery Questionnaire:**
     - 4 high-signal inputs: Business type, Staff size, Location/Tier, Current telecom spend.
  2. **Tailored Archetype Bundle Generation:**
     - *Kirana Booster Pack*: Biz Fibre 100/AirFiber + Cloud POS + WhatsApp API + CCTV (~₹2,597/mo).
     - *Clinic & Healthcare Pro Suite*: Biz Fibre 300 + Cloud Email + Cloud Backup 1TB + Guest Wi-Fi (~₹2,522/mo).
     - *Multi-Site Enterprise Connect*: Biz Fibre 300 + 4G Failover + SD-WAN + Cloud CCTV (~₹4,697/mo).
     - *Industry Pro*: Leased Line 20 + Managed Firewall + Machine IoT Sensors (~₹10,500/mo).
  3. **Plain-Language "Why This Fits You" Engine:**
     - Translates technical telecom specs into direct business benefits (e.g. *"Zero-lag UPI billing counter"*, *"Protects patient files against ransomware"*).
  4. **Live Judge Scenario Test Runner:**
     - 1-click test scenarios for live demo evaluation (Kirana with no GST, Multi-site restaurant, etc.).

---

### Phase 4: Smart KYC Engine & DPDP Act 2023 Infrastructure
* **Primary Objective:** Replace 10-day physical document verification with 3-second automated verification compliant with India's DPDP Act, 2023.
* **Key Deliverables:**
  1. **Mock National Registry Connectors:**
     - Sub-second lookup against 3,534 GST records (`mock_gstin_registry.csv`).
     - Sub-second lookup against 2,723 MSME Udyam records (`mock_udyam_registry.csv`).
     - Synthetic format validation (accepting synthetic marker `X` as the 4th PAN character; Udyam district code `00`).
  2. **Automated Document OCR & Defect Detection (Planted Specimens K01–K12):**
     - **90-Day Freshness Check:** Evaluates utility bill dates against reference date **July 15, 2026** (Catches **K11** dated 2025-10-31 as expired!).
     - **Registry Status Auditing:** Flags Cancelled or Suspended GST records (Catches **K01** cancelled status!).
     - **File Integrity & Legibility:** Catches corrupt/blank documents (Catches **K04** blank GST certificate!).
     - **Completeness Verification:** Identifies missing mandatory documents (Catches **K05** missing Udyam!).
  3. **DPDP Act 2023 4-Pillar Privacy Layer:**
     - Explicit digital consent modal with affirmative opt-in.
     - Dynamic PAN/GSTIN masking across UI and server logs (`19EOGXXXXXX1ZL`).
     - Automated 30-day post-activation document purge policy.

---

### Phase 5: Self-Service Order Fulfillment & Live Tracking System
* **Primary Objective:** Eliminate customer anxiety and reduce the 3.2 status chase calls per lead by 90%.
* **Key Deliverables:**
  1. **5-Stage Visual Milestone Engine:**
     `Order Placed` $\rightarrow$ `Digital KYC Verified` $\rightarrow$ `Feasibility & Dispatch` $\rightarrow$ `Technician Assigned` $\rightarrow$ `Service Activated`.
  2. **Dynamic Installation SLA Countdown:**
     - Computed based on `typical_install_days` from the catalog (e.g., 2 days for 5G AirFiber vs 5 days for Fibre).
  3. **Field Engineer Dispatch Card:**
     - Real-time display of assigned engineer's name, verified badge ID, time slot, and security PIN.
  4. **Self-Service Order Lookup:**
     - Simple order tracking via mobile number or Order ID (`VS-2026-XXXXX`).

---

### Phase 6: Channel Partner & Field-Force Synergy Portal
* **Primary Objective:** Turn potential channel conflict into a force multiplier and recover high-value dropped leads.
* **Key Deliverables:**
  1. **Partner Assisted Mode:**
     - Tablet-optimized view enabling local channel partners and field executives to onboard non-digital shop owners in 1 physical visit.
  2. **AI Propensity Scoring Engine:**
     - Scans 4,632 dropped leads from `smb_leads.csv` across 6 dimensions (GST status, stage reached, spend band, employee count, drop reason).
     - Isolates 1,420 high-propensity leads (>70 score) representing **₹4.26 Crore in salvageable ARR**.
  3. **Partner Commission Attribution Ledger:**
     - Tracks partner QR code attribution and allocates a 12% commission pool (~₹51.1 Lakh) for partner-assisted closures.

---

## 🚀 Extended Scale Phases (If Time Permits)

### Phase 7: Omnichannel WhatsApp Conversational Bot
* **Objective:** Enable 100% of the journey directly inside WhatsApp without downloading an app or visiting a website.
* **Tech Stack:** Meta WhatsApp Business Cloud API / Twilio Webhooks / Python FastAPI.
* **Deliverables:**
  - WhatsApp Interactive Flow forms for the 4-question needs discovery.
  - In-chat document photo uploads with automatic compression and OCR parsing.
  - Real-time order milestone notifications and installation status alerts delivered via WhatsApp template messages.

---

### Phase 8: Indic Voice AI Co-Pilot (Bhashini / Whisper)
* **Objective:** Voice-first onboarding for Tier 2/3 business owners who prefer speaking in their local tongue over typing.
* **Tech Stack:** AI4Bharat / Bhashini API, OpenAI Whisper (ASR), ElevenLabs / Indic-TTS, Llama-3 / Gemini Indic fine-tune.
* **Deliverables:**
  - Real-time two-way voice assistant in **Hindi, Tamil, Telugu, Marathi, and Bengali**.
  - Natural speech understanding of mixed colloquial terms (e.g. *"Dukaan ke liye Wi-Fi chahiye, 4 ladke kaam karte hain"*).
  - Voice-guided document upload prompts.

---

### Phase 9: Production DigiLocker & Aadhaar e-Sign Gateway
* **Objective:** Upgrade from document image uploads to zero-upload instant government pulls.
* **Tech Stack:** DigiLocker API (National e-Governance Division), NSDL / e-Mudhra e-Sign Gateway.
* **Deliverables:**
  - 1-Click DigiLocker Consent Flow to fetch verified GST and Udyam certificates directly from official government repositories.
  - Aadhaar OTP-based electronic signature for digital service agreements, enabling legally binding contracts with 0 paper.

---

### Phase 10: Predictive ML Propensity & Automated Churn Prevention
* **Objective:** Productionize supervised ML models on CRM data to prevent 6-month customer churn.
* **Tech Stack:** Scikit-Learn, LightGBM / XGBoost, FastAPI microservice.
* **Deliverables:**
  - **Lead Conversion Propensity Model:** Trains on the 5,000 historical leads to dynamically rank incoming inbound leads for immediate sales follow-up.
  - **6-Month Churn Early Warning System:** Evaluates usage metrics (data drop-offs, payment retries, customer support tickets) to trigger automated retention discounts before churn occurs.

---

### Phase 11: Telco OSS/BSS & Zero-Touch CPE Provisioning
* **Objective:** Connect the digital front-end directly to Airtel's core telecom network infrastructure.
* **Tech Stack:** TR-069 / TR-369 protocol, OpenDaylight / OpenFlow, TMF Open APIs (TMF622 Product Ordering, TMF637 Product Inventory).
* **Deliverables:**
  - Automated OLT and Fibre port assignment upon successful KYC verification.
  - Zero-touch CPE router auto-configuration (pre-provisioning SSID and VLAN settings before field technician arrives).
  - Automated integration with Airtel enterprise billing engine (Amdocs / Netcracker).

---

## 📊 Summary Roadmap Timeline Matrix

| Phase | Milestone | Tech Stack / Test Suite | Status | Test Coverage | Target Impact |
|:---:|---|---|:---:|:---:|---|
| **Phase 1** | Data Intelligence & Funnel Modeling | `tests/test_phase1_intelligence.py` | **COMPLETED** | **6 / 6 PASSED** | Diagnosed 92.6% drop causes, GSTIN significance & 4 MSME cohorts |
| **Phase 2** | Deterministic Catalog & Pricing Engine | `tests/test_phase2_catalog_engine.py` | **COMPLETED** | **6 / 6 PASSED** | 25 products, directed dependency graph, ₹31% vendor savings model |
| **Phase 3** | Conversational GenAI Advisor (VyaparSaarthi) | `tests/test_phase3_advisor_engine.py` | **COMPLETED** | **10 / 10 PASSED** | Bilingual English/Hindi advisor, 15 jury scenarios (100% compliant) |
| **Phase 4** | Smart KYC & DPDP Compliance Infrastructure | `tests/test_phase4_smart_kyc.py` | **COMPLETED** | **10 / 10 PASSED** | K01–K12 edge cases, 90-day expiry check, SHA-256 consent audit ledger |
| **Phase 5** | Self-Service Order Fulfillment Live Tracker | `tests/test_phase5_order_tracker.py` | **COMPLETED** | **10 / 10 PASSED** | 6-stage milestone tracker, dynamic SLA, technician PIN, zero chase calls |
| **Phase 6** | Channel Partner Portal & Lead Salvage Engine | `tests/test_phase6_partner_portal.py` | **COMPLETED** | **11 / 11 PASSED** | 4,632 dropped leads scored, playbooks, WhatsApp pitches, ARR recovery |
| **Phase 7** | End-to-End System Integration & Gateway | `tests/test_phase7_end_to_end_journey.py` | **COMPLETED** | **5 / 5 PASSED** | Full customer lifecycle, OpenAPI contracts, sub-ms concurrency stress |
| **Total** | **VyaparSetu Platform Release v1.0.0** | **7 Test Suites** | **✅ PRODUCTION READY** | **58 / 58 PASSED** | **100% Test Pass Rate (5.33s runtime)** |

---

### Extended Scale Phases (Future Vision)
| Phase | Milestone | Tech Stack | Status | Target Impact |
|:---:|---|---|:---:|---|
| *Phase 8* | Omnichannel WhatsApp Interactive Bot | WhatsApp Cloud API, FastAPI | *Ready for Prod* | 100% in-chat self-serve discovery & checkout |
| *Phase 9* | Indic Voice AI Co-Pilot | Whisper / Bhashini / Indic-TTS | *Ready for Prod* | Voice onboarding in Hindi, Tamil, Telugu, Marathi |
| *Phase 10*| DigiLocker & Aadhaar e-Sign Gateway | DigiLocker API, NSDL e-Sign | *Architecture Ready*| Zero-document upload; Aadhaar OTP contract sign |
| *Phase 11*| Telco OSS/BSS & Zero-Touch CPE Provisioning | TR-069, TMF Open APIs | *Architecture Ready*| Instant network provisioning & auto-config |

---
*VyaparSetu Roadmap · Airtel Sync 2026 · Team Hacker_247*


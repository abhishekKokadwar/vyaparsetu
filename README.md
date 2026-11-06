# VyaparSetu (व्यापारसेतु) · Airtel Sync 2026 (Enterprise Track A)

> **"Making small businesses go digital in one sitting"**  
> **VyaparSetu** — Next-Gen MSME Digital Acquisition & Onboarding Platform  
> Official Submission by **Team Hacker_247** for **Airtel Sync 2026 - Digital Track**.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-brightgreen.svg)](https://www.python.org/)
[![Track: Enterprise Track A](https://img.shields.io/badge/Track-Enterprise%20Track%20A-red.svg)](https://unstop.com/college-fests/airtel-sync-2026-airtel-522045)

---

## 📌 Executive Summary

India's 6 Crore+ Micro, Small, and Medium Enterprises (MSMEs) are increasingly adopting digital tools (UPI/POS, WhatsApp Business, cloud email, CCTV). However, Accel Business (Airtel Enterprise) currently suffers from a **7.36% funnel conversion**, **₹15,000 CAC**, **17.6-day onboarding cycles**, and **3+ status chase calls** per customer due to legacy field-sales processes and complex documentation.

**Project Udyam Digital** reimagines this journey as a 10-minute, digital-first self-serve experience on mobile:
1. **GenAI Conversational Advisor:** Multilingual (Hindi/English) discovery engine that asks 4 intuitive questions and recommends a tailored product bundle adhering strictly to `product_catalogue.csv` rules.
2. **Transparent Quote & Checkout:** Unified single monthly bill with real-time add-on customization.
3. **Smart KYC Engine:** 1-click GSTIN & Udyam lookups (`mock_gstin_registry.csv`, `mock_udyam_registry.csv`), automated 90-day expiry checking against reference date **July 15, 2026**, document defect detection (e.g., K01-K12 applicants), and full **DPDP Act, 2023** compliance.
4. **Self-Service Order Tracker:** Real-time visibility into order status, SLA countdowns, and engineer dispatch.
5. **Partner & Field Coexistence:** Assisted Mode and AI propensity scoring to salvage dropped leads.

---

## 📂 Project Structure

```text
├── airtel_sync_case/              # Official problem statement, template, and case analysis
│   ├── Airtel_SYNC_Case.pdf       # Original Case Study PDF
│   └── Submission Template_Sync.pptx # Official Presentation Template
├── udyam_digital_data/            # Synthetic hackathon dataset
│   ├── product_catalogue.csv      # 25 products, pricing, rules, and dependencies
│   ├── smb_leads.csv              # 5,000 leads, funnel stages, and drop reasons
│   ├── mock_gstin_registry.csv    # 3,534 GST records with status and addresses
│   ├── mock_udyam_registry.csv    # 2,723 MSME Udyam records
│   └── kyc_documents/             # 47 specimen KYC documents (K01-K12)
├── PLAN.md                        # Complete project blueprint & execution plan
├── README.md                      # Project overview and documentation
└── .gitignore                     # Git ignore rules
```

---

## 🎯 Target Impact Metrics

| Metric | Current Baseline | Project Udyam Digital Target | Improvement |
|---|---|---|---|
| **Lead-to-Activation Conversion** | 7.36% (368 / 5,000) | **24.5%** | **3.3x Increase** |
| **Blended CAC** | ₹15,000 | **₹2,800** | **81% Cost Reduction** |
| **Lead-to-Activation Cycle Time** | 17.6 days | **< 48 hours** | **89% Faster Onboarding** |
| **Customer Status Chases** | 3.2 calls / lead | **< 0.3 calls / lead** | **90% Call Center Deflection** |
| **6-Month Churn Rate** | ~18.4% | **< 8.0%** | Higher stickiness from bundle synergy |

---

## 📑 Deliverables Roadmap

- [x] **Project Execution Plan & Data Analysis** (`PLAN.md`)
- [ ] **Interactive Full-Stack Web Application** (FastAPI backend + Interactive UI)
- [ ] **Smart KYC Engine with Automated Document & Expiry Verification**
- [ ] **Solution Architecture Diagram**
- [ ] **Official 7-Slide Submission Presentation Deck** (`.pptx` & `.pdf`)
- [ ] **1-Page DPDP Act 2023 Compliance & Data Minimisation Note**
- [ ] **3-Minute Demo Video Walkthrough Script**

---

*Authored for the Airtel Sync 2026 Innovation Challenge.*


# VyaparSetu (व्यापारसेतु) · Airtel Sync 2026 (Enterprise Track A)

> **"Making small businesses go digital in one sitting"**  
> **VyaparSetu** — Next-Gen MSME Digital Acquisition & Onboarding Platform  
> Official Submission by **Team Hacker_247** for **Airtel Sync 2026 - Digital Track**.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-brightgreen.svg)](https://www.python.org/)
[![Track: Enterprise Track A](https://img.shields.io/badge/Track-Enterprise%20Track%20A-red.svg)](https://unstop.com/college-fests/airtel-sync-2026-airtel-522045)

---

## 📌 Executive Summary

India's 6 Crore+ Micro, Small, and Medium Enterprises (MSMEs) are increasingly adopting digital tools (UPI/POS, WhatsApp Business, cloud email, CCTV). However, Accel Business (Airtel Enterprise) currently suffers from a **7.36% funnel conversion**, **₹15,053 CAC**, **17.6-day onboarding cycles**, and **3.0 status chase calls** per customer due to legacy field-sales processes and complex documentation.

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
├── ROADMAP.md                     # Comprehensive 6 Fixed + 5 Stretch Phases Roadmap
├── PLAN.md                        # Complete project blueprint & execution plan
├── DPDP_COMPLIANCE_NOTE.md        # Official 1-Page DPDP Act 2023 compliance architecture
├── DEMO_SCRIPT.md                 # 3-Minute timed demo walkthrough script
├── Hacker_247_ABVIIITMGwalior.pptx  # 7-slide submission deck (official Sync template)
├── Hacker_247_ABVIIITMGwalior.pdf   # Same deck as PDF
├── deck/index.html                 # Deck source: every slide drawn as SVG by JS
├── scripts/build_svg_deck.py       # Rebuilds the PPTX + PDF from deck/index.html
├── app/                           # Full-stack working prototype (FastAPI + Modern UI)
├── run.py                         # One-click runner (http://localhost:8000)
└── README.md                      # Project overview and documentation
```

---

## 🎯 Target Impact Metrics

6-month targets against the Apr–Jun 2026 baseline (`smb_leads.csv`).

| Metric | Today | 6-month target | Main lever |
|---|---|---|---|
| **Lead → activation** | 7.4% (368 / 5,000) | **15%** | advisor + instant quote |
| **Time to activate** | 17.6 days | **≤ 5 days** (fibre install-bound) | paperless KYC |
| **Status chase calls** | 3.0 per customer | **< 0.5** | tracker + WhatsApp updates |
| **Cost per activation** | ₹15,053 | **≤ ₹7,500** | fewer field visits |
| **6-month churn** | 15.2% | **< 10%** | right-sized bundles |

Same 5,000 leads a quarter → 750 activations instead of 368: about +₹26 L a month in new revenue (382 × ₹6,900 median bundle), roughly ₹3.2 Cr a year from each quarter's leads.

---

## 📑 Deliverables Roadmap

- [x] **Project Execution Plan & Data Analysis** (`PLAN.md`)
- [x] **Comprehensive Product & Engineering Roadmap (6 Fixed + 5 Stretch Phases)** (`ROADMAP.md`)
- [x] **Interactive Full-Stack Web Application** (FastAPI backend + Modern UI served via `run.py`)
- [x] **Smart KYC Engine with Automated Document & Expiry Verification** (Live K01–K12 Answer Key)
- [x] **7-Slide Submission Deck on the official template** (`Hacker_247_ABVIIITMGwalior.pptx`)
- [x] **Submission PDF** (`Hacker_247_ABVIIITMGwalior.pdf`)
- [x] **1-Page DPDP Act 2023 Compliance & Data Minimisation Note** (`DPDP_COMPLIANCE_NOTE.md`)
- [x] **3-Minute Demo Video Walkthrough Script** (`DEMO_SCRIPT.md`)

---

*Authored for the Airtel Sync 2026 Innovation Challenge.*


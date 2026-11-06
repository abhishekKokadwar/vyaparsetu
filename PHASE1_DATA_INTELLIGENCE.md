# Phase 1: Data Intelligence & Funnel Root-Cause Report
## Empirical Analysis of SMB Acquisition Telemetry (smb_leads.csv)
**Project:** VyaparSetu (व्यापारसेतु) · Airtel Sync 2026 (Enterprise Track A)
**Dataset:** 5,000 synthetic SMB leads across Tier 1 & Tier 2 cities (Apr–Jun 2026)

---

## 1. Funnel Decomposition & Stage Leakage

- **Total Inbound Leads:** 5,000
- **Total Activated Customers:** 368
- **Overall Conversion Rate:** **7.36%**
- **Total Lost Pipeline:** 4,632 leads (92.64% leakage)

| Funnel Stage | Reached Volume | Drop at this Stage | Step Conversion % | Cumulative % |
|---|:---:|:---:|:---:|:---:|
| **Lead** | 5,000 | 0 | 100.0% | 100.0% |
| **Contacted** | 3,406 | 1,594 | 68.12% | 68.12% |
| **Needs assessed** | 1,974 | 1,432 | 57.96% | 39.48% |
| **Quote accepted** | 861 | 1,113 | 43.62% | 17.22% |
| **KYC complete** | 588 | 273 | 68.29% | 11.76% |
| **Activated** | 368 | 220 | 62.59% | 7.36% |

> [!IMPORTANT]
> **Steepest Drop Point:** The sharpest drop-off occurs between **Needs assessed $\rightarrow$ Quote accepted**, where **56% of leads drop out** (only 43.6% accept). The second critical drop is between **Quote accepted $\rightarrow$ KYC complete** (31.7% drop).

---

## 2. Drop-Cause Taxonomy & Root-Cause Clustering

All 21 discrete drop reasons were categorized into 5 operational clusters:

| Operational Cluster | Dropped Leads | % of Drops | GST Registered % | Addressability via VyaparSetu |
|---|:---:|:---:|:---:|---|
| **Field Scheduling & Sales Friction** | 2,102 | 45.38% | 71.55% | HIGH (Directly solved by self-serve advisor & tracker) |
| **Quote & Pricing Friction** | 1,113 | 24.03% | 65.23% | HIGH (Directly solved by self-serve advisor & tracker) |
| **Incumbent Lock-in & Intent Gap** | 605 | 13.06% | 66.78% | MEDIUM / LOW |
| **Fulfillment, Payment & Network Friction** | 539 | 11.64% | 80.15% | MEDIUM / LOW |
| **Paperwork & Verification Bottlenecks** | 273 | 5.89% | 47.62% | HIGH (Directly solved by self-serve advisor & tracker) |

---

## 3. Multi-Cohort Econometric Profiling

| Segment | Base Share | Conversion | Avg Existing Spend | Median Bundle | Blended CAC | Cycle Time | 6M Churn | NPS |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Micro retail & services** | 54.2% | 4.06% | ₹903.29 | ₹2,504.82/mo | ₹812.4 | 16.65d | 22.73% | 7.05/10 |
| **Professional offices** | 24.9% | 11.07% | ₹2,592.7 | ₹6,795.87/mo | ₹1,183.54 | 16.92d | 13.77% | 6.92/10 |
| **Small multi-site businesses** | 15.1% | 10.99% | ₹9,123.64 | ₹31,233.49/mo | ₹1,716.54 | 18.77d | 10.84% | 6.7/10 |
| **Small manufacturers** | 5.8% | 12.8% | ₹13,914.19 | ₹19,979.73/mo | ₹1,961.94 | 20.51d | 8.11% | 6.46/10 |

---

## 4. Statistical Signal Verification

### Test 1: GSTIN Significance Test (Chi-Square)
- **Hypothesis:** H1: Leads with verified GSTIN activate at a significantly higher rate than non-GST leads.
- **Chi-Square Statistic:** `84.7907`
- **p-value:** `3.3168e-20` (Statistically Significant: **True**)
- **Conclusion:** GSTIN status is an extreme positive predictor (p < 0.001). 1-click GST auto-validation is critical.

### Test 2: Onboarding Chase Calls vs. Customer Churn (Welch's t-test)
- **Hypothesis:** H1: Customers who experienced high chase calls during onboarding exhibit higher 6-month churn.
- **t-statistic:** `2.706`
- **p-value:** `8.4457e-03` (Statistically Significant: **True**)
- **Mean calls by churned:** 3.39 vs **Retained:** 2.94
- **Conclusion:** Customers who made 4+ chase calls are significantly more likely to churn within 6 months. Order tracking directly protects LTV.

---
*Phase 1 Analysis Complete · Generated automatically by DataIntelligenceEngine*
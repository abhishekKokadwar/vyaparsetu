# VyaparSetu · Data Privacy & Security Architecture Note
## Compliance with India's Digital Personal Data Protection (DPDP) Act, 2023
**Platform:** VyaparSetu (व्यापारसेतु) · Next-Gen MSME Onboarding Engine  
**Entity:** Accel Business (Enterprise Arm of Accel Telecom)  
**Hackathon Track:** Airtel Sync 2026 · Enterprise Track A (Project Udyam Digital)  
**Team:** Hacker_247 · November 2026

---

### 1. Executive Summary

As enterprise telecom onboarding shifts from physical paper collection to instant, self-service digital onboarding, compliance with the **Digital Personal Data Protection (DPDP) Act, 2023** becomes paramount. 

Small business owners frequently share highly sensitive financial and identity records during KYC—including Permanent Account Numbers (PAN embedded in GSTIN), Udyam MSME certifications, utility billing records, and personal signatory IDs (Aadhaar / Voter ID / Passport). 

**VyaparSetu** integrates privacy-by-design at every layer of the customer journey, adhering strictly to the four core principles of the DPDP Act: **Explicit Consent**, **Purpose Limitation**, **Data Minimisation**, and **Storage Limitation**.

---

### 2. The Four Pillars of DPDP Act 2023 Compliance in VyaparSetu

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                      VyaparSetu Privacy-by-Design Matrix                      │
├───────────────────────┬───────────────────────────────────────────────────────┤
│ DPDP Act Requirement  │ Technical Implementation in VyaparSetu                │
├───────────────────────┼───────────────────────────────────────────────────────┤
│ 1. Notice & Consent   │ Granular, plain-language affirmative digital consent  │
│    (Section 5 & 6)    │ checkbox before triggering any document upload or API.│
├───────────────────────┼───────────────────────────────────────────────────────┤
│ 2. Purpose Limitation │ Data processed strictly for business identification,  │
│    (Section 7)        │ eligibility checks, and service dispatch.             │
├───────────────────────┼───────────────────────────────────────────────────────┤
│ 3. Data Minimisation  │ Masking central 6 PAN characters in GSTIN across logs │
│    (Section 8)        │ and client UI (e.g. 19EOGXXXXXX1ZL).                  │
├───────────────────────┼───────────────────────────────────────────────────────┤
│ 4. Storage Limitation │ Automated 30-day post-activation purging of specimen  │
│    (Section 8(7))     │ files; retained only as tamper-proof SHA-256 hashes.  │
└───────────────────────┴───────────────────────────────────────────────────────┘
```

#### Pillar 1: Plain-Language Notice and Explicit Consent (Sections 5 & 6)
* Prior to requesting any documentation, the business owner is presented with a concise, non-legalese consent modal available in their preferred language (**English or Hindi**).
* Consent is **affirmative, granular, and unbundled**—the customer can proceed with discovery without KYC, and KYC consent is captured only when proceeding to checkout.
* Each consent event logs a cryptographic timestamp, IP address, and unique consent token for regulatory audit trails.

#### Pillar 2: Purpose Limitation (Section 7)
* Data collected via GSTIN and Udyam registries is restricted strictly to:
  1. Entity verification and legal name validation.
  2. Installation address feasibility check.
  3. Direct telecom billing contact authorization.
* **No secondary commercialization:** Information is cryptographically isolated and never shared with third-party advertisers, credit scoring aggregators, or external marketing brokers.

#### Pillar 3: Data Minimisation & Identifier Masking (Section 8)
* **On-the-Fly Redaction:** The 10-character PAN embedded within the 15-character GSTIN has its middle 6 characters dynamically masked in all client-facing UI components and server access logs (`19EOGXXXXXX1ZL`).
* **Zero Aadhaar Storage:** When signatory IDs are scanned, personal identifiers (e.g., full Aadhaar numbers or personal dates of birth) are parsed solely in memory to extract name and authorization validity, and discarded without persisting raw numbers to disk.
* **Role-Based Access Control (RBAC):** Channel partners and field sales agents operating in "Assisted Mode" have access only to status indicators (e.g., "KYC Approved" or "Address Proof Expired"), preventing unauthorized exposure of raw utility bills or financial records.

#### Pillar 4: Storage Limitation & Automated Purge Policy (Section 8(7))
* In accordance with Section 8(7) of the DPDP Act, personal data is not retained beyond the period necessary to satisfy the purpose for which it was processed:
  * **Document Purge Schedule:** Raw uploaded PDF/PNG specimen images are queued for automated deletion **30 days post-activation**.
  * **Cryptographic Attestation:** Once verified, only a one-way cryptographic hash (SHA-256) of the document, the registry transaction ID, and the compliance timestamp are retained in the permanent order ledger.
  * **Right to Erasure:** Small business owners can trigger account deactivation and document wipe-out directly through the self-service Order Tracker.

---

### 3. Cryptographic and Network Security Measures

1. **In-Transit Security:** All API endpoints enforce strict **TLS 1.3 encryption**, disabling deprecated cipher suites.
2. **At-Rest Security:** Customer records, registry caches, and temporary document stores are encrypted using **AES-256-GCM**.
3. **Internal Log Hygiene:** Automated log sanitization filters strip PANs, GSTINs, mobile numbers, and authorization tokens before logs are ingested into observability pipelines.

---
*VyaparSetu · Designed with privacy, trust, and enterprise compliance from Day 1.*


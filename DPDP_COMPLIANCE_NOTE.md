# VyaparSetu: Data Privacy & Security Note (DPDP Act, 2023)

One-page PDF for submission: [Hacker_247_Privacy_Note.pdf](Hacker_247_Privacy_Note.pdf). Source: `deck/privacy_note.html`.

**Collected:** business and owner name, mobile, city, GSTIN, Udyam number, address-proof date, signatory-ID name/validity. Used only to verify the business, check serviceability and create the order. All data is synthetic; registries are mock files.

## Built and verified in the prototype

| Principle | What the running system does |
|---|---|
| Consent (s.5-6) | Upload and verification stay locked until the owner ticks a plain-language consent. Each grant, revocation and purge is appended to a ledger (consent ID, timestamp, purpose, retention, SHA-256 audit hash) in Neon Postgres. |
| Withdrawal | A revoke call halts processing; a purge job issues deletion receipts, also written to the ledger. |
| Minimisation (s.8) | Documents are read in memory and never written to disk or the database. Only extracted fields and the verdict are kept. 4 MB file cap, PDFs rejected. GSTINs are masked in responses. |
| Purpose limitation (s.7) | Data feeds only the KYC rules, serviceability and the order. |
| Order access | Tracker needs order number and the registered mobile; the server returns one identical "not found" for a wrong number or unknown order. |

**Sub-processors:** Google Gemini API (document transcription, advisor language understanding; free tier in the prototype), Neon Postgres, Vercel.

## Known limits (not built yet)

No customer login (production: mobile OTP). Partner portal is open demo data (production: SSO + role-based access). Purge is a callable job, not yet scheduled (production: automatic 30 days after activation). Field-level encryption, log scrubbing, breach-notification runbook, DigiLocker consent flow and data-principal rights screens are planned.

# VyaparSetu · Video Demo Guide & Recording Script
## Airtel Sync 2026 · Enterprise Track A (Project Udyam Digital)
**Target Video Duration:** Exactly 3:00 minutes (180 seconds)  
**Deliverable:** 3-Minute Video Walkthrough Link / MP4  
**Presenter:** Team Hacker_247 (ABV-IIITM Gwalior)  

---

# Part 1 · Presenter Demo Guide (Setup & Checklist)

### 1. Pre-Recording Technical Setup
1. **Start Local Backend Server:**
   ```powershell
   cd d:\CODES\hackathons_and_activities\airtel
   py -m uvicorn app.main:app --port 8000
   ```
   *Verify it loads cleanly at `http://127.0.0.1:8000`.*
2. **Prepare Browser Window:**
   - Recommended Browser: Google Chrome or Microsoft Edge.
   - Window Resolution: Set display to **1920 × 1080 (1080p)**, zoom level **100%**.
   - Press `Ctrl + Shift + B` to hide the bookmarks bar for a clean interface.
   - Clear browser cache / `localStorage` once before recording (`F12` $\rightarrow$ Application $\rightarrow$ Clear site data) so you start fresh.
3. **Folder Shortcut for Drag-and-Drop:**
   - Open Windows File Explorer to:
     `d:\CODES\hackathons_and_activities\airtel\udyam_digital_data\kyc_documents`
   - Pre-select the 4 files for **K07**:
     - `K07_gst_certificate.png`
     - `K07_udyam_certificate.png`
     - `K07_address_proof.png`
     - `K07_signatory_id.png`
   - Position this Explorer window on one side so you can smoothly drag them into the upload box (or click "Choose Files").
4. **Clipboard Text Ready:**
   - Copy this sample vernacular query to your clipboard:
     ```text
     मेरी जयपुर में 2-counter किराना दुकान है 2 लोग काम करते हैं, wifi और बिलिंग चाहिए
     ```
5. **Recording Tool Settings:**
   - Tools: OBS Studio, Loom, or Windows Game Bar (`Win + Alt + R`).
   - Frame Rate: 30 fps or 60 fps.
   - Audio: Use a dedicated headset/USB mic with noise cancellation in a quiet room.

---

### 2. Live Demo Flow Overview (180 Seconds)

```
[00:00 - 00:25]  Scene 1: The Problem Hook (The 93% Funnel Drop)
[00:25 - 00:55]  Scene 2: Conversational GenAI Advisor & Rule Alignment
[00:55 - 01:20]  Scene 3: Transparent Single-Bill Quote & Add-ons
[01:20 - 02:05]  Scene 4: Smart KYC, DPDP 2023 & Live Edge Cases (K11 & K07)
[02:05 - 02:35]  Scene 5: Self-Service Order Tracker & Partner Salvage Portal
[02:35 - 03:00]  Scene 6: Business Impact & Strategic Wrap-up
```

---

# Part 2 · Teleprompter Video Script (Second-by-Second)

---

### Scene 1 · The Problem Hook (00:00 – 00:25)
* **Visual Action:**
  - Start on Slide 1 or the VyaparSetu Landing Page showing the header: *"Project Udyam Digital · Making Small Businesses Go Digital in One Sitting"*.
  - Cursor briefly highlights the subtitle or funnel context.
* **Narration:**
  > *"Hello Airtel leadership and jury members! Over 6 Crore Indian MSMEs are digitizing rapidly, yet enterprise telecom drops **93% of small business leads**.*  
  > *In Accel Business's baseline data, acquiring a simple clinic or kirana takes **17.6 days of paper friction**, **3 status chase calls**, and costs **₹15,053 in blended CAC**.*  
  > *We built **VyaparSetu (व्यापारसेतु)** to collapse this two-week ordeal into a **10-minute self-serve onboarding journey in a single sitting** on mobile."*

---

### Scene 2 · Conversational GenAI Advisor (00:25 – 00:55)
* **Visual Action:**
  - Show the **Advisor tab**.
  - Paste the query into the chat box:  
    `"मेरी जयपुर में 2-counter किराना दुकान है 2 लोग काम करते हैं, wifi और बिलिंग चाहिए"`  
    and click **Ask VyaparSaarthi** (or click the **Kirana Booster** quick scenario button).
  - Point cursor to the extracted archetype: **Micro Retail**, **City Tier 2**, **2 Staff**, **Single Site**.
  - Highlight the recommended pack: **Kirana & Retail Digital Booster (~₹2,196/mo)**.
* **Narration:**
  > *"Instead of waiting days for a sales rep, a business owner opens VyaparSetu and types or speaks in their daily vernacular—English, Hindi, Marathi, Tamil, or Punjabi.*  
  > *Our GenAI Advisor extracts business archetype, employee scale, and connectivity needs in real time.*  
  > *Notice that while the query mentioned '2 counters', our engine correctly understands that counters are not separate branches—classifying it as a single-site micro business!*  
  > *Crucially, the LLM **never hallucinates pricing**: our deterministic rules engine evaluates all 25 catalog constraints, generating a tailored bundle with zero guesswork."*

---

### Scene 3 · Transparent Quote & Single Invoicing (00:55 – 01:20)
* **Visual Action:**
  - Click on the **Quote & Bundle** tab.
  - Hover over the transparent bill breakdown.
  - Toggle an add-on (e.g., check **Cloud CCTV** or **Guest Wi-Fi**).
  - Watch the monthly bill total update instantly in real time (e.g. from ₹2,196 to ₹2,545).
  - Point to the **"~28.6% Savings vs Fragmented Vendors"** badge.
* **Narration:**
  > *"Next, the Quote Configurator gives small merchants 100% price transparency. No hidden charges or unexpected multi-vendor bills.*  
  > *The owner can toggle business add-ons like Cloud CCTV or Secure Guest Wi-Fi, and the monthly subscription recalculates live on a single invoice.*  
  > *By consolidating connectivity, POS, security, and cloud backup into one bill, VyaparSetu delivers **28.6% cost savings** over fragmented local providers."*

---

### Scene 4 · Smart KYC, DPDP 2023 & Live Planted Edge Cases (01:20 – 02:05)
⭐ *Jury Highlight & Core Technical Climax*

* **Visual Action:**
  - Click on the **Smart KYC** tab.
  - Point cursor to the **DPDP Act 2023 Consent Checkbox** and cryptographic SHA-256 audit ledger hash.
  - **Check 1 (K11 - Expired Bill):**  
    Select **K11 (Trinity Bake House)** from the dropdown and click *Verify Applicant*.  
    Show the red rejection: `"Address proof expired: 257 days old (exceeds 90-day maximum limit)"`.
  - **Check 2 (Real Upload / K07 - Planted Legal Name Mismatch):**  
    Click or drag the 4 **K07 PNG files** into the file upload zone.  
    Wait 2 seconds as OCR extracts the text live.  
    Show the red rejection: `"Legal entity mismatch: Certificate says 'Neha Banerjee (Prop. Shri Physio Clinic)' but GST registry says 'Neha Banerjee (Prop. Neelgiri Physio Clinic)'"`.
  - **Check 3 (K02 - Clean Pass):**  
    Select **K02 (Harmony Dental Clinic)** from the dropdown.  
    Click *Verify Applicant*.  
    Instantly show the bright green **VERIFIED** card with all checks passed!
* **Narration:**
  > *"Now, the core innovation: Smart KYC, engineered from the ground up for the **DPDP Act 2023** with explicit affirmative consent and end-to-end PII masking.*  
  > *Watch how our engine handles the hackathon's planted fraud edge cases:*  
  > *First, **Applicant K11**: Our OCR date validator cross-references the electricity bill against the reference date of July 15, 2026. The bill is 257 days old—**instantly rejected** for violating the 90-day freshness rule!*  
  > *Next, **Real Multi-Document Upload**: We drop 4 actual scanned certificates for **Applicant K07**. Without relying on filenames, our OCR classifies each document, queries the National GST registry, and flags a critical fraud attempt: the certificate prints 'Shri Physio Clinic', but the official tax registry records 'Neelgiri Physio Clinic'—**tampering caught immediately!***  
  > *Finally, **Applicant K02**: Active GSTIN, verified Udyam certificate, 54-day fresh utility bill—**fully verified in under 3 seconds!**"*

---

### Scene 5 · Self-Service Order Tracker & Partner Portal (02:05 – 02:35)
* **Visual Action:**
  - In the KYC tab, click **"Proceed to Activation & Create Order"**.
  - The UI automatically switches to the **Order Tracker tab**.
  - Highlight the newly minted Order ID (e.g., `VS-2026-XXXXX`), the 6 progressive milestone badges, the dynamic 5-day SLA, and the **4-digit Technician PIN (e.g. 8412)**.
  - Switch to the **Partner Portal tab**.
  - Show the live stats: **932 Salvageable Leads**, **₹1.91 Cr Recoverable ARR**, **15% Partner Commission Pool (~₹28.6 Lakh)**.
  - Click on the first lead row to view the pre-filled **WhatsApp Re-engagement Playbook** with masked contact name (`Gurpreet J.`).
* **Narration:**
  > *"With KYC approved, the customer confirms their order with one tap. Zero sales chasing!*  
  > *The Order Tracker displays transparent SLA milestones, assigned field engineer, and a 4-digit security PIN to authorize the physical installation handover.*  
  > *Meanwhile, what happens to the 4,632 dropped leads in the dataset?*  
  > *Our **Channel Partner Portal** analyzes dropped funnel telemetry. By applying an 80th-percentile propensity score, it isolates the top **932 high-value salvageable leads representing ₹1.91 Crore in recoverable ARR**.*  
  > *Local partners receive pre-populated WhatsApp playbooks and a 15% revenue-share commission pool (~₹28.6 Lakh), transforming field channel competition into active digital synergy!"*

---

### Scene 6 · Business Impact & Strategic Close (02:35 – 03:00)
* **Visual Action:**
  - Show the **Impact Summary slide** or the interactive **Diagrams view** (`/diagrams`).
  - Hover over the 5 core business metrics.
* **Narration:**
  > *"In summary, VyaparSetu fundamentally transforms Accel Business's unit economics:*  
  > *1. **Lead Conversion doubles** from 7.4% to **15.0%**.*  
  > *2. **Blended CAC is cut in half**, dropping from ₹15,053 to **under ₹7,500**.*  
  > *3. **Fulfillment drops** from 17.6 days to **under 5 days**, and anxious chase calls fall from 3.0 to **under 0.5**.*  
  > *4. Backed by **69 passing tests**, a 32-endpoint REST architecture, and DPDP compliance, VyaparSetu enables India's small businesses to go digital in one sitting.*  
  > *Thank you!"*

---

# Part 3 · Quick Speaker Cue Card

| Timestamp | Screen | Key Dialogue / Words to Stress |
|---|---|---|
| **0:00 - 0:25** | Landing / Funnel | *"Drops 93%... ₹15,053 CAC... 10 minutes in a single sitting"* |
| **0:25 - 0:55** | Advisor Tab | *"Vernacular Hindi/Marathi... counters aren't sites... deterministic rules"* |
| **0:55 - 1:20** | Quote Tab | *"Single invoice... 28.6% savings over fragmented local vendors"* |
| **1:20 - 1:35** | KYC / K11 | *"DPDP consent... K11 rejected: 257 days old bill violates 90-day limit"* |
| **1:35 - 1:55** | KYC Upload K07 | *"Real file upload... OCR catches Shri Physio vs Neelgiri Physio tampering"* |
| **1:55 - 2:05** | KYC / K02 | *"K02 verified cleanly in 3 seconds"* |
| **2:05 - 2:20** | Order Tracker | *"6 milestones... 4-digit technician PIN... zero chase calls"* |
| **2:20 - 2:35** | Partner Portal | *"932 salvageable leads... ₹1.91 Cr ARR... 15% partner commission"* |
| **2:35 - 3:00** | Impact / Wrap-up | *"Conversion 7.4% to 15%... CAC under ₹7,500... 5-day activation"* |

---

# Part 4 · Troubleshooting & Recording Tips

1. **If File Upload takes 2–3 seconds:**
   - Speak naturally through the upload: *"As the files are processed, our server runs dynamic OCR and document classification..."*
2. **If You Stumble on Words:**
   - Don't restart from 0:00! Pause for 2 seconds, re-say the sentence clearly, and use a simple free video editor (e.g. Clipchamp, CapCut, or Premiere) to trim the 2-second gap.
3. **Pacing:**
   - Total words in script: **~390 words**.
   - At a standard conversational pace of **130 words per minute**, 390 words fits comfortably into **2 minutes 50 seconds**, leaving 10 seconds of natural breathing room.

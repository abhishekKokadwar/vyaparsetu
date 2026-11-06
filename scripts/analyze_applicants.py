import json, re
import pandas as pd
from datetime import datetime

with open('udyam_digital_data/kyc_extracted.json', encoding='utf-8') as f:
    data = json.load(f)

gst_df = pd.read_csv('udyam_digital_data/mock_gstin_registry.csv')
udyam_df = pd.read_csv('udyam_digital_data/mock_udyam_registry.csv')

applicants = {}
for fname, text in data.items():
    code = fname.split('_')[0]
    dtype = '_'.join(fname.split('_')[1:]).replace('.png', '')
    applicants.setdefault(code, {})[dtype] = text

TODAY = datetime.strptime("2026-07-15", "%Y-%m-%d")

print("APPLICANT GROUND TRUTH ANALYSIS:")
print("="*60)

for app_id in sorted(applicants.keys()):
    docs = applicants[app_id]
    addr = docs.get('address_proof', '')
    gst = docs.get('gst_certificate', '')
    udyam = docs.get('udyam_certificate', '')
    sig = docs.get('signatory_id', '')

    # Signatory business name
    m_sig_biz = re.search(r'For business\s+(.*?)\s+ID no', sig)
    biz_name = m_sig_biz.group(1).strip() if m_sig_biz else "Unknown"

    # Signatory person name
    m_sig_person = re.search(r'Name\s+(.*?)\s+Designation', sig)
    person_name = m_sig_person.group(1).strip() if m_sig_person else "Unknown"

    # Bill date
    m_bill_date = re.search(r'202\d-\d{2}-\d{2}', addr)
    bill_date_str = m_bill_date.group(0) if m_bill_date else "Missing"
    days_old = None
    if bill_date_str != "Missing":
        b_dt = datetime.strptime(bill_date_str, "%Y-%m-%d")
        days_old = (TODAY - b_dt).days

    # Registry lookups
    gst_match = gst_df[gst_df['trade_name'].str.lower() == biz_name.lower()]
    if gst_match.empty:
        gst_match = gst_df[gst_df['legal_name'].str.lower().str.contains(biz_name.lower(), regex=False, na=False)]
    
    gst_status = gst_match['status'].values[0] if not gst_match.empty else "NOT_IN_REGISTRY"
    gst_gstin = gst_match['gstin'].values[0] if not gst_match.empty else "N/A"
    
    udyam_match = udyam_df[udyam_df['enterprise_name'].str.lower() == biz_name.lower()]
    udyam_status = "FOUND" if not udyam_match.empty else "NOT_IN_REGISTRY"
    udyam_no = udyam_match['udyam_number'].values[0] if not udyam_match.empty else "N/A"

    has_udyam_doc = 'udyam_certificate' in docs
    has_gst_doc = 'gst_certificate' in docs and len(gst) > 50

    issues = []
    if gst_status != 'Active':
        issues.append(f"GSTIN is {gst_status} ({gst_gstin})")
    if days_old is not None and days_old > 90:
        issues.append(f"Address proof is {days_old} days old (>90 days limit!)")
    if not has_udyam_doc:
        issues.append("Missing Udyam Certificate document")
    if not has_gst_doc:
        issues.append("Corrupt or missing GST certificate")

    status_verdict = "REJECT" if issues else "PASS"
    print(f"[{app_id}] {biz_name} ({person_name})")
    print(f"     Verdict: {status_verdict}")
    print(f"     GSTIN: {gst_gstin} ({gst_status}) | Udyam: {udyam_no} ({udyam_status})")
    print(f"     Bill Date: {bill_date_str} ({days_old} days old as of 2026-07-15)")
    print(f"     Has Udyam Doc: {has_udyam_doc} | Has Valid GST Doc: {has_gst_doc}")
    if issues:
        print(f"     ISSUES: {'; '.join(issues)}")
    print("-" * 60)

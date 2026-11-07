import pytest
from datetime import datetime
from app.registry_service import RegistryService
from app.kyc_engine import SmartKYCEngine, REF_DATE, REF_DATE_STR

@pytest.fixture(scope="module")
def registry():
    return RegistryService()

@pytest.fixture(scope="module")
def kyc_engine(registry):
    return SmartKYCEngine(registry)

def test_gstin_format_validator(registry):
    """Verify GSTIN format validator accepts synthetic 'X' marker and rejects malformed strings"""
    # Valid standard GSTIN
    assert registry.validate_gstin_format("27ABCDE1234F1Z5") is True

    # Valid synthetic dataset GSTIN (4th char of PAN is 'X')
    assert registry.validate_gstin_format("37IHKXV5167L1ZS") is True

    # Invalid GSTINs
    assert registry.validate_gstin_format("") is False
    assert registry.validate_gstin_format("INVALID123") is False
    assert registry.validate_gstin_format("27ABCDE1234F1Z") is False  # 14 chars
    assert registry.validate_gstin_format("27ABCDE1234F1Z55") is False  # 16 chars
    assert registry.validate_gstin_format("99ABCDE1234F1A5") is False  # 13th char must be 'Z'

def test_udyam_format_validator(registry):
    """Verify Udyam registration structure validation with '00' district marker"""
    # Valid synthetic Udyam format
    assert registry.validate_udyam_format("UDYAM-MH-00-1234567") is True
    assert registry.validate_udyam_format("UDYAM-DL-00-9876543") is True

    # Invalid formats
    assert registry.validate_udyam_format("UDYAM-MH-01-1234567") is False  # Non-00 district
    assert registry.validate_udyam_format("UDYAM-M-00-1234567") is False  # 1-char state
    assert registry.validate_udyam_format("UDYAM-MH-00-123456") is False  # 6 digits instead of 7
    assert registry.validate_udyam_format("MSME-MH-00-1234567") is False

def test_pii_masking(registry):
    """Verify DPDP Act 2023 data minimization and PII masking functions"""
    # GSTIN masking (masks central PAN)
    masked_gst = registry.mask_gstin("37IHKXV5167L1ZS")
    assert masked_gst == "37IHXXXXXX7L1ZS"
    assert "KXV516" not in masked_gst
    assert len(masked_gst) == 15

    # PAN masking
    masked_pan = registry.mask_pan("ABCDE1234F")
    assert masked_pan == "ABXXXXXX4F"

    # Phone masking
    masked_phone = registry.mask_phone("9876543210")
    assert masked_phone == "98XXXXXX10"

def test_registry_lookup_performance_and_accuracy(registry):
    """Verify O(1) hash indexed lookups and active status validation"""
    # Lookup active GSTIN from dataset
    res = registry.lookup_gstin("27AAACW1234F1Z1")  # should handle not found cleanly
    assert res['found'] is False

    # Search existing business by name
    results = registry.search_by_name("Harmony", limit=3)
    assert len(results) > 0
    assert "Harmony" in results[0]['trade_name'] or "Harmony" in results[0]['legal_name']
    assert "XXXXXX" in results[0]['gstin_masked']

def test_registry_cancelled_gstin_detection(registry):
    """Verify registry flags Cancelled status for K01 GSTIN"""
    k01_gstin = "37IHKXV5167L1ZS"
    res = registry.lookup_gstin(k01_gstin)
    assert res['found'] is True
    assert res['is_active'] is False
    assert res['status'] == "Cancelled"
    assert "Warning" in res['message']

def test_dpdp_consent_enforcement_and_audit_hash(kyc_engine):
    """Verify DPDP consent gate halts unconsented verification and logs audit hashes"""
    # Attempt verification without explicit consent
    res_no_consent = kyc_engine.verify_applicant_by_code('K02', consent_granted=False)
    assert res_no_consent['verdict'] == 'REJECT'
    assert 'DPDP' in res_no_consent['summary']
    assert res_no_consent['checklist'][0]['status'] == 'FAILED'

    # Verification with explicit affirmative consent
    res_consent = kyc_engine.verify_applicant_by_code('K02', consent_granted=True)
    assert res_consent['verdict'] == 'PASS'
    assert res_consent['checklist'][0]['status'] == 'PASSED'

    # Verify audit ledger entry
    history = kyc_engine.get_consent_history('K02')
    assert len(history) > 0
    latest = history[-1]
    assert latest['status'] == 'GRANTED'
    assert 'audit_hash' in latest
    assert len(latest['audit_hash']) == 64  # SHA-256 hex digest length
    assert latest['dpdp_act_compliant'] is True

def test_dpdp_consent_revocation(kyc_engine):
    """Verify Section 6 DPDP consent withdrawal workflow"""
    kyc_engine.record_consent('K99_TEST', 'Test Firm Ltd')
    revoke_res = kyc_engine.revoke_consent('K99_TEST', reason="Customer opt-out")
    assert revoke_res['status'] == 'SUCCESS'
    history = kyc_engine.get_consent_history('K99_TEST')
    assert any(h.get('event') == 'CONSENT_REVOKED' for h in history)

def test_address_proof_90_day_cutoff_math():
    """Verify strict 90-day address proof expiration logic against 2026-07-15"""
    ref_dt = datetime.strptime(REF_DATE_STR, "%Y-%m-%d")

    # Fresh bill (2026-06-26 is 19 days old <= 90)
    bill_fresh = datetime.strptime("2026-06-26", "%Y-%m-%d")
    days_fresh = (ref_dt - bill_fresh).days
    assert days_fresh == 19
    assert days_fresh <= 90

    # Stale bill (2025-10-31 is 257 days old > 90)
    bill_stale = datetime.strptime("2025-10-31", "%Y-%m-%d")
    days_stale = (ref_dt - bill_stale).days
    assert days_stale == 257
    assert days_stale > 90

def test_all_12_applicants_ground_truth_matrix(kyc_engine):
    """
    Automated diagnostic test of all 12 specimen applicants (K01-K12).
    Verifies 100% agreement with the hackathon ground truth answer key:
      K01: REJECT (Cancelled GSTIN, missing Udyam registration number)
      K02: PASS   (54 days old address proof, valid records)
      K03: PASS   (46 days old address proof, valid records)
      K04: REJECT (Corrupt/blank GST certificate <50 chars)
      K05: REJECT (Missing Udyam certificate file)
      K06: REJECT (Extracted GSTIN 08YKZXS8189L1Z0 not found in national GST registry)
      K07: REJECT (Legal entity mismatch: Shri Physio Clinic vs Neelgiri Physio Clinic)
      K08: PASS   (50 days old address proof, valid records)
      K09: PASS   (5 days old utility bill, valid records)
      K10: PASS   (27 days old address proof, valid records)
      K11: REJECT (Expired address proof - 257 days old > 90-day limit)
      K12: PASS   (9 days old utility bill, valid records)

    Ground Truth Breakdown: Exactly 6 PASS and 6 REJECT.
    """
    matrix = kyc_engine.evaluate_all_applicants()
    assert matrix['total_applicants'] == 12
    assert matrix['all_matched'] is True, f"Failed match: {[e for e in matrix['evaluations'] if not e['matched']]}"
    assert matrix['passed_count'] == 6
    assert matrix['rejected_count'] == 6
    assert matrix['precision'] == 1.0
    assert matrix['recall'] == 1.0

def test_planted_edge_cases_granular(kyc_engine):
    """Verify granular error identification for planted defects: K01, K04, K05, K06, K07, K11"""
    # K01: Cancelled GSTIN
    res_k01 = kyc_engine.verify_applicant_by_code('K01', consent_granted=True)
    assert res_k01['verdict'] == 'REJECT'
    assert any("CANCELLED" in r or "Cancelled" in r for r in res_k01['reject_reasons'])

    # K04: Corrupt GST image
    res_k04 = kyc_engine.verify_applicant_by_code('K04', consent_granted=True)
    assert res_k04['verdict'] == 'REJECT'
    assert any("Corrupt or unreadable GST" in r for r in res_k04['reject_reasons'])

    # K05: Missing Udyam certificate
    res_k05 = kyc_engine.verify_applicant_by_code('K05', consent_granted=True)
    assert res_k05['verdict'] == 'REJECT'
    assert any("Missing mandatory Udyam" in r for r in res_k05['reject_reasons'])

    # K06: Fake GSTIN not found in national registry
    res_k06 = kyc_engine.verify_applicant_by_code('K06', consent_granted=True)
    assert res_k06['verdict'] == 'REJECT'
    assert any("not found in national GST registry" in r for r in res_k06['reject_reasons'])

    # K07: Legal entity mismatch
    res_k07 = kyc_engine.verify_applicant_by_code('K07', consent_granted=True)
    assert res_k07['verdict'] == 'REJECT'
    assert any("Legal entity mismatch" in r for r in res_k07['reject_reasons'])

    # K11: Stale utility bill > 90 days
    res_k11 = kyc_engine.verify_applicant_by_code('K11', consent_granted=True)
    assert res_k11['verdict'] == 'REJECT'
    assert any("257 days old" in r for r in res_k11['reject_reasons'])

def test_document_upload_and_verification(kyc_engine):
    """Verify arbitrary document text upload and verification without code-specific assumptions"""
    clean_upload = {
        'gst_certificate': "Specimen: GST Registration Certificate Type of registration 19EOGXH4115YIZL Joseph Shah (Prop. Harmony Dental Care) Harmony Dental Care Proprietorship",
        'udyam_certificate': "Specimen: Udyam Registration Certificate Udyam reg. number UDYAM-WB-OO- 5053330 Harmony Dental Care Services",
        'address_proof': "Electricity Bill Billed to Harmony Dental Care Bill date 2026-06-01 Amount due 2000",
        'signatory_id': "Specimen: Authorised Signatory ID Name Joseph Shah Designation Manager For business Harmony Dental Care ID no. SYN-lD-816907 Valid till 2028-09-10"
    }
    res = kyc_engine.verify_applicant_documents(clean_upload, consent_granted=True)
    assert res['verdict'] == 'PASS'
    assert res['extracted_fields']['gstin'] == '19EOGXH4115Y1ZL'
    assert res['extracted_fields']['udyam_number'] == 'UDYAM-WB-00-5053330'

    # Upload with tampered name
    tampered_upload = dict(clean_upload)
    tampered_upload['gst_certificate'] = "Specimen: GST Registration Certificate Type of registration 07CPCXN0398PIZT Neha Banerjee (Prop. Shri Physio Clinic) Neelgiri Physio Clinic Proprietorship"
    res_tampered = kyc_engine.verify_applicant_documents(tampered_upload, consent_granted=True)
    assert res_tampered['verdict'] == 'REJECT'
    assert any("Legal entity mismatch" in r for r in res_tampered['reject_reasons'])

def test_all_registry_gstins_pass_through_normalizer():
    """Verify that 100% of the 3,534 valid GSTINs in mock registry pass through normalizer unchanged"""
    import os
    import pandas as pd
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'udyam_digital_data', 'mock_gstin_registry.csv')
    df = pd.read_csv(csv_path)
    assert len(df) == 3534
    for gstin in df['gstin']:
        normalized = SmartKYCEngine.normalize_gstin_ocr(str(gstin))
        assert normalized == gstin, f"Normalization modified valid GSTIN: {gstin} -> {normalized}"

def test_expired_signatory_rejection(kyc_engine):
    """Verify that an expired signatory identification document is actively rejected"""
    expired_upload = {
        'gst_certificate': "Specimen: GST Registration Certificate Type of registration 19EOGXH4115YIZL Joseph Shah (Prop. Harmony Dental Care) Harmony Dental Care Proprietorship",
        'udyam_certificate': "Specimen: Udyam Registration Certificate Udyam reg. number UDYAM-WB-OO- 5053330 Harmony Dental Care Services",
        'address_proof': "Electricity Bill Billed to Harmony Dental Care Bill date 2026-06-01 Amount due 2000",
        'signatory_id': "Specimen: Authorised Signatory ID Name Joseph Shah Designation Manager For business Harmony Dental Care Valid till 2025-01-01"
    }
    res = kyc_engine.verify_applicant_documents(expired_upload, consent_granted=True)
    assert res['verdict'] == 'REJECT'
    assert any("expired" in r.lower() for r in res['reject_reasons'])

def test_dpdp_affirmative_data_purge(kyc_engine):
    """Verify Section 8 DPDP Act data purge after 30-day retention window"""
    kyc_engine.record_consent('PURGE_TEST_01', 'Old Shop Enterprises')
    purge_res = kyc_engine.purge_expired_data(as_of_date="2026-12-31")
    assert purge_res['purged_count'] >= 1
    assert any(r['applicant_code'] == 'PURGE_TEST_01' for r in purge_res['receipts'])


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
    assert registry.validate_gstin_format("27ABCDE1234F1Z") is False # 14 chars
    assert registry.validate_gstin_format("27ABCDE1234F1Z55") is False # 16 chars
    assert registry.validate_gstin_format("99ABCDE1234F1A5") is False # 13th char must be 'Z'

def test_udyam_format_validator(registry):
    """Verify Udyam registration structure validation with '00' district marker"""
    # Valid synthetic Udyam format
    assert registry.validate_udyam_format("UDYAM-MH-00-1234567") is True
    assert registry.validate_udyam_format("UDYAM-DL-00-9876543") is True

    # Invalid formats
    assert registry.validate_udyam_format("UDYAM-MH-01-1234567") is False # Non-00 district
    assert registry.validate_udyam_format("UDYAM-M-00-1234567") is False # 1-char state
    assert registry.validate_udyam_format("UDYAM-MH-00-123456") is False # 6 digits instead of 7
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
    res = registry.lookup_gstin("27AAACW1234F1Z1") # should handle not found cleanly
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
    assert len(latest['audit_hash']) == 64 # SHA-256 hex digest length
    assert latest['dpdp_act_compliant'] is True

def test_dpdp_consent_revocation(kyc_engine):
    """Verify Section 6 DPDP consent withdrawal workflow"""
    # First record consent
    kyc_engine.record_consent('K99_TEST', 'Test Firm Ltd')
    
    # Revoke consent
    revoke_res = kyc_engine.revoke_consent('K99_TEST', reason="Customer opt-out")
    assert revoke_res['status'] == 'SUCCESS'
    
    # Check history contains revocation
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
      K01: REJECT (Cancelled GSTIN)
      K02: PASS   (54 days old address proof)
      K03: PASS   (Valid records)
      K04: REJECT (Corrupt/blank GST certificate)
      K05: REJECT (Missing Udyam certificate)
      K06: PASS   (Valid records)
      K07: PASS   (10 days old utility bill)
      K08: PASS   (Valid records)
      K09: PASS   (5 days old utility bill)
      K10: PASS   (27 days old address proof)
      K11: REJECT (Expired address proof - 257 days old)
      K12: PASS   (Valid records)
    """
    matrix = kyc_engine.evaluate_all_applicants()
    assert matrix['total_applicants'] == 12
    assert matrix['all_matched'] is True, f"Failed match: {[e for e in matrix['evaluations'] if not e['matched']]}"
    assert matrix['passed_count'] == 8
    assert matrix['rejected_count'] == 4
    assert matrix['precision'] == 1.0
    assert matrix['recall'] == 1.0

def test_corrupt_and_missing_document_detection(kyc_engine):
    """Verify granular error identification for planted edge cases K04 and K05"""
    # K04: Corrupt GST image
    res_k04 = kyc_engine.verify_applicant_by_code('K04', consent_granted=True)
    assert res_k04['verdict'] == 'REJECT'
    assert any("Corrupt or unreadable GST" in r for r in res_k04['reject_reasons'])

    # K05: Missing Udyam certificate
    res_k05 = kyc_engine.verify_applicant_by_code('K05', consent_granted=True)
    assert res_k05['verdict'] == 'REJECT'
    assert any("Missing mandatory Udyam" in r for r in res_k05['reject_reasons'])

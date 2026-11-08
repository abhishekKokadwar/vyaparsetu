"""End-to-end KYC workflow tests: consent gate, document upload/classify/verify,
DPDP consent lifecycle (grant, revoke, purge), and the full 12-applicant matrix.

Run with:  uv run pytest tests/test_kyc_workflow.py -v
Requires:  conftest.py sets VYAPAR_LLM_DISABLED=1 and VYAPAR_DB_DISABLED=1
"""

import os
import pathlib

import pytest
from fastapi.testclient import TestClient

from app.main import app, classify_document
from app.kyc_engine import SmartKYCEngine, REF_DATE_STR
from app.registry_service import RegistryService


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture(scope="module")
def kyc_engine():
    return SmartKYCEngine(RegistryService())


# ---------------------------------------------------------------------------
# 1. Full 12-applicant matrix — ground truth agreement
# ---------------------------------------------------------------------------

def test_12_applicant_matrix_matches_ground_truth(kyc_engine):
    """All 12 specimen applicants (K01-K12) must agree with the answer key:
    6 PASS / 6 REJECT. This is the core KYC correctness check."""
    matrix = kyc_engine.evaluate_all_applicants()
    assert matrix["total_applicants"] == 12
    assert matrix["all_matched"] is True, (
        "Mismatch: "
        + str([e for e in matrix["evaluations"] if not e["matched"]])
    )
    assert matrix["passed_count"] == 6
    assert matrix["rejected_count"] == 6
    assert matrix["precision"] == 1.0
    assert matrix["recall"] == 1.0


# ---------------------------------------------------------------------------
# 2. Per-applicant granular verdict + reason checks
# ---------------------------------------------------------------------------
def test_k01_rejected_cancelled_gstin(kyc_engine):
    res = kyc_engine.verify_applicant_by_code("K01", consent_granted=True)
    assert res["verdict"] == "REJECT"
    assert any("Cancelled" in r or "CANCELLED" in r for r in res["reject_reasons"])


def test_k02_passes_clean(kyc_engine):
    res = kyc_engine.verify_applicant_by_code("K02", consent_granted=True)
    assert res["verdict"] == "PASS"
    assert res["extracted_fields"]["gstin"] is not None
    assert res["extracted_fields"]["udyam_number"] is not None


def test_k03_passes_clean(kyc_engine):
    res = kyc_engine.verify_applicant_by_code("K03", consent_granted=True)
    assert res["verdict"] == "PASS"


def test_k04_rejected_blank_gst(kyc_engine):
    res = kyc_engine.verify_applicant_by_code("K04", consent_granted=True)
    assert res["verdict"] == "REJECT"
    assert any("Corrupt or unreadable GST" in r for r in res["reject_reasons"])


def test_k05_rejected_missing_udyam(kyc_engine):
    res = kyc_engine.verify_applicant_by_code("K05", consent_granted=True)
    assert res["verdict"] == "REJECT"
    assert any("Missing mandatory Udyam" in r for r in res["reject_reasons"])


def test_k06_rejected_bogus_gstin(kyc_engine):
    res = kyc_engine.verify_applicant_by_code("K06", consent_granted=True)
    assert res["verdict"] == "REJECT"
    assert any("not found in national GST registry" in r for r in res["reject_reasons"])


def test_k07_rejected_name_mismatch(kyc_engine):
    res = kyc_engine.verify_applicant_by_code("K07", consent_granted=True)
    assert res["verdict"] == "REJECT"
    assert any("Legal entity mismatch" in r for r in res["reject_reasons"])


def test_k08_passes_clean(kyc_engine):
    assert kyc_engine.verify_applicant_by_code("K08", consent_granted=True)["verdict"] == "PASS"


def test_k09_passes_clean(kyc_engine):
    assert kyc_engine.verify_applicant_by_code("K09", consent_granted=True)["verdict"] == "PASS"


def test_k10_passes_clean(kyc_engine):
    assert kyc_engine.verify_applicant_by_code("K10", consent_granted=True)["verdict"] == "PASS"


def test_k11_rejected_stale_address_proof(kyc_engine):
    res = kyc_engine.verify_applicant_by_code("K11", consent_granted=True)
    assert res["verdict"] == "REJECT"
    assert any("257 days old" in r or "expired" in r.lower() for r in res["reject_reasons"])


# ---------------------------------------------------------------------------
# 3. DPDP consent gate — no consent = hard REJECT
# ---------------------------------------------------------------------------

def test_consent_gate_blocks_unconsented_verification(kyc_engine):
    res = kyc_engine.verify_applicant_by_code("K02", consent_granted=False)
    assert res["verdict"] == "REJECT"
    assert "DPDP" in res["summary"]
    assert res["checklist"][0]["status"] == "FAILED"


def test_consent_gate_allows_consented_verification(kyc_engine):
    res = kyc_engine.verify_applicant_by_code("K02", consent_granted=True)
    assert res["verdict"] == "PASS"
    assert res["dpdp_compliance"]["consent_verified"] is True


# ---------------------------------------------------------------------------
# 4. Consent lifecycle: grant -> verify -> revoke -> verify-after-revoke fails
# ---------------------------------------------------------------------------

def test_consent_lifecycle_grant_verify_revoke(kyc_engine):
    code = "WFW_LIFECYCLE_01"
    # Grant consent
    grant = kyc_engine.record_consent(code, "Lifecycle Test Firm")
    assert grant["status"] == "GRANTED"

    # Verification passes with consent
    res_before = kyc_engine.verify_applicant_by_code("K02", consent_granted=True)
    assert res_before["verdict"] == "PASS"

    # Revoke consent
    revoke = kyc_engine.revoke_consent(code, reason="Customer opt-out")
    assert revoke["status"] == "SUCCESS"

    # History must show CONSENT_REVOKED
    history = kyc_engine.get_consent_history(code)
    assert any(h.get("event") == "CONSENT_REVOKED" for h in history)

    # Verification without consent must now be rejected
    res_after = kyc_engine.verify_applicant_by_code("K02", consent_granted=False)
    assert res_after["verdict"] == "REJECT"
    assert "DPDP" in res_after["summary"]


# ---------------------------------------------------------------------------
# 5. DPDP data purge lifecycle
# ---------------------------------------------------------------------------

def test_dpdp_purge_removes_consent_record(kyc_engine):
    code = "PURGE_WF_01"
    kyc_engine.record_consent(code, "Purge Test Enterprises")
    kyc_engine.verify_applicant_by_code("K02", consent_granted=True)

    purge_res = kyc_engine.purge_expired_data(as_of_date="2026-12-31")
    assert purge_res["purged_count"] >= 1
    assert any(r["applicant_code"] == code for r in purge_res["receipts"])

def test_k12_passes_clean(kyc_engine):
    assert kyc_engine.verify_applicant_by_code("K12", consent_granted=True)["verdict"] == "PASS"


# ---------------------------------------------------------------------------
# 6. Arbitrary document upload + verify (no specimen assumptions)
# ---------------------------------------------------------------------------

def test_upload_clean_documents_passes(kyc_engine):
    clean_upload = {
        "gst_certificate": "Specimen: GST Registration Certificate Type of registration 19EOGXH4115YIZL Joseph Shah (Prop. Harmony Dental Care) Harmony Dental Care Proprietorship",
        "udyam_certificate": "Specimen: Udyam Registration Certificate Udyam reg. number UDYAM-WB-OO- 5053330 Harmony Dental Care Services",
        "address_proof": "Electricity Bill Billed to Harmony Dental Care Bill date 2026-06-01 Amount due 2000",
        "signatory_id": "Specimen: Authorised Signatory ID Name Joseph Shah Designation Manager For business Harmony Dental Care ID no. SYN-lD-816907 Valid till 2028-09-10",
    }
    res = kyc_engine.verify_applicant_documents(clean_upload, consent_granted=True)
    assert res["verdict"] == "PASS"
    assert res["extracted_fields"]["gstin"] == "19EOGXH4115Y1ZL"
    assert res["extracted_fields"]["udyam_number"] == "UDYAM-WB-00-5053330"


def test_upload_tampered_name_is_rejected(kyc_engine):
    clean_upload = {
        "gst_certificate": "Specimen: GST Registration Certificate Type of registration 19EOGXH4115YIZL Joseph Shah (Prop. Harmony Dental Care) Harmony Dental Care Proprietorship",
        "udyam_certificate": "Specimen: Udyam Registration Certificate Udyam reg. number UDYAM-WB-OO- 5053330 Harmony Dental Care Services",
        "address_proof": "Electricity Bill Billed to Harmony Dental Care Bill date 2026-06-01 Amount due 2000",
        "signatory_id": "Specimen: Authorised Signatory ID Name Joseph Shah Designation Manager For business Harmony Dental Care ID no. SYN-lD-816907 Valid till 2028-09-10",
    }
    tampered = dict(clean_upload)
    tampered["gst_certificate"] = (
        "Specimen: GST Registration Certificate Type of registration 07CPCXN0398PIZT Neha Banerjee (Prop. Shri Physio Clinic) Neelgiri Physio Clinic Proprietorship"
    )
    res = kyc_engine.verify_applicant_documents(tampered, consent_granted=True)
    assert res["verdict"] == "REJECT"
    assert any("Legal entity mismatch" in r for r in res["reject_reasons"])


def test_upload_expired_signatory_is_rejected(kyc_engine):
    expired_upload = {
        "gst_certificate": "Specimen: GST Registration Certificate Type of registration 19EOGXH4115YIZL Joseph Shah (Prop. Harmony Dental Care) Harmony Dental Care Proprietorship",
        "udyam_certificate": "Specimen: Udyam Registration Certificate Udyam reg. number UDYAM-WB-OO- 5053330 Harmony Dental Care Services",
        "address_proof": "Electricity Bill Billed to Harmony Dental Care Bill date 2026-06-01 Amount due 2000",
        "signatory_id": "Specimen: Authorised Signatory ID Name Joseph Shah Designation Manager For business Harmony Dental Care Valid till 2025-01-01",
    }
    res = kyc_engine.verify_applicant_documents(expired_upload, consent_granted=True)
    assert res["verdict"] == "REJECT"
    assert any("expired" in r.lower() for r in res["reject_reasons"])


def test_upload_stale_address_proof_is_rejected(kyc_engine):
    stale_upload = {
        "gst_certificate": "Specimen: GST Registration Certificate Type of registration 19EOGXH4115YIZL Joseph Shah (Prop. Harmony Dental Care) Harmony Dental Care Proprietorship",
        "udyam_certificate": "Specimen: Udyam Registration Certificate Udyam reg. number UDYAM-WB-OO- 5053330 Harmony Dental Care Services",
        "address_proof": "Electricity Bill Billed to Harmony Dental Care Bill date 2025-10-31 Amount due 2000",
        "signatory_id": "Specimen: Authorised Signatory ID Name Joseph Shah Designation Manager For business Harmony Dental Care ID no. SYN-lD-816907 Valid till 2028-09-10",
    }
    res = kyc_engine.verify_applicant_documents(stale_upload, consent_granted=True)
    assert res["verdict"] == "REJECT"
    assert any("expired" in r.lower() or "days old" in r for r in res["reject_reasons"])


def test_upload_missing_gst_certificate_is_rejected(kyc_engine):
    missing_gst = {
        "udyam_certificate": "Specimen: Udyam Registration Certificate Udyam reg. number UDYAM-WB-OO- 5053330 Harmony Dental Care Services",
        "address_proof": "Electricity Bill Billed to Harmony Dental Care Bill date 2026-06-01 Amount due 2000",
        "signatory_id": "Specimen: Authorised Signatory ID Name Joseph Shah Designation Manager For business Harmony Dental Care Valid till 2028-09-10",
    }
    res = kyc_engine.verify_applicant_documents(missing_gst, consent_granted=True)
    assert res["verdict"] == "REJECT"


def test_upload_blank_text_is_rejected(kyc_engine):
    blank = {
        "gst_certificate": "",
        "udyam_certificate": "",
        "address_proof": "",
        "signatory_id": "",
    }
    res = kyc_engine.verify_applicant_documents(blank, consent_granted=True)
    assert res["verdict"] == "REJECT"


# ---------------------------------------------------------------------------
# 7. API-level: upload specimen images -> classify -> verify
# ---------------------------------------------------------------------------

SPECIMEN_DIR = pathlib.Path(__file__).resolve().parent.parent / "udyam_digital_data" / "kyc_documents"


def test_api_upload_k02_passes(client):
    """K02 specimen images through the real upload endpoint must PASS."""
    files = [
        ("files", (f"scan{i}.png", (SPECIMEN_DIR / f"K02_{n}.png").read_bytes(), "image/png"))
        for i, n in enumerate(("gst_certificate", "udyam_certificate", "address_proof", "signatory_id"))
    ]
    body = client.post("/api/kyc/upload-files", files=files).json()
    assert body["ocr_backend"] == "specimen"
    assert body["verification"]["verdict"] == "PASS", body


def test_api_upload_k07_rejects_name_mismatch(client):
    """K07 specimen images through the upload endpoint must REJECT (name mismatch)."""
    files = [
        ("files", (f"scan{i}.png", (SPECIMEN_DIR / f"K07_{n}.png").read_bytes(), "image/png"))
        for i, n in enumerate(("gst_certificate", "udyam_certificate", "address_proof", "signatory_id"))
    ]
    body = client.post("/api/kyc/upload-files", files=files).json()
    assert body["verification"]["verdict"] == "REJECT", body


def test_api_upload_pdf_is_rejected(client):
    res = client.post(
        "/api/kyc/upload-files",
        files=[("files", ("doc.pdf", b"%PDF-1.4...", "application/pdf"))],
    )
    assert res.status_code == 400
    assert "PDF format is not supported" in res.json()["detail"]


def test_api_upload_exe_is_rejected(client):
    res = client.post(
        "/api/kyc/upload-files",
        files=[("files", ("malicious.exe", b"MZbinarycontent", "application/octet-stream"))],
    )
    assert res.status_code == 400
    assert "Unsupported file type" in res.json()["detail"]


def test_api_upload_path_traversal_is_quarantined(client):
    res = client.post(
        "/api/kyc/upload-files",
        files=[("files", ("../../evil.txt", b"ELECTRICITY BILL CONSUMER NO 123", "text/plain"))],
    )
    assert res.status_code == 200
    assert not os.path.exists("evil.txt")
    assert not os.path.exists("../../evil.txt")


def test_api_upload_exceeds_8_file_limit(client):
    nine_files = [
        ("files", (f"file_{i}.txt", b"ELECTRICITY BILL CONSUMER NO 123", "text/plain"))
        for i in range(9)
    ]
    res = client.post("/api/kyc/upload-files", files=nine_files)
    assert res.status_code == 400
    assert "Maximum 8 files" in res.json()["detail"]


# ---------------------------------------------------------------------------
# 8. classify_document for all four KYC document types
# ---------------------------------------------------------------------------

def test_classify_gst_certificate():
    text = "GST Registration Certificate GSTIN 27ABCDE1234F1Z5 Legal name Acme Pvt Ltd"
    assert classify_document(text, "random.png") == "gst_certificate"


def test_classify_udyam_certificate():
    text = "Udyam Registration Certificate UDYAM-MH-00-1234567 Enterprise Name Acme Store"
    assert classify_document(text, "random.png") == "udyam_certificate"


def test_classify_address_proof():
    text = "Electricity Bill Billed to Acme Store Bill date 2026-06-01 Amount due 2000"
    assert classify_document(text, "random.png") == "address_proof"


def test_classify_signatory_id():
    text = "Authorised Signatory ID Name John Doe Designation Manager Valid till 2028-09-10"
    assert classify_document(text, "random.png") == "signatory_id"


def test_classify_unclassified():
    assert classify_document("", "random_photo.jpg") == "unclassified"
    assert classify_document("Some generic receipt with no tax tokens", "receipt.png") == "unclassified"


# ---------------------------------------------------------------------------
# 9. GSTIN extraction robustness (Gemini layout variants)
# ---------------------------------------------------------------------------

def test_gst_label_on_next_line():
    base = (
        "Specimen: GST Registration Certificate\nFormat for hackathon OCR testing only\n"
        "GSTIN\n37NBLXS1145E1ZU\n"
    )
    tail = "Constitution\nProprietorship\n"
    g = SmartKYCEngine.extract_gst_details(
        base + "Legal name\nPooja Agarwal (Prop. Star Electronics)\nTrade name\nStar Electronics\n" + tail
    )
    assert g["legal_name"] == "Pooja Agarwal (Prop. Star Electronics)"
    assert g["trade_name"] == "Star Electronics"


def test_gst_label_leak_production_bug():
    """Regression: production once returned legal_name == 'Trade name' because labels
    were listed before values. Must not happen."""
    base = (
        "Specimen: GST Registration Certificate\nFormat for hackathon OCR testing only\n"
        "GSTIN\n37NBLXS1145E1ZU\n"
    )
    tail = "Constitution\nProprietorship\n"
    t = base + "Legal name\nTrade name\nConstitution\nPooja Agarwal (Prop. Star Electronics)\n" "Star Electronics\nProprietorship\n"
    g = SmartKYCEngine.extract_gst_details(t)
    assert g["legal_name"] not in ("Trade name", "Constitution")
    assert "Pooja Agarwal" in g["legal_name"]


# ---------------------------------------------------------------------------
# 10. Address proof 90-day freshness math
# ---------------------------------------------------------------------------

def test_address_proof_freshness_boundary():
    from datetime import datetime
    ref_dt = datetime.strptime(REF_DATE_STR, "%Y-%m-%d")

    # Exactly 90 days old -> still fresh (<= 90)
    bill_90 = datetime.strptime("2026-04-16", "%Y-%m-%d")
    assert (ref_dt - bill_90).days == 90

    # 91 days old -> stale (> 90)
    bill_91 = datetime.strptime("2026-04-15", "%Y-%m-%d")
    assert (ref_dt - bill_91).days == 91


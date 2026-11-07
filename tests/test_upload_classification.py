import os
import json
import pytest
from app.main import classify_document

def test_k02_documents_classification_accuracy():
    """
    Asserts that real extracted OCR text from K02 applicant documents
    are correctly classified into their respective document categories
    without conflicting or overwriting each other.
    """
    json_path = os.path.join(os.path.dirname(__file__), '..', 'udyam_digital_data', 'kyc_extracted.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        extracted = json.load(f)

    # 1. K02 Udyam Certificate
    udyam_text = extracted.get("K02_udyam_certificate.png", "")
    assert len(udyam_text) > 0
    # Must classify as udyam_certificate, despite containing "Registration Certificate"
    assert classify_document(udyam_text, "random_name_1.png") == "udyam_certificate"

    # 2. K02 GST Certificate
    gst_text = extracted.get("K02_gst_certificate.png", "")
    assert len(gst_text) > 0
    assert classify_document(gst_text, "random_name_2.png") == "gst_certificate"

    # 3. K02 Address Proof
    addr_text = extracted.get("K02_address_proof.png", "")
    assert len(addr_text) > 0
    assert classify_document(addr_text, "random_name_3.png") == "address_proof"

    # 4. K02 Signatory ID
    sig_text = extracted.get("K02_signatory_id.png", "")
    assert len(sig_text) > 0
    assert classify_document(sig_text, "random_name_4.png") == "signatory_id"

def test_filename_fallback_and_unclassified():
    """Verifies that filename keywords work when text is sparse, and never defaults to gst_certificate"""
    assert classify_document("", "invoice_udyam_copy.png") == "udyam_certificate"
    assert classify_document("", "electricity_bill_june.png") == "address_proof"
    assert classify_document("", "signatory_specimen_card.png") == "signatory_id"
    assert classify_document("", "gst_reg_01.png") == "gst_certificate"
    assert classify_document("", "random_photo.jpg") == "unclassified"
    assert classify_document("Some generic receipt with no tax tokens", "receipt.png") == "unclassified"

def test_upload_security_and_resource_limits():
    """Tests path traversal sanitization, unsupported format rejection, and max file constraints"""
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)

    # 1. Unsupported extension (.exe) -> HTTP 400
    res_exe = client.post(
        "/api/kyc/upload-files",
        files=[("files", ("malicious.exe", b"MZbinarycontent", "application/octet-stream"))]
    )
    assert res_exe.status_code == 400
    assert "Unsupported file type" in res_exe.json()["detail"]

    # 2. PDF rejection with informative message -> HTTP 400
    res_pdf = client.post(
        "/api/kyc/upload-files",
        files=[("files", ("doc.pdf", b"%PDF-1.4...", "application/pdf"))]
    )
    assert res_pdf.status_code == 400
    assert "PDF format is not supported" in res_pdf.json()["detail"]

    # 3. Path traversal attack attempt in filename -> Should be safely quarantined & handled
    res_traversal = client.post(
        "/api/kyc/upload-files",
        files=[("files", ("../../evil.txt", b"ELECTRICITY BILL CONSUMER NO 123", "text/plain"))]
    )
    assert res_traversal.status_code == 200
    assert not os.path.exists("evil.txt")
    assert not os.path.exists("../../evil.txt")

    # 4. Exceeding 8 files limit -> HTTP 400
    nine_files = [("files", (f"file_{i}.txt", b"ELECTRICITY BILL CONSUMER NO 123", "text/plain")) for i in range(9)]
    res_limit = client.post("/api/kyc/upload-files", files=nine_files)
    assert res_limit.status_code == 400
    assert "Maximum 8 files" in res_limit.json()["detail"]

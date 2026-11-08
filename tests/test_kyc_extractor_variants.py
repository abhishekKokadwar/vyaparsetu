"""Gemini transcribes the same specimen in different layouts from run to run. The extractors must cope."""
from app.kyc_engine import SmartKYCEngine as K

BASE = "Specimen: GST Registration Certificate\nFormat for hackathon OCR testing only\nGSTIN\n37NBLXS1145E1ZU\n"
TAIL = "Constitution\nProprietorship\n"


def test_label_value_on_next_line():
    t = BASE + "Legal name\nPooja Agarwal (Prop. Star Electronics)\nTrade name\nStar Electronics\n" + TAIL
    g = K.extract_gst_details(t)
    assert g["legal_name"] == "Pooja Agarwal (Prop. Star Electronics)"
    assert g["trade_name"] == "Star Electronics"


def test_label_value_on_same_line():
    t = BASE + "Legal name: Pooja Agarwal (Prop. Star Electronics)\nTrade name: Star Electronics\n" + TAIL
    g = K.extract_gst_details(t)
    assert g["legal_name"] == "Pooja Agarwal (Prop. Star Electronics)"
    assert g["trade_name"] == "Star Electronics"


def test_labels_listed_first_never_leak_into_names():
    # the failure seen in production: legal name came back as the literal label "Trade name"
    t = (BASE + "Legal name\nTrade name\nConstitution\nPooja Agarwal (Prop. Star Electronics)\n"
         "Star Electronics\nProprietorship\n")
    g = K.extract_gst_details(t)
    assert g["legal_name"] not in ("Trade name", "Constitution")
    assert "Pooja Agarwal" in g["legal_name"]


def test_bill_date_formats():
    for txt, iso in [("Bill date\n2026-07-06", "2026-07-06"), ("Bill date: 06/07/2026", "2026-07-06"),
                     ("Bill date 6 Jul 2026", "2026-07-06")]:
        assert K.extract_address_details(txt)["bill_date"] == iso


def test_signatory_layouts():
    for t in ["Name: Anita Kulkarni\nDesignation: Owner\nValid till: 2028-09-10",
              "Name Anita Kulkarni Designation Owner Valid till 2028-09-10",
              "Name\nAnita Kulkarni\nDesignation\nOwner\nValid till\n2028-09-10"]:
        r = K.extract_signatory_details(t)
        assert (r["name"], r["designation"], r["expiry_date"]) == ("Anita Kulkarni", "Owner", "2028-09-10")


def test_specimen_upload_passes_without_cloud_ocr():
    """K02 (clean) must PASS and K07 (name mismatch) must REJECT using only the stored specimen transcriptions."""
    import pathlib
    from fastapi.testclient import TestClient
    from app.main import app
    docs = pathlib.Path(__file__).resolve().parent.parent / "udyam_digital_data" / "kyc_documents"
    client = TestClient(app)
    for code, expected in (("K02", "PASS"), ("K07", "REJECT")):
        files = [("files", (f"scan{i}.png", (docs / f"{code}_{n}.png").read_bytes(), "image/png"))
                 for i, n in enumerate(("gst_certificate", "udyam_certificate", "address_proof", "signatory_id"))]
        body = client.post("/api/kyc/upload-files", files=files).json()
        assert body["ocr_backend"] == "specimen"
        assert body["verification"]["verdict"] == expected, code


def test_pitch_and_quote_report_the_same_savings():
    """The advisor's narrative and the quote must quote one savings figure, not two."""
    from fastapi.testclient import TestClient
    from app.main import app
    rec = TestClient(app).post("/api/advisor/recommend", json={
        "business_type": "Clinic & Healthcare", "city_tier": 1, "employee_count": 6, "num_sites": 1,
        "has_gstin": True, "current_spend": 3000, "preferred_language": "en"}).json()
    assert rec["savings"]["annual_savings_inr"] == rec["pricing"]["vendor_savings_benchmark"]["annual_savings_inr"]

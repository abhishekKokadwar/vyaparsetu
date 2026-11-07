from fastapi import FastAPI, HTTPException, Query, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from typing import List, Optional, Tuple
import os
import shutil
import tempfile
import subprocess
import uuid

from app.catalog_engine import CatalogEngine
from app.advisor_engine import AdvisorEngine
from app.registry_service import RegistryService
from app.kyc_engine import SmartKYCEngine
from app.order_service import OrderService
from app.partner_service import PartnerService
from app.data_intelligence import DataIntelligenceEngine

app = FastAPI(
    title="VyaparSetu Platform API",
    description="Next-Gen MSME Digital Acquisition & Onboarding Platform (Airtel Sync 2026 - Enterprise Track A)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engines
catalog_engine = CatalogEngine()
advisor_engine = AdvisorEngine(catalog_engine)
registry_service = RegistryService()
kyc_engine = SmartKYCEngine(registry_service)
order_service = OrderService()
partner_service = PartnerService()
data_intelligence = DataIntelligenceEngine()

# Models
class ProfileRequest(BaseModel):
    business_type: str
    segment: Optional[str] = None
    city_tier: int = 1
    employee_count: int = 2
    num_sites: int = 1
    has_gstin: bool = True
    current_spend: Optional[int] = 0
    preferred_language: str = "en"

class ChatQueryRequest(BaseModel):
    query: str
    current_profile: Optional[dict] = None

class ValidationRequest(BaseModel):
    selected_product_ids: List[str]
    city_tier: int = 1
    employee_count: int = 1
    num_sites: int = 1
    has_gstin: bool = True

class BundlePricingRequest(BaseModel):
    items: List[dict] # [{'product_id': 'P01', 'quantity': 1}]

class KYCVerifyRequest(BaseModel):
    applicant_code: str
    consent_granted: bool = True

class KYCDocumentUploadRequest(BaseModel):
    applicant_code: Optional[str] = "CUSTOM_UPLOAD"
    business_name: Optional[str] = "Uploaded Business Entity"
    address_proof_text: Optional[str] = None
    gst_certificate_text: Optional[str] = None
    udyam_certificate_text: Optional[str] = None
    signatory_id_text: Optional[str] = None
    consent_granted: bool = True

class ConsentRecordRequest(BaseModel):
    applicant_code: str
    entity_name: str
    purpose: Optional[str] = "telecom_kyc_and_activation"

class ConsentRevokeRequest(BaseModel):
    applicant_code: str
    reason: Optional[str] = "User withdrawal of digital consent"

class OrderCreateRequest(BaseModel):
    business_name: str
    contact_name: str
    contact_phone: str
    city: str
    bundle_name: str
    monthly_amount_inr: int
    estimated_install_days: int = 3
    selected_products: List[str] = []

class OrderAdvanceRequest(BaseModel):
    technician_pin: Optional[str] = None

class OrderRescheduleRequest(BaseModel):
    new_slot: str
    days_extension: Optional[int] = 1

class SalvageCampaignRequest(BaseModel):
    lead_ids: List[str]
    partner_id: Optional[str] = "PARTNER-BENGALURU-01"

# --- API Endpoints ---

@app.get("/api/catalogue")
def get_catalogue():
    return {
        'total': len(catalog_engine.products),
        'products': catalog_engine.get_all()
    }

@app.post("/api/catalogue/validate")
def validate_catalogue(req: ValidationRequest):
    is_valid, errors, suggestions = catalog_engine.validate_selection(
        req.selected_product_ids,
        city_tier=req.city_tier,
        employees=req.employee_count,
        sites=req.num_sites,
        has_gstin=req.has_gstin
    )
    return {'is_valid': is_valid, 'errors': errors, 'suggestions': suggestions}

@app.post("/api/catalogue/pricing")
def get_bundle_pricing(req: BundlePricingRequest):
    return catalog_engine.calculate_bundle_pricing(req.items)

@app.post("/api/advisor/recommend")
def recommend_bundle(req: ProfileRequest):
    return advisor_engine.recommend(req.model_dump())

@app.post("/api/advisor/chat")
def advisor_chat(req: ChatQueryRequest):
    updated_profile = advisor_engine.parse_conversational_query(req.query, req.current_profile)
    clarifications = advisor_engine.detect_clarifications(updated_profile)
    recommendation = advisor_engine.recommend(updated_profile)
    return {
        'profile': updated_profile,
        'clarifications': clarifications,
        'recommendation': recommendation
    }

@app.get("/api/advisor/benchmark-matrix")
def get_benchmark_matrix():
    return advisor_engine.evaluate_jury_scenarios()

@app.get("/api/advisor/cache-stats")
def get_advisor_cache_stats():
    return advisor_engine.get_cache_stats()

@app.get("/api/registry/gstin/{gstin}")
def lookup_gstin(gstin: str):
    return registry_service.lookup_gstin(gstin)

@app.get("/api/registry/udyam/{udyam_no}")
def lookup_udyam(udyam_no: str):
    return registry_service.lookup_udyam(udyam_no)

@app.get("/api/registry/search")
def search_registry(q: str = Query(..., min_length=2)):
    return registry_service.search_by_name(q)

@app.get("/api/kyc/applicants")
def get_kyc_applicants():
    return {
        'total': 12,
        'applicants': kyc_engine.get_test_applicants()
    }

@app.post("/api/kyc/verify-applicant")
def verify_kyc_applicant(req: KYCVerifyRequest):
    return kyc_engine.verify_applicant_by_code(req.applicant_code, consent_granted=req.consent_granted)

@app.post("/api/kyc/upload-and-verify")
def upload_and_verify_documents(req: KYCDocumentUploadRequest):
    docs_map = {
        'address_proof': req.address_proof_text or "",
        'gst_certificate': req.gst_certificate_text or "",
        'udyam_certificate': req.udyam_certificate_text or "",
        'signatory_id': req.signatory_id_text or ""
    }
    file_presence = {
        'has_address_proof': bool(req.address_proof_text and req.address_proof_text.strip()),
        'has_gst_certificate': bool(req.gst_certificate_text and req.gst_certificate_text.strip()),
        'has_udyam_certificate': bool(req.udyam_certificate_text and req.udyam_certificate_text.strip()),
        'has_signatory_id': bool(req.signatory_id_text and req.signatory_id_text.strip()),
    }
    return kyc_engine.verify_applicant_documents(
        docs_map=docs_map,
        file_presence=file_presence,
        applicant_code=req.applicant_code or "CUSTOM_UPLOAD",
        default_business_name=req.business_name or "Uploaded Business Entity",
        consent_granted=req.consent_granted
    )

def classify_document(text: str, filename: str) -> str:
    """
    Auto-classifies document type based on OCR text content first (most specific to least),
    falling back to filename keywords, and never defaulting to gst_certificate.
    Returns: 'udyam_certificate' | 'gst_certificate' | 'address_proof' | 'signatory_id' | 'unclassified'
    """
    text_upper = (text or "").upper()
    # 1. Udyam Registration Certificate (must precede GST because Udyam contains 'Registration Certificate')
    if "UDYAM REG" in text_upper or "UDYAM-" in text_upper:
        return "udyam_certificate"
    # 2. GST Registration Certificate
    if "GSTIN" in text_upper or "GST REGISTRATION" in text_upper:
        return "gst_certificate"
    # 3. Address Proof (Utility / Electricity Bill)
    if "ELECTRICITY BILL" in text_upper or "BILL DATE" in text_upper or "CONSUMER NO" in text_upper or "SUPPLY ADDRESS" in text_upper:
        return "address_proof"
    # 4. Authorized Signatory Credential Card
    if "SIGNATORY" in text_upper or "VALID TILL" in text_upper or "DESIGNATION" in text_upper:
        return "signatory_id"

    # Filename fallback
    fn_lower = (filename or "").lower()
    if "udyam" in fn_lower or "msme" in fn_lower:
        return "udyam_certificate"
    if "gst" in fn_lower:
        return "gst_certificate"
    if "elec" in fn_lower or "bill" in fn_lower or "addr" in fn_lower:
        return "address_proof"
    if "sig" in fn_lower or "id" in fn_lower or "pan" in fn_lower:
        return "signatory_id"

    return "unclassified"


def extract_text_from_file(file_path: str, ext: str, file_bytes: bytes, original_filename: str) -> Tuple[str, str]:
    """
    Extracts text from an uploaded document using:
    - Native UTF-8 decode for text/json
    - Native Windows OCR when running on Windows (unless OCR_BACKEND=llm)
    - GenAI Vision OCR fallback for Linux/Vercel environments
    Returns: (extracted_text, backend_name)
    """
    if ext in ['.txt', '.json']:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read().strip(), "text"
        except Exception:
            return "", "none"

    if ext in ['.png', '.jpg', '.jpeg', '.bmp', '.webp']:
        # Windows Native Runtime OCR
        if os.name == "nt" and os.environ.get("OCR_BACKEND") != "llm":
            ocr_script = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts', 'ocr_test.ps1'))
            cmd = ['powershell', '-ExecutionPolicy', 'Bypass', '-File', ocr_script, '-ImagePath', os.path.abspath(file_path)]
            try:
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
                text = res.stdout.strip()
                if text:
                    return text, "windows"
            except Exception:
                pass

        # LLM Vision OCR Fallback (Linux / Vercel cloud)
        mime_map = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.webp': 'image/webp',
            '.bmp': 'image/bmp'
        }
        mime = mime_map.get(ext, 'image/png')
        ocr_text = advisor_engine.llm.ocr_image(file_bytes, mime=mime)
        if ocr_text:
            return ocr_text.strip(), "llm"

    return "", "none"


@app.post("/api/kyc/upload-files")
async def upload_kyc_files(
    files: List[UploadFile] = File(...),
    consent_granted: bool = Form(True)
):
    """
    Accepts real uploaded document files (.png, .jpg, .jpeg, .webp, .txt),
    extracts text dynamically using native Windows OCR or Cloud LLM Vision OCR,
    auto-classifies document types with strict conflict resolution (no overwrites),
    and executes dynamic Smart KYC verification.
    """
    if len(files) > 8:
        raise HTTPException(status_code=400, detail="Maximum 8 files per upload request.")

    temp_dir = tempfile.mkdtemp(prefix="vyaparsetu_ocr_")
    docs_map = {'address_proof': '', 'gst_certificate': '', 'udyam_certificate': '', 'signatory_id': ''}
    extracted_snippets = {}
    warnings = []
    unclassified_files = []
    backends_used = set()

    try:
        # First pass: validate extensions and sizes, save securely using UUIDs
        processed_files = []
        max_size = 5 * 1024 * 1024  # 5 MB

        for file in files:
            orig_name = file.filename or "unknown"
            ext = os.path.splitext(orig_name)[1].lower()

            if ext == ".pdf":
                raise HTTPException(status_code=400, detail="PDF format is not supported yet. Please upload PNG, JPG, or WEBP image files.")

            if ext not in {'.png', '.jpg', '.jpeg', '.webp', '.txt', '.json'}:
                raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}. Allowed: .png, .jpg, .jpeg, .webp, .txt")

            # Read stream in 64 KB chunks, enforce 5 MB cap
            chunks = []
            total_size = 0
            while True:
                chunk = await file.read(64 * 1024)
                if not chunk:
                    break
                total_size += len(chunk)
                if total_size > max_size:
                    raise HTTPException(status_code=413, detail=f"File '{orig_name}' exceeds 5 MB limit.")
                chunks.append(chunk)

            file_bytes = b"".join(chunks)

            # Secure path traversal prevention: save using UUID
            safe_name = f"{uuid.uuid4().hex}{ext}"
            file_path = os.path.join(temp_dir, safe_name)
            with open(file_path, "wb") as f:
                f.write(file_bytes)

            processed_files.append((orig_name, ext, file_path, file_bytes))

        # Second pass: OCR text extraction and classification
        for orig_name, ext, file_path, file_bytes in processed_files:
            text, backend = extract_text_from_file(file_path, ext, file_bytes, orig_name)
            if backend != "none":
                backends_used.add(backend)

            if not text:
                warnings.append(f"Could not read text from {orig_name}")
                unclassified_files.append(orig_name)
                extracted_snippets[f"unreadable_{len(unclassified_files)}"] = {
                    'filename': orig_name,
                    'chars_extracted': 0,
                    'preview': '',
                    'ocr_backend': backend
                }
                continue

            doc_type = classify_document(text, orig_name)

            if doc_type in docs_map:
                if docs_map[doc_type]:
                    # Slot already occupied - DO NOT overwrite existing document
                    existing_fn = extracted_snippets[doc_type]['filename']
                    warnings.append(f"Two files look like {doc_type}: {existing_fn}, {orig_name}")
                    unclassified_files.append(orig_name)
                    extracted_snippets[f"duplicate_{orig_name}"] = {
                        'filename': orig_name,
                        'chars_extracted': len(text),
                        'preview': text[:200],
                        'ocr_backend': backend,
                        'assigned_type': 'unclassified (duplicate)'
                    }
                else:
                    docs_map[doc_type] = text
                    extracted_snippets[doc_type] = {
                        'filename': orig_name,
                        'chars_extracted': len(text),
                        'preview': text[:200],
                        'ocr_backend': backend,
                        'assigned_type': doc_type
                    }
            else:
                unclassified_files.append(orig_name)
                extracted_snippets[f"unclassified_{orig_name}"] = {
                    'filename': orig_name,
                    'chars_extracted': len(text),
                    'preview': text[:200],
                    'ocr_backend': backend,
                    'assigned_type': 'unclassified'
                }

        file_presence = {
            'has_address_proof': bool(docs_map['address_proof']),
            'has_gst_certificate': bool(docs_map['gst_certificate']),
            'has_udyam_certificate': bool(docs_map['udyam_certificate']),
            'has_signatory_id': bool(docs_map['signatory_id']),
        }

        res = kyc_engine.verify_applicant_documents(
            docs_map=docs_map,
            file_presence=file_presence,
            applicant_code="CUSTOM_UPLOAD",
            default_business_name="Uploaded Business Entity",
            consent_granted=consent_granted
        )

        effective_backend = "windows" if "windows" in backends_used else ("llm" if "llm" in backends_used else "text")

        return {
            'status': 'SUCCESS',
            'files_received': len(files),
            'ocr_backend': effective_backend,
            'warnings': warnings,
            'extracted_snippets': extracted_snippets,
            'verification': res
        }
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

@app.post("/api/kyc/consent")
def record_kyc_consent(req: ConsentRecordRequest):
    return kyc_engine.record_consent(req.applicant_code, req.entity_name, purpose=req.purpose)

@app.post("/api/kyc/consent/revoke")
def revoke_kyc_consent(req: ConsentRevokeRequest):
    return kyc_engine.revoke_consent(req.applicant_code, reason=req.reason)

@app.get("/api/kyc/consent/logs")
def get_consent_logs(applicant_code: Optional[str] = None):
    return {
        'total': len(kyc_engine.get_consent_history(applicant_code)),
        'logs': kyc_engine.get_consent_history(applicant_code)
    }

@app.get("/api/kyc/evaluate-all")
def evaluate_all_kyc_applicants():
    return kyc_engine.evaluate_all_applicants()

@app.post("/api/orders/create")
def create_order(req: OrderCreateRequest):
    return order_service.create_order(req.model_dump())

@app.get("/api/orders/{order_id}")
def get_order_tracking(order_id: str):
    res = order_service.get_order(order_id)
    if not res:
        raise HTTPException(status_code=404, detail="Order not found")
    return res

@app.post("/api/orders/{order_id}/advance")
def advance_order_stage(order_id: str, req: OrderAdvanceRequest):
    res = order_service.advance_stage(order_id, technician_pin=req.technician_pin)
    if res.get('status') == 'ERROR':
        raise HTTPException(status_code=404, detail=res['message'])
    if res.get('status') == 'PIN_AUTHENTICATION_FAILED':
        raise HTTPException(status_code=403, detail=res['message'])
    return res

@app.post("/api/orders/{order_id}/reschedule")
def reschedule_order(order_id: str, req: OrderRescheduleRequest):
    res = order_service.reschedule_appointment(order_id, new_slot=req.new_slot, days_extension=req.days_extension)
    if res.get('status') == 'ERROR':
        raise HTTPException(status_code=404, detail=res['message'])
    return res

@app.get("/api/orders/lookup/{phone}")
def lookup_orders_by_phone(phone: str):
    orders = order_service.lookup_by_phone(phone)
    return {'total': len(orders), 'orders': orders}

@app.get("/api/orders/{order_id}/notifications")
def get_order_notifications(order_id: str):
    res = order_service.get_order_notifications(order_id)
    return {'order_id': order_id, 'notifications': res}

@app.get("/api/partner/leads")
def get_partner_leads(
    limit: int = 15,
    offset: int = 0,
    segment: Optional[str] = None,
    city_tier: Optional[int] = None,
    min_score: Optional[int] = None,
    drop_category: Optional[str] = None,
    propensity_tier: Optional[str] = None
):
    leads = partner_service.get_dropped_leads(
        limit=limit,
        offset=offset,
        segment=segment,
        city_tier=city_tier,
        min_score=min_score,
        drop_category=drop_category,
        propensity_tier=propensity_tier
    )
    return {
        'total': len(leads),
        'limit': limit,
        'offset': offset,
        'leads': leads
    }

@app.get("/api/partner/lead/{lead_id}")
def get_partner_lead_detail(lead_id: str):
    res = partner_service.get_lead_detail(lead_id)
    if not res:
        raise HTTPException(status_code=404, detail="Lead not found")
    return res

@app.get("/api/partner/stats")
def get_partner_stats():
    return partner_service.get_partner_stats()

@app.post("/api/partner/salvage-campaign")
def trigger_salvage_campaign(req: SalvageCampaignRequest):
    return partner_service.simulate_salvage_campaign(req.lead_ids, partner_id=req.partner_id)

@app.get("/api/intelligence/summary")
def get_intelligence_summary():
    return data_intelligence.generate_full_report()

# Mount frontend static files
static_dir = os.path.join(os.path.dirname(__file__), 'static')
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/favicon.ico", include_in_schema=False)
def serve_favicon():
    return Response(content=b"", media_type="image/x-icon")

@app.get("/diagrams")
def serve_diagrams():
    diag_file = os.path.join(static_dir, 'diagrams.html')
    if os.path.exists(diag_file):
        return FileResponse(diag_file)
    return {"message": "Diagrams viewer not found."}

@app.get("/")
def serve_index():
    index_file = os.path.join(static_dir, 'index.html')
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "VyaparSetu API is running. Build static frontend to access UI."}


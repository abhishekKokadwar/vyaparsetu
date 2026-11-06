from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import os

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


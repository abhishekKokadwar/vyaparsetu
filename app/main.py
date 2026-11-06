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

class OrderCreateRequest(BaseModel):
    business_name: str
    contact_name: str
    contact_phone: str
    city: str
    bundle_name: str
    monthly_amount_inr: int
    estimated_install_days: int = 3
    selected_products: List[str] = []

# --- API Endpoints ---

@app.get("/api/catalogue")
def get_catalogue():
    return {
        'total': len(catalog_engine.products),
        'products': catalog_engine.get_all()
    }

@app.post("/api/catalogue/validate")
def validate_catalogue(req: ValidationRequest):
    is_valid, errors = catalog_engine.validate_selection(
        req.selected_product_ids,
        city_tier=req.city_tier,
        employees=req.employee_count,
        sites=req.num_sites,
        has_gstin=req.has_gstin
    )
    return {'is_valid': is_valid, 'errors': errors}

@app.post("/api/catalogue/pricing")
def get_bundle_pricing(req: BundlePricingRequest):
    return catalog_engine.calculate_bundle_pricing(req.items)

@app.post("/api/advisor/recommend")
def recommend_bundle(req: ProfileRequest):
    return advisor_engine.recommend(req.model_dump())

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

@app.post("/api/orders/create")
def create_order(req: OrderCreateRequest):
    return order_service.create_order(req.model_dump())

@app.get("/api/orders/{order_id}")
def get_order_tracking(order_id: str):
    res = order_service.get_order(order_id)
    if not res:
        raise HTTPException(status_code=404, detail="Order not found")
    return res

@app.get("/api/partner/leads")
def get_partner_leads(limit: int = 15, segment: Optional[str] = None):
    return {
        'leads': partner_service.get_dropped_leads(limit=limit, segment=segment)
    }

@app.get("/api/partner/stats")
def get_partner_stats():
    return partner_service.get_partner_stats()

# Mount frontend static files
static_dir = os.path.join(os.path.dirname(__file__), 'static')
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def serve_index():
    index_file = os.path.join(static_dir, 'index.html')
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "VyaparSetu API is running. Build static frontend to access UI."}

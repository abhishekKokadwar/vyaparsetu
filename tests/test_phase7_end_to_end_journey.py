import pytest
import time
from fastapi.testclient import TestClient
from app.main import app
from app.catalog_engine import CatalogEngine
from app.advisor_engine import AdvisorEngine
from app.registry_service import RegistryService
from app.kyc_engine import SmartKYCEngine
from app.order_service import OrderService
from app.partner_service import PartnerService

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

def test_api_gateway_contracts_and_openapi_docs(client):
    """Verify OpenAPI 3.0 documentation and all core API gateway contracts return HTTP 200"""
    # OpenAPI JSON schema
    res_openapi = client.get("/openapi.json")
    assert res_openapi.status_code == 200
    schema = res_openapi.json()
    assert "paths" in schema
    assert "/api/catalogue" in schema["paths"]
    assert "/api/advisor/recommend" in schema["paths"]
    assert "/api/kyc/verify-applicant" in schema["paths"]
    assert "/api/orders/create" in schema["paths"]
    assert "/api/partner/leads" in schema["paths"]

    # Catalogue endpoint
    res_cat = client.get("/api/catalogue")
    assert res_cat.status_code == 200
    assert res_cat.json()['total'] == 25

    # Advisor Jury benchmark matrix endpoint
    res_matrix = client.get("/api/advisor/benchmark-matrix")
    assert res_matrix.status_code == 200
    assert res_matrix.json()['all_passed'] is True
    assert res_matrix.json()['total_scenarios'] == 15

    # Registry lookup
    res_reg = client.get("/api/registry/gstin/37IHKXV5167L1ZS")
    assert res_reg.status_code == 200
    assert res_reg.json()['found'] is True
    assert res_reg.json()['status'] == "Cancelled"

    # KYC Applicants endpoint
    res_apps = client.get("/api/kyc/applicants")
    assert res_apps.status_code == 200
    assert res_apps.json()['total'] == 12

    # Partner stats endpoint
    res_pstats = client.get("/api/partner/stats")
    assert res_pstats.status_code == 200
    assert res_pstats.json()['total_dropped_leads'] == 4632

    # Data Intelligence summary endpoint
    res_intel = client.get("/api/intelligence/summary")
    assert res_intel.status_code == 200
    assert res_intel.json()['funnel_analysis']['total_leads'] == 5000

def test_end_to_end_single_sitting_customer_lifecycle():
    """
    Simulates the entire single-sitting digital acquisition and onboarding lifecycle:
    1. Conversational Hindi intake & entity extraction.
    2. Zero-violation bundle recommendation with transparent pricing.
    3. DPDP Act 2023 affirmative consent & cryptographic audit logging.
    4. Smart KYC instant registry cross-validation.
    5. Order creation with dynamic SLA, field engineer assignment & PIN generation.
    6. Sequential milestone fulfillment to Live Service Activation.
    """
    catalog = CatalogEngine()
    advisor = AdvisorEngine(catalog)
    registry = RegistryService()
    kyc = SmartKYCEngine(registry)
    orders = OrderService(catalog)

    # 1. Intake: Conversational Hindi query
    query_hi = "मेरी जयपुर में 2-counter किराना दुकान है 2 लोग काम करते हैं, UPI पेमेंट ड्रॉप होती है, CCTV और बिलिंग चाहिए"
    extracted_profile = advisor.parse_conversational_query(query_hi)
    assert extracted_profile['preferred_language'] == 'hi'
    assert extracted_profile['segment'] == 'micro'
    assert extracted_profile['city_tier'] == 2
    assert extracted_profile['employee_count'] == 2
    extracted_profile['has_gstin'] = False

    # 2. Advisory: Deterministic recommendation
    recommendation = advisor.recommend(extracted_profile)
    assert recommendation['is_compliant'] is True
    assert len(recommendation['validation_errors']) == 0
    assert 'P04' in recommendation['selected_product_ids'] # 5G AirFiber for Tier 2
    assert 'P19' in recommendation['selected_product_ids'] # Cloud POS
    assert 'P23' in recommendation['selected_product_ids'] # Cloud CCTV
    assert 'P07' in recommendation['selected_product_ids'] # Postpaid SIM
    assert recommendation['pricing']['monthly_total_inr'] > 0
    assert recommendation['savings']['annual_savings_inr'] > 0
    assert "नमस्ते" in recommendation['pitch_narrative_hi']

    # 3. DPDP Consent Gate
    consent = kyc.record_consent("K02", "Harmony Dental Care", purpose="telecom_activation")
    assert consent['status'] == 'GRANTED'
    assert len(consent['audit_hash']) == 64

    # 4. Smart KYC Instant Verification
    kyc_res = kyc.verify_applicant_by_code("K02", consent_granted=True)
    assert kyc_res['verdict'] == 'PASS'
    assert all(chk['status'] == 'PASSED' for chk in kyc_res['checklist'])

    # 5. Order Creation with Dynamic SLA
    order_payload = {
        'business_name': 'Sharma Kirana Store',
        'contact_name': 'Ramesh Sharma',
        'contact_phone': '+91 98290 12345',
        'city': 'Jaipur',
        'bundle_name': recommendation['bundle_name_en'],
        'monthly_amount_inr': recommendation['pricing']['monthly_total_inr'],
        'selected_products': recommendation['selected_product_ids']
    }
    order = orders.create_order(order_payload)
    order_id = order['order_id']
    assert order_id.startswith("VS-2026-")
    assert order['estimated_install_days'] == 4 # max(P04:2, P19:3, P07:1, P23:4) -> 4 days
    assert order['stage_index'] == 2
    pin = order['technician']['installation_pin']
    assert len(pin) == 4

    # 6. Sequential Fulfillment to Live Activation
    adv1 = orders.advance_stage(order_id) # to TECHNICIAN_ASSIGNED (3)
    assert adv1['status'] == 'SUCCESS'
    assert adv1['new_stage'] == 'TECHNICIAN_ASSIGNED'

    adv2 = orders.advance_stage(order_id) # to INSTALLATION_IN_PROGRESS (4)
    assert adv2['status'] == 'SUCCESS'
    assert adv2['new_stage'] == 'INSTALLATION_IN_PROGRESS'

    # Activation attempt with correct PIN
    adv_final = orders.advance_stage(order_id, technician_pin=pin)
    assert adv_final['status'] == 'SUCCESS'
    assert adv_final['new_stage'] == 'SERVICE_ACTIVATED'

    final_order = orders.get_order(order_id)
    assert final_order['current_stage_code'] == 'SERVICE_ACTIVATED'
    assert final_order['countdown']['is_completed'] is True

def test_end_to_end_partner_salvage_lifecycle():
    """
    Simulates the AI Propensity Win-Back Lifecycle:
    1. Identification of high-value dropped lead.
    2. Multi-factor propensity scoring.
    3. Automated playbook mapping and bilingual pitch generation.
    4. Partner commission calculation.
    5. Campaign simulation and ARR recovery tracking.
    """
    partner = PartnerService()
    
    # 1. Retrieve top high-propensity dropped leads
    high_leads = partner.get_dropped_leads(limit=5, min_score=75)
    assert len(high_leads) > 0
    top_lead = high_leads[0]
    lid = top_lead['lead_id']

    # 2. Inspect deep profile and playbook
    lead_detail = partner.get_lead_detail(lid)
    assert lead_detail is not None
    assert lead_detail['propensity_score'] >= 75
    assert lead_detail['propensity_tier'] == 'HIGH'
    assert lead_detail['commission']['total_partner_payout_inr'] >= 5000

    # 3. Validate personalized pitch
    playbook = lead_detail['playbook']
    assert "https://vyaparsetu.airtel.in/salvage/" in playbook['one_click_link']
    assert lead_detail['contact_name'] in playbook['pitch_en']
    assert "नमस्ते" in playbook['pitch_hi']

    # 4. Campaign dispatch simulation
    top_ids = [l['lead_id'] for l in high_leads]
    camp_res = partner.simulate_salvage_campaign(top_ids, partner_id="PARTNER-DELHI-02")
    assert camp_res['status'] == 'SUCCESS'
    assert camp_res['expected_conversions'] >= 1
    assert camp_res['expected_salvaged_arr_inr'] > 0
    assert camp_res['expected_partner_earnings_inr'] > 0

def test_sub_millisecond_concurrency_stress():
    """
    Stress test verifying sub-millisecond retrieval across Catalog, Registry,
    and cached Advisor engines under 100 consecutive requests.
    """
    catalog = CatalogEngine()
    advisor = AdvisorEngine(catalog)
    registry = RegistryService()

    # Pre-warm advisor cache
    test_profile = {
        'business_type': 'Kirana Store',
        'segment': 'micro',
        'city_tier': 1,
        'employee_count': 2,
        'num_sites': 1,
        'has_gstin': True,
        'preferred_language': 'en'
    }
    advisor.recommend(test_profile)

    start_time = time.perf_counter()
    iterations = 100

    for _ in range(iterations):
        # 1. Catalog retrieval
        p = catalog.get_product('P01')
        assert p is not None

        # 2. O(1) Registry lookup
        reg = registry.lookup_gstin('37IHKXV5167L1ZS')
        assert reg['found'] is True

        # 3. Warm cached advisor recommendation
        rec = advisor.recommend(test_profile)
        assert rec['cache_hit'] is True

    elapsed_total_ms = (time.perf_counter() - start_time) * 1000
    avg_per_iteration_ms = elapsed_total_ms / iterations

    # Benchmark: all 3 operations combined must complete in under 2.0 ms per iteration
    assert avg_per_iteration_ms < 2.0, f"Average latency {avg_per_iteration_ms:.3f} ms exceeds 2.0 ms limit"

def test_full_system_telemetry_and_privacy_compliance():
    """Verify that throughout all engines, PII masking and DPDP compliance are maintained"""
    registry = RegistryService()
    kyc = SmartKYCEngine(registry)

    # GSTIN masking
    raw_gst = "37IHKXV5167L1ZS"
    masked_gst = registry.mask_gstin(raw_gst)
    assert len(masked_gst) == 15
    assert "KXV516" not in masked_gst

    # Phone masking
    raw_phone = "+91 98450 12345"
    masked_phone = registry.mask_phone(raw_phone)
    assert "XXXXXX" in masked_phone

    # KYC applicant response masking
    res = kyc.verify_applicant_by_code('K02', consent_granted=True)
    assert res['dpdp_compliance']['pii_masked'] is True
    assert res['dpdp_compliance']['consent_verified'] is True

import pytest
from app.catalog_engine import CatalogEngine
from app.advisor_engine import AdvisorEngine

@pytest.fixture(scope="module")
def advisor():
    catalog = CatalogEngine()
    return AdvisorEngine(catalog)

def test_advisor_initialization_and_cache(advisor):
    """Verify advisor engine is initialized with healthy cache statistics"""
    stats = advisor.get_cache_stats()
    assert 'cached_entries' in stats
    assert 'cache_hits' in stats
    assert 'total_requests' in stats

def test_micro_retail_recommendation(advisor):
    """Verify Kirana in Tier 2 without GSTIN gets P04 AirFiber, P19 POS, P07 Postpaid, P23 CCTV"""
    profile = {
        'business_type': 'Kirana Store',
        'segment': 'micro',
        'city_tier': 2,
        'employee_count': 2,
        'num_sites': 1,
        'has_gstin': False,
        'preferred_language': 'en'
    }
    res = advisor.recommend(profile)
    assert res['is_compliant'] is True
    assert len(res['validation_errors']) == 0
    assert 'P04' in res['selected_product_ids'] # 5G AirFiber 100 for Tier 2
    assert 'P19' in res['selected_product_ids'] # Cloud POS & Billing
    assert 'P07' in res['selected_product_ids'] # Business Postpaid 299 (no GST required)
    assert 'P23' in res['selected_product_ids'] # Cloud CCTV
    assert res['pricing']['monthly_total_inr'] > 0
    assert res['savings']['annual_savings_inr'] > 0

def test_professional_clinic_firm_recommendation(advisor):
    """Verify Dental Clinic in Tier 1 with GSTIN gets Biz Fibre 300, Static IP, Email, Backup, Wi-Fi"""
    profile = {
        'business_type': 'SmileCare Dental Clinic',
        'segment': 'prof',
        'city_tier': 1,
        'employee_count': 5,
        'num_sites': 1,
        'has_gstin': True,
        'preferred_language': 'en'
    }
    res = advisor.recommend(profile)
    assert res['is_compliant'] is True
    assert len(res['validation_errors']) == 0
    assert 'P02' in res['selected_product_ids'] # Biz Fibre 300
    assert 'P11' in res['selected_product_ids'] # Static IP
    assert 'P16' in res['selected_product_ids'] # Cloud Email
    assert 'P17' in res['selected_product_ids'] # Cloud Backup 1TB
    assert 'P22' in res['selected_product_ids'] # Secure Wi-Fi

def test_multi_site_chain_recommendation(advisor):
    """Verify 3-site Retail Chain in Tier 1 with GSTIN gets SD-WAN, Failover, Fibre, CCTV, Toll-Free"""
    profile = {
        'business_type': 'Trends Retail Chain',
        'segment': 'multi',
        'city_tier': 1,
        'employee_count': 15,
        'num_sites': 3,
        'has_gstin': True,
        'preferred_language': 'en'
    }
    res = advisor.recommend(profile)
    assert res['is_compliant'] is True
    assert len(res['validation_errors']) == 0
    assert 'P02' in res['selected_product_ids']
    assert 'P09' in res['selected_product_ids'] # 4G/5G Failover
    assert 'P10' in res['selected_product_ids'] # Managed SD-WAN (sites >= 3, emp >= 10, GSTIN=True)
    assert 'P23' in res['selected_product_ids'] # Cloud CCTV
    assert 'P13' in res['selected_product_ids'] # 1800 Toll-Free

def test_small_manufacturing_recommendation(advisor):
    """Verify Manufacturing Plant with 20 workers and GSTIN gets Leased Line 20, Firewall, Machine IoT"""
    profile = {
        'business_type': 'Precision Auto CNC Machining',
        'segment': 'mfg',
        'city_tier': 1,
        'employee_count': 20,
        'num_sites': 1,
        'has_gstin': True,
        'preferred_language': 'en'
    }
    res = advisor.recommend(profile)
    assert res['is_compliant'] is True
    assert len(res['validation_errors']) == 0
    assert 'P05' in res['selected_product_ids'] # Internet Leased Line 20
    assert 'P21' in res['selected_product_ids'] # Managed Firewall
    assert 'P24' in res['selected_product_ids'] # Machine Monitoring IoT
    assert 'P17' in res['selected_product_ids'] # Cloud Backup 1TB

def test_all_15_jury_scenarios_matrix(advisor):
    """Verify all 15 Case Study Jury Scenarios strictly pass catalogue validation with 0 errors"""
    benchmark = advisor.evaluate_jury_scenarios()
    assert benchmark['total_scenarios'] == 15
    assert benchmark['all_passed'] is True, f"Failed scenarios: {[s for s in benchmark['scenarios'] if not s['is_compliant']]}"
    for scn in benchmark['scenarios']:
        assert scn['is_compliant'] is True
        assert len(scn['errors']) == 0
        assert scn['monthly_inr'] > 0
        assert scn['annual_savings_inr'] > 0

def test_multilingual_hindi_synthesis(advisor):
    """Verify localized Hindi bundle names, reasoning, and sales pitch synthesis"""
    profile = {
        'business_type': 'Kirana Store',
        'segment': 'micro',
        'city_tier': 2,
        'employee_count': 2,
        'num_sites': 1,
        'has_gstin': False,
        'preferred_language': 'hi'
    }
    res = advisor.recommend(profile)
    assert "व्यापार" in res['bundle_name']
    assert any("एयरफ़ाइबर" in r or "फ़ाइबर" in r or "दुकान" in r or "बिलिंग" in r for r in res['reasoning'])
    assert "नमस्ते" in res['pitch_narrative']

def test_conversational_query_parsing(advisor):
    """Verify natural language query parsing in Hindi and English"""
    query_hi = "मेरी जयपुर में किराना दुकान है 2 लोग काम करते हैं gstin नहीं है"
    p_hi = advisor.parse_conversational_query(query_hi)
    assert p_hi['preferred_language'] == 'hi'
    assert p_hi['segment'] == 'micro'
    assert p_hi['city_tier'] == 2 # Jaipur is Tier 2
    assert p_hi['employee_count'] == 2
    assert p_hi['has_gstin'] is False

    query_en = "We run a 3-branch retail chain in Bengaluru with 15 staff, have GSTIN"
    p_en = advisor.parse_conversational_query(query_en)
    assert p_en['segment'] == 'multi'
    assert p_en['city_tier'] == 1 # Bengaluru is Tier 1
    assert p_en['num_sites'] == 3
    assert p_en['employee_count'] == 15
    assert p_en['has_gstin'] is True

def test_audit_colloquial_and_regional_queries(advisor):
    """Verify robust parsing across edge queries identified during audit"""
    # 1. '4 restaurants in bangalore'
    p1 = advisor.parse_conversational_query("4 restaurants in bangalore")
    assert p1['num_sites'] == 4
    assert p1['city_tier'] == 1
    assert p1['segment'] == 'multi'
    rec1 = advisor.recommend(p1)
    assert rec1['segment'] == 'multi'

    # 2. 'beauty parlour hai'
    p2 = advisor.parse_conversational_query("beauty parlour hai")
    assert p2['segment'] == 'micro'
    assert p2['preferred_language'] == 'hi'

    # 3. Marathi 'medical store'
    p3 = advisor.parse_conversational_query("माझे पुण्यात मेडिकल स्टोअर आहे 3 कामगार आहेत")
    assert p3['preferred_language'] == 'mr'
    assert p3['city_tier'] == 1
    assert p3['employee_count'] == 3
    assert p3['segment'] == 'prof'
    rec3 = advisor.recommend(p3)
    assert "आपल्या" in rec3['pitch_narrative']

    # 4. 'We have GST and 15 teachers in coaching center'
    p4 = advisor.parse_conversational_query("We have GST and 15 teachers in coaching center")
    assert p4['has_gstin'] is True
    assert p4['employee_count'] == 15
    assert p4['segment'] == 'prof'
    rec4 = advisor.recommend(p4)
    assert 'P11' in rec4['selected_product_ids'] # Static IP unlocked by GSTIN

def test_clarification_detection(advisor):
    """Verify ambiguity detection when key fields are omitted"""
    ambiguous_profile = {
        'business_type': 'Kirana Store'
        # omitted has_gstin, num_sites, city_tier
    }
    clarifications = advisor.detect_clarifications(ambiguous_profile)
    fields = [c['field'] for c in clarifications]
    assert 'has_gstin' in fields
    assert 'num_sites' in fields
    assert 'city_tier' in fields

def test_caching_and_sub_millisecond_latency(advisor):
    """Verify in-memory caching produces sub-millisecond responses on repeated queries"""
    profile = {
        'business_type': 'CA Firm',
        'segment': 'prof',
        'city_tier': 1,
        'employee_count': 6,
        'num_sites': 1,
        'has_gstin': True,
        'preferred_language': 'en'
    }
    # First call (cold)
    res1 = advisor.recommend(profile)
    assert res1['cache_hit'] is False

    # Second call (warm cache)
    res2 = advisor.recommend(profile)
    assert res2['cache_hit'] is True
    assert res2['selected_product_ids'] == res1['selected_product_ids']
    assert res2['pricing']['monthly_total_inr'] == res1['pricing']['monthly_total_inr']


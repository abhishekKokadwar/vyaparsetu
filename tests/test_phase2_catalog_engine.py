import pytest
from app.catalog_engine import CatalogEngine

@pytest.fixture(scope="module")
def catalog():
    return CatalogEngine()

def test_catalog_inventory_integrity(catalog):
    """Verify that all 25 products from product_catalogue.csv are loaded and indexed"""
    products = catalog.get_all()
    assert len(products) == 25, "Catalogue must contain exactly 25 products"
    
    categories = list(catalog.category_index.keys())
    expected_categories = ['Connectivity', 'Communication', 'Cloud & Productivity', 'Security', 'IoT & Physical']
    for cat in expected_categories:
        assert cat in categories, f"Missing category index: {cat}"

def test_gstin_rule_enforcement(catalog):
    """Verify that products requiring GSTIN are strictly rejected when has_gstin=False"""
    # P05 is Internet Leased Line 20 (requires_gstin = Y, min_employees = 10)
    is_valid, errors, suggestions = catalog.validate_selection(['P05'], employees=10, has_gstin=False)
    assert is_valid is False
    assert any("requires an active GST" in err for err in errors)
    assert len(suggestions) > 0

    # With GSTIN=True and employees=10, P05 should pass
    is_valid_with_gst, errors_with_gst, _ = catalog.validate_selection(['P05'], employees=10, has_gstin=True)
    assert is_valid_with_gst is True
    assert len(errors_with_gst) == 0

def test_city_tier_rule_enforcement(catalog):
    """Verify that Tier 1 exclusive products cannot be selected in Tier 2 cities"""
    # P03 is Biz Fibre 1G (available only in Tier 1, min_employees = 5)
    is_valid, errors, suggestions = catalog.validate_selection(['P03'], city_tier=2, employees=5, has_gstin=True)
    assert is_valid is False
    assert any("only available in City Tier" in err for err in errors)

    # In Tier 1 with employees=5, P03 should pass
    is_valid_t1, errors_t1, _ = catalog.validate_selection(['P03'], city_tier=1, employees=5, has_gstin=True)
    assert is_valid_t1 is True

def test_directed_dependency_graph(catalog):
    """Verify requires_one_of prerequisite connectivity enforcement"""
    # P23 is Cloud CCTV (requires one of P01|P02|P03|P04|P05|P06)
    is_valid_alone, errors_alone, suggestions_alone = catalog.validate_selection(['P23'])
    assert is_valid_alone is False
    assert any("requires at least one base connection" in err for err in errors_alone)
    assert any("Add Biz Fibre 100" in sug for sug in suggestions_alone)

    # When bundled with P01 (Biz Fibre 100), dependency is satisfied
    is_valid_bundled, errors_bundled, _ = catalog.validate_selection(['P01', 'P23'])
    assert is_valid_bundled is True
    assert len(errors_bundled) == 0

def test_static_ip_dependency(catalog):
    """Verify Static IP (P11) requires Fibre base connection P01|P02|P03"""
    is_valid_fail, errors_fail, _ = catalog.validate_selection(['P11', 'P07']) # P07 is SIM, not Fibre
    assert is_valid_fail is False

    is_valid_pass, errors_pass, _ = catalog.validate_selection(['P11', 'P02']) # P02 is Biz Fibre 300
    assert is_valid_pass is True

def test_bundle_pricing_and_savings_calculation(catalog):
    """Verify pricing math, setup fee aggregation, contract duration and savings calculation"""
    items = [
        {'product_id': 'P01', 'quantity': 1}, # Biz Fibre 100 (₹999/mo, setup ₹0, 12m contract, 5 days install)
        {'product_id': 'P19', 'quantity': 1}, # Cloud POS (₹599/mo, setup ₹2500, 12m contract, 3 days install)
        {'product_id': 'P07', 'quantity': 2}, # 2x Postpaid SIM (2x ₹299 = ₹598/mo, setup ₹0, 1m contract, 1 day install)
        {'product_id': 'P23', 'quantity': 1}  # Cloud CCTV (₹199/mo, setup ₹1800, 12m contract, 4 days install)
    ]
    
    pricing = catalog.calculate_bundle_pricing(items)
    
    expected_monthly = 999 + 599 + (299 * 2) + 199 # = ₹2,395
    expected_setup = 0 + 2500 + 0 + 1800           # = ₹4,300
    
    assert pricing['monthly_recurring_total_inr'] == expected_monthly
    assert pricing['one_time_setup_total_inr'] == expected_setup
    assert pricing['contract_lock_months'] == 12
    assert pricing['estimated_install_sla_days'] == 5 # max install days
    
    # Verify savings
    savings = pricing['vendor_savings_benchmark']
    assert savings['monthly_savings_inr'] > 0
    assert savings['annual_savings_inr'] == savings['monthly_savings_inr'] * 12
    assert savings['first_year_total_savings_inr'] > savings['annual_savings_inr']

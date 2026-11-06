import pytest
from app.catalog_engine import CatalogEngine
from app.order_service import OrderService

@pytest.fixture(scope="module")
def catalog():
    return CatalogEngine()

@pytest.fixture(scope="module")
def order_service(catalog):
    return OrderService(catalog)

def test_order_service_initialization_and_seed(order_service):
    """Verify OrderService seeds demo orders with full milestone tracking"""
    seed_id = "VS-2026-90412"
    order = order_service.get_order(seed_id)
    assert order is not None
    assert order['order_id'] == seed_id
    assert order['business_name'] == 'Balaji Dental Clinic'
    assert len(order['stages']) == 6
    assert order['technician']['name'] == 'Ramesh Kumar'
    assert 'countdown' in order
    assert order['countdown']['progress_percent'] > 0

def test_order_creation_and_id_format(order_service):
    """Verify order creation generates valid human-readable ID and milestone state"""
    order_data = {
        'business_name': 'Gupta Kirana Store',
        'contact_name': 'Ramesh Gupta',
        'contact_phone': '+91 98230 44556',
        'city': 'Jaipur',
        'bundle_name': 'Vyapar Booster Pack',
        'monthly_amount_inr': 2395,
        'selected_products': ['P04', 'P19', 'P07', 'P23']
    }
    order = order_service.create_order(order_data)
    assert order['order_id'].startswith("VS-2026-")
    assert order['business_name'] == 'Gupta Kirana Store'
    assert order['current_stage_code'] == 'FEASIBILITY_DISPATCH'
    assert order['stage_index'] == 2
    assert len(order['technician']['installation_pin']) == 4
    assert len(order['stages']) == 6

def test_dynamic_sla_calculation(order_service):
    """Verify dynamic installation SLA calculation from catalog typical_install_days"""
    # 5G AirFiber micro pack (max of P04: 2d, P19: 3d, P07: 1d) -> 3 days
    sla_airfiber = order_service.calculate_bundle_sla(['P04', 'P19', 'P07'])
    assert sla_airfiber == 3

    # Biz Fibre 300 professional suite (P02: 5d, P11: 1d, P16: 1d) -> 5 days
    sla_fibre300 = order_service.calculate_bundle_sla(['P02', 'P11', 'P16'])
    assert sla_fibre300 == 5

    # Biz Fibre 1G suite (P03: 7d, P11: 1d, P16: 1d) -> 7 days
    sla_fibre1g = order_service.calculate_bundle_sla(['P03', 'P11', 'P16'])
    assert sla_fibre1g == 7

    # Managed SD-WAN multi-site (P02: 5d, P10: 14d, P23: 4d) -> 14 days
    sla_sdwan = order_service.calculate_bundle_sla(['P02', 'P10', 'P23'])
    assert sla_sdwan == 14

    # Dedicated Leased Line 20 manufacturing (P05: 21d, P21: 10d) -> 21 days
    sla_leased20 = order_service.calculate_bundle_sla(['P05', 'P21'])
    assert sla_leased20 == 21

    # Dedicated Leased Line 100 enterprise (P06: 30d, P21: 10d) -> 30 days
    sla_leased100 = order_service.calculate_bundle_sla(['P06', 'P21'])
    assert sla_leased100 == 30

def test_state_machine_sequential_advancement(order_service):
    """Verify strict sequential state transitions through fulfillment milestones"""
    order = order_service.create_order({
        'business_name': 'Advance Test Co',
        'contact_name': 'Owner',
        'contact_phone': '+91 99999 11111',
        'selected_products': ['P01', 'P19']
    })
    oid = order['order_id']
    assert order['stage_index'] == 2 # starts at FEASIBILITY_DISPATCH

    # Advance to TECHNICIAN_ASSIGNED (stage index 3)
    res1 = order_service.advance_stage(oid)
    assert res1['status'] == 'SUCCESS'
    assert res1['new_stage'] == 'TECHNICIAN_ASSIGNED'
    assert res1['stage_index'] == 3

    # Advance to INSTALLATION_IN_PROGRESS (stage index 4)
    res2 = order_service.advance_stage(oid)
    assert res2['status'] == 'SUCCESS'
    assert res2['new_stage'] == 'INSTALLATION_IN_PROGRESS'
    assert res2['stage_index'] == 4

def test_technician_pin_authentication_at_activation(order_service):
    """Verify final live activation strictly requires customer's 4-digit installation PIN"""
    order = order_service.create_order({
        'business_name': 'PIN Auth Test Clinic',
        'contact_name': 'Dr. Test',
        'contact_phone': '+91 99999 22222',
        'selected_products': ['P02']
    })
    oid = order['order_id']
    correct_pin = order['technician']['installation_pin']

    # Advance to stage 3 then 4
    order_service.advance_stage(oid)
    order_service.advance_stage(oid)

    # Attempt activation with wrong PIN
    res_wrong = order_service.advance_stage(oid, technician_pin="0000")
    assert res_wrong['status'] == 'PIN_AUTHENTICATION_FAILED'

    # Attempt activation with correct PIN
    res_correct = order_service.advance_stage(oid, technician_pin=correct_pin)
    assert res_correct['status'] == 'SUCCESS'
    assert res_correct['new_stage'] == 'SERVICE_ACTIVATED'
    assert res_correct['stage_index'] == 5

    # Check updated order
    activated_order = order_service.get_order(oid)
    assert activated_order['current_stage_code'] == 'SERVICE_ACTIVATED'
    assert activated_order['countdown']['is_completed'] is True

def test_customer_appointment_rescheduling(order_service):
    """Verify customer self-service visit window rescheduling and date recalculation"""
    order = order_service.create_order({
        'business_name': 'Reschedule Test Retail',
        'contact_name': 'Shop Owner',
        'contact_phone': '+91 99999 33333',
        'selected_products': ['P01']
    })
    oid = order['order_id']
    new_slot = "Friday, 02:00 PM - 05:00 PM"

    res = order_service.reschedule_appointment(oid, new_slot=new_slot, days_extension=2)
    assert res['status'] == 'SUCCESS'
    assert res['new_slot'] == new_slot

    updated = order_service.get_order(oid)
    assert updated['technician']['slot'] == new_slot

def test_zero_chase_notification_feed(order_service):
    """Verify automated WhatsApp & SMS notifications with bilingual messages"""
    seed_id = "VS-2026-90412"
    notifications = order_service.get_order_notifications(seed_id)
    assert len(notifications) >= 4

    channels = [n['channel'] for n in notifications]
    assert any('WhatsApp' in c for c in channels)
    assert any('SMS' in c for c in channels)

    # Verify bilingual content
    first_notif = notifications[0]
    assert "Namaste" in first_notif['message_en']
    assert "नमस्ते" in first_notif['message_hi']
    assert seed_id in first_notif['message_en']

def test_customer_lookup_by_phone(order_service):
    """Verify looking up orders by raw and normalized customer phone numbers"""
    phone = "+91 98450 12345"
    orders = order_service.lookup_by_phone(phone)
    assert len(orders) > 0
    assert any(o['order_id'] == "VS-2026-90412" for o in orders)

    # Lookup by digits only
    orders_clean = order_service.lookup_by_phone("9845012345")
    assert len(orders_clean) > 0

def test_countdown_telemetry(order_service):
    """Verify live countdown telemetry metrics"""
    seed_id = "VS-2026-90412"
    order = order_service.get_order(seed_id)
    countdown = order['countdown']
    assert 'days_remaining' in countdown
    assert 'hours_remaining' in countdown
    assert 'progress_percent' in countdown
    assert countdown['progress_percent'] >= 60

def test_already_activated_boundary(order_service):
    """Verify boundary condition when attempting to advance an already activated order"""
    order = order_service.create_order({
        'business_name': 'Boundary Test',
        'contact_name': 'Owner',
        'contact_phone': '+91 99999 44444',
        'selected_products': ['P01']
    })
    oid = order['order_id']
    pin = order['technician']['installation_pin']

    # Advance to end
    order_service.advance_stage(oid)
    order_service.advance_stage(oid)
    order_service.advance_stage(oid, technician_pin=pin)

    # Try advancing beyond final stage
    res_extra = order_service.advance_stage(oid)
    assert res_extra['status'] == 'ALREADY_ACTIVATED'

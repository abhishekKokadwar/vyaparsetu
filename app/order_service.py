import uuid
from datetime import datetime, timedelta

class OrderService:
    def __init__(self):
        self.orders = {}
        self._seed_sample_orders()

    def _seed_sample_orders(self):
        """Seed a couple of orders in various stages for live tracking demos"""
        sample_id = "VS-2026-90412"
        self.orders[sample_id] = {
            'order_id': sample_id,
            'business_name': 'Balaji Dental Clinic',
            'contact_name': 'Dr. Balaji Rao',
            'contact_phone': '+91 98450 12345',
            'city': 'Bengaluru',
            'bundle_name': 'Vyapar Professional Suite',
            'monthly_amount_inr': 2522,
            'current_stage': 'TECHNICIAN_ASSIGNED',
            'stage_index': 3,
            'created_at': (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M"),
            'estimated_activation_date': (datetime.now() + timedelta(days=2)).strftime("%d %b %Y"),
            'stages': [
                {'name': 'Order Placed', 'code': 'ORDER_PLACED', 'status': 'COMPLETED', 'timestamp': 'Yesterday, 10:30 AM', 'detail': 'Bundle configured & checkout completed.'},
                {'name': 'Digital KYC Verified', 'code': 'KYC_VERIFIED', 'status': 'COMPLETED', 'timestamp': 'Yesterday, 10:33 AM', 'detail': 'GSTIN and DPDP consent verified digitally.'},
                {'name': 'Feasibility & Dispatch', 'code': 'FEASIBILITY_DISPATCH', 'status': 'COMPLETED', 'timestamp': 'Yesterday, 03:15 PM', 'detail': 'Fibre port assigned; Wi-Fi 6 router dispatched.'},
                {'name': 'Technician Assigned', 'code': 'TECHNICIAN_ASSIGNED', 'status': 'IN_PROGRESS', 'timestamp': 'Today, 09:00 AM', 'detail': 'Engineer Ramesh Kumar (+91 98401 22334) visiting tomorrow, 11:00 AM.'},
                {'name': 'Service Activated', 'code': 'ACTIVATED', 'status': 'PENDING', 'timestamp': 'Est. 2 days', 'detail': 'Speed test & single unified billing start.'}
            ],
            'technician': {
                'name': 'Ramesh Kumar',
                'phone': '+91 98401 22334',
                'badge_id': 'AB-ENG-491',
                'slot': 'Tomorrow, 11:00 AM - 01:00 PM',
                'pin': '8492'
            }
        }

    def create_order(self, order_data: dict):
        order_num = f"VS-2026-{uuid.uuid4().hex[:5].upper()}"
        install_days = order_data.get('estimated_install_days', 3)
        est_activation = (datetime.now() + timedelta(days=install_days)).strftime("%d %b %Y")

        new_order = {
            'order_id': order_num,
            'business_name': order_data.get('business_name', 'My Business'),
            'contact_name': order_data.get('contact_name', 'Business Owner'),
            'contact_phone': order_data.get('contact_phone', '+91 98000 00000'),
            'city': order_data.get('city', 'Tier 1 City'),
            'bundle_name': order_data.get('bundle_name', 'Custom Vyapar Pack'),
            'monthly_amount_inr': order_data.get('monthly_amount_inr', 1999),
            'current_stage': 'FEASIBILITY_DISPATCH',
            'stage_index': 2,
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'estimated_activation_date': est_activation,
            'stages': [
                {'name': 'Order Placed', 'code': 'ORDER_PLACED', 'status': 'COMPLETED', 'timestamp': 'Just now', 'detail': 'Bundle confirmed on VyaparSetu.'},
                {'name': 'Digital KYC Verified', 'code': 'KYC_VERIFIED', 'status': 'COMPLETED', 'timestamp': 'Just now', 'detail': 'Registry validation & DPDP consent approved.'},
                {'name': 'Feasibility & Dispatch', 'code': 'FEASIBILITY_DISPATCH', 'status': 'IN_PROGRESS', 'timestamp': 'In Progress', 'detail': f'Automated line check initiated (SLA: {install_days} days).'},
                {'name': 'Technician Assigned', 'code': 'TECHNICIAN_ASSIGNED', 'status': 'PENDING', 'timestamp': 'Pending', 'detail': 'Field technician appointment booking.'},
                {'name': 'Service Activated', 'code': 'ACTIVATED', 'status': 'PENDING', 'timestamp': f'Est. {est_activation}', 'detail': 'Final speed check and unified invoicing.'}
            ],
            'technician': {
                'name': 'Suresh Patel',
                'phone': '+91 98765 43210',
                'badge_id': 'AB-TECH-108',
                'slot': f"Within {install_days} days",
                'pin': '3910'
            }
        }
        self.orders[order_num] = new_order
        return new_order

    def get_order(self, order_id: str):
        return self.orders.get(order_id.strip().upper())


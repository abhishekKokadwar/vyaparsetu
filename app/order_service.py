import uuid
import re
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any
from app.catalog_engine import CatalogEngine

# Milestone definitions in strict progression
MILESTONE_STAGES = [
    {
        'code': 'ORDER_PLACED',
        'name': 'Order Placed & Quote Locked',
        'name_hi': 'ऑर्डर स्वीकार और कोटेशन लॉक',
        'detail': 'Single-bill bundle configured and payment schedule confirmed on VyaparSetu.',
        'detail_hi': 'व्यापारसेतु पर सिंगल-बिल बंडल कन्फ़र्म और भुगतान शेड्यूल लॉक किया गया।'
    },
    {
        'code': 'KYC_VERIFIED',
        'name': 'Digital KYC & DPDP Verified',
        'name_hi': 'डिजिटल KYC और DPDP सत्यापन पूर्ण',
        'detail': 'National registry (GSTIN/Udyam) cross-validated and affirmative consent logged.',
        'detail_hi': 'राष्ट्रीय रजिस्ट्री (GSTIN/Udyam) और सहमति का सफल सत्यापन।'
    },
    {
        'code': 'FEASIBILITY_DISPATCH',
        'name': 'Feasibility Check & Hardware Dispatched',
        'name_hi': 'फ़िजिबिलिटी चेक और हार्डवेयर डिस्पैच',
        'detail': 'Optical fiber port reserved; CPE business router and SIMs dispatched via BlueDart.',
        'detail_hi': 'ऑप्टिकल फ़ाइबर पोर्ट रिज़र्व; बिज़नेस राउटर और सिम कूरियर द्वारा डिस्पैच।'
    },
    {
        'code': 'TECHNICIAN_ASSIGNED',
        'name': 'Field Engineer Assigned & Scheduled',
        'name_hi': 'फ़ील्ड इंजीनियर नियुक्त और अपॉइंटमेंट तय',
        'detail': 'Dedicated Airtel enterprise field engineer assigned with confirmed site visit slot.',
        'detail_hi': 'एयरटेल एंटरप्राइज इंजीनियर नियुक्त — निर्धारित विज़िट स्लॉट तय।'
    },
    {
        'code': 'INSTALLATION_IN_PROGRESS',
        'name': 'Site Installation & Fiber Splicing',
        'name_hi': 'साइट इंस्टॉलेशन और फ़ाइबर कनेक्शन',
        'detail': 'On-site fiber drop cable laying, optical power calibration, and Wi-Fi 6 router setup.',
        'detail_hi': 'फ़ाइबर केबल बिछाना, सिग्नल कैलिब्रेशन और वाई-फ़ाई 6 राउटर कॉन्फ़िगरेशन जारी।'
    },
    {
        'code': 'SERVICE_ACTIVATED',
        'name': 'Service Activated & Live Handover',
        'name_hi': 'सेवा सक्रिय — लाइव हैंडओवर पूर्ण',
        'detail': 'Bandwidth throughput test passed with 99.5%+ SLA; unified monthly bill cycle started.',
        'detail_hi': 'स्पीड और 99.5%+ SLA टेस्ट पास — सिंगल बिलिंग चक्र लाइव।'
    }
]

class OrderService:
    """
    Phase 5: Self-Service Order Fulfillment & Live Tracker Engine (Zero-Chase Delivery).
    Implements:
      1. Catalog-derived dynamic installation SLA calculation (AirFiber=2d, Fibre=5d, Leased Line=21d).
      2. 6-stage milestone state machine with strict sequential advancement.
      3. Field engineer dispatch management and 4-digit installation PIN authentication.
      4. Customer self-service visit window rescheduling.
      5. Zero-chase proactive notifications simulation (WhatsApp & SMS) with live countdown timers.
      6. Fast in-memory multi-indexing (order ID & customer phone).
    """
    def __init__(self, catalog: Optional[CatalogEngine] = None):
        self.catalog = catalog or CatalogEngine()
        self.orders: Dict[str, dict] = {}
        self.phone_index: Dict[str, List[str]] = {}
        self._seed_sample_orders()

    def _normalize_phone(self, phone: str) -> str:
        clean = re.sub(r'[^0-9]', '', str(phone))
        if len(clean) > 10:
            clean = clean[-10:]
        return clean

    def calculate_bundle_sla(self, product_ids: List[str]) -> int:
        """
        Dynamically calculates overall installation SLA duration in days
        as max(typical_install_days) across all products in the bundle.
        """
        if not product_ids:
            return 3
        days = []
        for pid in product_ids:
            p = self.catalog.get_product(pid)
            if p and 'typical_install_days' in p:
                days.append(int(p['typical_install_days']))
        return max(days) if days else 3

    def _seed_sample_orders(self):
        """Pre-seeds realistic sample orders in diverse stages for immediate demo"""
        sample_id = "VS-2026-90412"
        now = datetime.now()
        
        stages = []
        for i, m in enumerate(MILESTONE_STAGES):
            if i < 3:
                status = 'COMPLETED'
                time_str = (now - timedelta(hours=(3-i)*4)).strftime("%d %b, %I:%M %p")
            elif i == 3:
                status = 'IN_PROGRESS'
                time_str = now.strftime("%d %b, %I:%M %p")
            else:
                status = 'PENDING'
                time_str = f"Est. {(now + timedelta(days=i-2)).strftime('%d %b')}"

            stages.append({
                'code': m['code'],
                'name': m['name'],
                'name_hi': m['name_hi'],
                'status': status,
                'timestamp': time_str,
                'detail': m['detail'],
                'detail_hi': m['detail_hi']
            })

        order = {
            'order_id': sample_id,
            'business_name': 'Balaji Dental Clinic',
            'contact_name': 'Dr. Balaji Rao',
            'contact_phone': '+91 98450 12345',
            'city': 'Bengaluru',
            'bundle_name': 'Vyapar Professional Suite',
            'monthly_amount_inr': 2522,
            'selected_products': ['P02', 'P11', 'P16', 'P17', 'P22'],
            'estimated_install_days': 5,
            'current_stage_code': 'TECHNICIAN_ASSIGNED',
            'stage_index': 3,
            'created_at': (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M"),
            'estimated_activation_date': (now + timedelta(days=2)).strftime("%d %b %Y"),
            'stages': stages,
            'technician': {
                'name': 'Ramesh Kumar',
                'phone': '+91 98401 22334',
                'badge_id': 'AB-ENG-491',
                'slot': 'Tomorrow, 10:00 AM - 01:00 PM',
                'installation_pin': '8492'
            },
            'courier': {
                'awb_number': 'BLUEDART-8891234',
                'courier_name': 'BlueDart Express',
                'equipment': 'Airtel Wi-Fi 6 Business Gateway + 4G Dongle',
                'dispatch_status': 'Out for delivery'
            }
        }
        self.orders[sample_id] = order
        clean_phone = self._normalize_phone(order['contact_phone'])
        self.phone_index.setdefault(clean_phone, []).append(sample_id)

    def create_order(self, order_data: dict) -> dict:
        """
        Creates a new trackable order with catalog-derived dynamic SLA,
        assigned field engineer, installation PIN, and 6-stage milestone tracker.
        """
        order_num = f"VS-2026-{uuid.uuid4().hex[:5].upper()}"
        prods = order_data.get('selected_products', [])
        
        # Dynamic SLA calculation from products with strict catalog floor enforcement
        catalog_sla = self.calculate_bundle_sla(prods)
        if 'estimated_install_days' in order_data and int(order_data['estimated_install_days']) > 0:
            # Enforce catalog SLA floor: cannot promise faster delivery than physical infrastructure allows
            install_days = max(int(order_data['estimated_install_days']), catalog_sla)
        else:
            install_days = catalog_sla

        now = datetime.now()
        est_activation = (now + timedelta(days=install_days)).strftime("%d %b %Y")
        pin = f"{uuid.uuid4().int % 9000 + 1000}" # secure 4-digit PIN

        stages = []
        for i, m in enumerate(MILESTONE_STAGES):
            if i == 0:
                status = 'COMPLETED'
                t_str = now.strftime("%d %b, %I:%M %p")
            elif i == 1:
                status = 'COMPLETED'
                t_str = now.strftime("%d %b, %I:%M %p")
            elif i == 2:
                status = 'IN_PROGRESS'
                t_str = now.strftime("%d %b, %I:%M %p")
            else:
                status = 'PENDING'
                t_str = f"Within {install_days} days"

            stages.append({
                'code': m['code'],
                'name': m['name'],
                'name_hi': m['name_hi'],
                'status': status,
                'timestamp': t_str,
                'detail': m['detail'],
                'detail_hi': m['detail_hi']
            })

        order = {
            'order_id': order_num,
            'business_name': order_data.get('business_name', 'My Business'),
            'contact_name': order_data.get('contact_name', 'Business Owner'),
            'contact_phone': order_data.get('contact_phone', '+91 98000 00000'),
            'city': order_data.get('city', 'Tier 1 City'),
            'bundle_name': order_data.get('bundle_name', 'Custom Vyapar Pack'),
            'monthly_amount_inr': int(order_data.get('monthly_amount_inr', 1999)),
            'selected_products': prods,
            'estimated_install_days': install_days,
            'current_stage_code': 'FEASIBILITY_DISPATCH',
            'stage_index': 2,
            'created_at': now.strftime("%Y-%m-%d %H:%M"),
            'estimated_activation_date': est_activation,
            'stages': stages,
            'technician': {
                'name': 'Suresh Patel',
                'phone': '+91 98765 43210',
                'badge_id': 'AB-TECH-108',
                'slot': f"Within {install_days} days (10:00 AM - 01:00 PM)",
                'installation_pin': pin
            },
            'courier': {
                'awb_number': f"BD-{uuid.uuid4().hex[:8].upper()}",
                'courier_name': 'BlueDart Express',
                'equipment': 'Airtel Enterprise Gateway & POS Terminal',
                'dispatch_status': 'In Transit'
            }
        }

        self.orders[order_num] = order
        clean_phone = self._normalize_phone(order['contact_phone'])
        self.phone_index.setdefault(clean_phone, []).append(order_num)
        return order

    def get_order(self, order_id: str) -> Optional[dict]:
        """Retrieves order with real-time countdown telemetry"""
        clean_id = order_id.strip().upper() if order_id else ""
        order = self.orders.get(clean_id)
        if not order:
            return None

        # Add live countdown telemetry
        order_copy = dict(order)
        order_copy['countdown'] = self._compute_countdown(order)
        return order_copy

    def lookup_by_phone(self, phone: str) -> List[dict]:
        """Looks up orders associated with a customer phone number"""
        clean_phone = self._normalize_phone(phone)
        order_ids = self.phone_index.get(clean_phone, [])
        return [self.get_order(oid) for oid in order_ids if self.get_order(oid)]

    def advance_stage(self, order_id: str, technician_pin: Optional[str] = None) -> dict:
        """
        Advances order to the next milestone in strict sequence.
        Requires valid 4-digit installation_pin to activate service (final stage).
        """
        clean_id = order_id.strip().upper()
        order = self.orders.get(clean_id)
        if not order:
            return {'status': 'ERROR', 'message': f"Order '{order_id}' not found."}

        current_idx = order['stage_index']
        if current_idx >= len(MILESTONE_STAGES) - 1:
            return {'status': 'ALREADY_ACTIVATED', 'message': 'Order is already fully activated.'}

        next_idx = current_idx + 1
        next_stage = MILESTONE_STAGES[next_idx]

        # Final activation requires technician PIN match
        if next_stage['code'] == 'SERVICE_ACTIVATED':
            expected_pin = order['technician']['installation_pin']
            if not technician_pin or str(technician_pin).strip() != str(expected_pin).strip():
                return {
                    'status': 'PIN_AUTHENTICATION_FAILED',
                    'message': 'Invalid installation PIN. Please request the 4-digit PIN from the business owner.'
                }

        # Update stage statuses
        now_str = datetime.now().strftime("%d %b, %I:%M %p")
        order['stages'][current_idx]['status'] = 'COMPLETED'
        order['stages'][current_idx]['timestamp'] = now_str

        order['stages'][next_idx]['status'] = 'COMPLETED' if next_idx == len(MILESTONE_STAGES) - 1 else 'IN_PROGRESS'
        order['stages'][next_idx]['timestamp'] = now_str

        order['stage_index'] = next_idx
        order['current_stage_code'] = next_stage['code']

        return {
            'status': 'SUCCESS',
            'order_id': clean_id,
            'previous_stage': MILESTONE_STAGES[current_idx]['code'],
            'new_stage': next_stage['code'],
            'stage_index': next_idx,
            'message': f"Order advanced to '{next_stage['name']}'."
        }

    def reschedule_appointment(self, order_id: str, new_slot: str, days_extension: int = 1) -> dict:
        """
        Allows the MSME customer to reschedule the site visit window without cancelling.
        Dynamically recalculates estimated activation date.
        """
        clean_id = order_id.strip().upper()
        order = self.orders.get(clean_id)
        if not order:
            return {'status': 'ERROR', 'message': f"Order '{order_id}' not found."}

        old_slot = order['technician']['slot']
        order['technician']['slot'] = new_slot

        # Recalculate estimated activation date
        current_est = datetime.strptime(order['estimated_activation_date'], "%d %b %Y")
        new_est = (current_est + timedelta(days=days_extension)).strftime("%d %b %Y")
        order['estimated_activation_date'] = new_est

        # Update technician stage timestamp
        for st in order['stages']:
            if st['code'] == 'TECHNICIAN_ASSIGNED':
                st['detail'] = f"Engineer {order['technician']['name']} rescheduled visit to {new_slot}."

        return {
            'status': 'SUCCESS',
            'order_id': clean_id,
            'previous_slot': old_slot,
            'new_slot': new_slot,
            'new_activation_date': new_est,
            'message': f"Appointment successfully rescheduled to '{new_slot}'."
        }

    def _compute_countdown(self, order: dict) -> dict:
        """Computes hours/days remaining and percentage completed"""
        total_stages = len(MILESTONE_STAGES)
        current_idx = order.get('stage_index', 0)
        progress_pct = int(((current_idx + 1) / total_stages) * 100)

        # Parse activation date
        try:
            target_dt = datetime.strptime(order['estimated_activation_date'], "%d %b %Y")
            now = datetime.now()
            diff = target_dt - now
            days_rem = max(0, diff.days)
            hours_rem = max(0, int(diff.total_seconds() // 3600))
        except Exception:
            days_rem = 2
            hours_rem = 48

        return {
            'days_remaining': days_rem,
            'hours_remaining': hours_rem,
            'progress_percent': min(100, progress_pct),
            'on_track': True if current_idx >= 2 else True,
            'is_completed': current_idx == total_stages - 1
        }

    def get_order_notifications(self, order_id: str) -> List[dict]:
        """
        Returns simulated proactive WhatsApp & SMS notification events
        sent to the business owner, preventing status chase calls.
        """
        order = self.get_order(order_id)
        if not order:
            return []

        notifications = []
        c_name = order['contact_name']
        b_name = order['bundle_name']
        o_id = order['order_id']
        t_name = order['technician']['name']
        t_phone = order['technician']['phone']
        pin = order['technician']['installation_pin']

        curr_idx = order['stage_index']

        if curr_idx >= 0:
            notifications.append({
                'channel': 'WhatsApp & SMS',
                'milestone': 'ORDER_PLACED',
                'title': 'Order Confirmed',
                'timestamp': order['created_at'],
                'message_en': f"Namaste {c_name}! Your order {o_id} for '{b_name}' is confirmed. Track live: https://vyaparsetu.airtel.in/track/{o_id}",
                'message_hi': f"नमस्ते {c_name}! '{b_name}' के लिए आपका ऑर्डर {o_id} कन्फ़र्म हो गया है। लाइव ट्रैक करें: https://vyaparsetu.airtel.in/track/{o_id}"
            })

        if curr_idx >= 1:
            notifications.append({
                'channel': 'WhatsApp',
                'milestone': 'KYC_VERIFIED',
                'title': 'KYC Approved',
                'timestamp': order['stages'][1]['timestamp'],
                'message_en': f"Instant KYC Approval! Your business registration was verified digitally. Zero paperwork required.",
                'message_hi': f"डिजिटल KYC स्वीकृत! आपके बिज़नेस दस्तावेज़ ऑनलाइन सत्यापित हो गए हैं। कोई कागज़ी भागदौड़ नहीं।"
            })

        if curr_idx >= 2:
            awb = order['courier']['awb_number']
            notifications.append({
                'channel': 'WhatsApp & SMS',
                'milestone': 'FEASIBILITY_DISPATCH',
                'title': 'Hardware Dispatched',
                'timestamp': order['stages'][2]['timestamp'],
                'message_en': f"Your Airtel Enterprise Gateway & POS terminal are dispatched (Tracking: {awb}). Delivery in progress.",
                'message_hi': f"आपका एयरटेल बिज़नेस गेटवे और POS टर्मिनल डिस्पैच हो गया है (ट्रैकिंग: {awb})।"
            })

        if curr_idx >= 3:
            slot = order['technician']['slot']
            notifications.append({
                'channel': 'WhatsApp',
                'milestone': 'TECHNICIAN_ASSIGNED',
                'title': 'Technician Scheduled',
                'timestamp': order['stages'][3]['timestamp'],
                'message_en': f"Engineer {t_name} ({t_phone}) will visit during {slot}. Your Secret Verification PIN is: {pin}.",
                'message_hi': f"इंजीनियर {t_name} ({t_phone}) {slot} पर विज़िट करेंगे। आपका गुप्त वेरिफिकेशन PIN है: {pin}।"
            })

        if curr_idx >= 5:
            notifications.append({
                'channel': 'WhatsApp & SMS',
                'milestone': 'SERVICE_ACTIVATED',
                'title': 'Service Activated',
                'timestamp': order['stages'][5]['timestamp'],
                'message_en': f"Congratulations! Your '{b_name}' is LIVE with 99.5%+ SLA. Welcome to Airtel VyaparSetu!",
                'message_hi': f"बधाई हो! आपकी '{b_name}' सेवा 99.5%+ SLA के साथ सक्रिय हो गई है। एयरटेल व्यापारसेतु में आपका स्वागत है!"
            })

        return notifications

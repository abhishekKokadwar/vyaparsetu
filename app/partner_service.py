import pandas as pd
import os
import re
from typing import Dict, List, Optional, Any
from app.registry_service import RegistryService

LEADS_PATH = os.path.join(os.path.dirname(__file__), '..', 'udyam_digital_data', 'smb_leads.csv')

DROP_PLAYBOOKS = {
    'BUDGET_MISMATCH': {
        'playbook_code': 'PB_FLEX_PRICING',
        'category_name': 'Budget Mismatch / High Price',
        'category_name_hi': 'बजट या कीमत की समस्या',
        'recommended_action': 'Offer Down-Sized Pack (Biz Fibre 100 + Cloud POS at ₹1,598/mo) with zero setup fee',
        'recommended_action_hi': 'कम बजट वाला व्यापार पैक (बिज़ फ़ाइबर + POS मात्र ₹1,598/माह) बिना सेटअप शुल्क के पेश करें',
        'default_bundle': 'P01;P19',
        'template_en': "Namaste {contact_name}! We noticed our enterprise package was outside your monthly budget. We created the 'Vyapar Starter Pack' for {business_name} at just ₹1,598/month with ZERO installation fee. View & activate in 1 click: {link}",
        'template_hi': "नमस्ते {contact_name}! {business_name} के लिए हमने खास 'व्यापार स्टार्टर पैक' तैयार किया है — हाई-स्पीड इंटरनेट और बिलिंग मात्र ₹1,598/माह में, बिना किसी इंस्टॉलेशन शुल्क के। 1-क्लिक में शुरू करें: {link}"
    },
    'KYC_DOC_FRICTION': {
        'playbook_code': 'PB_SMART_KYC_ASSIST',
        'category_name': 'KYC Friction / Paperwork Hassle',
        'category_name_hi': 'दस्तावेज़ या कागज़ी कार्रवाई की परेशानी',
        'recommended_action': 'Trigger 1-Sitting Assisted Digital KYC with instant GSTIN/Udyam pre-fill',
        'recommended_action_hi': '1-सिटिंग डिजिटल KYC लिंक भेजें — सरकारी रजिस्ट्री से स्वतः डेटा प्री-फिल',
        'default_bundle': 'P01;P19;P07',
        'template_en': "Hello {contact_name}! No paperwork needed anymore. With Airtel VyaparSetu, complete your business verification in 2 minutes using just your GSTIN or Udyam number online. Complete here: {link}",
        'template_hi': "नमस्ते {contact_name}! अब कागज़ात जमा करने की कोई ज़रूरत नहीं। अपने GSTIN या उद्यम नंबर से मात्र 2 मिनट में ऑनलाइन वेरिफिकेशन पूरा करें: {link}"
    },
    'SALES_INACTIVITY': {
        'playbook_code': 'PB_PARTNER_DISPATCH',
        'category_name': 'Sales Inactivity / No Follow-Up',
        'category_name_hi': 'फ़ॉलो-अप की कमी / सेल्स इनएक्टिविटी',
        'recommended_action': 'Assign dedicated channel partner with 24-hr visit SLA and ₹2,500 win-back bounty',
        'recommended_action_hi': 'स्थानीय पार्टनर को 24-घंटे विज़िट SLA और ₹2,500 बाउंस-बैक बोनस के साथ असाइन करें',
        'default_bundle': 'P02;P11;P16',
        'template_en': "Apologies {contact_name} for the delay earlier. Your dedicated Airtel Relationship Manager has been assigned to visit {business_name} tomorrow. Schedule your preferred visit time: {link}",
        'template_hi': "नमस्ते {contact_name}, पूर्व में देरी के लिए क्षमा चाहते हैं। {business_name} के लिए आपके व्यक्तिगत एयरटेल मैनेजर नियुक्त किए गए हैं। विज़िट का समय चुनें: {link}"
    },
    'TIME_CONSTRAINT': {
        'playbook_code': 'PB_SELF_SERVE_QUOTE',
        'category_name': 'Time Constraint / Store Visit Friction',
        'category_name_hi': 'समय की कमी / दुकान पर विज़िट की समस्या',
        'recommended_action': 'Send WhatsApp 1-Click Transparent Checkout link (Zero physical store visit required)',
        'recommended_action_hi': 'व्हाट्सएप 1-क्लिक चेकआउट लिंक भेजें — दुकान छोड़ने की कोई ज़रूरत नहीं',
        'default_bundle': 'P04;P19;P23',
        'template_en': "Hi {contact_name}! Don't leave your shop counter. Get Airtel Biz 5G AirFiber + Cloud POS delivered to {business_name} in 48 hours. Confirm your order in 60 seconds: {link}",
        'template_hi': "नमस्ते {contact_name}! दुकान छोड़कर कहीं जाने की ज़रूरत नहीं। एयरटेल बिज़ 5G एयरफ़ाइबर 48 घंटे में आपकी दुकान पर लाइव। 60 सेकंड में ऑर्डर करें: {link}"
    },
    'COMPETITIVE_CONFUSION': {
        'playbook_code': 'PB_ROI_BENCHMARK',
        'category_name': 'Competitor Comparison / Complex Quote',
        'category_name_hi': 'प्रतियोगी तुलना / जटिल कोटेशन',
        'recommended_action': 'Send Unorganized Vendor vs Airtel ROI benchmark proving 31% savings + 18% GST ITC',
        'recommended_action_hi': 'लोकल वेंडर बनाम एयरटेल ROI रिपोर्ट भेजें — 31% सीधी बचत और 18% GST इनपुट क्रेडिट',
        'default_bundle': 'P02;P09;P23',
        'template_en': "Dear {contact_name}, why juggle 4 different local vendors? Airtel VyaparSetu gives {business_name} broadband, CCTV, and billing under ONE bill, saving ₹18,000/year. View savings proof: {link}",
        'template_hi': "नमस्ते {contact_name}, 4 अलग-अलग वेंडरों के झंझट से बचें! एयरटेल व्यापारसेतु पर ब्रॉडबैंड, CCTV और बिलिंग एक ही बिल में पाएं और हर साल ₹18,000 बचाएं: {link}"
    }
}

class PartnerService:
    """
    Phase 6: Channel Partner Portal & AI Propensity Salvage Engine.
    Implements:
      1. Multi-factor AI propensity-to-salvage mathematical scoring (0-100%).
      2. Root-cause drop taxonomy with automated micro-intervention playbooks.
      3. Bilingual WhatsApp/SMS win-back pitch synthesis.
      4. Channel partner commission & bounty calculation.
      5. Portfolio recoverable ARR & commission pool analytics.
      6. Batch salvage campaign simulation with conversion tracking.
    """
    def __init__(self, leads_path: str = LEADS_PATH):
        self.leads_path = leads_path
        self.df = pd.read_csv(self.leads_path)
        self.scored_leads = self._compute_propensity_scores()
        self._lead_index: Dict[str, dict] = {}
        self._build_index()

    def _categorize_drop_reason(self, drop_reason: str) -> str:
        d = str(drop_reason).lower() if pd.notna(drop_reason) else ""
        if any(w in d for w in ['price', 'expensive', 'budget', 'cost', 'discount', 'high']):
            return 'BUDGET_MISMATCH'
        elif any(w in d for w in ['paperwork', 'document', 'gst', 'kyc', 'proof', 'aadhaar', 'hassle']):
            return 'KYC_DOC_FRICTION'
        elif any(w in d for w in ['visit', 'time', 'busy', 'schedule', 'counter']):
            return 'TIME_CONSTRAINT'
        elif any(w in d for w in ['competitor', 'bundle', 'complex', 'confus', 'tata', 'jio', 'local']):
            return 'COMPETITIVE_CONFUSION'
        else:
            return 'SALES_INACTIVITY'

    def _compute_propensity_scores(self) -> pd.DataFrame:
        leads = self.df[self.df['outcome'] == 'Dropped'].copy()

        def score_lead(row):
            score = 25 # baseline base score
            
            # 1. Funnel Stage Progression Weight (W_stage)
            stage = str(row.get('stage_reached', '')).strip()
            if stage == 'KYC complete':
                score += 30
            elif stage == 'Quote accepted':
                score += 25
            elif stage == 'Needs assessed':
                score += 15
            elif stage == 'Contacted':
                score += 5

            # 2. Registrations Weight (W_registrations)
            if str(row.get('has_gstin')).upper() == 'Y':
                score += 20
            if str(row.get('has_udyam')).upper() == 'Y':
                score += 10

            # 3. Monthly Spend Weight (W_spend)
            spend = row.get('monthly_telecom_spend_inr', 0)
            if pd.notna(spend):
                try:
                    s_val = float(spend)
                    if s_val >= 5000:
                        score += 15
                    elif s_val >= 2000:
                        score += 10
                except ValueError:
                    pass

            # 4. Workforce Scale Weight (W_scale)
            emp = row.get('employee_count', 1)
            if pd.notna(emp):
                try:
                    e_val = int(emp)
                    if e_val >= 5:
                        score += 10
                except ValueError:
                    pass

            # 5. Drop Friction Penalties (P_friction)
            drop = str(row.get('drop_reason', '')).lower()
            if 'wrong or invalid number' in drop:
                return 10 # immediate penalty floor
            elif 'out of service area' in drop:
                return 12
            elif 'not interested' in drop:
                score = max(15, score - 20)
            elif 'site not feasible' in drop:
                # Infeasible for wired fibre; salvageable only via Airtel 5G AirFiber FWA
                score = min(score, 52)
            elif 'unreachable' in drop:
                score = max(15, score - 15)
            elif 'locked in' in drop:
                score = max(15, score - 10)

            return min(98, max(10, score))

        leads['propensity_score'] = leads.apply(score_lead, axis=1)
        leads['drop_category'] = leads['drop_reason'].apply(self._categorize_drop_reason)
        
        # Propensity tier
        def get_tier(score):
            if score >= 70:
                return 'HIGH'
            elif score >= 45:
                return 'MEDIUM'
            else:
                return 'LOW'

        leads['propensity_tier'] = leads['propensity_score'].apply(get_tier)
        return leads.sort_values(by='propensity_score', ascending=False)

    def _build_index(self):
        """Builds fast in-memory dictionary for sub-millisecond retrieval by lead_id"""
        for _, r in self.scored_leads.iterrows():
            lid = str(r['lead_id']).strip().upper()
            self._lead_index[lid] = r.to_dict()

    @staticmethod
    def mask_contact_name(name: str) -> str:
        """Masks personal contact names for DPDP Act 2023 compliance: 'Neha Banerjee' -> 'Neha B.'"""
        if not name or not str(name).strip():
            return "Business Owner"
        parts = str(name).strip().split()
        if len(parts) == 1:
            first = parts[0]
            return f"{first[0]}***" if len(first) > 2 else first
        first = parts[0]
        last_initial = parts[-1][0].upper()
        return f"{first} {last_initial}."

    def get_commission_estimate(self, segment: str, monthly_bundle_inr: int = 2500) -> dict:
        """
        Calculates channel partner economic incentives:
        Fixed win-back bounty + 15% annual recurring revenue share.
        """
        seg = str(segment).lower()
        if 'micro' in seg:
            bounty = 1500
        elif 'prof' in seg:
            bounty = 2500
        elif 'multi' in seg:
            bounty = 3500
        else: # mfg
            bounty = 3500

        annual_contract_value = monthly_bundle_inr * 12
        rev_share = int(annual_contract_value * 0.15)
        total_payout = bounty + rev_share

        return {
            'fixed_bounty_inr': bounty,
            'rev_share_percent': 15,
            'first_year_rev_share_inr': rev_share,
            'total_partner_payout_inr': total_payout
        }

    def synthesize_win_back_pitch(self, lead_data: dict) -> dict:
        """
        Synthesizes personalized, bilingual WhatsApp & SMS recovery pitches
        with 1-click self-serve links.
        """
        drop_cat = lead_data.get('drop_category', 'SALES_INACTIVITY')
        playbook = DROP_PLAYBOOKS.get(drop_cat, DROP_PLAYBOOKS['SALES_INACTIVITY'])

        lid = lead_data.get('lead_id', 'LEAD-001')
        b_name = lead_data.get('business_name', 'Your Business')
        c_name = lead_data.get('contact_name', 'Business Owner')
        bundle_code = playbook['default_bundle']
        link = f"https://vyaparsetu.airtel.in/salvage/{lid}?bundle={bundle_code}"

        msg_en = playbook['template_en'].format(
            contact_name=c_name,
            business_name=b_name,
            link=link
        )
        msg_hi = playbook['template_hi'].format(
            contact_name=c_name,
            business_name=b_name,
            link=link
        )

        return {
            'playbook_code': playbook['playbook_code'],
            'category_name': playbook['category_name'],
            'category_name_hi': playbook['category_name_hi'],
            'recommended_action': playbook['recommended_action'],
            'recommended_action_hi': playbook['recommended_action_hi'],
            'one_click_link': link,
            'pitch_en': msg_en,
            'pitch_hi': msg_hi
        }

    def get_dropped_leads(
        self,
        limit: int = 20,
        offset: int = 0,
        segment: Optional[str] = None,
        city_tier: Optional[int] = None,
        min_score: Optional[int] = None,
        drop_category: Optional[str] = None,
        propensity_tier: Optional[str] = None
    ) -> List[dict]:
        """Filtered retrieval of dropped leads with pagination and commission metadata"""
        subset = self.scored_leads

        if segment:
            seg_lower = segment.lower().strip()
            if seg_lower in ['micro', 'retail']:
                subset = subset[subset['segment'].str.lower().str.contains('micro', na=False)]
            elif seg_lower in ['prof', 'professional', 'office', 'offices']:
                subset = subset[subset['segment'].str.lower().str.contains('prof', na=False)]
            elif seg_lower in ['multi', 'chain', 'sites', 'multi-site']:
                subset = subset[subset['segment'].str.lower().str.contains('multi', na=False)]
            elif seg_lower in ['mfg', 'manufactur', 'factory', 'plant']:
                subset = subset[subset['segment'].str.lower().str.contains('manufactur', na=False)]
            else:
                subset = subset[subset['segment'].str.lower().str.contains(seg_lower, na=False)]
        if city_tier:
            subset = subset[subset['city_tier'] == int(city_tier)]
        if min_score:
            subset = subset[subset['propensity_score'] >= int(min_score)]
        if drop_category:
            subset = subset[subset['drop_category'] == drop_category.upper()]
        if propensity_tier:
            subset = subset[subset['propensity_tier'] == propensity_tier.upper()]

        total_matching = len(subset)
        sliced = subset.iloc[offset:offset+limit]

        results = []
        for _, r in sliced.iterrows():
            comm = self.get_commission_estimate(r['segment'], 2500)
            lead_dict = {
                'lead_id': r['lead_id'],
                'business_name': r['business_name'],
                'contact_name': self.mask_contact_name(r.get('contact_name', 'Business Owner')),
                'contact_name_masked': self.mask_contact_name(r.get('contact_name', 'Business Owner')),
                'contact_role': r.get('contact_role', 'Owner'),
                'segment': r['segment'],
                'city': r['city'],
                'city_tier': int(r['city_tier']),
                'has_gstin': str(r['has_gstin']).upper() == 'Y',
                'has_udyam': str(r.get('has_udyam', 'N')).upper() == 'Y',
                'gstin': RegistryService.mask_gstin(str(r['gstin'])) if pd.notna(r['gstin']) and str(r['gstin']).strip() else '',
                'gstin_masked': RegistryService.mask_gstin(str(r['gstin'])) if pd.notna(r['gstin']) and str(r['gstin']).strip() else '',
                'employee_count': int(r['employee_count']) if pd.notna(r['employee_count']) else 1,
                'monthly_spend': int(r['monthly_telecom_spend_inr']) if pd.notna(r['monthly_telecom_spend_inr']) else 0,
                'stage_reached': r['stage_reached'],
                'drop_reason': r['drop_reason'],
                'drop_category': r['drop_category'],
                'propensity_score': int(r['propensity_score']),
                'propensity_tier': r['propensity_tier'],
                'recommended_action': DROP_PLAYBOOKS.get(r['drop_category'], DROP_PLAYBOOKS['SALES_INACTIVITY'])['recommended_action'],
                'partner_commission_inr': comm['total_partner_payout_inr']
            }
            results.append(lead_dict)

        return results

    def get_lead_detail(self, lead_id: str) -> Optional[dict]:
        """Returns deep profile, score breakdown, and personalized pitch for a single lead"""
        clean_id = lead_id.strip().upper()
        raw = self._lead_index.get(clean_id)
        if not raw:
            return None

        comm = self.get_commission_estimate(raw['segment'], 2500)
        pitch = self.synthesize_win_back_pitch(raw)

        return {
            'lead_id': raw['lead_id'],
            'business_name': raw['business_name'],
            'contact_name': raw.get('contact_name', 'Business Owner'),
            'contact_role': raw.get('contact_role', 'Owner'),
            'segment': raw['segment'],
            'city': raw['city'],
            'city_tier': int(raw['city_tier']),
            'has_gstin': str(raw['has_gstin']).upper() == 'Y',
            'has_udyam': str(raw.get('has_udyam', 'N')).upper() == 'Y',
            'employee_count': int(raw['employee_count']) if pd.notna(raw['employee_count']) else 1,
            'monthly_spend_inr': int(raw['monthly_telecom_spend_inr']) if pd.notna(raw['monthly_telecom_spend_inr']) else 0,
            'stage_reached': raw['stage_reached'],
            'drop_reason': raw['drop_reason'],
            'drop_category': raw['drop_category'],
            'propensity_score': int(raw['propensity_score']),
            'propensity_tier': raw['propensity_tier'],
            'commission': comm,
            'playbook': pitch
        }

    def get_partner_stats(self) -> dict:
        """
        Calculates macro portfolio-level salvage statistics, recoverable ARR,
        and channel partner commission incentive pools.
        """
        total_dropped = len(self.scored_leads)
        high_pool = self.scored_leads[self.scored_leads['propensity_score'] >= 70]
        med_pool = self.scored_leads[(self.scored_leads['propensity_score'] >= 45) & (self.scored_leads['propensity_score'] < 70)]
        low_pool = self.scored_leads[self.scored_leads['propensity_score'] < 45]

        n_high = len(high_pool)
        n_med = len(med_pool)
        n_low = len(low_pool)

        # Econometric model:
        # High pool converts at 35% with partner intervention
        # Medium pool converts at 15% with automated WhatsApp playbooks
        avg_monthly_bundle = 2500
        annual_per_sub = avg_monthly_bundle * 12 # ₹30,000 ARR

        recoverable_subs = int((n_high * 0.35) + (n_med * 0.15))
        potential_arr = recoverable_subs * annual_per_sub
        partner_commission_pool = int(potential_arr * 0.15) # 15% commission pool

        # Category breakdown
        cat_counts = self.scored_leads['drop_category'].value_counts().to_dict()

        return {
            'total_dropped_leads': total_dropped,
            'high_propensity_count': n_high,
            'medium_propensity_count': n_med,
            'low_propensity_count': n_low,
            'high_propensity_pct': round((n_high / total_dropped) * 100, 1),
            'projected_recoverable_subscribers': recoverable_subs,
            'projected_recoverable_arr_inr': potential_arr,
            'partner_commission_pool_inr': partner_commission_pool,
            'drop_categories_breakdown': cat_counts
        }

    def simulate_salvage_campaign(self, lead_ids: List[str], partner_id: str = "PARTNER-BENGALURU-01") -> dict:
        """
        Simulates launching a targeted salvage campaign across selected leads.
        Computes expected recovered subscribers, generated ARR, and partner earnings.
        """
        selected = [self.get_lead_detail(lid) for lid in lead_ids if self.get_lead_detail(lid)]
        if not selected:
            return {'status': 'ERROR', 'message': 'No valid leads selected for campaign.'}

        total_bounty = sum(s['commission']['fixed_bounty_inr'] for s in selected)
        total_potential_arr = len(selected) * 2500 * 12
        # Expected conversions based on propensity scores
        expected_conversions = sum((s['propensity_score'] / 100.0) * 0.45 for s in selected)
        expected_conversions = max(1, round(expected_conversions))
        expected_salvaged_arr = expected_conversions * 2500 * 12
        expected_partner_earnings = expected_conversions * 2500 + int(expected_salvaged_arr * 0.15)

        return {
            'status': 'SUCCESS',
            'partner_id': partner_id,
            'leads_targeted_count': len(selected),
            'expected_conversions': expected_conversions,
            'conversion_rate_pct': round((expected_conversions / len(selected)) * 100, 1),
            'expected_salvaged_arr_inr': expected_salvaged_arr,
            'expected_partner_earnings_inr': expected_partner_earnings,
            'dispatch_summary': f"Successfully dispatched automated personalized WhatsApp win-back campaigns to {len(selected)} high-propensity leads."
        }

import pandas as pd
import os

LEADS_PATH = os.path.join(os.path.dirname(__file__), '..', 'udyam_digital_data', 'smb_leads.csv')

class PartnerService:
    def __init__(self):
        self.df = pd.read_csv(LEADS_PATH)
        self.scored_leads = self._compute_propensity_scores()

    def _compute_propensity_scores(self):
        leads = self.df[self.df['outcome'] == 'Dropped'].copy()

        def score_lead(row):
            score = 30 # baseline
            if str(row.get('has_gstin')).upper() == 'Y':
                score += 25
            if str(row.get('has_udyam')).upper() == 'Y':
                score += 15
            
            stage = str(row.get('stage_reached', ''))
            if stage in ['Quote accepted', 'KYC complete']:
                score += 25
            elif stage == 'Needs assessed':
                score += 15
            elif stage == 'Contacted':
                score += 5

            spend = row.get('monthly_telecom_spend_inr', 0)
            if pd.notna(spend):
                if spend >= 5000:
                    score += 15
                elif spend >= 2000:
                    score += 10

            emp = row.get('employee_count', 1)
            if pd.notna(emp) and emp >= 5:
                score += 10

            # Penalize invalid numbers or outright not interested
            drop = str(row.get('drop_reason', '')).lower()
            if 'wrong or invalid number' in drop:
                score = 10
            elif 'not interested' in drop:
                score = max(15, score - 20)

            return min(98, max(12, score))

        leads['propensity_score'] = leads.apply(score_lead, axis=1)
        return leads.sort_values(by='propensity_score', ascending=False)

    def get_dropped_leads(self, limit=20, segment=None, min_score=None):
        subset = self.scored_leads
        if segment:
            subset = subset[subset['segment'].str.lower() == segment.lower()]
        if min_score:
            subset = subset[subset['propensity_score'] >= min_score]

        results = []
        for _, r in subset.head(limit).iterrows():
            results.append({
                'lead_id': r['lead_id'],
                'business_name': r['business_name'],
                'segment': r['segment'],
                'city': r['city'],
                'city_tier': int(r['city_tier']),
                'has_gstin': str(r['has_gstin']).upper() == 'Y',
                'gstin': r['gstin'] if pd.notna(r['gstin']) else '',
                'employee_count': int(r['employee_count']) if pd.notna(r['employee_count']) else 1,
                'monthly_spend': int(r['monthly_telecom_spend_inr']) if pd.notna(r['monthly_telecom_spend_inr']) else 0,
                'stage_reached': r['stage_reached'],
                'drop_reason': r['drop_reason'],
                'propensity_score': int(r['propensity_score']),
                'recommended_action': self._get_recovery_action(r['drop_reason'], r['propensity_score'])
            })
        return results

    def _get_recovery_action(self, drop_reason, score):
        d = str(drop_reason).lower()
        if 'visit' in d or 'time' in d:
            return "Send WhatsApp 1-Sitting Self-Serve Link (Zero visit required)"
        elif 'quote' in d or 'complex' in d:
            return "Share 1-Click Transparent Vyapar Pack with instant pricing"
        elif 'paperwork' in d or 'gst' in d or 'document' in d:
            return "Trigger Smart KYC Assisted Mode with automated registry lookup"
        elif 'price' in d or 'competitor' in d:
            return "Offer Vyapar Booster Pack (Fibre + Cloud POS at ₹1,598/mo)"
        else:
            return "Partner WhatsApp outreach with promotional install waiver"

    def get_partner_stats(self):
        total_dropped = len(self.scored_leads)
        high_propensity = len(self.scored_leads[self.scored_leads['propensity_score'] >= 70])
        est_recoverable_arr = high_propensity * 2500 * 12
        return {
            'total_dropped_leads': total_dropped,
            'high_propensity_salvageable': high_propensity,
            'salvageable_percentage': round(high_propensity / total_dropped * 100, 1),
            'potential_arr_inr': est_recoverable_arr,
            'commission_pool_inr': int(est_recoverable_arr * 0.12)
        }

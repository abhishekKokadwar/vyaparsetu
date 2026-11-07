import pytest
from app.partner_service import PartnerService, DROP_PLAYBOOKS

@pytest.fixture(scope="module")
def partner_service():
    return PartnerService()

def test_partner_service_initialization(partner_service):
    """Verify PartnerService loads all 4,632 dropped leads from dataset and scores them"""
    assert len(partner_service.scored_leads) == 4632
    assert 'propensity_score' in partner_service.scored_leads.columns
    assert 'drop_category' in partner_service.scored_leads.columns
    assert 'propensity_tier' in partner_service.scored_leads.columns

def test_propensity_score_bounds_and_distribution(partner_service):
    """Verify all scores are strictly bounded between 10 and 98 with valid tier distribution"""
    scores = partner_service.scored_leads['propensity_score']
    assert scores.min() >= 10
    assert scores.max() <= 98

    tiers = partner_service.scored_leads['propensity_tier'].value_counts().to_dict()
    assert 'HIGH' in tiers
    assert 'MEDIUM' in tiers
    assert 'LOW' in tiers
    assert tiers['HIGH'] > 0

def test_propensity_monotonicity_across_funnel_stages(partner_service):
    """Verify leads dropping later in the funnel have higher average recovery propensity"""
    df = partner_service.scored_leads
    mean_quote = df[df['stage_reached'] == 'Quote accepted']['propensity_score'].mean()
    mean_contacted = df[df['stage_reached'] == 'Contacted']['propensity_score'].mean()
    assert mean_quote > mean_contacted, f"Expected Quote accepted ({mean_quote}) > Contacted ({mean_contacted})"

def test_gstin_and_udyam_registration_boost(partner_service):
    """Verify registered MSMEs have higher propensity than unregistered businesses"""
    df = partner_service.scored_leads
    mean_gst = df[df['has_gstin'] == 'Y']['propensity_score'].mean()
    mean_no_gst = df[df['has_gstin'] == 'N']['propensity_score'].mean()
    assert mean_gst > mean_no_gst

def test_drop_friction_penalties(partner_service):
    """Verify invalid phone numbers receive maximum friction penalties down to floor"""
    df = partner_service.scored_leads
    invalid_leads = df[df['drop_reason'].str.lower().str.contains('wrong or invalid number', na=False)]
    assert len(invalid_leads) > 0
    for _, r in invalid_leads.iterrows():
        assert r['propensity_score'] <= 12

def test_playbook_mapping_completeness(partner_service):
    """Verify all 5 drop categories map to valid recovery playbooks with actions and copy"""
    expected_cats = ['BUDGET_MISMATCH', 'KYC_DOC_FRICTION', 'SALES_INACTIVITY', 'TIME_CONSTRAINT', 'COMPETITIVE_CONFUSION']
    for cat in expected_cats:
        assert cat in DROP_PLAYBOOKS
        pb = DROP_PLAYBOOKS[cat]
        assert 'recommended_action' in pb
        assert 'recommended_action_hi' in pb
        assert 'template_en' in pb
        assert 'template_hi' in pb
        assert 'default_bundle' in pb

def test_bilingual_win_back_pitch_synthesis(partner_service):
    """Verify personalized English and Hindi WhatsApp copy generation with dynamic links"""
    sample_lead = partner_service.get_dropped_leads(limit=1)[0]
    pitch = partner_service.synthesize_win_back_pitch(sample_lead)

    assert 'pitch_en' in pitch
    assert 'pitch_hi' in pitch
    assert 'one_click_link' in pitch
    assert sample_lead['lead_id'] in pitch['one_click_link']
    assert sample_lead['business_name'] in pitch['pitch_en']
    assert "नमस्ते" in pitch['pitch_hi']

def test_channel_partner_commission_math(partner_service):
    """Verify partner economics: fixed win-back bounty + 15% ARR revenue share"""
    # Micro bundle (₹2,500/mo): bounty ₹1,500 + 15% of ₹30,000 (₹4,500) = ₹6,000
    comm_micro = partner_service.get_commission_estimate('micro', 2500)
    assert comm_micro['fixed_bounty_inr'] == 1500
    assert comm_micro['first_year_rev_share_inr'] == 4500
    assert comm_micro['total_partner_payout_inr'] == 6000

    # Multi-site bundle (₹2,500/mo): bounty ₹3,500 + ₹4,500 = ₹8,000
    comm_multi = partner_service.get_commission_estimate('multi', 2500)
    assert comm_multi['fixed_bounty_inr'] == 3500
    assert comm_multi['total_partner_payout_inr'] == 8000

def test_lead_filtering_by_segment_and_score(partner_service):
    """Verify multi-parameter filtering by segment, tier, and propensity threshold"""
    # Filter by segment
    micro_leads = partner_service.get_dropped_leads(limit=10, segment='micro')
    assert len(micro_leads) > 0
    assert all('micro' in l['segment'].lower() for l in micro_leads)

    # Filter by high propensity (score >= 70)
    high_leads = partner_service.get_dropped_leads(limit=10, min_score=70)
    assert len(high_leads) > 0
    assert all(l['propensity_score'] >= 70 for l in high_leads)

    # Filter by city tier 2
    tier2_leads = partner_service.get_dropped_leads(limit=10, city_tier=2)
    assert len(tier2_leads) > 0
    assert all(l['city_tier'] == 2 for l in tier2_leads)

def test_batch_salvage_campaign_simulation(partner_service):
    """Verify batch campaign execution produces expected conversions and partner revenue"""
    top_leads = partner_service.get_dropped_leads(limit=5, min_score=70)
    top_ids = [l['lead_id'] for l in top_leads]

    res = partner_service.simulate_salvage_campaign(top_ids, partner_id="PARTNER-MUMBAI-05")
    assert res['status'] == 'SUCCESS'
    assert res['leads_targeted_count'] == 5
    assert res['expected_conversions'] >= 1
    assert res['expected_salvaged_arr_inr'] > 0
    assert res['expected_partner_earnings_inr'] > 0

def test_macro_portfolio_salvage_stats(partner_service):
    """Verify macro salvage portfolio calculations across all 4,632 dropped leads"""
    stats = partner_service.get_partner_stats()
    assert stats['total_dropped_leads'] == 4632
    assert stats['high_propensity_count'] > 0
    assert 18.0 <= stats['high_propensity_pct'] <= 22.0
    assert stats['medium_propensity_count'] > 0
    assert stats['projected_recoverable_subscribers'] > 0
    assert stats['projected_recoverable_arr_inr'] > 0
    assert stats['partner_commission_pool_inr'] > 0
    assert len(stats['drop_categories_breakdown']) == 5

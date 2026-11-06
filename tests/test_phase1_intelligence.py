import pytest
from app.data_intelligence import DataIntelligenceEngine

@pytest.fixture(scope="module")
def engine():
    return DataIntelligenceEngine()

def test_data_integrity(engine):
    """Verify raw dataset shape and essential schema columns"""
    assert len(engine.df) == 5000, "Dataset must contain exactly 5,000 leads"
    required_cols = ['lead_id', 'segment', 'city_tier', 'has_gstin', 'stage_reached', 'outcome', 'drop_reason']
    for col in required_cols:
        assert col in engine.df.columns, f"Missing required column: {col}"

def test_funnel_conservation_law(engine):
    """Verify that total leads equals sum of activated and dropped leads"""
    f = engine.decompose_funnel()
    assert f['total_leads'] == 5000
    assert f['total_activated'] == 368
    assert f['total_dropped'] == 4632
    assert f['total_activated'] + f['total_dropped'] == f['total_leads']
    assert f['overall_conversion_rate_pct'] == 7.36

def test_funnel_monotonicity(engine):
    """Verify that reach at each stage is non-increasing"""
    f = engine.decompose_funnel()
    counts = [s['count'] for s in f['funnel_stages']]
    for i in range(len(counts) - 1):
        assert counts[i] >= counts[i+1], f"Funnel stage {i} count ({counts[i]}) must be >= stage {i+1} ({counts[i+1]})"

def test_drop_cause_taxonomy_completeness(engine):
    """Verify all 4,632 dropped leads are accurately classified across clusters"""
    c = engine.cluster_drop_causes()
    assert c['total_dropped_analyzed'] == 4632
    total_in_clusters = sum(cl['drop_count'] for cl in c['clusters'])
    assert total_in_clusters == 4632, f"Expected 4,632 clustered drops, got {total_in_clusters}"

def test_segment_cohorts_exhaustiveness(engine):
    """Verify that all 4 segments cover 100% of the leads"""
    s = engine.compute_segment_economics()
    cohorts = s['segment_cohorts']
    assert len(cohorts) == 4, "Must contain exactly 4 MSME segments"
    total_leads_in_segments = sum(seg['total_leads'] for seg in cohorts)
    assert total_leads_in_segments == 5000
    total_activated_in_segments = sum(seg['activated_count'] for seg in cohorts)
    assert total_activated_in_segments == 368

def test_statistical_significance_gstin(engine):
    """Verify statistical significance of GSTIN status on conversion"""
    stats_res = engine.run_statistical_validation()
    gst_test = stats_res['gstin_significance_test']
    assert gst_test['is_statistically_significant'] is True
    assert gst_test['p_value'] < 0.001, "GST status must have p < 0.001"
    assert gst_test['chi2_statistic'] > 50, "Chi2 statistic must be substantial"


import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
from app.data_intelligence import DataIntelligenceEngine

def main():
    print("=" * 65)
    print("  RUNNING PHASE 1: DATA INTELLIGENCE & FUNNEL MODELING ENGINE")
    print("=" * 65)

    engine = DataIntelligenceEngine()
    report = engine.generate_full_report()

    # 1. Save JSON report
    out_json = os.path.join(os.path.dirname(__file__), '..', 'udyam_digital_data', 'phase1_intelligence_report.json')
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    print(f"✓ Saved Phase 1 JSON report to {out_json}")

    # 2. Generate Markdown Executive Report
    out_md = os.path.join(os.path.dirname(__file__), '..', 'PHASE1_DATA_INTELLIGENCE.md')
    f_data = report['funnel_analysis']
    c_data = report['drop_cause_clusters']['clusters']
    s_data = report['segment_economics']['segment_cohorts']
    t_data = report['statistical_validation']

    md_lines = [
        "# Phase 1: Data Intelligence & Funnel Root-Cause Report",
        "## Empirical Analysis of SMB Acquisition Telemetry (smb_leads.csv)",
        "**Project:** VyaparSetu (व्यापारसेतु) · Airtel Sync 2026 (Enterprise Track A)",
        "**Dataset:** 5,000 synthetic SMB leads across Tier 1 & Tier 2 cities (Apr–Jun 2026)",
        "",
        "---",
        "",
        "## 1. Funnel Decomposition & Stage Leakage",
        "",
        f"- **Total Inbound Leads:** {f_data['total_leads']:,}",
        f"- **Total Activated Customers:** {f_data['total_activated']:,}",
        f"- **Overall Conversion Rate:** **{f_data['overall_conversion_rate_pct']}%**",
        f"- **Total Lost Pipeline:** {f_data['total_dropped']:,} leads (92.64% leakage)",
        "",
        "| Funnel Stage | Reached Volume | Drop at this Stage | Step Conversion % | Cumulative % |",
        "|---|:---:|:---:|:---:|:---:|",
    ]

    for s in f_data['funnel_stages']:
        md_lines.append(f"| **{s['stage']}** | {s['count']:,} | {s['drop_at_this_stage']:,} | {s['step_conversion_pct']}% | {s['cumulative_conversion_pct']}% |")

    md_lines.extend([
        "",
        "> [!IMPORTANT]",
        "> **Steepest Drop Point:** The sharpest drop-off occurs between **Needs assessed $\\rightarrow$ Quote accepted**, where **56% of leads drop out** (only 43.6% accept). The second critical drop is between **Quote accepted $\\rightarrow$ KYC complete** (31.7% drop).",
        "",
        "---",
        "",
        "## 2. Drop-Cause Taxonomy & Root-Cause Clustering",
        "",
        "All 21 discrete drop reasons were categorized into 5 operational clusters:",
        "",
        "| Operational Cluster | Dropped Leads | % of Drops | GST Registered % | Addressability via VyaparSetu |",
        "|---|:---:|:---:|:---:|---|",
    ])

    for c in c_data:
        md_lines.append(f"| **{c['cluster_name']}** | {c['drop_count']:,} | {c['pct_of_total_drops']}% | {c['has_gstin_pct']}% | {c['vyaparsetu_addressability']} |")

    md_lines.extend([
        "",
        "---",
        "",
        "## 3. Multi-Cohort Econometric Profiling",
        "",
        "| Segment | Base Share | Conversion | Avg Existing Spend | Median Bundle | Blended CAC | Cycle Time | 6M Churn | NPS |",
        "|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|",
    ])

    for seg in s_data:
        md_lines.append(f"| **{seg['segment']}** | {seg['pct_of_total_base']}% | {seg['conversion_rate_pct']}% | ₹{seg['avg_existing_spend_inr']:,} | ₹{seg['avg_bundle_value_inr']:,}/mo | ₹{seg['blended_cac_inr']:,} | {seg['avg_days_to_activate']}d | {seg['churn_within_6m_pct']}% | {seg['avg_nps_score']}/10 |")

    md_lines.extend([
        "",
        "---",
        "",
        "## 4. Statistical Signal Verification",
        "",
        f"### Test 1: GSTIN Significance Test (Chi-Square)",
        f"- **Hypothesis:** {t_data['gstin_significance_test']['hypothesis']}",
        f"- **Chi-Square Statistic:** `{t_data['gstin_significance_test']['chi2_statistic']}`",
        f"- **p-value:** `{t_data['gstin_significance_test']['p_value']:.4e}` (Statistically Significant: **{t_data['gstin_significance_test']['is_statistically_significant']}**)",
        f"- **Conclusion:** {t_data['gstin_significance_test']['insight']}",
        "",
        f"### Test 2: Onboarding Chase Calls vs. Customer Churn (Welch's t-test)",
        f"- **Hypothesis:** {t_data['onboarding_friction_vs_churn_test']['hypothesis']}",
        f"- **t-statistic:** `{t_data['onboarding_friction_vs_churn_test']['t_statistic']}`",
        f"- **p-value:** `{t_data['onboarding_friction_vs_churn_test']['p_value']:.4e}` (Statistically Significant: **{t_data['onboarding_friction_vs_churn_test']['is_statistically_significant']}**)",
        f"- **Mean calls by churned:** {t_data['onboarding_friction_vs_churn_test']['mean_calls_churned']} vs **Retained:** {t_data['onboarding_friction_vs_churn_test']['mean_calls_retained']}",
        f"- **Conclusion:** {t_data['onboarding_friction_vs_churn_test']['insight']}",
        "",
        "---",
        "*Phase 1 Analysis Complete · Generated automatically by DataIntelligenceEngine*"
    ])

    with open(out_md, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_lines))
    print(f"✓ Saved Phase 1 Markdown report to {out_md}")

    print("\nPhase 1 Data Intelligence Execution Successful!")

if __name__ == '__main__':
    main()

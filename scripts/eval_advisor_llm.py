import os
import sys
import time
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Ensure LLM is NOT disabled for this evaluation script
os.environ.pop("VYAPAR_LLM_DISABLED", None)

from app.catalog_engine import CatalogEngine
from app.advisor_engine import AdvisorEngine

TEST_CASES = [
    {
        "message": "I run a dental clinic in Pune with 6 staff, we have GST",
        "segment": "prof",
        "checks": {"employee_count": 6, "has_gstin": True}
    },
    {
        "message": "मेरी किराना दुकान है, 2 लोग काम करते हैं, GST नहीं है",
        "segment": "micro",
        "checks": {"has_gstin": False}
    },
    {
        "message": "we have 4 restaurants in bangalore, need cctv and one bill",
        "segment": "multi",
        "checks": {"num_sites": 4}
    },
    {
        "message": "small garment factory in Surat, 40 workers, machines need monitoring",
        "segment": "mfg",
        "checks": {"employee_count": 40}
    },
    {
        "message": "I'm a chartered accountant, 3 people, need email and backup",
        "segment": "prof",
        "checks": {"employee_count": 3}
    },
    {
        "message": "beauty parlour hai, wifi chahiye customers ke liye",
        "segment": "micro",
        "checks": {}
    },
    {
        "message": "माझे मेडिकल स्टोअर आहे नाशिक मध्ये",
        "segment": "micro",
        "checks": {"preferred_language": "mr"}
    },
    {
        "message": "We are a coaching institute with 2 branches and 15 teachers",
        "segment": "multi",
        "checks": {"num_sites": 2, "employee_count": 15}
    },
    {
        "message": "hardware shop chalata hoon Indore mein, akela hi hoon",
        "segment": "micro",
        "checks": {"employee_count": 1}
    },
    {
        "message": "Our law firm has 12 lawyers in one office in Delhi, GST registered",
        "segment": "prof",
        "checks": {"employee_count": 12, "has_gstin": True}
    },
    {
        "message": "chain of 6 pharmacies across Hyderabad",
        "segment": "multi",
        "checks": {"num_sites": 6}
    },
    {
        "message": "எனக்கு ஒரு மளிகை கடை இருக்கிறது, சென்னை",
        "segment": "micro",
        "checks": {"preferred_language": "ta"}
    },
    {
        "message": "we make auto parts, 25 machines, plant in Pune, have GSTIN",
        "segment": "mfg",
        "checks": {"has_gstin": True}
    },
    {
        "message": "Mobile repair shop, 1 helper, no GST",
        "segment": "micro",
        "checks": {"has_gstin": False}
    },
    {
        "message": "3 branches of our gym in Jaipur",
        "segment": "multi",
        "checks": {"num_sites": 3}
    },
    {
        "message": "eye hospital with 30 staff",
        "segment": "prof",
        "checks": {"employee_count": 30}
    },
    {
        "message": "ਮੇਰੀ ਬੇਕਰੀ ਹੈ ਲੁਧਿਆਣਾ ਵਿੱਚ",
        "segment": "micro",
        "checks": {"preferred_language": "pa"}
    },
    {
        "message": "मेरी जयपुर में 2-counter किराना दुकान है 2 लोग काम करते हैं",
        "segment": "micro",
        "checks": {"num_sites": 1}
    }
]

def main():
    print("=" * 70)
    print("VyaparSetu · Advisor GenAI LLM Benchmark Evaluation (18 scenarios)")
    print("=" * 70)

    catalog = CatalogEngine()
    advisor = AdvisorEngine(catalog)

    passed = 0
    total = len(TEST_CASES)
    total_latency = 0.0

    for idx, tc in enumerate(TEST_CASES, start=1):
        msg = tc["message"]
        exp_seg = tc["segment"]
        checks = tc["checks"]

        t0 = time.time()
        profile = advisor.parse_conversational_query(msg)
        latency = time.time() - t0
        total_latency += latency

        matched = True
        reasons = []

        if profile.get("segment") != exp_seg:
            matched = False
            reasons.append(f"segment expected {exp_seg}, got {profile.get('segment')}")

        for k, v in checks.items():
            got = profile.get(k)
            if got != v:
                matched = False
                reasons.append(f"{k} expected {v}, got {got}")

        source = profile.get("_source", "unknown")
        if matched:
            passed += 1
            print(f"[{idx:02d}/18] OK   ({latency:.2f}s, {source}) :: \"{msg[:42]}...\"")
        else:
            print(f"[{idx:02d}/18] MISS ({latency:.2f}s, {source}) :: \"{msg[:42]}...\" -> {', '.join(reasons)}")

    avg_latency = total_latency / total
    print("-" * 70)
    print(f"Result: {passed}/{total} passed ({(passed/total)*100:.1f}%) | Avg Latency: {avg_latency:.2f}s")
    print("=" * 70)

    if passed < 17:
        print(f"FAIL: Target is >= 17/18 correct (got {passed}/18).")
        sys.exit(1)
    else:
        print("PASS: Met required >= 17/18 accuracy gate.")
        sys.exit(0)

if __name__ == "__main__":
    main()

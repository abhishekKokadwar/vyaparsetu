import os
import json
import re
import hashlib
import urllib.request
import urllib.error
from typing import Optional, Dict, Any
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Manual fallback for .env loading if dotenv not available or not loaded
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = os.environ.get("OPENROUTER_MODEL", "openai/gpt-4o-mini")
REQUEST_TIMEOUT_SECONDS = 5.0

SYSTEM_EXTRACTION_PROMPT = """You are VyaparSaarthi, Airtel's B2B AI Business Advisor for Indian MSMEs.
Your role is to understand business owners communicating in English, Hindi, Hinglish, Marathi, Tamil, Telugu, Punjabi, Gujarati, etc., and extract their business parameters into a strict JSON object.

Extract these exact fields:
{
  "business_type": string (e.g., "Kirana / Retail Store", "Clinic / Healthcare / Pharmacy", "CA / Legal / Consulting Firm", "Retail Chain / Multi-Site", "Manufacturing / Plant", "Salon / Beauty Parlour", "Coaching / Education Center", "Restaurant / Cafe / Food"),
  "segment": string (strictly one of: "micro", "prof", "multi", "mfg"),
  "employee_count": integer or null,
  "num_sites": integer (default 1 if single location, >1 if chain/outlets mentioned),
  "city": string or null,
  "city_tier": integer (1 for Metros: Delhi, NCR, Mumbai, Bengaluru, Pune, Hyderabad, Chennai, Kolkata; 2 for Tier 2/3: Jaipur, Lucknow, Indore, Bhopal, Nagpur, etc.),
  "has_gstin": boolean or null,
  "preferred_language": string ("en", "hi", "mr", "ta", "te", "pa", "gu", etc.),
  "clarifying_question": string or null (one polite, empathetic question in the user's language if critical information like GSTIN or employee count is missing)
}

Segment assignment rules:
- num_sites > 1 or multiple branches/outlets/restaurants/chain -> "multi"
- manufacturing/factory/plant/workshop/machining/textile/fabrication/packaging -> "mfg"
- clinic/doctor/dental/hospital/medical/pharmacy/ca/law/consulting/coaching/school -> "prof" (unless single retail pharmacy/chemist shop -> "micro")
- kirana/retail/store/mobile shop/hardware/salon/parlour/cafe/single restaurant -> "micro"

Return ONLY pure JSON. No markdown code blocks, no preamble."""

SYSTEM_PITCH_PROMPT = """You are VyaparSaarthi, Airtel's AI Business Advisor for Indian MSMEs.
Write a warm, empathetic, 2-3 sentence personalized pitch explaining why the recommended bundle is the perfect fit for this business.
CRITICAL CONSTRAINT: You MUST NOT invent any prices or product names. Use ONLY the exact bundle name, products, monthly price, and annual savings provided to you in the prompt.
Write in the customer's preferred language (English, Hindi, Marathi, Tamil, Punjabi, etc.).
Return ONLY the text of the pitch."""

class LLMAdvisorClient:
    """
    GenAI LLM Integration Client via OpenRouter.
    Provides natural language understanding and multilingual pitch synthesis
    with strict fallback to deterministic rules.
    """
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY", "") or OPENROUTER_API_KEY
        self.model = model or os.environ.get("OPENROUTER_MODEL", DEFAULT_MODEL)
        self._cache: Dict[str, dict] = {}

    def extract_profile(self, query: str, base_profile: Optional[dict] = None) -> Optional[dict]:
        """
        Uses LLM to parse natural language inquiry into structured business parameters.
        Returns None on any error or timeout (triggering immediate deterministic fallback).
        """
        if not self.api_key or not query or not query.strip():
            return None

        cache_key = hashlib.md5(f"parse:{query.strip().lower()}".encode('utf-8')).hexdigest()
        if cache_key in self._cache:
            return dict(self._cache[cache_key])

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_EXTRACTION_PROMPT},
                {"role": "user", "content": f"User inquiry: {query}"}
            ],
            "max_tokens": 400,
            "temperature": 0.1
        }

        try:
            req = urllib.request.Request(
                OPENROUTER_URL,
                data=json.dumps(payload).encode('utf-8'),
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://vyaparsetu.airtel.in",
                    "X-Title": "Airtel VyaparSetu"
                }
            )
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                content = data['choices'][0]['message']['content'].strip()
                clean_json = re.sub(r'^```(?:json)?\s*|\s*```$', '', content.strip(), flags=re.MULTILINE)
                parsed = json.loads(clean_json)

                # Merge with base profile
                result = dict(base_profile or {})
                for k, v in parsed.items():
                    if v is not None:
                        result[k] = v

                # Enforce valid segment
                if result.get('num_sites', 1) > 1 and result.get('segment') != 'mfg':
                    result['segment'] = 'multi'

                self._cache[cache_key] = result
                return result

        except Exception as e:
            # Return None on network blip, quota or timeout to ensure zero hang
            return None

    def synthesize_narrative(
        self,
        business_type: str,
        bundle_name: str,
        products_list: list,
        monthly_cost_inr: int,
        annual_savings_inr: int,
        language: str = "en"
    ) -> Optional[str]:
        """
        Uses LLM to synthesize a high-empathy sales pitch in the customer's language.
        Returns None on timeout/error (falling back to template narrative).
        """
        if not self.api_key:
            return None

        prompt_input = (
            f"Business: {business_type}\n"
            f"Recommended Bundle: {bundle_name}\n"
            f"Included Products: {', '.join(products_list)}\n"
            f"Monthly Bill: ₹{monthly_cost_inr:,}\n"
            f"Annual Savings: ₹{annual_savings_inr:,}\n"
            f"Language: {language}"
        )

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PITCH_PROMPT},
                {"role": "user", "content": prompt_input}
            ],
            "max_tokens": 300,
            "temperature": 0.3
        }

        try:
            req = urllib.request.Request(
                OPENROUTER_URL,
                data=json.dumps(payload).encode('utf-8'),
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://vyaparsetu.airtel.in",
                    "X-Title": "Airtel VyaparSetu"
                }
            )
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                pitch = data['choices'][0]['message']['content'].strip()
                return pitch
        except Exception:
            return None

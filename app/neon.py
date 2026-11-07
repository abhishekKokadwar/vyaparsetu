"""Neon Postgres over HTTPS - parameterised queries, no driver, works on Vercel serverless.

Reads DATABASE_URL from the environment / .env (never hard-code it). Every call is best-effort:
on any failure it returns None and the app keeps working from memory.
Set VYAPAR_DB_DISABLED=1 to turn it off (unit tests do).
"""
import json
import os
import urllib.parse
import urllib.request
from typing import List, Optional

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
except ImportError:
    pass

_SCHEMA = [
    """create table if not exists vyaparsetu_orders (
         order_id text primary key,
         contact_phone text,
         order_data jsonb not null,
         updated_at timestamptz not null default now())""",
    """create table if not exists vyaparsetu_consents (
         id bigserial primary key,
         applicant_code text not null,
         kind text not null,
         payload jsonb not null,
         created_at timestamptz not null default now())""",
    "create index if not exists vyaparsetu_consents_code on vyaparsetu_consents (applicant_code, id)",
]
_ready = False


def enabled() -> bool:
    return bool(os.environ.get("DATABASE_URL")) and os.environ.get("VYAPAR_DB_DISABLED") != "1"


def _post(sql: str, params: list, timeout: float) -> Optional[List[dict]]:
    url = os.environ["DATABASE_URL"]
    host = urllib.parse.urlparse(url).hostname
    req = urllib.request.Request(
        f"https://{host}/sql",
        data=json.dumps({"query": sql, "params": params}).encode("utf-8"),
        headers={"Neon-Connection-String": url, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8")).get("rows", [])


def query(sql: str, params: Optional[list] = None, timeout: float = 4.0) -> Optional[List[dict]]:
    """Run one parameterised statement ($1, $2 ...). Returns rows, or None if the DB is off/unreachable."""
    global _ready
    if not enabled():
        return None
    try:
        if not _ready:
            for ddl in _SCHEMA:
                _post(ddl, [], timeout)
            _ready = True
        return _post(sql, params or [], timeout)
    except Exception:
        return None

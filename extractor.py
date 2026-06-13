import json
import os
import sys
from datetime import datetime, timezone
from groq import Groq

MODEL = "llama-3.3-70b-versatile"

client = None


def _get_client():
    global client
    if client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise OSError("GROQ_API_KEY is not set.")
        client = Groq(api_key=api_key)
    return client


def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        lines = lines[1:] if lines[0].startswith("```") else lines
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


def extract(snapshot: dict) -> dict:
    prompt = f"""You are an SEO auditor. Analyze this page snapshot and return ONLY a JSON object.
No prose. No explanation. No markdown fences. Raw JSON only.

Page data:
- URL: {snapshot.get('final_url')}
- Status code: {snapshot.get('status_code')}
- Title: {snapshot.get('title')}
- Meta description: {snapshot.get('meta_description')}
- H1 tags: {snapshot.get('h1s')}
- Canonical: {snapshot.get('canonical')}

Return this exact schema:
{{
  "url": "string",
  "final_url": "string",
  "status_code": number,
  "title": {{"value": "string or null", "length": number, "status": "PASS or FAIL"}},
  "description": {{"value": "string or null", "length": number, "status": "PASS or FAIL"}},
  "h1": {{"count": number, "value": "string or null", "status": "PASS or FAIL"}},
  "canonical": {{"value": "string or null", "status": "PASS or FAIL"}},
  "flags": ["array of strings describing specific issues"],
  "human_review": false,
  "audited_at": "ISO timestamp"
}}

PASS/FAIL rules:
- title: FAIL if null or length > 60 characters
- description: FAIL if null or length > 160 characters
- h1: FAIL if count is 0 (missing) or count > 1 (multiple)
- canonical: FAIL if null
- flags: list every failing field with a clear description
- audited_at: use current UTC time in ISO 8601 format"""

    groq_client = _get_client()

    response = groq_client.chat.completions.create(
        model=MODEL,
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
    )

    raw = response.choices[0].message.content
    clean = _strip_fences(raw)

    try:
        return json.loads(clean)
    except json.JSONDecodeError as exc:
        print(f"[extractor] JSON parse error: {exc}", file=sys.stderr)
        return _error_result(snapshot, str(exc))


def _error_result(snapshot: dict, reason: str) -> dict:
    return {
        "url": snapshot.get("final_url", ""),
        "final_url": snapshot.get("final_url", ""),
        "status_code": snapshot.get("status_code"),
        "title": {"value": None, "length": 0, "status": "ERROR"},
        "description": {"value": None, "length": 0, "status": "ERROR"},
        "h1": {"count": 0, "value": None, "status": "ERROR"},
        "canonical": {"value": None, "status": "ERROR"},
        "flags": [f"Extraction error: {reason}"],
        "human_review": True,
        "audited_at": datetime.now(timezone.utc).isoformat(),
    }
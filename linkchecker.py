import asyncio
import logging
from urllib.parse import urlparse
import httpx

CAP = 50
TIMEOUT = 5.0
logger = logging.getLogger(__name__)


def _same_domain(link: str, final_url: str) -> bool:
    if not link:
        return False
    lower = link.strip().lower()
    if lower.startswith(("#", "mailto:", "javascript:", "tel:", "data:")):
        return False
    try:
        page_host = urlparse(final_url).netloc.lower()
        parsed = urlparse(link)
        return parsed.scheme in ("http", "https") and parsed.netloc.lower() == page_host
    except Exception:
        return False


async def _check_link(client: httpx.AsyncClient, url: str) -> tuple[str, bool]:
    try:
        resp = await client.head(url, follow_redirects=True, timeout=TIMEOUT)
        return url, resp.status_code != 200
    except Exception:
        return url, True


async def _run_checks(links: list[str]) -> list[str]:
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(*[_check_link(client, url) for url in links])
    return [url for url, broken in results if broken]


def check_links(raw_links: list[str], final_url: str) -> dict:
    same_domain = [l for l in raw_links if _same_domain(l, final_url)]

    capped = len(same_domain) > CAP
    if capped:
        same_domain = same_domain[:CAP]

    broken = asyncio.run(_run_checks(same_domain))

    return {
        "broken": broken,
        "count": len(broken),
        "status": "FAIL" if broken else "PASS",
        "capped": capped,
    }
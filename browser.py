import sys
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

TIMEOUT = 20
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def fetch_page(url: str) -> dict:
    result = {
        "final_url": url,
        "status_code": None,
        "title": None,
        "meta_description": None,
        "h1s": [],
        "canonical": None,
        "raw_links": [],
    }

    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        result["status_code"] = resp.status_code
        result["final_url"] = resp.url

        soup = BeautifulSoup(resp.text, "html.parser")

        title_tag = soup.find("title")
        result["title"] = title_tag.get_text(strip=True) if title_tag else None

        meta_desc = soup.find("meta", attrs={"name": "description"})
        result["meta_description"] = meta_desc.get("content", None) if meta_desc else None

        result["h1s"] = [h1.get_text(strip=True) for h1 in soup.find_all("h1")]

        canonical_tag = soup.find("link", attrs={"rel": "canonical"})
        result["canonical"] = canonical_tag.get("href", None) if canonical_tag else None

        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            full_url = urljoin(result["final_url"], href)
            links.append(full_url)
        result["raw_links"] = links[:100]

    except requests.exceptions.Timeout:
        result["status_code"] = 408
    except Exception as exc:
        print(f"[browser] Error: {exc}", file=sys.stderr)
        result["status_code"] = None

    return result
import csv
import os
import sys
import time

from state import load_state, is_audited, mark_audited, add_to_needs_human
from browser import fetch_page
from extractor import extract
from linkchecker import check_links
from hitl import should_pause, pause_reason
from reporter import write_result, write_summary

INPUT_CSV = os.path.join(os.path.dirname(__file__), "input.csv")


def read_urls(path: str) -> list[str]:
    with open(path, newline="", encoding="utf-8") as f:
        return [row["url"].strip() for row in csv.DictReader(f) if row.get("url", "").strip()]


def read_urls_from_text(text: str) -> list[str]:
    urls = []
    for line in text.strip().splitlines():
        line = line.strip()
        if line and line.startswith("http"):
            urls.append(line)
    return urls


def audit_single(url: str) -> dict:
    snapshot = fetch_page(url)

    if should_pause(snapshot):
        reason = pause_reason(snapshot)
        add_to_needs_human(url)
        mark_audited(url)
        return {
            "url": url,
            "skipped": True,
            "reason": reason,
        }

    result = extract(snapshot)
    links = check_links(snapshot.get("raw_links", []), snapshot.get("final_url", url))
    result["broken_links"] = links

    write_result(result)
    mark_audited(url)

    overall = "PASS" if all(
        result.get(f, {}).get("status") == "PASS"
        for f in ["title", "description", "h1", "canonical"]
    ) and links["status"] == "PASS" else "FAIL"

    result["overall"] = overall
    return result


def run_batch(urls: list[str], progress_callback=None) -> list[dict]:
    results = []
    total = len(urls)

    for i, url in enumerate(urls):
        if progress_callback:
            progress_callback(i, total, url)

        result = audit_single(url)
        results.append(result)

    write_summary()
    return results
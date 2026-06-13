import json
import os
from datetime import datetime, timezone

REPORT_JSON = os.path.join(os.path.dirname(__file__), "report.json")
REPORT_TXT = os.path.join(os.path.dirname(__file__), "report-summary.txt")


def _load_report() -> list:
    if not os.path.exists(REPORT_JSON):
        return []
    with open(REPORT_JSON, encoding="utf-8") as f:
        return json.load(f)


def write_result(result: dict) -> None:
    entries = _load_report()
    url = result.get("url", "")

    for i, entry in enumerate(entries):
        if entry.get("url") == url:
            entries[i] = result
            break
    else:
        entries.append(result)

    with open(REPORT_JSON, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)


def _is_overall_pass(result: dict) -> bool:
    fields = ["title", "description", "h1", "canonical"]
    for field in fields:
        if result.get(field, {}).get("status") not in ("PASS",):
            return False
    if result.get("broken_links", {}).get("status") == "FAIL":
        return False
    return True


def write_summary() -> None:
    entries = _load_report()
    passed = sum(1 for e in entries if _is_overall_pass(e))

    lines = []
    for entry in entries:
        overall = "PASS" if _is_overall_pass(entry) else "FAIL"
        failed_fields = [
            f for f in ["title", "description", "h1", "canonical", "broken_links"]
            if entry.get(f, {}).get("status") == "FAIL"
        ]
        suffix = f" [{', '.join(failed_fields)}]" if failed_fields else ""
        lines.append(f"{entry.get('url', 'unknown'):<60} | {overall}{suffix}")

    lines.append("")
    lines.append(f"{passed}/{len(entries)} URLs passed")

    with open(REPORT_TXT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def get_report_data() -> list:
    return _load_report()
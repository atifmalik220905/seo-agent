from state import add_to_needs_human

LOGIN_KEYWORDS = {"login", "sign in", "sign-in", "access denied", "log in", "unauthorized"}
REDIRECT_CODES = {301, 302, 307, 308}


def should_pause(snapshot: dict) -> bool:
    code = snapshot.get("status_code")

    if code is None:
        return True

    if code != 200 and code not in REDIRECT_CODES:
        return True

    title = (snapshot.get("title") or "").lower()
    h1s = [h.lower() for h in (snapshot.get("h1s") or [])]

    if any(kw in title for kw in LOGIN_KEYWORDS):
        return True
    if any(kw in h1 for kw in LOGIN_KEYWORDS for h1 in h1s):
        return True

    return False


def pause_reason(snapshot: dict) -> str:
    code = snapshot.get("status_code")
    if code is None:
        return "Navigation failed (None status)"
    if code != 200 and code not in REDIRECT_CODES:
        return f"Unexpected status code: {code}"
    return "Possible login wall detected"
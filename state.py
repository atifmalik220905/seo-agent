import json
import os

STATE_FILE = os.path.join(os.path.dirname(__file__), "state.json")

_DEFAULT_STATE = {"audited": [], "pending": [], "needs_human": []}


def load_state() -> dict:
    if not os.path.exists(STATE_FILE):
        save_state(_DEFAULT_STATE.copy())
    with open(STATE_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_state(state: dict) -> None:
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def is_audited(url: str) -> bool:
    return url in load_state()["audited"]


def mark_audited(url: str) -> None:
    state = load_state()
    if url not in state["audited"]:
        state["audited"].append(url)
    save_state(state)


def add_to_needs_human(url: str) -> None:
    state = load_state()
    if url not in state["needs_human"]:
        state["needs_human"].append(url)
    save_state(state)


def reset_state() -> None:
    save_state(_DEFAULT_STATE.copy())
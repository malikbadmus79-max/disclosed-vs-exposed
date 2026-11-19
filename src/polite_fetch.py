"""Rate-limited, robots-aware HTTP helper for the Phase 0 audit.

Rules enforced here:
- robots.txt is checked before each request; a disallowed URL is not fetched.
- At least 2 seconds pass between any two requests in a process.
- One honest User-Agent. A block (401/403/429/451) is reported, never retried.

Every attempt is appended to data/interim/fetch_log.csv.
"""
from __future__ import annotations

import csv
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests

ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = ROOT / "data" / "interim" / "fetch_log.csv"
USER_AGENT = "nigeria-disclosed-vs-exposed-feasibility-audit/0.1 (academic research; python-requests)"
MIN_INTERVAL_S = 2.0
TIMEOUT_S = 60

_session = requests.Session()
_session.headers["User-Agent"] = USER_AGENT
_robots: dict[str, RobotFileParser | None] = {}
_last_request = 0.0


def _wait() -> None:
    global _last_request
    delay = MIN_INTERVAL_S - (time.monotonic() - _last_request)
    if delay > 0:
        time.sleep(delay)
    _last_request = time.monotonic()


def _log(url: str, status: str, note: str = "", size: int | str = "") -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    new = not LOG_PATH.exists()
    with LOG_PATH.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if new:
            writer.writerow(["utc_time", "url", "status", "bytes", "note"])
        writer.writerow([datetime.now(timezone.utc).isoformat(timespec="seconds"), url, status, size, note])


def robots_allows(url: str) -> tuple[bool, str]:
    """Return (allowed, reason). A missing robots.txt (404) allows access."""
    parts = urlparse(url)
    base = f"{parts.scheme}://{parts.netloc}"
    if base not in _robots:
        _wait()
        try:
            resp = _session.get(f"{base}/robots.txt", timeout=TIMEOUT_S)
        except requests.RequestException as exc:
            _robots[base] = None
            _log(f"{base}/robots.txt", "error", type(exc).__name__)
            return False, f"robots.txt unreachable ({type(exc).__name__})"
        _log(f"{base}/robots.txt", str(resp.status_code))
        if resp.status_code in (401, 403) or resp.status_code >= 500:
            _robots[base] = None
            return False, f"robots.txt returned {resp.status_code}"
        parser = RobotFileParser()
        parser.parse(resp.text.splitlines() if resp.status_code == 200 else [])
        _robots[base] = parser
    parser = _robots[base]
    if parser is None:
        return False, "robots.txt unavailable; not fetching"
    return (True, "ok") if parser.can_fetch(USER_AGENT, url) else (False, "disallowed by robots.txt")


def fetch(url: str, dest: Path | None = None, max_bytes: int | None = None,
          deadline: float | None = None) -> requests.Response | None:
    """GET a URL, optionally streaming to dest. Returns None if not fetched.

    deadline is a time.monotonic() value; a streaming download that passes it is abandoned and removed.
    """
    allowed, reason = robots_allows(url)
    if not allowed:
        _log(url, "not_fetched", reason)
        print(f"NOT FETCHED {url}: {reason}", file=sys.stderr)
        return None
    _wait()
    try:
        resp = _session.get(url, timeout=TIMEOUT_S, stream=dest is not None)
    except requests.RequestException as exc:
        _log(url, "error", type(exc).__name__)
        print(f"ERROR {url}: {type(exc).__name__}", file=sys.stderr)
        return None
    if dest is None or resp.status_code != 200:
        _log(url, str(resp.status_code), resp.headers.get("Content-Type", ""), len(resp.content))
        return resp
    dest.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    tmp = dest.with_suffix(dest.suffix + ".part")
    try:
        with tmp.open("wb") as f:
            for chunk in resp.iter_content(1 << 16):
                f.write(chunk)
                written += len(chunk)
                if max_bytes and written > max_bytes:
                    break
                if deadline and time.monotonic() > deadline:
                    break
    except requests.RequestException as exc:
        tmp.unlink(missing_ok=True)
        _log(url, "error", f"connection lost mid-download: {type(exc).__name__}", written)
        print(f"ERROR {url}: connection lost after {written} bytes", file=sys.stderr)
        return None
    if deadline and time.monotonic() > deadline:
        tmp.unlink()
        _log(url, "abandoned_deadline", "batch deadline reached", written)
        return None
    if max_bytes and written > max_bytes:
        tmp.unlink()
        _log(url, "skipped_too_large", f"over {max_bytes} bytes", written)
        return None
    tmp.replace(dest)
    _log(url, str(resp.status_code), resp.headers.get("Content-Type", ""), written)
    return resp

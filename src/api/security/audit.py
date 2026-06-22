"""Append-only audit logger.

Every mutating HTTP request, every login attempt, and every privileged
action ends up here. The log is intentionally simple (JSONL, one event
per line) so it can be shipped to a SIEM (Splunk, Elastic, Datadog)
without parsing.
"""
from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path


class AuditLogger:
    def __init__(self, path: str):
        self.path = Path(path)
        self._lock = threading.Lock()
        # Ensure parent directory exists (best-effort; in production this
        # would be a mounted volume).
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            # Restrict to owner only.
            if not self.path.exists():
                self.path.touch()
                os.chmod(self.path, 0o600)
        except OSError:
            # Fall back to /tmp if the configured path is not writable.
            self.path = Path("/tmp/kinz-audit.log")
            self.path.touch(exist_ok=True)

    def log(self, action: str, user: str = "anonymous", detail: str = "", ip: str = "") -> None:
        event = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "user": user,
            "ip": ip,
            "detail": detail,
        }
        line = json.dumps(event, ensure_ascii=False)
        with self._lock:
            with self.path.open("a", encoding="utf-8") as f:
                f.write(line + "\n")


# Module-level singleton used by the rest of the codebase.
_audit: AuditLogger | None = None


def get_audit_logger() -> AuditLogger:
    global _audit
    if _audit is None:
        from src.api.utils.config import settings

        _audit = AuditLogger(settings.AUDIT_LOG_PATH)
    return _audit

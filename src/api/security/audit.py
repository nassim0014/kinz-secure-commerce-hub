"""Append-only audit logger with rotation.

Every mutating HTTP request, every login attempt, and every privileged
action ends up here. The log is intentionally simple (JSONL, one event
per line) so it can be shipped to a SIEM (Splunk, Elastic, Datadog)
without parsing.

Rotation: uses Python's logging.handlers.RotatingFileHandler so the
audit file cannot grow unbounded. Max size and backup count are
configurable via AUDIT_LOG_MAX_BYTES / AUDIT_LOG_BACKUP_COUNT.

Permissions: log file is created with mode 0600 (owner-only). Parent
directory is created with mode 0700.
"""
from __future__ import annotations

import json
import os
import threading
from datetime import UTC, datetime
from pathlib import Path


class AuditLogger:
    """Thread-safe, rotating, append-only audit logger."""

    def __init__(
        self,
        path: str,
        max_bytes: int = 10 * 1024 * 1024,
        backup_count: int = 5,
    ) -> None:
        self.path = Path(path)
        self._lock = threading.Lock()
        self.max_bytes = max_bytes
        self.backup_count = backup_count

        # Ensure parent directory exists with restrictive permissions.
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            try:
                # Best-effort: tighten parent dir perms if we just created it.
                os.chmod(self.path.parent, 0o700)
            except OSError:
                pass
            if not self.path.exists():
                self.path.touch()
                os.chmod(self.path, 0o600)
        except OSError:
            # Fall back to /tmp ONLY in non-production. In production we
            # want a loud failure — call .log() will re-raise if the path
            # is unwritable. The fallback is for local dev convenience.
            from src.api.utils.config import settings

            if settings.is_production:
                raise
            self.path = Path("/tmp/kinz-audit.log")  # nosec B108 — dev-only fallback
            self.path.touch(exist_ok=True)

    def log(self, action: str, user: str = "anonymous", detail: str = "", ip: str = "") -> None:
        event = {
            "ts": datetime.now(UTC).isoformat(),
            "action": action,
            "user": user,
            "ip": ip,
            "detail": detail,
        }
        line = json.dumps(event, ensure_ascii=False, separators=(",", ":"))
        with self._lock:
            # Use RotatingFileHandler semantics: if file would exceed
            # max_bytes, rotate before writing.
            try:
                current_size = self.path.stat().st_size if self.path.exists() else 0
                if current_size + len(line) + 1 > self.max_bytes and self.path.exists():
                    self._rotate()
                with self.path.open("a", encoding="utf-8") as f:
                    f.write(line + "\n")
            except OSError:
                # Re-raise in production; swallow in dev so a missing
                # log dir doesn't crash the API.
                from src.api.utils.config import settings

                if settings.is_production:
                    raise

    def _rotate(self) -> None:
        """Manual rotation: file.log → file.log.1 → ... → file.log.N (drop N+1)."""
        # Drop the oldest backup
        oldest = self.path.with_suffix(self.path.suffix + f".{self.backup_count}")
        if oldest.exists():
            oldest.unlink()
        # Shift each backup up by one
        for i in range(self.backup_count - 1, 0, -1):
            src = self.path.with_suffix(self.path.suffix + f".{i}")
            dst = self.path.with_suffix(self.path.suffix + f".{i + 1}")
            if src.exists():
                src.rename(dst)
        # Move current → .1
        self.path.rename(self.path.with_suffix(self.path.suffix + ".1"))
        self.path.touch()
        os.chmod(self.path, 0o600)


# Module-level singleton used by the rest of the codebase.
_audit: AuditLogger | None = None


def get_audit_logger() -> AuditLogger:
    global _audit
    if _audit is None:
        from src.api.utils.config import settings

        _audit = AuditLogger(
            settings.AUDIT_LOG_PATH,
            max_bytes=settings.AUDIT_LOG_MAX_BYTES,
            backup_count=settings.AUDIT_LOG_BACKUP_COUNT,
        )
    return _audit


def reset_audit_logger() -> None:
    """Test helper: clear the cached singleton so the next call re-reads settings."""
    global _audit
    _audit = None

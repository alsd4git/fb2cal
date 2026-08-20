"""Canonical JSON interchange/debug exporter."""

from __future__ import annotations

import json
from collections.abc import Iterable
from datetime import datetime, timezone
from pathlib import Path

from .contact import BirthdayContact
from .pipeline import summarize_contacts


class JSONExporter:
    def __init__(
        self, contacts: Iterable[BirthdayContact], extracted_at: str | None = None
    ):
        self.contacts = list(contacts)
        self.extracted_at = extracted_at or datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        summary = summarize_contacts(self.contacts)
        return {
            "version": 1,
            "source": "facebook",
            "extracted_at": self.extracted_at,
            "summary": summary.to_dict(),
            "contacts": [contact.to_dict() for contact in self.contacts],
        }

    def export(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2) + "\n"

    def write(self, path: str | Path) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(self.export(), encoding="utf-8")
        target.chmod(0o600)

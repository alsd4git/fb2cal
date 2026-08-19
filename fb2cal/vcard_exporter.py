"""Interoperable vCard 3.0 exporter."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from .contact import BirthdayContact


def _escape(value: str | None) -> str:
    if not value:
        return ""
    return value.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


class VCardExporter:
    def __init__(self, contacts: Iterable[BirthdayContact]):
        self.contacts = list(contacts)

    def export(self) -> str:
        cards = []
        for contact in self.contacts:
            birthday = f"{contact.birthday_year:04}-{contact.birthday_month:02}-{contact.birthday_day:02}" if contact.birthday_year is not None else f"--{contact.birthday_month:02}-{contact.birthday_day:02}"
            lines = [
                "BEGIN:VCARD",
                "VERSION:3.0",
                f"UID:fb2cal-facebook-{_escape(contact.id)}",
                f"FN:{_escape(contact.name)}",
                f"N:{_escape(contact.name)};;;;",
                f"BDAY:{birthday}",
                f"URL;TYPE=Facebook:{_escape(contact.profile_url)}",
                f"PHOTO;VALUE=URI:{_escape(contact.picture_url)}",
                "X-FB2CAL-SOURCE:facebook",
                "END:VCARD",
            ]
            cards.append("\r\n".join(lines))
        return "\r\n".join(cards) + ("\r\n" if cards else "")

    def write(self, path: str | Path) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(self.export(), encoding="utf-8", newline="")

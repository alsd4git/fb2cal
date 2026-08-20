"""Interoperable vCard exporter with 4.0 and legacy 3.0 output."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Literal

from .contact import BirthdayContact
from .text_format import serialize_content_lines

VCardVersion = Literal["3.0", "4.0"]


def _escape_text(value: str | None) -> str:
    if not value:
        return ""
    return (
        value.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\r\n", "\n")
        .replace("\r", "\n")
        .replace("\n", "\\n")
    )


def _sanitize_uri(value: str | None) -> str:
    if not value:
        return ""
    return value.replace("\r", "").replace("\n", "")


class VCardExporter:
    def __init__(
        self, contacts: Iterable[BirthdayContact], version: VCardVersion = "4.0"
    ):
        if version not in ("3.0", "4.0"):
            raise ValueError(f"Unsupported vCard version: {version}")
        self.contacts = list(contacts)
        self.version = version

    def export(self) -> str:
        lines = []
        for contact in self.contacts:
            if self.version == "4.0":
                birthday = (
                    f"{contact.birthday_year:04}{contact.birthday_month:02}{contact.birthday_day:02}"
                    if contact.birthday_year is not None
                    else f"--{contact.birthday_month:02}{contact.birthday_day:02}"
                )
            else:
                birthday = (
                    f"{contact.birthday_year:04}-{contact.birthday_month:02}-{contact.birthday_day:02}"
                    if contact.birthday_year is not None
                    else f"--{contact.birthday_month:02}-{contact.birthday_day:02}"
                )

            lines.extend(
                [
                    "BEGIN:VCARD",
                    f"VERSION:{self.version}",
                    f"UID:fb2cal-facebook-{_escape_text(contact.id)}",
                    f"FN:{_escape_text(contact.name)}",
                    f"N:{_escape_text(contact.name)};;;;",
                    f"BDAY:{birthday}",
                ]
            )
            if contact.profile_url:
                lines.append(f"URL;TYPE=Facebook:{_sanitize_uri(contact.profile_url)}")
            if contact.picture_url:
                photo = (
                    f"PHOTO;VALUE=URI:{_sanitize_uri(contact.picture_url)}"
                    if self.version == "3.0"
                    else f"PHOTO:{_sanitize_uri(contact.picture_url)}"
                )
                lines.append(photo)
            lines.extend(
                [
                    "X-FB2CAL-SOURCE:facebook",
                    "END:VCARD",
                ]
            )
        return serialize_content_lines(lines)

    def write(self, path: str | Path) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(self.export(), encoding="utf-8", newline="")
        target.chmod(0o600)

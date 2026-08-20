"""Extraction pipeline shared by CLI and programmatic callers."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from .facebook_client import FacebookClient
from .transformer import Transformer


@dataclass(frozen=True)
class ExtractionSummary:
    """Counts that can be derived from the birthday query itself."""

    contacts: int
    with_year: int
    without_year: int

    def to_dict(self) -> dict[str, int]:
        return {
            "contacts": self.contacts,
            "with_year": self.with_year,
            "without_year": self.without_year,
        }


def extract_birthdays(client: FacebookClient, offsets: Iterable[int] = (0, 3, 6, 9)):
    """Fetch, transform, and deduplicate birthday contacts by Facebook ID."""
    transformer = Transformer()
    contacts = {}
    for offset_month in offsets:
        result = client.query_graph_ql_birthday_comet_monthly(offset_month)
        for contact in transformer.transform_birthday_comet_monthly_to_birthdays(
            result
        ):
            contacts[contact.id] = contact
    return sorted(contacts.values())


def summarize_contacts(contacts) -> ExtractionSummary:
    contacts = list(contacts)
    with_year = sum(contact.birthday_year is not None for contact in contacts)
    return ExtractionSummary(
        contacts=len(contacts),
        with_year=with_year,
        without_year=len(contacts) - with_year,
    )

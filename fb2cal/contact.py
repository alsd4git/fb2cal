"""Facebook-independent birthday contact model."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class BirthdayContact:
    id: str
    name: str
    profile_url: str | None
    picture_url: str | None
    birthday_day: int
    birthday_month: int
    birthday_year: int | None = None
    source: str = "facebook"

    @property
    def profile_picture_uri(self) -> str | None:
        """Compatibility spelling used by the original FacebookUser model."""
        return self.picture_url

    def __str__(self) -> str:
        year = "????" if self.birthday_year is None else f"{self.birthday_year:04}"
        return f"{self.name} ({self.birthday_day:02}/{self.birthday_month:02}/{year})"

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, BirthdayContact):
            return NotImplemented
        return (self.birthday_month, self.birthday_day, self.name, self.id) < (
            other.birthday_month,
            other.birthday_day,
            other.name,
            other.id,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "profile_url": self.profile_url,
            "picture_url": self.picture_url,
            "birthday": {
                "day": self.birthday_day,
                "month": self.birthday_month,
                "year": self.birthday_year,
            },
            "source": self.source,
        }

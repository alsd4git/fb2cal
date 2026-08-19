"""Facebook HTTP client, independent from authentication creation."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import mechanicalsoup
import requests

from .__init__ import __title__, __version__
from .errors import FacebookCheckpointError, GraphQLQueryError, SessionExpiredError
from .facebook_queries import (
    GRAPHQL_ENDPOINT,
    build_birthday_payload,
    parse_birthday_response,
)
from .facebook_token import FacebookDTSGParser

BIRTHDAY_PAGE_URL = "https://www.facebook.com/events/birthdays/"


@dataclass(frozen=True)
class SessionValidation:
    status: str
    user_id: str | None
    fb_dtsg: str


class FacebookClient:
    def __init__(self, session: requests.Session | None = None):
        self.logger = logging.getLogger("fb2cal")
        self.session = session if session is not None else requests.Session()
        self.browser = mechanicalsoup.StatefulBrowser(session=self.session)
        self.browser.set_user_agent(f"{__title__}/{__version__}")
        self._cached_token: str | None = None

    def get_token(self) -> str:
        if self._cached_token:
            return self._cached_token
        response = self.browser.get(BIRTHDAY_PAGE_URL)
        self._raise_for_auth_response(response)
        self._cached_token = FacebookDTSGParser.extract(response.text)
        return self._cached_token

    def validate_session(self) -> SessionValidation:
        response = self.browser.get(BIRTHDAY_PAGE_URL)
        self._raise_for_auth_response(response)
        token = FacebookDTSGParser.extract(response.text)
        self._cached_token = token
        user_id = self.session.cookies.get("c_user")
        return SessionValidation(status="authenticated", user_id=user_id, fb_dtsg=token)

    def is_authenticated(self) -> bool:
        try:
            self.validate_session()
        except (SessionExpiredError, FacebookCheckpointError):
            return False
        return True

    def query_graph_ql_birthday_comet_monthly(self, offset_month: int) -> dict[str, Any]:
        payload = build_birthday_payload(offset_month, self.get_token())
        response = self.browser.post(GRAPHQL_ENDPOINT, data=payload)
        if response.status_code != 200:
            raise GraphQLQueryError(f"Facebook GraphQL request returned HTTP {response.status_code}")
        return parse_birthday_response(response.text)

    def _raise_for_auth_response(self, response: Any) -> None:
        text = response.text or ""
        url = str(getattr(response, "url", ""))
        if getattr(response, "status_code", 0) in (401, 403) or "/login" in url:
            raise SessionExpiredError("Facebook session is expired or login is required")
        if "checkpointSubmitButton" in text or "/two_step_verification/" in text:
            raise FacebookCheckpointError("Facebook requires checkpoint or two-step verification")
        if "login_form" in text and "DTSGInitialData" not in text:
            raise SessionExpiredError("Facebook session is expired or login is required")
        if getattr(response, "status_code", 0) != 200:
            raise SessionExpiredError(f"Facebook birthday page returned HTTP {response.status_code}")

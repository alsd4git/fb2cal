"""Backward-compatible browser facade for the legacy authentication API."""

from __future__ import annotations

from .auth.legacy import LegacyFacebookAuthenticator
from .facebook_client import FacebookClient


class FacebookBrowser(FacebookClient):
    """Compatibility name that keeps email/password login available."""

    def authenticate(self, email: str, password: str) -> None:
        LegacyFacebookAuthenticator(self).authenticate(email, password)

    def _get_datr_token_from_html(self, html: str) -> str:
        return LegacyFacebookAuthenticator._extract_datr(html)

    def _get_pubkey_from_html(self, html: str) -> tuple[str, int]:
        return LegacyFacebookAuthenticator._extract_pubkey(html)

    @property
    def _FacebookBrowser__cached_token(self):  # pragma: no cover - compatibility only
        return self._cached_token

    @_FacebookBrowser__cached_token.setter
    def _FacebookBrowser__cached_token(self, value):  # pragma: no cover - compatibility only
        self._cached_token = value

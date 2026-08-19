"""Legacy email/password Facebook login."""

from __future__ import annotations

import re

from bs4 import Tag

from ..errors import AuthenticationError, FacebookCheckpointError
from ..utils import facebook_web_encrypt_password


class LegacyFacebookAuthenticator:
    """Compatibility backend for Facebook's legacy login form."""

    def __init__(self, client):
        self.client = client

    def authenticate(self, email: str, password: str) -> None:
        login_page = self.client.browser.open("https://www.facebook.com/login")
        if login_page.status_code != 200:
            raise AuthenticationError(f"Facebook login page returned HTTP {login_page.status_code}")

        datr = self._extract_datr(login_page.text)
        self.client.session.cookies.set("datr", datr, domain=".facebook.com", path="/")
        self.client.session.cookies.set("_js_datr", datr, domain=".facebook.com", path="/")

        login_form = self.client.browser.select_form("form#login_form")
        if login_form is None:
            raise AuthenticationError("Could not find Facebook login form")
        login_form.set("email", email)

        public_key, key_id = self._extract_pubkey(login_page.text)
        enc_pass = facebook_web_encrypt_password(key_id, public_key, password)
        login_form.form.append(Tag(name="input", attrs={"type": "hidden", "name": "encpass", "value": enc_pass}))

        login_response = self.client.browser.submit_selected()
        if login_response.status_code != 200:
            raise AuthenticationError(f"Facebook login returned HTTP {login_response.status_code}")
        if login_response.soup.find("button", {"id": "checkpointSubmitButton"}):
            raise FacebookCheckpointError("Facebook requires a security checkpoint")

        c_user = self.client.session.cookies.get("c_user")
        if not c_user or not str(c_user).isnumeric():
            raise AuthenticationError("Facebook rejected the supplied email/password")

    @staticmethod
    def _extract_datr(text: str) -> str:
        match = re.search(r'"_js_datr","(.*?)"', text, re.MULTILINE)
        if not match:
            raise AuthenticationError("Could not extract Facebook datr token")
        return match.group(1)

    @staticmethod
    def _extract_pubkey(text: str) -> tuple[str, int]:
        match = re.search(r'"pubKey":\{"publicKey":"(.+?)","keyId":(\d+?)}}', text, re.MULTILINE)
        if not match:
            raise AuthenticationError("Could not extract Facebook login public key")
        return match.group(1), int(match.group(2))

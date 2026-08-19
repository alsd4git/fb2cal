"""Explicit Facebook session loading.

The loader intentionally accepts a file supplied by the user.  It never reads
browser profiles, decrypts browser databases, or discovers cookies implicitly.
"""

from __future__ import annotations

import json
import os
import stat
import warnings
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import requests

from .errors import CookieFileError


class FacebookSession(requests.Session):
    """A requests session with a safe, explicit cookie-file loader."""

    @classmethod
    def from_cookie_file(cls, path: str | os.PathLike[str]) -> FacebookSession:
        cookie_path = Path(path).expanduser()
        if not cookie_path.is_file():
            raise CookieFileError(f"Cookie file does not exist: {cookie_path}")

        try:
            mode = stat.S_IMODE(cookie_path.stat().st_mode)
            if mode & 0o077:
                warnings.warn(
                    f"Cookie file {cookie_path} is readable by other users; "
                    "restrict its permissions (for example chmod 600).",
                    UserWarning,
                    stacklevel=2,
                )
        except OSError as exc:
            raise CookieFileError(f"Could not inspect cookie file: {cookie_path}") from exc

        try:
            raw = json.loads(cookie_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise CookieFileError(f"Could not read cookie JSON: {cookie_path}") from exc

        cookies = raw.get("cookies") if isinstance(raw, Mapping) else raw
        if not isinstance(cookies, list):
            raise CookieFileError("Cookie JSON must be a list or an object with a 'cookies' list")

        session = cls()
        for item in cookies:
            cookie = cls._cookie_from_mapping(item)
            session.cookies.set_cookie(cookie)

        if not session.cookies.get("c_user"):
            raise CookieFileError("Cookie file does not contain the required c_user cookie")
        return session

    @staticmethod
    def _cookie_from_mapping(item: Any) -> requests.cookies.Cookie:
        if not isinstance(item, Mapping):
            raise CookieFileError("Each cookie must be an object")
        name = item.get("name")
        value = item.get("value")
        if not isinstance(name, str) or not name or not isinstance(value, str):
            raise CookieFileError("Each cookie requires string name and value fields")

        domain = item.get("domain", ".facebook.com")
        path = item.get("path", "/")
        if not isinstance(domain, str) or not isinstance(path, str):
            raise CookieFileError(f"Invalid domain/path for cookie {name}")

        kwargs: dict[str, Any] = {
            "domain": domain,
            "path": path,
            "secure": bool(item.get("secure", True)),
        }
        if item.get("expirationDate") is not None:
            try:
                kwargs["expires"] = int(item["expirationDate"])
            except (TypeError, ValueError) as exc:
                raise CookieFileError(f"Invalid expirationDate for cookie {name}") from exc
        elif item.get("expires") is not None:
            try:
                kwargs["expires"] = int(item["expires"])
            except (TypeError, ValueError) as exc:
                raise CookieFileError(f"Invalid expires value for cookie {name}") from exc

        return requests.cookies.create_cookie(name=name, value=value, **kwargs)

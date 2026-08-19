"""Strategies for extracting Facebook's ``fb_dtsg`` token from HTML."""

from __future__ import annotations

import html
import re

from .errors import TokenExtractionError


class FacebookDTSGParser:
    """Extract a CSRF token using a small, ordered set of known strategies."""

    _PATTERNS = (
        re.compile(r'\["DTSGInitialData",\[\],\{"token":"([^"]+)"'),
        re.compile(r'"DTSGInitialData"\s*,\s*\[\]\s*,\s*\{\s*"token"\s*:\s*"([^"]+)"'),
        re.compile(r'"token"\s*:\s*"([^"]+)"[^\n]{0,120}"DTSGInitialData"'),
    )

    @classmethod
    def extract(cls, html_text: str) -> str:
        if not isinstance(html_text, str):
            raise TokenExtractionError("Facebook birthday page is not text")
        candidate_text = html.unescape(html_text)
        for pattern in cls._PATTERNS:
            match = pattern.search(candidate_text)
            if match and match.group(1):
                return match.group(1)
        raise TokenExtractionError("Could not extract fb_dtsg from the Facebook birthday page")

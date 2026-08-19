import json
import os
import tempfile
import unittest
from pathlib import Path

from fb2cal.errors import CookieFileError
from fb2cal.facebook_session import FacebookSession


class TestFacebookSession(unittest.TestCase):
    def test_loads_full_cookie_export(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cookies.json"
            path.write_text(json.dumps({"cookies": [
                {"name": "c_user", "value": "123", "domain": ".facebook.com", "path": "/"},
                {"name": "xs", "value": "secret", "domain": ".facebook.com", "path": "/", "secure": True},
            ]}))
            os.chmod(path, 0o600)

            session = FacebookSession.from_cookie_file(path)

            self.assertEqual(session.cookies.get("c_user"), "123")
            self.assertEqual(session.cookies.get("xs"), "secret")

    def test_requires_c_user(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cookies.json"
            path.write_text(json.dumps([]))
            os.chmod(path, 0o600)
            with self.assertRaises(CookieFileError):
                FacebookSession.from_cookie_file(path)

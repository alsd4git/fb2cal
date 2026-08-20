import json
import types
import unittest
from unittest.mock import Mock

import requests

from fb2cal.errors import FacebookCheckpointError, SessionExpiredError
from fb2cal.facebook_client import FacebookClient


class TestFacebookClient(unittest.TestCase):
    def _client(self, page_text):
        session = requests.Session()
        session.cookies.set("c_user", "123", domain=".facebook.com")
        client = FacebookClient(session=session)
        client.browser.get = Mock(
            return_value=types.SimpleNamespace(
                status_code=200,
                text=page_text,
                url="https://www.facebook.com/events/birthdays/",
            )
        )
        return client

    def test_validate_session_extracts_token_without_network(self):
        client = self._client('["DTSGInitialData",[],{"token":"fixture-token"}]')
        validation = client.validate_session()
        self.assertEqual(validation.status, "authenticated")
        self.assertEqual(validation.user_id, "123")
        self.assertTrue(client.is_authenticated())

    def test_expired_and_checkpoint_states_are_typed(self):
        expired = self._client("<form id='login_form'></form>")
        with self.assertRaises(SessionExpiredError):
            expired.validate_session()

        checkpoint = self._client("checkpointSubmitButton")
        with self.assertRaises(FacebookCheckpointError):
            checkpoint.validate_session()

    def test_query_uses_sanitized_response_parser(self):
        client = self._client('["DTSGInitialData",[],{"token":"fixture-token"}]')
        client.browser.post = Mock(
            return_value=types.SimpleNamespace(
                status_code=200,
                text="for (;;);" + json.dumps({"data": {"viewer": {}}}),
            )
        )
        response = client.query_graph_ql_birthday_comet_monthly(0)
        self.assertIn("data", response)
        payload = client.browser.post.call_args.kwargs["data"]
        self.assertEqual(payload["fb_dtsg"], "fixture-token")

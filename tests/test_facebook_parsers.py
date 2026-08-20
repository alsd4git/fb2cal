import json
import unittest

from fb2cal.errors import GraphQLSchemaError, PersistedQueryError, TokenExtractionError
from fb2cal.facebook_queries import build_birthday_payload, parse_birthday_response
from fb2cal.facebook_token import FacebookDTSGParser


class TestFacebookParsers(unittest.TestCase):
    def test_token_fixture(self):
        html = '<script>["DTSGInitialData",[],{"token":"fixture-token"}]</script>'
        self.assertEqual(FacebookDTSGParser.extract(html), "fixture-token")

    def test_token_missing(self):
        with self.assertRaises(TokenExtractionError):
            FacebookDTSGParser.extract("<html>login required</html>")

    def test_graphql_payload_and_anti_hijacking(self):
        payload = build_birthday_payload(3, "fixture-token")
        self.assertEqual(json.loads(payload["variables"])["offset_month"], 3)
        parsed = parse_birthday_response('for (;;);{"data": {"viewer": {}}}')
        self.assertIn("data", parsed)

    def test_persisted_query_error_is_explicit(self):
        body = json.dumps(
            {"error": 100, "errorDescription": "Unknown persisted query doc_id"}
        )
        with self.assertRaises(PersistedQueryError):
            parse_birthday_response(body)

    def test_schema_error_without_data(self):
        with self.assertRaises(GraphQLSchemaError):
            parse_birthday_response('{"data": null}')

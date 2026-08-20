import json
import unittest

from fb2cal.contact import BirthdayContact
from fb2cal.json_exporter import JSONExporter
from fb2cal.vcard_exporter import VCardExporter


class TestExportersAndModel(unittest.TestCase):
    def setUp(self):
        self.contacts = [
            BirthdayContact(
                "1",
                "Leap",
                "https://facebook.com/leap",
                "https://img/leap",
                29,
                2,
                None,
            ),
            BirthdayContact(
                "2", "Known", "https://facebook.com/known", None, 4, 5, 1980
            ),
        ]

    def test_partial_year_is_preserved_in_json(self):
        payload = json.loads(
            JSONExporter(
                self.contacts, extracted_at="2025-01-01T00:00:00+00:00"
            ).export()
        )
        self.assertIsNone(payload["contacts"][0]["birthday"]["year"])
        self.assertEqual(payload["contacts"][0]["source"], "facebook")
        self.assertEqual(
            payload["summary"], {"contacts": 2, "with_year": 1, "without_year": 1}
        )

    def test_vcard_uses_partial_date_without_inventing_year(self):
        output = VCardExporter(self.contacts).export()
        self.assertIn("BDAY:--02-29", output)
        self.assertIn("BDAY:1980-05-04", output)

    def test_sorting_compares_other_day(self):
        self.assertLess(
            self.contacts[0], BirthdayContact("3", "Later", "", "", 1, 3, None)
        )

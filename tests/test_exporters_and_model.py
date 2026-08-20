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

    def test_vcard_4_is_default_and_uses_basic_dates(self):
        output = VCardExporter(self.contacts).export()
        self.assertIn("VERSION:4.0", output)
        self.assertIn("BDAY:--0229", output)
        self.assertIn("BDAY:19800504", output)

    def test_vcard_3_legacy_format_preserves_hyphenated_dates(self):
        output = VCardExporter(self.contacts, version="3.0").export()
        self.assertIn("VERSION:3.0", output)
        self.assertIn("BDAY:--02-29", output)
        self.assertIn("BDAY:1980-05-04", output)

    def test_vcard_lines_use_crlf_and_are_folded_to_75_octets(self):
        output = VCardExporter(self.contacts).export()
        self.assertNotIn("\n", output.replace("\r\n", ""))
        lines = output.encode("utf-8").split(b"\r\n")
        self.assertEqual(lines[-1], b"")
        self.assertTrue(all(len(line) <= 75 for line in lines[:-1]))

    def test_vcard_rejects_unsupported_version(self):
        with self.assertRaises(ValueError):
            VCardExporter(self.contacts, version="2.1")

    def test_sorting_compares_other_day(self):
        self.assertLess(
            self.contacts[0], BirthdayContact("3", "Later", "", "", 1, 3, None)
        )

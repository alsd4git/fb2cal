import io
import unittest
from contextlib import redirect_stderr

from fb2cal.__main__ import _print_recap, build_parser
from fb2cal.contact import BirthdayContact


class TestCliRecap(unittest.TestCase):
    def test_recap_reports_visible_contacts_and_years(self):
        contacts = [
            BirthdayContact("1", "Known", "", "", 1, 1, 2000),
            BirthdayContact("2", "Partial", "", "", 2, 2, None),
        ]
        output = io.StringIO()
        with redirect_stderr(output):
            _print_recap(contacts)
        self.assertIn("friends with visible birthdays: 2", output.getvalue())
        self.assertIn("birthdays with year: 1", output.getvalue())
        self.assertIn("birthdays without year: 1", output.getvalue())

    def test_vcard_version_defaults_to_4_and_accepts_legacy_flag(self):
        parser = build_parser()
        default_args = parser.parse_args(
            ["export", "--cookies", "cookies.json", "--format", "vcf"]
        )
        self.assertEqual(default_args.vcard_version, "4.0")

        legacy_args = parser.parse_args(
            [
                "export",
                "--cookies",
                "cookies.json",
                "--format",
                "vcf",
                "--vcard-version",
                "3.0",
            ]
        )
        self.assertEqual(legacy_args.vcard_version, "3.0")

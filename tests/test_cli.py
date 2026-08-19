import io
import unittest
from contextlib import redirect_stderr

from fb2cal.__main__ import _print_recap
from fb2cal.facebook_user import FacebookUser


class TestCliRecap(unittest.TestCase):
    def test_recap_reports_visible_contacts_and_years(self):
        contacts = [
            FacebookUser("1", "Known", "", "", 1, 1, 2000),
            FacebookUser("2", "Partial", "", "", 2, 2, None),
        ]
        output = io.StringIO()
        with redirect_stderr(output):
            _print_recap(contacts)
        self.assertIn("amici con compleanno visibile: 2", output.getvalue())
        self.assertIn("compleanni con anno: 1", output.getvalue())
        self.assertIn("compleanni senza anno: 1", output.getvalue())

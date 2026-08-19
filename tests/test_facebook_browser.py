import unittest

import requests

from fb2cal.facebook_browser import FacebookBrowser


class TestFacebookBrowserSession(unittest.TestCase):
    def test_uses_injected_session(self):
        session = requests.Session()
        session.cookies.set('c_user', '123456', domain='.facebook.com')

        facebook_browser = FacebookBrowser(session=session)

        self.assertIs(facebook_browser.session, session)
        self.assertIs(facebook_browser.browser.session, session)
        self.assertEqual(
            facebook_browser.browser.get_cookiejar().get('c_user'),
            '123456',
        )

    def test_creates_session_when_not_provided(self):
        facebook_browser = FacebookBrowser()

        self.assertIsInstance(facebook_browser.session, requests.Session)
        self.assertIs(facebook_browser.browser.session, facebook_browser.session)


if __name__ == '__main__':
    unittest.main()

import time
import unittest

from web_auth import create_session_token, render_login_html, verify_session_token


class WebAuthTests(unittest.TestCase):
    def test_round_trip_valid_session(self):
        token = create_session_token("admin", "secret", now=1_000)
        self.assertTrue(verify_session_token(token, "admin", "secret", now=1_100, max_age=200))

    def test_wrong_secret_is_rejected(self):
        token = create_session_token("admin", "secret", now=1_000)
        self.assertFalse(verify_session_token(token, "admin", "other", now=1_100, max_age=200))

    def test_expired_session_is_rejected(self):
        token = create_session_token("admin", "secret", now=1_000)
        self.assertFalse(verify_session_token(token, "admin", "secret", now=1_201, max_age=200))

    def test_wrong_username_is_rejected(self):
        token = create_session_token("admin", "secret", now=1_000)
        self.assertFalse(verify_session_token(token, "operator", "secret", now=1_100, max_age=200))

    def test_login_html_renders_css_and_error(self):
        html = render_login_html("Sai mật khẩu")
        self.assertIn("*{box-sizing:border-box}", html)
        self.assertIn("Sai mật khẩu", html)


if __name__ == "__main__":
    unittest.main()

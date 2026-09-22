import unittest
from pathlib import Path


class FrontendAuthTests(unittest.TestCase):
    def test_admin_api_requests_send_login_cookie(self):
        html = Path("web/index.html").read_text(encoding="utf-8")
        self.assertIn("credentials: 'include'", html)
        self.assertNotIn("credentials: 'omit'", html)

    def test_unauthorized_session_redirects_to_login_without_admin_key_prompt(self):
        html = Path("web/index.html").read_text(encoding="utf-8")
        self.assertIn("window.location.assign('/login')", html)
        self.assertNotIn("promptAdminKey();", html)


if __name__ == "__main__":
    unittest.main()

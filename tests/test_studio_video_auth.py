import unittest
from unittest.mock import patch

from fastapi import HTTPException

import server


class StudioVideoAuthTests(unittest.TestCase):
    def test_logged_in_studio_can_use_client_api_without_bearer(self):
        with patch.object(server.store, "has_enabled_keys", return_value=True):
            client = server._auth(None, web_session_valid=True)

        self.assertEqual(client["api_key_name"], "Studio Web Session")
        self.assertIsNone(client["api_key_hash"])

    def test_external_api_still_requires_bearer_token(self):
        with patch.object(server.store, "has_enabled_keys", return_value=True):
            with self.assertRaises(HTTPException) as caught:
                server._auth(None, web_session_valid=False)

        self.assertEqual(caught.exception.status_code, 401)
        self.assertEqual(caught.exception.detail, "missing bearer token")


if __name__ == "__main__":
    unittest.main()

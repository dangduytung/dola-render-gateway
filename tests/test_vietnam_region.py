import inspect
import unittest

import add_account
import browser
import config
import import_cookie
import server
import video_worker_ui


class VietnamRegionTests(unittest.TestCase):
    def test_runtime_defaults_to_vietnam_region(self):
        self.assertEqual(config.BROWSER_LOCALE, "vi-VN")
        self.assertEqual(config.BROWSER_TIMEZONE, "Asia/Ho_Chi_Minh")
        self.assertEqual(config.LIMIT_RESET_TZ, "Asia/Ho_Chi_Minh")

    def test_all_browser_launchers_use_shared_region_config(self):
        for module in (browser, add_account, import_cookie, server):
            source = inspect.getsource(module)
            self.assertNotIn('"locale": "ja-JP"', source)
            self.assertNotIn('"timezone_id": "Asia/Tokyo"', source)
            self.assertIn("config.BROWSER_LOCALE", source)
            self.assertIn("config.BROWSER_TIMEZONE", source)

    def test_video_controls_accept_vietnamese_labels(self):
        self.assertRegex("Tự động · 10 giây", video_worker_ui.SETTINGS_SUMMARY_RE)
        self.assertRegex("Tạo video", video_worker_ui.VIDEO_BUTTON_RE)
        self.assertRegex("10 giây", video_worker_ui.duration_option_re(10))


if __name__ == "__main__":
    unittest.main()

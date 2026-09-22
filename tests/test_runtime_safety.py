import inspect
import unittest

import server
import video_worker_ui


class RuntimeSafetyTests(unittest.TestCase):
    def test_task_polling_accepts_logged_in_studio_session(self):
        source = inspect.getsource(server.get_video)
        self.assertIn("request: Request", source)
        self.assertIn("web_session_valid=_web_session_valid(request)", source)

    def test_requested_duration_does_not_silently_fall_back(self):
        source = inspect.getsource(video_worker_ui.generate_video)
        self.assertNotIn("Failed to set duration, using default", source)
        self.assertIn("Requested duration", source)
        self.assertIn("not available in Dola UI", source)

    def test_requested_ratio_does_not_silently_fall_back(self):
        source = inspect.getsource(video_worker_ui.generate_video)
        self.assertNotIn("Failed to set ratio, using default", source)
        self.assertIn("Requested ratio", source)
        self.assertIn("not available in Dola UI", source)


if __name__ == "__main__":
    unittest.main()

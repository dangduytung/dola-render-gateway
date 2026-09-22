import asyncio
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from pydantic import ValidationError

import server


class VideoSequenceContractTests(unittest.TestCase):
    def test_sequence_accepts_configurable_segments_and_options(self):
        request = server.VideoSequenceRequest(
            name="Chuyến đi đêm",
            common_prompt="Giữ nguyên cô gái áo vàng và phong cách điện ảnh.",
            ratio="9:16",
            continuity="last_frame",
            output_mode="both",
            segments=[
                {"prompt": "Cô gái bước vào hẻm.", "model": "seedance-2.5", "duration": 10},
                {"prompt": "Cô nghe tiếng động và quay lại.", "model": "seedance-2.0", "duration": 15},
            ],
        )

        self.assertEqual(len(request.segments), 2)
        self.assertEqual(request.segments[1].duration, 15)
        self.assertEqual(request.continuity, "last_frame")
        self.assertEqual(request.output_mode, "both")

    def test_sequence_rejects_fewer_than_two_segments(self):
        with self.assertRaises(ValidationError):
            server.VideoSequenceRequest(
                common_prompt="same cast",
                segments=[{"prompt": "only one", "duration": 10}],
            )

    def test_sequence_rejects_unsupported_duration(self):
        with self.assertRaises(ValidationError):
            server.VideoSequenceRequest(
                segments=[
                    {"prompt": "one", "duration": 10},
                    {"prompt": "two", "duration": 12},
                ]
            )

    def test_compose_segment_prompt_combines_shared_and_segment_text(self):
        prompt = server._compose_segment_prompt(
            "Giữ nguyên nhân vật và ánh sáng.",
            "Nhân vật mở chiếc hộp.",
            2,
            4,
            True,
        )

        self.assertIn("Giữ nguyên nhân vật và ánh sáng.", prompt)
        self.assertIn("Cảnh 2/4", prompt)
        self.assertIn("tiếp diễn trực tiếp", prompt.lower())
        self.assertIn("Nhân vật mở chiếc hộp.", prompt)

    def test_frontend_exposes_configurable_sequence_controls(self):
        html = Path("web/index.html").read_text(encoding="utf-8")
        for marker in (
            'id="generation_mode"',
            'id="single_model_options"',
            'id="single_duration_options"',
            'id="sequence_segments"',
            'id="sequence_continuity"',
            'id="sequence_output_mode"',
            'id="gen_ref_files"',
            "uploadReferenceFiles(",
            "addSequenceSegment()",
            "/api/reference-images",
            "/v1/video-sequences",
        ):
            self.assertIn(marker, html)

    def test_local_reference_ids_are_accepted_without_public_url_resolution(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "safe-image.jpg").write_bytes(b"image")
            with patch.object(server.config, "REFERENCE_UPLOAD_DIR", tmp):
                refs = asyncio.run(server.validate_reference_urls(["local-ref://safe-image.jpg"]))
        self.assertEqual(refs, ["local-ref://safe-image.jpg"])

    def test_local_reference_ids_reject_path_traversal(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(server.config, "REFERENCE_UPLOAD_DIR", tmp):
                with self.assertRaises(ValueError):
                    asyncio.run(server.validate_reference_urls(["local-ref://../secret.jpg"]))

    def test_uploaded_image_validator_writes_verified_image(self):
        from io import BytesIO
        from PIL import Image

        with tempfile.TemporaryDirectory() as tmp:
            image = BytesIO()
            Image.new("RGB", (4, 4), "red").save(image, format="PNG")
            with patch.object(server.config, "REFERENCE_UPLOAD_DIR", tmp):
                ref = server._save_uploaded_reference("sample.png", image.getvalue())
                saved = Path(tmp) / ref.removeprefix("local-ref://")

            self.assertTrue(saved.exists())
            self.assertEqual(saved.suffix, ".png")

    def test_uploaded_image_validator_rejects_non_image(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(server.config, "REFERENCE_UPLOAD_DIR", tmp):
                with self.assertRaises(ValueError):
                    server._save_uploaded_reference("fake.png", b"not an image")


class VideoSequenceMediaTests(unittest.IsolatedAsyncioTestCase):
    async def test_extract_last_frame_invokes_ffmpeg_and_creates_jpeg(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source.mp4"
            target = Path(tmp) / "last.jpg"
            source.write_bytes(b"video")

            async def fake_exec(*args, **kwargs):
                target.write_bytes(b"jpeg")
                process = AsyncMock()
                process.communicate.return_value = (b"", b"")
                process.returncode = 0
                return process

            with patch("server.asyncio.create_subprocess_exec", side_effect=fake_exec) as execute:
                result = await server._extract_last_frame(source, target)

            self.assertEqual(result, target)
            args = execute.call_args.args
            self.assertEqual(args[0], "ffmpeg")
            self.assertIn("-sseof", args)
            self.assertTrue(target.exists())


if __name__ == "__main__":
    unittest.main()

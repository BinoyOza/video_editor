import json
import os
from django.conf import settings
from unittest.mock import patch

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from videos.models import Video


class VideoAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.api_token = "test_api_token"
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.api_token}")

        self.video1_path = self._create_test_video("video1.mp4", duration=10)
        self.video2_path = self._create_test_video("video2.mp4", duration=15)

        self.video1 = Video.objects.create(
            file=f"test_videos/video1.mp4",
            size=os.path.getsize(self.video1_path) / (1024 * 1024),
            duration=10,
        )
        self.video2 = Video.objects.create(
            file=f"test_videos/video2.mp4",
            size=os.path.getsize(self.video2_path) / (1024 * 1024),
            duration=15,
        )

    def _create_test_video(self, file_name, duration=10, fps=24):
        import os
        from moviepy.editor import ColorClip
        from django.conf import settings

        test_videos_dir = os.path.join(settings.MEDIA_ROOT, "test_videos")
        os.makedirs(test_videos_dir, exist_ok=True)

        file_path = os.path.join(test_videos_dir, file_name)

        clip = ColorClip(size=(640, 480), color=(255, 0, 0))
        clip = clip.set_duration(duration)
        clip = clip.set_fps(fps)
        clip.write_videofile(file_path, codec="libx264", fps=fps)

        return file_path

    def tearDown(self):
        import shutil

        test_videos_dir = os.path.join(settings.MEDIA_ROOT, "test_videos")
        if os.path.exists(test_videos_dir):
            shutil.rmtree(test_videos_dir)

    @patch("video_editor.middleware.StaticTokenAuthentication.authenticate")
    def test_upload_valid_video(self, mock_authenticate):
        mock_authenticate.return_value = (None, None)
        with open(self.video1_path, "rb") as video:
            response = self.client.post(
                "/api/videos/upload/",
                {"file": video, "title": video.name},
                format="multipart",
            )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        os.remove(os.path.join(settings.MEDIA_ROOT, "static", "videos",
                               response.data.get('file').split("/")[-1]))

    @patch("video_editor.middleware.StaticTokenAuthentication.authenticate")
    def test_upload_large_video(self, mock_authenticate):
        mock_authenticate.return_value = (None, None)
        large_video_path = self._create_test_video("large_video.mp4", duration=30, fps=24)

        os.truncate(large_video_path, 26 * 1024 * 1024)

        with open(large_video_path, "rb") as video:
            response = self.client.post(
                "/api/videos/upload/",
                {"file": video},
                format="multipart",
            )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("File size exceeds", str(response.data))

    @patch("video_editor.middleware.StaticTokenAuthentication.authenticate")
    def test_trim_video(self, mock_authenticate):
        mock_authenticate.return_value = (None, None)
        payload = {"start_time": 2, "end_time": 5}
        response = self.client.post(f"/api/videos/{self.video1.id}/trim/", data=payload,
                                    )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("trimmed_video", response.data)

    @patch("video_editor.middleware.StaticTokenAuthentication.authenticate")
    def test_merge_videos(self, mock_authenticate):
        mock_authenticate.return_value = (None, None)
        payload = {"video_ids": [self.video1.id, self.video2.id]}
        response = self.client.post("/api/videos/merge/", data=json.dumps(payload),
                                    content_type="application/json",)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("merged_video", response.data)

    @patch("video_editor.middleware.StaticTokenAuthentication.authenticate")
    def test_generate_shareable_link(self, mock_authenticate):
        mock_authenticate.return_value = (None, None)
        response = self.client.get(f"/api/videos/{self.video1.id}/share/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("video_url", response.data)

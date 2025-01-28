import os
from datetime import timedelta

from django.conf import settings
from django.utils.timezone import now
from rest_framework import status
from rest_framework.generics import get_object_or_404, ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from moviepy.editor import VideoFileClip, concatenate_videoclips

from videos.models import Video
from videos.serializers import VideoUploadSerializer


class VideoUploadView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = VideoUploadSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VideoTrimView(APIView):
    def post(self, request, video_id):
        try:
            video = get_object_or_404(Video, pk=video_id)
            start_time = int(request.data.get('start_time', 0))
            end_time = int(request.data.get('end_time', video.duration))

            output_dir = os.path.join(settings.MEDIA_ROOT, 'trimmed_static', 'videos')
            output_path = os.path.join(output_dir, f"trimmed_{os.path.basename(video.file.name)}")
            os.makedirs(output_dir, exist_ok=True)

            with VideoFileClip(video.file.path) as clip:
                video_duration = clip.duration
                if start_time < 0 or start_time >= video_duration:
                    return Response({
                        "error": f"Invalid start_time. Must be between 0 and {video_duration:.2f} seconds."
                    }, status=400)
                if end_time <= 0 or end_time > video_duration:
                    return Response({
                        "error": f"Invalid end_time. Must be between 0 and {video_duration:.2f} seconds."
                    }, status=400)
                if start_time >= end_time:
                    return Response({
                        "error": "start_time must be less than end_time."
                    }, status=400)

                output_dir = os.path.join(settings.MEDIA_ROOT, 'trimmed_static/videos/')
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, f"trimmed_{os.path.basename(video.file.name)}")

                trimmed_clip = clip.subclip(start_time, end_time)
                trimmed_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

            return Response({
                "message": "Video trimmed successfully.",
                "trimmed_video": output_path.replace(settings.MEDIA_ROOT, settings.MEDIA_URL)  # Convert path to URL
            }, status=200)

        except OSError as e:
            return Response({"error": f"OS error: {e}"}, status=500)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class VideoMergeView(APIView):
    def post(self, request):
        try:
            video_ids = request.data.get('video_ids', [])
            if not video_ids or len(video_ids) < 2:
                return Response({"error": "At least two video IDs are required for merging."}, status=400)

            videos = Video.objects.filter(id__in=video_ids)
            if len(videos) != len(video_ids):
                return Response({"error": "Some video IDs are invalid."}, status=400)

            clips = []
            for video in videos:
                clips.append(VideoFileClip(video.file.path))

            merged_clip = concatenate_videoclips(clips, method="compose")

            output_dir = os.path.join(settings.MEDIA_ROOT, 'merged_static/videos/')
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, "merged_video.mp4")

            merged_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

            for clip in clips:
                clip.close()
            merged_clip.close()

            merged_video_url = output_path.replace(settings.MEDIA_ROOT, settings.MEDIA_URL)
            return Response({"message": "Videos merged successfully.", "merged_video": merged_video_url}, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=500)


class ShareLinkView(APIView):
    def get(self, request, video_id):
        try:
            video = get_object_or_404(Video, pk=video_id)

            expiry_time = now() + timedelta(hours=1)
            video_url = video.file.url.replace(settings.MEDIA_ROOT, settings.MEDIA_URL)

            return Response({
                "message": "Temporary share link generated successfully.",
                "video_url": video_url,
                "expires_at": expiry_time
            }, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=500)


class VideoListView(ListAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoUploadSerializer


class VideoDetailView(RetrieveAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoUploadSerializer

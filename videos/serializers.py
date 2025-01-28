import tempfile

from django.conf import settings
from moviepy.video.io.VideoFileClip import VideoFileClip
from rest_framework import serializers
from .models import Video


class VideoUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'title', 'file', 'size', 'duration', 'uploaded_at']
        read_only_fields = ['id', 'size', 'duration', 'uploaded_at']

    def validate_file(self, file):
        size_mb = file.size / (1024 * 1024)
        max_size = getattr(settings, 'MAX_VIDEO_SIZE_MB', 25)
        if size_mb > max_size:
            raise serializers.ValidationError(f"File size exceeds the {max_size}MB limit.")

        min_duration = getattr(settings, 'MIN_VIDEO_DURATION_SECS', 5)
        max_duration = getattr(settings, 'MAX_VIDEO_DURATION_SECS', 25)
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
                for chunk in file.chunks():
                    temp_file.write(chunk)
                temp_file_path = temp_file.name

            with VideoFileClip(temp_file_path) as clip:
                duration = clip.duration
                if duration < min_duration:
                    raise serializers.ValidationError(
                        f"Video duration is too short. Minimum duration is {min_duration} seconds."
                    )
                if duration > max_duration:
                    raise serializers.ValidationError(
                        f"Video duration exceeds the maximum limit of {max_duration} seconds."
                    )
        except Exception as e:
            raise serializers.ValidationError(f"Error processing video: {str(e)}")

        return file

    def create(self, validated_data):
        video = validated_data.get('file')
        validated_data['size'] = video.size
        validated_data['duration'] = self.get_video_duration(video)
        return super().create(validated_data)

    def get_video_duration(self, video):
        return 120

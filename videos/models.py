from django.db import models
import os


class Video(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='static/videos/')
    size = models.FloatField()
    duration = models.FloatField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    expiry_time = models.DateTimeField(null=True, blank=True)

    def delete(self, *args, **kwargs):
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.title

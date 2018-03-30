from django.db import models
from django.utils import timezone

class MosaicArt(models.Model):
    ma_id = models.AutoField()
    user = models.ForeignKey('auth.User')
    file_name = models.CharField(max_length=200)
    original_image = models.CharField(max_length=200)
    created_date = models.DateTimeField(
            default=timezone.now)

    def __str__(self):
        return self.file_name

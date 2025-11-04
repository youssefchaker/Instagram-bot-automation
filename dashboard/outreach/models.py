from django.db import models

class ScrapedUser(models.Model):
    username = models.CharField(max_length=255)
    followed_by_viewer = models.BooleanField(default=False)
    requested_by_viewer = models.BooleanField(default=False)
    profile_url = models.URLField()

    def __str__(self):
        return self.username

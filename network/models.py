from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models


class User(AbstractUser):
    pass


class Posts(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE)
    time_posted = models.DateTimeField(auto_now_add=True)
    content = models.CharField(max_length=300)

    def __str__(self):
        return f"{self.user_id} - {self.time_posted}"


class Followers(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="user",
        on_delete=models.CASCADE)
    followed = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} followed {self.follows}"

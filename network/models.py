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

    class Meta:
        ordering = ["-time_posted"]

    def __str__(self):
        return f"{self.user_id} - {self.content}"


class Followers(models.Model):
    # TODO: Make user (user, followed) combination remains unique
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="user",
        on_delete=models.CASCADE)
    followed = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE)

    class Meta:
        """Make each row of user, followed unique"""
        constraints = [
            models.UniqueConstraint(
                fields=["user", "followed"],
                name="unq_user_followed"
            )
        ]

    def __str__(self):
        return f"{self.user} followed {self.followed}"

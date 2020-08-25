from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models


class User(AbstractUser):
    pass


class Post(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    time_posted = models.DateTimeField(auto_now_add=True)
    content = models.CharField(max_length=300)

    class Meta:
        ordering = ["-time_posted"]

    def __str__(self):
        return f"{self.user_id} - {self.content}"


class Follower(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="user",
        on_delete=models.CASCADE
    )
    followed = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    class Meta:
        """Make each row of user, followed unique"""
        constraints = [
            models.UniqueConstraint(
                fields=["user", "followed"],
                name="unq_user_follower"
            )
        ]

    def __str__(self):
        return f"{self.user} followed {self.followed}"


class Like(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE
    )

    class Meta:
        """Make each (user, liked post) unique"""
        constraints = [
            models.UniqueConstraint(
                fields=["user", "post"],
                name="unq_user_likes"
            )
        ]

    def __str__(self):
        return f"{self.user} liked: {self.post.content}"


from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile/<str:username>", views.view_profile, name="view_profile"),
    path("follow-unfollow", views.follow_unfollow, name="follow_unfollow"),
    path("following", views.following_view, name="following"),
    path("like-unlike", views.like_unlike, name="like_unlike")
]

import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse

from .models import User, Posts


def index(request):
    if request.method == "POST":
        content = json.loads(request.body)["content"]
        if not content:
            # When content is empty
            return JsonResponse({"invalid_post": True})
        post = Posts(user=request.user, content=content)
        post.save()
        return JsonResponse({"updated": True})
    # Gather all posts in reverse ordered by time posted
    posts = Posts.objects.all().order_by("-time_posted")
    return render(request, "network/index.html", {"posts": posts})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def view_profile(request, username):
    posts = Posts.objects.filter(user=User.objects.get(
        username=username)).order_by("-time_posted")
    selected_user = User.objects.get(username=username)
    can_follow = username != request.user.username
    context = {
        "posts": posts,
        "selected_user": selected_user,
        "can_follow": can_follow
    }
    return render(request, "network/profile.html", context)

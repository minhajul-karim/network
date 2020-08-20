import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse

from .models import User, Posts, Followers


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
    return HttpResponseRedirect(reverse("login"))


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
    # All posts of the user whose profile we wish to see
    posts = Posts.objects.filter(user=User.objects.get(
        username=username)).order_by("-time_posted")
    # user object for username
    user = User.objects.get(username=username)
    # The list of people the authonticated user follows
    user_follows = Followers.objects.filter(user=request.user)
    # Check if user already follows username
    follower_found = False
    for person in user_follows:
        if str(person.followed) == username:
            follower_found = True
            break
    # Check whether user is visiting his/her own profile
    self_profile = username == str(request.user)  # True or False
    context = {
        "posts": posts,
        "the_user": user,
        "self_profile": self_profile,
        "follower_found": follower_found
    }
    return render(request, "network/profile.html", context)

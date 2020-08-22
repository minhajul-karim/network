import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.urls import reverse

from .models import User, Posts, Followers


@login_required
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
    context = {
        "posts": posts,
        "can_post": True,
    }
    return render(request, "network/index.html", context)


def following_view(request):
    # Users in following list
    following = Followers.objects.filter(
        user=request.user.id).values_list("followed", flat=True)
    # Post of users in following list
    posts = Posts.objects.filter(
        user__in=following).order_by("-time_posted")
    context = {
        "posts": posts,
        "can_post": False,
    }
    return render(request, "network/index.html", context)


@login_required
def view_profile(request, username):
    """
    Display details of a user profile along with all posts.
    """
    # All posts of the user whose profile we wish to see
    try:
        posts = Posts.objects.filter(user=User.objects.get(
            username=username)).order_by("-time_posted")
    except ObjectDoesNotExist:
        return render(request, "network/404.html")
    # user object for username
    user = User.objects.get(username=username)
    # The list of people the authonticated user follows
    user_follows = Followers.objects.filter(user=request.user)
    # Check if user already follows the username
    already_follows = False
    for person in user_follows:
        if str(person.followed) == username:
            already_follows = True
            break
    # Check whether user is visiting his/her own profile
    self_profile = username == str(request.user)
    # Number of follows(How many people username follows)
    try:
        follows = Followers.objects.filter(
            user=User.objects.get(username=username)).count()
    except ObjectDoesNotExist:
        follows = 0
    # Number of followers(How many people follows username)
    try:
        followers = Followers.objects.filter(
            followed=User.objects.get(username=username)).count()
    except ObjectDoesNotExist:
        followers = 0
    context = {
        "posts": posts,
        "the_user": user,
        "self_profile": self_profile,
        "already_follows": already_follows,
        "followers": followers,
        "follows": follows
    }
    return render(request, "network/profile.html", context)


def follow_unfollow(request):
    if request.method == "POST":
        # user_id represents the person whom the authneticated user
        # wants to follow or unfollow
        user_id = json.loads(request.body)["userId"]
        already_follows = json.loads(request.body)["alreadyFollows"]
        if already_follows == "True":
            follower_to_be_deleted = Followers.objects.get(
                user=request.user.id,
                followed=user_id
            )
            follower_to_be_deleted.delete()
            return JsonResponse({"unfollowed": True})
        else:
            follower_to_be_added = Followers(
                user=User.objects.get(pk=request.user.id),
                followed=User.objects.get(pk=user_id)
            )
            follower_to_be_added.save()
            return JsonResponse({"followed": True})
    return render(request, "network/404.html")


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

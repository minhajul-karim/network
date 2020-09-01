import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
from django.db.models import Count, OuterRef, Exists

from .models import User, Post, Follower, Like


@login_required
def index(request):
    if request.method == "POST":
        content = json.loads(request.body)["content"]
        if not content:
            # When content is empty
            return JsonResponse({"invalid_post": True})
        post = Post(user=request.user, content=content)
        post.save()
        return JsonResponse({"updated": True})
    # All posts with info about whether user has liked
    # a post and the total number of likes per post
    posts = Post.objects.annotate(
        number_of_likes=Count("likes"),
        has_liked=Exists(
            Like.objects.filter(
                user=request.user,
                post=OuterRef('pk')))).order_by("-time_posted")
    # Show n posts per page
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
        "can_post": True
    }
    return render(request, "network/index.html", context)


def following_view(request):
    # The people whom user follows
    user = User.objects.get(pk=request.user.id)
    user_follows = user.follows.all().values_list("followed", flat=True)
    # Post of users in following list
    posts = Post.objects.filter(user__in=user_follows).annotate(
        number_of_likes=Count("like__post"),
        has_liked=Exists(
            Like.objects.filter(
                user=request.user,
                post=OuterRef('pk')))).order_by("-time_posted")
    # Show n posts per page
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
        "can_post": False
    }
    return render(request, "network/index.html", context)


@login_required
def view_profile(request, username):
    """
    Display details of a user profile along with all posts.
    """
    # All posts of the user whose profile we wish to see
    try:
        user = User.objects.get(username=username)
        posts = user.posts.all().annotate(
            number_of_likes=Count("likes"),
            has_liked=Exists(
                Like.objects.filter(
                    user=5,
                    post=OuterRef('pk')))).order_by("-time_posted")
    except ObjectDoesNotExist:
        return render(request, "network/404.html")
    # User object for username
    user = User.objects.get(username=username)
    # The list of people the authenticated user follows
    user_follows = Follower.objects.filter(user=request.user)
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
        follows = Follower.objects.filter(
            user=User.objects.get(username=username)).count()
    except ObjectDoesNotExist:
        follows = 0
    # Number of followers(How many people follows username)
    try:
        followers = Follower.objects.filter(
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
        # user_id represents the person whom the authenticated user
        # wants to follow or unfollow
        user_id = json.loads(request.body)["userId"]
        already_follows = json.loads(request.body)["alreadyFollows"]
        if already_follows == "True":
            follower_to_be_deleted = Follower.objects.get(
                user=request.user.id,
                followed=user_id
            )
            follower_to_be_deleted.delete()
            return JsonResponse({"unfollowed": True})
        else:
            try:
                Follower.objects.create(
                    user=User.objects.get(pk=request.user.id),
                    followed=User.objects.get(pk=user_id)
                )
            except IntegrityError:
                return JsonResponse({"error": True})
            return JsonResponse({"followed": True})
    return render(request, "network/404.html")


def like_unlike(request):
    if request.method == "POST":
        post_id = json.loads(request.body)["postId"]
        has_liked = json.loads(request.body)["hasLiked"]
        # When has_likes == "True", delete (user id, post id) from like
        if has_liked == "True":
            like = Like.objects.get(user=request.user.id, post=post_id)
            like.delete()
            return JsonResponse({"unliked": True})
        else:
            # insert (user id, post id) in Like
            new_like = Like(
                user=User.objects.get(pk=request.user.id),
                post=Post.objects.get(pk=post_id)
            )
            new_like.save()
            return JsonResponse({"liked": True})
    return render(request, "network/404.html")


def edit_post(request):
    if request.method == "POST":
        post_id = json.loads(request.body)["postId"]
        content = json.loads(request.body)["content"]
        post = Post.objects.get(pk=post_id)
        post.content = content
        post.save()
        return JsonResponse({
            "edited": True
        })
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
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(
                username,
                email,
                password,
                first_name=first_name,
                last_name=last_name
            )
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

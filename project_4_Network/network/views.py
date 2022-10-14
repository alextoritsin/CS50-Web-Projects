import json
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db import IntegrityError
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.core.paginator import Paginator

from .models import User, Post


def index(request):
    if request.method == "POST":
        content = request.POST['post']
        Post.objects.create(author=request.user, content=content)
        return redirect('index')
    else:
        posts = Post.objects.all()
        paginator = Paginator(posts, 10)

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'network/index.html', {
            "page_obj": page_obj,
        })
        


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


@ensure_csrf_cookie
def likes_management(request, post_id):

    # Query for requested post
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found"}, status=404)

    if request.method == "PUT":
        data = json.loads(request.body)
        if data.get("liked"):
            post.likes.add(request.user)  
        else:
            post.likes.remove(request.user)
        post.save()
        return JsonResponse(post.serialize())


@ensure_csrf_cookie
def follow_management(request, user_id):
    # get sub user
    follower = request.user

    # get user been followed
    try:
        profile = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        raise Http404("This user does not exist")

    if request.method == "PUT":
        data = json.loads(request.body)

        # unfollowing case
        if data.get("followed"):
            profile.followers.remove(follower)
            follower.following.remove(profile)
        else:
            # following case
            profile.followers.add(follower)
            follower.following.add(profile)
            
        profile.save()
        follower.save()
        # send modified profile object
        return JsonResponse(profile.serialize())


def profile(request, user_id):
    try:
        profile = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        raise Http404("This user does not exist")

    posts = profile.posts.all()
    paginator = Paginator(posts, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    
    return render(request, 'network/profile.html', {
        'profile': profile,
        'page_obj': page_obj,
    })


def following(request):
    # get all following users
    users = request.user.following.all()
    posts = Post.objects.filter(author__in=users).all()
    paginator = Paginator(posts, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'network/index.html', {
        "page_obj": page_obj,
    })


def edit_post(request, post_id):
    if request.method == 'PUT':
        post = get_object_or_404(Post, pk=post_id)
        if post.author != request.user:
            return JsonResponse({
                "error": "You're not allowed to edit another user's post"
            })
        else:
            now = timezone.localtime()
            data = json.loads(request.body)
            Post.objects.filter(pk=post_id).update(
                    content=data.get('content'),
                    updated=True,
                    timestamp=now,
            )
            return JsonResponse({
                "timestamp": now.strftime("%b %#d, %Y, %#I:%M %p"),
            })


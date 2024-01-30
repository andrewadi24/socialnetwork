from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import User, Post, Like, Following
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
import json
def index(request):
    posts = Post.objects.all().order_by('-date')
    for p in posts:
        if request.user.is_authenticated:
            p.is_liked = Like.objects.filter(liked_post=p, user=request.user).exists()
        else:
            p.is_liked = False
    posts_per_page = 10
    paginator = Paginator(posts, posts_per_page)

    page_number = request.GET.get('page')  # Get the current page number from the request's query parameters
    page_obj = paginator.get_page(page_number)  # Get the Page object for the current page number

    # Pass the `page_obj` to the template context
    context = {'page_obj': page_obj}
    return render(request, "network/index.html", context)


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

@csrf_exempt
@login_required
def create_post(request):
    if request.method == 'POST':
        print(request.POST)
        user_id = request.POST[('user_id')]
        content = request.POST[('content')]
        print(user_id, content)
        if not user_id or not content:
            return JsonResponse({'error': 'Missing user_id or content'}, status=400)
        post = Post.objects.create(user_id=user_id, content=content)
        return redirect('index')

    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
def profile_view(request, username):
    # Get the user object. If a User with the provided username doesn't exist, this will raise a Http404 exception.
    user = get_object_or_404(User, username=username)
    followed = False
    if request.user.is_authenticated:
        followed = Following.objects.filter(user=request.user, followed_user=user).exists()
    follower_count = Following.objects.filter(followed_user=user).count()
    following_count = Following.objects.filter(user = user).count()
    post_count = Post.objects.filter(user = user).count()
    # Render the profile template with the user's data.
    posts = Post.objects.filter(user = user).order_by('-date')
    for p in posts:
        if request.user.is_authenticated:
            p.is_liked = Like.objects.filter(liked_post=p, user=request.user).exists()
        else:
            p.is_liked = False
    posts_per_page = 10
    paginator = Paginator(posts, posts_per_page)

    page_number = request.GET.get('page')  # Get the current page number from the request's query parameters
    page_obj = paginator.get_page(page_number)  # Get the Page object for the current page number

    # Pass the `page_obj` to the template context
    context =  {
        'user': user,
        'posts' : posts,
        'followed' : followed,
        'follower_count' : follower_count,
        'following_count' : following_count,
        'post_count' : post_count,
        'page_obj': page_obj
    }
    return render(request, 'network/profile.html', context)


def toggle_like(request):
    post_id = request.GET.get('post_id')
    post = Post.objects.get(id=post_id)
    user = request.user
    liked = Like.objects.filter(liked_post=post, user=user).exists()
    if liked:
        #delete like
        Like.objects.filter(liked_post=post, user=user).delete()
        post.like_count -= 1
        post.save()
        pass
    else:
        # Create like and save
        new_like = Like(liked_post=post, user=user)
        new_like.save()
        # Increment the like_count
        post.like_count += 1
        post.save()
    return JsonResponse({'liked': liked})


def toggle_follow(request):
    followed_user_name = request.GET.get('follows')
    print(followed_user_name)
    followedUser = User.objects.get(username=followed_user_name)
    user = request.user
    followed = Following.objects.filter(user=user, followed_user=followedUser).exists()
    if not followed:
        follow = Following(user=user, followed_user=followedUser)
        follow.save()
    else:
        Following.objects.filter(user=request.user, followed_user = followedUser).delete()
    follower_count = Following.objects.filter(followed_user=followedUser).count()
    return JsonResponse({'followed': not followed, 'follower_count' : follower_count})

def update_post(request, post_id):
    if request.method == 'PUT':
        data = json.loads(request.body)
        post = Post.objects.get(id=post_id)
        post.content = data.get('content', post.content)
        post.save()
        return JsonResponse({'message': 'Post updated successfully'}, status=200)
    

def following_page(request):
    following_objects = Following.objects.filter(user=request.user)
    following_users = following_objects.values_list('followed_user', flat=True)
    posts = Post.objects.filter(user__in=following_users).order_by('-date')
    for p in posts:
        if request.user.is_authenticated:
            p.is_liked = Like.objects.filter(liked_post=p, user=request.user).exists()
        else:
            p.is_liked = False
    posts_per_page = 10
    paginator = Paginator(posts, posts_per_page)

    page_number = request.GET.get('page')  # Get the current page number from the request's query parameters
    page_obj = paginator.get_page(page_number)  # Get the Page object for the current page number

    # Pass the `page_obj` to the template context
    context = {'page_obj': page_obj}
    return render(request, "network/following_page.html", context)
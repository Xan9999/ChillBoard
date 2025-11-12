
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import User
from .models import ImagePost
from .forms import ImagePostForm, CustomUserCreationForm
from django.contrib.auth.forms import AuthenticationForm

# Create your views here.


# 1. Home – list all users with boards
def home(request):
    users = ImagePost.objects.values('user__username').distinct()
    return render(request, 'home.html', {'users': users})

# 2. Post image (login required)
@login_required
def post_image(request):
    if request.method == 'POST':
        form = ImagePostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('user_board', username=request.user.username)
    else:
        form = ImagePostForm()
    return render(request, 'post.html', {'form': form})

# 3. View a user's board
def user_board(request, username):
    user = get_object_or_404(User, username=username)
    images = user.images.all().order_by('-created_at')
    return render(request, 'board.html', {'board_user': user, 'images': images})

# 4. Login

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('home')
        else:   
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()  # Empty form for GET

    return render(request, 'login.html', {'form': form})

# 5. Logout
def logout_view(request):
    logout(request)
    return redirect('home')

# 6. Register
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            messages.success(request, 'Account created successfully')
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
        messages.error(request, 'Please correct the errors below')
    return render(request, 'register.html', {'form': form})
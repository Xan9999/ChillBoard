
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import User
from .models import ImagePost
from .models import BackgroundImage
from .models import DEFAULT_BACKGROUND_IMAGE, DEFAULT_PROFILE_IMAGE, ProfileImage
from .forms import ImagePostForm, BackgroundPostForm, ProfilePostForm, CustomUserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
import json
from django.templatetags.static import static

# Create your views here.


# 1. Home – list all users with boards
def home(request):
    users = User.objects.all().order_by('username')
    profiles = ProfileImage.objects.filter(user__in=users)
    profile_by_user_id = {p.user_id: p for p in profiles}
    for user in users:
        profile = profile_by_user_id.get(user.id)
        if profile and profile.image:
            user.profile_url = static(profile.image.name) if profile.image.name == DEFAULT_PROFILE_IMAGE else profile.image.url
        else:
            user.profile_url = None
    return render(request, 'home.html', {'users': users})

# 2. Post image (login required)
@login_required
def post_image(request):
    if request.method == 'POST':
        form = ImagePostForm(request.POST, request.FILES)
        if form.is_valid():
            a = request.POST.get('pos', '{}').split(',')
            post = form.save(commit=False)
            post.user = request.user
            post.pos_x = int(float(a[0])) if len(a) > 0 else 0
            post.pos_y = int(float(a[1])) if len(a) > 1 else 0
            post.save()
            return redirect('user_board', username=request.user.username)
    else:
        form = ImagePostForm()
    return render(request, 'post.html', {'form': form})

@login_required
def delete_image(request, image_id):
    image = get_object_or_404(ImagePost, id=image_id, user=request.user)
    if request.method == 'POST':
        image.image.delete(save=False) 
        image.delete()
        messages.success(request, 'Image deleted successfully.')
        return redirect('user_board', username=request.user.username)
    return render(request, 'confirm_delete.html', {'image': image})

# 3. View a user's board
def user_board(request, username):
    user = get_object_or_404(User, username=username)
    images = user.images.all().order_by('-created_at')
    try:
        background = user.background
    except BackgroundImage.DoesNotExist:
        background = None
    background_url = None
    if background and background.background:
        background_url = static(background.background.name) if background.background.name == DEFAULT_BACKGROUND_IMAGE else background.background.url
    return render(request, 'board.html', {'board_user': user, 'images': images, 'background': background, 'background_url': background_url})

@login_required
def upload_background(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'invalid method'}, status=405)

    form = BackgroundPostForm(request.POST, request.FILES)
    if not form.is_valid():
        return JsonResponse({'error': 'invalid form', 'details': form.errors}, status=400)

    background_obj, _created = BackgroundImage.objects.get_or_create(user=request.user)
    if background_obj.background:
        if background_obj.background.name != DEFAULT_BACKGROUND_IMAGE:
            background_obj.background.delete(save=False)

    background_obj.background = form.cleaned_data['background']
    background_obj.save()
    return JsonResponse({'status': 'ok'})

@login_required
def upload_profile(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'invalid method'}, status=405)

    form = ProfilePostForm(request.POST, request.FILES)
    if not form.is_valid():
        return JsonResponse({'error': 'invalid form', 'details': form.errors}, status=400)

    profile_obj, _created = ProfileImage.objects.get_or_create(user=request.user)
    if profile_obj.image:
        if profile_obj.image.name != DEFAULT_PROFILE_IMAGE:
            profile_obj.image.delete(save=False)

    profile_obj.image = form.cleaned_data['image']
    profile_obj.save()
    return JsonResponse({'status': 'ok'})

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
            user = form.save()
            ProfileImage.objects.get_or_create(user=user)
            BackgroundImage.objects.get_or_create(user=user)
            return redirect('login')
    else:
        form = CustomUserCreationForm()
        messages.error(request, 'Please correct the errors below')
    return render(request, 'register.html', {'form': form})

@login_required
def save_position(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            image_id = data.get('id')
            x = int(float(data.get('x', 0)))  # handle "123px"
            y = int(float(data.get('y', 0)))

            img = ImagePost.objects.get(id=image_id, user=request.user)
            img.pos_x = x
            img.pos_y = y
            img.width = data['width']
            img.height = data['height']
            img.save()

            return JsonResponse({'status': 'saved', 'x': x, 'y': y})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'invalid method'}, status=405)


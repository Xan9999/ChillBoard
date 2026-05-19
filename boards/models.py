from django.db import models
from django.contrib.auth.models import User

def background_upload_to(instance, filename: str) -> str:
    return f"backgrounds/user_{instance.user_id}/{filename}"

def profile_upload_to(instance, filename: str) -> str:
    return f"profiles/user_{instance.user_id}/{filename}"

DEFAULT_PROFILE_IMAGE = "default_profile_image.png"
DEFAULT_BACKGROUND_IMAGE = "Gallery_texture.jpg"

class ImagePost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='boards/%Y/%m/%d/')
    caption = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    pos_x = models.IntegerField(default=100)   # pozicija slik
    pos_y = models.IntegerField(default=100)
    
    width = models.IntegerField(default=200)
    height = models.IntegerField(default=200)   

    def __str__(self):
        return f"{self.user.username} - {self.caption or 'Image'}"
    
class BackgroundImage(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='background')
    background = models.ImageField(upload_to=background_upload_to, default=DEFAULT_BACKGROUND_IMAGE)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - background"

class ProfileImage(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    image = models.ImageField(upload_to=profile_upload_to, default=DEFAULT_PROFILE_IMAGE)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - profile"

class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f"{self.follower.username} → {self.following.username}"

class Comment(models.Model):
    board_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='board_comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='written_comments')
    text = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.author.username} on {self.board_user.username}'s board"


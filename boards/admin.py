from django.contrib import admin
from .models import ImagePost, BackgroundImage, ProfileImage
# Register your models here.

admin.site.register(ImagePost)
admin.site.register(BackgroundImage)
admin.site.register(ProfileImage)

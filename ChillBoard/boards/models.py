from django.db import models
from django.contrib.auth.models import User

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


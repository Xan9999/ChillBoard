from django import forms
from .models import ImagePost
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class ImagePostForm(forms.ModelForm):
    class Meta:
        model = ImagePost
        fields = ['image', 'caption']
        widgets = {
            'caption': forms.TextInput(attrs={'placeholder': 'Add a caption...'})
        }

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


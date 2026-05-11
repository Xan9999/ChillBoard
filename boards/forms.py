from django import forms
from .models import ImagePost
from .models import BackgroundImage
from .models import ProfileImage
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class ImagePostForm(forms.ModelForm):
    class Meta:
        model = ImagePost
        fields = ['image', 'caption']
        widgets = {
            'caption': forms.TextInput(attrs={'placeholder': 'Add a caption...'})
        }

class BackgroundPostForm(forms.ModelForm):
    class Meta:
        model = BackgroundImage
        fields = ['background']

    def clean_background(self):
        file = self.cleaned_data.get('background')
        if not file:
            return file
        content_type = getattr(file, "content_type", "")
        if content_type and not content_type.startswith("image/"):
            raise forms.ValidationError("Only image files are allowed.")
        max_bytes = 10 * 1024 * 1024
        if file.size > max_bytes:
            raise forms.ValidationError("Background image must be 10MB or smaller.")
        return file

class ProfilePostForm(forms.ModelForm):
    class Meta:
        model = ProfileImage
        fields = ['image']

    def clean_image(self):
        file = self.cleaned_data.get('image')
        if not file:
            return file
        content_type = getattr(file, "content_type", "")
        if content_type and not content_type.startswith("image/"):
            raise forms.ValidationError("Only image files are allowed.")
        max_bytes = 10 * 1024 * 1024
        if file.size > max_bytes:
            raise forms.ValidationError("Profile image must be 10MB or smaller.")
        return file

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


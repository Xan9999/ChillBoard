from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('post/', views.post_image, name='post_image'),
    path('@<username>/', views.user_board, name='user_board'),
]
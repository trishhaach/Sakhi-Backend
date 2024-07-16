from django.urls import path, include
from user.views import UserResgistrationView

urlpatterns = [
    path('register/', UserResgistrationView.as_view(), name='register'),
]

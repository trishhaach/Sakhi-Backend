from django.urls import path, include
from user.views import UserRegistrationView, UserLoginView, UserProfileView, UserChangePasswordView, SendPasswordResetEmailView, UserPasswordResetView
# GoogleLoginCallbackView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('changepassword/', UserChangePasswordView.as_view(), name='changepassword'),
    path('sendresetpasswordemail/', SendPasswordResetEmailView.as_view(), name='sendresetpasswordemail'),
    path('resetpassword/<uidb64>/<token>/', UserPasswordResetView.as_view(), name='resetpassword'),
    # path('accounts/',include("allauth.urls")),
    # path('accounts/google/login/callback/', GoogleLoginCallbackView.as_view(), name='google_callback'),
]

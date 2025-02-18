


from django.urls import path
from user.views import UserRegistrationView, UserLoginView, UserProfileView, UserChangePasswordView, SendPasswordResetEmailView, UserPasswordResetView, UserUpdateView, UserDeleteView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from user.views import NonClinicalDetectionView, AdvancedDetectionView
from .views import NonClinicalDetectionResultsView, AdvancedDetectionResultsView, TrackPeriodCreateView, TrackPeriodRetrieveView, SymptomCategoryListView, SymptomListView
from .views import SymptomTrackCreateView, SymptomTrackListView
from rest_framework.permissions import AllowAny

# API Documentation setup
schema_view = get_schema_view(
    openapi.Info(
        title="Sakhi API",
        default_version='v1',
        description="API documentation for Sakhi backend",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="support@sakhi.local"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[AllowAny]  # Allow any user to access docs
)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('changepassword/', UserChangePasswordView.as_view(), name='changepassword'),
    path('sendresetpasswordemail/', SendPasswordResetEmailView.as_view(), name='sendresetpasswordemail'),
    path('resetpassword/<uidb64>/<token>/', UserPasswordResetView.as_view(), name='resetpassword'),
    path('user/update/', UserUpdateView.as_view(), name='user-update'),  
    path('user/delete/', UserDeleteView.as_view(), name='user-delete'),
    path('nonclinical/results/', NonClinicalDetectionResultsView.as_view(), name='nonclinical-results'),
    path('advanced/results/', AdvancedDetectionResultsView.as_view(), name='advanced-results'),
    path('nonclinical/', NonClinicalDetectionView.as_view(), name='nonclinical-detection'),
    path('advanced/', AdvancedDetectionView.as_view(), name='advanced-detection'),
    path('track-period/', TrackPeriodCreateView.as_view(), name='track-period-create'),  # Create period
    path('track-period/history/', TrackPeriodRetrieveView.as_view(), name='track-period-history'),  # Retrieve period history
    path('symptom-categories/', SymptomCategoryListView.as_view(), name='symptom-category-list'),
    path('symptoms/<int:category_id>/', SymptomListView.as_view(), name='symptom-list'),
    path('track-symptom/', SymptomTrackCreateView.as_view(), name='track-symptom'),
    path('tracked-symptoms/', SymptomTrackListView.as_view(), name='tracked-symptoms'),
    


    # Swagger UI documentation URL
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]

from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, login_page, register_page

urlpatterns = [
    path('api/register/', RegisterView.as_view(), name='api_register'),
    path('api/login/', TokenObtainPairView.as_view(), name='api_login'),
    path('api/login/refresh/', TokenRefreshView.as_view(), name='api_refresh'),
    path('login/', login_page, name='login_page'),
    path('register/', register_page, name='register_page'),
]

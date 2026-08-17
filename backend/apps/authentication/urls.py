from django.urls import path

from .views import (
    ChangePasswordView,
    CustomTokenObtainPairView,
    ForgotPasswordView,
    LogoutView,
    MeView,
    RegisterView,
    ResetPasswordConfirmView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='auth-login'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),
    path('me/', MeView.as_view(), name='auth-me'),
    path('change-password/', ChangePasswordView.as_view(), name='auth-change-password'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='auth-forgot-password'),
    path('reset-password/', ResetPasswordConfirmView.as_view(), name='auth-reset-password'),
]

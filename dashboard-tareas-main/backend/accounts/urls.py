from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, MeView, ExecutorsView, AdminCreateUserView, ChangePasswordView

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="auth_register"),
    path("auth/login/", TokenObtainPairView.as_view(), name="auth_login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="auth_refresh"),
    path("auth/me/", MeView.as_view(), name="auth_me"),
    path("auth/change-password/", ChangePasswordView.as_view(), name="auth_change_password"),
    path("users/executors/", ExecutorsView.as_view(), name="executors_list"),
    path("users/create/", AdminCreateUserView.as_view(), name="create_user"),
]

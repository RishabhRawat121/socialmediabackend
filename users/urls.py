from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    ChangePasswordView,
    PasswordResetView,
    PasswordResetConfirmView,
    MeProfileView,
    MeProfileUpdateView,
    view_profile
)
from .views import create_notification
from . import views
from .views import notify_post_action

from .views import UserNotificationsView
from .views import NotificationListView
from .views import toggle_follow
urlpatterns = [
    # Authentication
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),

    path("logout/", LogoutView.as_view(), name="logout"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),

    # Password reset
    path("password-reset/", PasswordResetView.as_view(), name="password-reset"),
    path("password-reset-confirm/", PasswordResetConfirmView.as_view(), name="password-reset-confirm"),

    # JWT
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Profile
    path("me/", MeProfileView.as_view(), name="me-profile"),
    path("me/update/", MeProfileUpdateView.as_view(), name="me-profile-update"),
    path("profile/<int:user_id>/", view_profile, name="view-profile"),
    

    path('like/<int:post_id>/', views.like_post, name="like_post"),
    path('notifications/', views.get_notifications, name="get_notifications"),
    path('api/posts/<int:post_id>/notify/', notify_post_action, name='notify_post_action'),

    path('posts/<int:post_id>/notify/', create_notification, name='create-notification'),
    path('notifications/', UserNotificationsView.as_view(), name='user-notifications'),
    path('notifications/', NotificationListView.as_view(), name='notifications'),

       # User search
    path("search/", views.UserSearchView.as_view(), name="user-search"),

    # urls.py
 path("profile/<int:user_id>/follow/", views.toggle_follow, name="toggle-follow"),


]

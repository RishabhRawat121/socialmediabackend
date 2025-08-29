from django.urls import path
from .views import (
    PostListCreateView,
    PostLikeToggleView,
    CommentListCreateView,
    NotificationListView,
    NotificationMarkReadView,
)

urlpatterns = [
    # Posts
    path("", PostListCreateView.as_view(), name="post-list-create"),
    path("<int:post_id>/like/", PostLikeToggleView.as_view(), name="post-like-toggle"),

    # Comments
    path("<int:post_id>/comments/", CommentListCreateView.as_view(), name="comment-list-create"),

    # Notifications
    path("notifications/", NotificationListView.as_view(), name="notifications"),
    path("notifications/<int:pk>/read/", NotificationMarkReadView.as_view(), name="notif-read"),
]

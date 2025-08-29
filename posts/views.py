from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from .models import Post, Comment, Like, Notification
from .serializers import PostSerializer, CommentSerializer, NotificationSerializer

# ----------------- Posts -----------------
class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all().select_related("author").prefetch_related("likes", "comments__author")
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

# ----------------- Likes -----------------
class PostLikeToggleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        like, created = Like.objects.get_or_create(post=post, user=request.user)

        if not created:
            like.delete()
            return Response({"message": "Like removed"}, status=status.HTTP_200_OK)

        # Notification for post author
        if post.author != request.user:
            Notification.objects.create(
                post=post,
                sender=request.user,
                receiver=post.author,
                notification_type='like',
                message=f"{request.user.username} liked your post"
            )

        return Response({"message": "Post liked"}, status=status.HTTP_201_CREATED)

# ----------------- Comments -----------------
class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        post_id = self.kwargs["post_id"]
        return Comment.objects.filter(post_id=post_id).select_related("author").order_by("-created_at")

    def perform_create(self, serializer):
        post_id = self.kwargs["post_id"]
        post = get_object_or_404(Post, id=post_id)
        comment = serializer.save(author=self.request.user, post=post)

        # Notification for post author
        if post.author != self.request.user:
            Notification.objects.create(
                post=post,
                sender=self.request.user,
                receiver=post.author,
                notification_type='comment',
                message=f"{self.request.user.username} commented: {comment.content}"
            )

# ----------------- Notifications -----------------
class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(receiver=self.request.user).order_by('-created_at')

class NotificationMarkReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        notif = get_object_or_404(Notification, pk=pk, receiver=request.user)
        notif.is_read = True
        notif.save(update_fields=["is_read"])
        return Response({"message": "Notification marked as read"}, status=status.HTTP_200_OK)

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.contrib.auth import get_user_model

# --------------------------
# Custom User
# --------------------------
class User(AbstractUser):
    # Avoid reverse accessor clashes
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return self.username

# --------------------------
# Profile
# --------------------------
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    avatar_url = models.URLField(max_length=500, blank=True, null=True)  # Supabase URL
    website = models.URLField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    visibility = models.CharField(
        max_length=20,
        choices=[("public", "Public"), ("private", "Private"), ("followers_only", "Followers Only")],
        default="public",
    )
    followers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='following', blank=True)

    def __str__(self):
        return f"Profile of {self.user.username}"

# --------------------------
# Post
# --------------------------
class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts")
    image_url = models.URLField(blank=True)
    caption = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Post {self.id} by {self.user.username}"

# --------------------------
# Follow (optional, can use Profile.followers instead)
# --------------------------
class Follow(models.Model):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="following_set")
    following = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="followers_set")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower", "following")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"

# --------------------------
# Notification
# --------------------------
User = get_user_model()

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('like', 'Like'),
        ('comment', 'Comment'),
    ]
    
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="notifications")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_notifications")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_notifications")
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField(blank=True, null=True)  # optional
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']  # newest first
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return f"Notification: {self.sender.username} {self.notification_type} on Post {self.post.id}"

    def mark_as_read(self):
        """Mark this notification as read."""
        self.is_read = True
        self.save()

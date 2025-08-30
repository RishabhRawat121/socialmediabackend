from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from .models import Profile, Post, Follow, Notification

User = get_user_model()


# --------------------------
# Register Serializer
# --------------------------
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "first_name", "last_name"]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", "")
        )
        Profile.objects.create(user=user)
        return user

# users/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import LoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken

class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }, status=status.HTTP_200_OK)


# --------------------------
# Profile Serializer
# --------------------------
class ProfileSerializer(serializers.ModelSerializer):
    avatar_url = serializers.URLField(read_only=True)

    class Meta:
        model = Profile
        fields = ["bio", "avatar_url", "website", "location", "visibility"]


# --------------------------
# User Serializer with stats
# --------------------------
class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    posts_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "profile",
            "followers_count",
            "following_count",
            "posts_count",
        ]

    def get_followers_count(self, obj):
        return Follow.objects.filter(following=obj).count()

    def get_following_count(self, obj):
        return Follow.objects.filter(follower=obj).count()

    def get_posts_count(self, obj):
        return Post.objects.filter(user=obj).count()


# --------------------------
# Post Serializer
# --------------------------
class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["id", "user", "image_url", "caption", "created_at"]
        read_only_fields = ["id", "created_at", "user"]


# --------------------------
# Notification Serializer
# --------------------------
class NotificationSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField()
    receiver = serializers.StringRelatedField()
    post = serializers.StringRelatedField()

    class Meta:
        model = Notification
        fields = "__all__"

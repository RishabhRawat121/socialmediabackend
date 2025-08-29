from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from .models import Profile, Post, Follow
from .supabase_utils import upload_avatar  # your utility function

User = get_user_model()


# --------------------------
# Register Serializer
# --------------------------
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()

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



# --------------------------
# Login Serializer
# --------------------------
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

User = get_user_model()

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        if not username and not email:
            raise serializers.ValidationError("Username or email is required")
        
        if not password:
            raise serializers.ValidationError("Password is required")
        
        # Authenticate user
        user = None
        
        if username:
            user = authenticate(username=username, password=password)
        elif email:
            try:
                user_obj = User.objects.get(email=email)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled")
        
        data['user'] = user
        return data

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


from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField()
    receiver = serializers.StringRelatedField()
    post = serializers.StringRelatedField()

    class Meta:
        model = Notification
        fields = '__all__'


from rest_framework import status, generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    ProfileSerializer,
)
from .models import Profile, Post, Follow
from .supabase_utils import upload_avatar
from django.db.models import Q
import time

User = get_user_model()
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, UserSerializer
from .supabase_utils import create_supabase_user

User = get_user_model()

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer
from .supabase_utils import create_supabase_user, upload_avatar
from .models import Profile

User = get_user_model()

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        # if not serializer.is_valid():
        #  print("Serializer errors:", serializer.errors)  # 🔍 debug
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            data = serializer.validated_data

            # Validate username (letters, numbers, @/./+/-/_ only)
            username = data["username"]
            if not all(c.isalnum() or c in "@.+-_" for c in username):
                return Response(
                    {"username": "Enter a valid username (letters, numbers, @/./+/-/_ only)"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 1️⃣ Create Django user
            user = User.objects.create_user(
                username=username,
                email=data["email"],
                password=data["password"],
                first_name=data.get("first_name", ""),
                last_name=data.get("last_name", ""),
            )

            # 2️⃣ Create profile
            profile = Profile.objects.create(user=user)

            # Optional: upload avatar if file is sent
            if request.FILES.get("avatar"):
                profile.avatar_url = upload_avatar(request.FILES["avatar"])
                profile.save()

            # 3️⃣ Create Supabase user
            success, supabase_user_id = create_supabase_user(
                email=data["email"],
                password=data["password"]
            )

            if not success:
                print("Supabase registration failed:", supabase_user_id)
                return Response(
                    {"error": "Supabase registration failed"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Optional: save username in Supabase table "profiles"
            try:
                supabase.table("profiles").insert({
                    "id": supabase_user_id,
                    "username": username
                }).execute()
            except Exception as e:
                print("Supabase table insert error:", e)

            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# --------------------------
# Login
# --------------------------
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, ProfileSerializer
from .models import Profile

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            # Get the authenticated user from serializer validation
            user = serializer.validated_data['user']
            
            # Get or create profile
            profile, _ = Profile.objects.get_or_create(user=user)
            
            # Prepare user data
            user_data = UserSerializer(user).data
            user_data["profile"] = ProfileSerializer(profile).data

            # Generate tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "user": user_data
            })
        
        # Print serializer errors for debugging
        print("Login serializer errors:", serializer.errors)
        return Response(serializer.errors, status=400)
# --------------------------
# Logout
# --------------------------
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)


# --------------------------
# Change Password
# --------------------------
class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        new_password = request.data.get("new_password")
        if not new_password:
            return Response({"error": "New password required"}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        user.password = make_password(new_password)
        user.save()
        return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)


# --------------------------
# Password Reset
# --------------------------
class PasswordResetView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
            send_mail(
                subject="Password Reset Request",
                message="Click the link to reset your password.",
                from_email="noreply@example.com",
                recipient_list=[email],
            )
            return Response({"message": "Password reset email sent"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "Email not found"}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        new_password = request.data.get("new_password")
        if not email or not new_password:
            return Response({"error": "Email and new password required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
            user.password = make_password(new_password)
            user.save()
            return Response({"message": "Password reset successfully"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "Invalid email"}, status=status.HTTP_400_BAD_REQUEST)


# --------------------------
# Me Profile
# --------------------------
class MeProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        profile, _ = Profile.objects.get_or_create(user=user)
        data = {
            "username": user.username,
            "email": user.email,
            "bio": profile.bio,
            "website": profile.website,
            "location": profile.location,
            "avatar_url": profile.avatar_url,
            "followers_count": Follow.objects.filter(following=user).count(),
            "following_count": Follow.objects.filter(follower=user).count(),
            "posts_count": Post.objects.filter(user=user).count(),
        }
        return Response(data)


# --------------------------
# Update Profile + Avatar
# --------------------------
class MeProfileUpdateView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user.profile

    def patch(self, request, *args, **kwargs):
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        avatar_file = request.FILES.get("avatar")
        if avatar_file:
            public_url = upload_avatar(avatar_file)
            if public_url:
                serializer.validated_data["avatar_url"] = public_url

        serializer.save()
        profile.refresh_from_db()

        user_data = UserSerializer(request.user).data
        if profile.avatar_url:
            user_data["profile"]["avatar_url"] += f"?t={int(time.time())}"

        return Response(user_data)


# --------------------------
# View another user's profile
# --------------------------
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def view_profile(request, user_id):
    try:
        profile = Profile.objects.get(user__id=user_id)
    except Profile.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    if profile.visibility == "private" and request.user != profile.user:
        return Response({"error": "Profile is private"}, status=403)
    if profile.visibility == "followers_only" and request.user != profile.user:
        if not Follow.objects.filter(follower=request.user, following=profile.user).exists():
            return Response({"error": "Only followers can view this profile"}, status=403)

    user_data = UserSerializer(profile.user).data
    return Response(user_data)



# views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Post, Notification
from .serializers import NotificationSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        user = request.user

        # Check if already liked
        if user in post.likes.all():
            return Response({"message": "Already liked"}, status=status.HTTP_200_OK)

        # Add like
        post.likes.add(user)

        # Create notification for post owner
        if post.author != user:
            Notification.objects.create(
                post=post,
                sender=user,
                receiver=post.author,
                notification_type='like',
                message=f"{user.username} liked your post"
            )

        return Response({"message": "Post liked & notification sent!"}, status=status.HTTP_200_OK)

    except Post.DoesNotExist:
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_notifications(request):
    user = request.user
    notifications = Notification.objects.filter(receiver=user).order_by('-created_at')
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data)


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Post, Notification
from django.contrib.auth import get_user_model

User = get_user_model()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def notify_post_action(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        action = request.data.get('action')
        username = request.data.get('username')

        if not action or not username:
            return Response({'error': 'Action and username are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Create a notification object
        Notification.objects.create(
            post=post,
            user=post.author,  # Post owner
            message=f"{username} {action} your post."
        )

        return Response({'message': 'Notification created successfully'}, status=status.HTTP_201_CREATED)

    except Post.DoesNotExist:
        return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Post, Notification
from .serializers import NotificationSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_notification(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    receiver = post.author  # Assuming Post has an author field

    data = {
        "post": post.id,
        "sender": request.user.id,
        "receiver": receiver.id,
        "notification_type": request.data.get("notification_type"),
        "message": request.data.get("message", "")
    }

    serializer = NotificationSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from .serializers import NotificationSerializer

class UserNotificationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        notifications = Notification.objects.filter(receiver=user).order_by('-created_at')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)
    
from rest_framework import generics
from .models import Notification
from .serializers import NotificationSerializer

class NotificationListView(generics.ListAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer



from rest_framework import generics, permissions
from django.contrib.auth import get_user_model
from .serializers import UserSerializer
from django.db.models import Q

User = get_user_model()

class UserSearchView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]  # require login
    serializer_class = UserSerializer

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        if query:
            return User.objects.filter(
                Q(username__icontains=query) |
                Q(email__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query)
            ).exclude(id=self.request.user.id)
        return User.objects.none()


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

User = get_user_model()

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def follow_unfollow_user(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    current_user = request.user

    if target_user == current_user:
        return Response({"error": "Cannot follow yourself"}, status=400)

    if target_user.followers.filter(id=current_user.id).exists():
        # Unfollow
        target_user.followers.remove(current_user)
        following = False
    else:
        # Follow
        target_user.followers.add(current_user)
        following = True

    data = {
        "followers_count": target_user.followers.count(),
        "following_count": target_user.following.count(),
        "following": following
    }
    return Response(data)

from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

User = get_user_model()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_follow(request, user_id):
    current_user = request.user
    target_user = get_object_or_404(User, id=user_id)

    profile = target_user.profile

    if current_user in profile.followers.all():
        profile.followers.remove(current_user)
        following = False
    else:
        profile.followers.add(current_user)
        following = True

    return Response({
        "following": following,
        "followers_count": profile.followers.count(),
        "following_count": current_user.profile.followers.count(),  # or use a helper
    })

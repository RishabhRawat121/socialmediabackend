# posts/tests.py
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Post, Notification

User = get_user_model()

class PostFlowTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="alice", email="alice@test.com", password="pass12345")
        self.user2 = User.objects.create_user(username="bob", email="bob@test.com", password="pass12345")

    def auth(self, user):
        self.client.force_authenticate(user=user)

    def test_create_like_comment_notification_flow(self):
        # user1 creates a post
        self.auth(self.user1)
        url_create = reverse("post-list-create")  # /api/posts/
        resp = self.client.post(url_create, {"content": "hello world"}, format="multipart")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        post_id = resp.data["id"]

        # user2 likes user1's post -> notification to user1
        self.auth(self.user2)
        url_like = reverse("post-like-toggle", kwargs={"post_id": post_id})
        resp = self.client.post(url_like)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["message"], "Liked")

        # user2 comments -> notification to user1
        url_cmt = reverse("comment-list-create", kwargs={"post_id": post_id})
        resp = self.client.post(url_cmt, {"content": "Nice!"})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # user1 sees notifications
        self.auth(self.user1)
        url_notifs = reverse("notification-list")
        resp = self.client.get(url_notifs)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(len(resp.data) >= 2)  # one for like, one for comment

        # mark one as read
        notif_id = resp.data[0]["id"]
        url_read = reverse("notif-read", kwargs={"pk": notif_id})
        resp = self.client.post(url_read)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

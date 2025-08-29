from rest_framework import permissions

class IsProfileVisible(permissions.BasePermission):
    """
    Allow access if:
      - profile.visibility == public
      - or request.user == profile.user
      - or visibility == followers_only and requester follows the user
      - or private only accessible to owner
    """

    def has_object_permission(self, request, view, obj):
        # obj is Profile instance
        if obj.visibility == "public":
            return True
        if request.user.is_anonymous:
            return False
        if request.user == obj.user:
            return True
        if obj.visibility == "private":
            return False
        if obj.visibility == "followers_only":
            # adapt to your Follow model lookup
            return obj.user.follower_edges.filter(follower=request.user).exists()
        return False

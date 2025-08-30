# backend/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .home import home
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("users.urls")),     # your auth app
    path("api/posts/", include("posts.urls")),    
    path("", home),# routes above
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

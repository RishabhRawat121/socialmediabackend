from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-default-key")
DEBUG = True
ALLOWED_HOSTS = ["*"]  # For development only

# SUPABASE
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://dcssjbdtwofaaiyyfzit.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "<your-key>")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "avatars")

# DATABASE
import dj_database_url

DATABASES = {
    "default": dj_database_url.parse(
        os.getenv(
            "DATABASE_URL",
            "postgresql://DB_USER:DB_PASSWORD@db.dcssjbdtwofaaiyyfzit.supabase.co:5432/DB_NAME?sslmode=require"
        ),
        conn_max_age=600,
        ssl_require=True
    )
}


# MEDIA
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# STATIC
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"  
# EMAIL (development)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "noreply@example.com"

ROOT_URLCONF = 'backend.urls'  # Replace 'backend' with the name of your Django project folder


# INSTALLED APPS
INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",

    # Your apps
    "users",
    'posts',
]

# MIDDLEWARE
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # must be first
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# CORS / CSRF
CORS_ALLOW_ALL_ORIGINS = True  # development only
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]

SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = False

# REST FRAMEWORK
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.AllowAny",
    ),
}

# TEMPLATES
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# DEFAULT PK
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# TIMEZONE / I18N
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

from django.conf import settings
from supabase import create_client

SUPABASE_URL = settings.SUPABASE_URL
SUPABASE_KEY = settings.SUPABASE_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

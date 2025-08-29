from supabase import create_client
import os

SUPABASE_URL = "your_supabase_url"
SUPABASE_KEY = "your_supabase_key"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Check a user by email
email_to_check = "rawatrishabh76@gmail.com"
response = supabase.auth.admin.get_user_by_email(email_to_check)

user = response.user
if user.email_confirmed_at:
    print(f"{email_to_check} is verified ✅")
else:
    print(f"{email_to_check} is not verified ❌")

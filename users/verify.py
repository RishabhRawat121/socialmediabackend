from .supabase_client import supabase

# Example: check a user by email
email_to_check = "rawatrishabh76@gmail.com"

# List users (requires service_role key, not anon key)
users = supabase.auth.admin.list_users()

for user in users.data:
    if user.email == email_to_check:
        if user.email_confirmed_at:
            print("User is verified")
        else:
            print("User is NOT verified")
        break

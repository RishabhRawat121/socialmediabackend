import os
from supabase import create_client, Client
import uuid

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = "Avatar"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_avatar(file):
    try:
        ext = file.name.split('.')[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        file_content = file.read()
        response = supabase.storage.from_(SUPABASE_BUCKET).upload(
            path=filename,
            file=file_content,
            content_type=file.content_type
        )
        if response.status_code not in [200, 201]:
            print("Supabase upload error:", response)
            return None
        public_url_data = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(filename)
        return public_url_data.public_url
    except Exception as e:
        print("Upload failed:", e)
        return None

def create_supabase_user(email, password):
    """
    Creates a user in Supabase auth.
    """
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })

        # Check if user is created
        if hasattr(response, "user") and response.user is not None:
            return True, response.user.id
        else:
            return False, response

    except Exception as e:
        print("Supabase error:", e)
        return False, str(e)


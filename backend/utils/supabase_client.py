import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
# SUPABASE_URL = os.environ.get("SUPABASE_URL")
# SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
SUPABASE_URL = "https://fjzrarnijrqwhnapfknk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZqenJhcm5panJxd2huYXBma25rIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDgyMzkyMDYsImV4cCI6MjA2MzgxNTIwNn0.n66H00sNDyy1Fuv-f0Uvtbp16iML44roJnOEOB-ahkE"


supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_user_by_nickname(nickname: str):
    response = supabase.table("users").select("*").eq("nickname", nickname).execute()
    users = response.data
    if users:
        return users[0]
    return None

def insert_character_prompt(character_data: dict):
    response = supabase.table("character_prompts").insert(character_data).execute()
    return response.data

def fetch_all_characters():
    response = supabase.table("character_prompts").select("*").execute()
    return response.data

import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
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

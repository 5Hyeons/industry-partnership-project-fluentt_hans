import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.supabase_client import supabase

# ✅ 성별 + MBTI 기반 voice 자동 매핑
def map_voice(gender: str, mbti: str) -> str:
    if gender == "남자":
        return "onyx" if mbti.startswith("I") else "alloy"
    elif gender == "여자":
        return "shimmer" if mbti.startswith("E") else "nova"
    return "fable"  # fallback

# ✅ MBTI 기반 말투(tone) 자동 설정 예시
def map_tone(mbti: str) -> str:
    if mbti.startswith("I"):
        return "차분하고 조용한 말투"
    elif mbti.startswith("E"):
        return "활기차고 친근한 말투"
    return "기본적인 말투"

# ✅ 캐릭터 전체 불러오기 (기본/사용자 모두 포함)
def load_characters():
    response = supabase.table("character_prompts").select("*").execute()
    return response.data

# ✅ alias 기준 캐릭터 1개 찾기
def get_character_by_alias(alias: str, characters: list):
    for c in characters:
        if c.get("alias") == alias:
            return c
    raise ValueError(f"alias '{alias}'에 해당하는 캐릭터를 찾을 수 없습니다.")

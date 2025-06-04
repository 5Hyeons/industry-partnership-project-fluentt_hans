from typing import Dict, Any
from .supabase_client import supabase
# from .species_table import process_species
import json

def get_mbti_info(mbti_type: str) -> Dict[str, Any]:
    """MBTI 정보를 가져옵니다."""
    try:
        response = supabase.table("mbti_profiles").select("*").eq("mbti", mbti_type).execute()
        if not response.data:
            print(f"⚠️ MBTI 정보 없음: {mbti_type}")
            return {}
        return response.data[0]
    except Exception as e:
        print(f"❌ MBTI 정보 조회 중 오류 발생: {str(e)}")
        return {}

def get_species_info(species_name: str) -> Dict[str, Any]:
    """종족 정보를 Supabase에서 가져옵니다."""
    try:
        response = supabase.table("species").select("*").eq("name", species_name).execute()
        if not response.data:
            print(f"⚠️ 종족 정보 없음: {species_name}")
            return {}
        return response.data[0]
    except Exception as e:
        print(f"❌ 종족 정보 조회 중 오류 발생: {str(e)}")
        return {}

def ensure_species_info(species_name: str) -> Dict[str, Any]:
    """종족 정보를 가져오거나, 없는 경우 생성합니다."""
    info = get_species_info(species_name)
    if not info:
        print(f"⚠️ {species_name} 종족 정보가 없습니다. 새로 생성합니다...")
        # process_species(species_name)
        info = get_species_info(species_name)
    return info

def get_prompt_config(key: str) -> str:
    """프롬프트 설정을 가져옵니다."""
    try:
        response = supabase.table("prompt_config").select("value").eq("key", key).execute()
        if response.data:
            return response.data[0]["value"]
        return ""
    except Exception as e:
        print(f"❌ 프롬프트 설정 조회 중 오류 발생: {str(e)}")
        return ""

def generate_character_prompt(character_info: Dict[str, Any]) -> str:
    """캐릭터 프롬프트를 생성합니다."""
    # 필수 정보 확인
    name = character_info.get("name", "")
    mbti = character_info.get("mbti", "")
    species = character_info.get("species", "")
    personality = character_info.get("type", "")  # 성격 요약
    voice = character_info.get("voice", "")  # 자동 매핑된 음성
    greeting = character_info.get("greeting", "")

    # MBTI와 종족 정보 가져오기
    mbti_info = get_mbti_info(mbti)
    species_info = ensure_species_info(species)

    # 프롬프트 생성
    prompt = f"당신은 감성형 AI 캐릭터 '{name}'입니다.\n\n"

    # 기본 정보 섹션
    prompt += "[기본 정보]\n"
    prompt += f"이름: {name}\n"
    prompt += f"MBTI: {mbti}\n"
    prompt += f"종족: {species}\n"
    prompt += f"성격: {personality}\n"
    prompt += f"음성 스타일: {voice}\n\n"

    # MBTI 특성 섹션
    if mbti_info:
        prompt += "[MBTI 특성]\n"
        prompt += f"{mbti_info.get('description', '')}\n\n"
        
        core_traits = mbti_info.get('core_traits', [])
        if core_traits:
            prompt += "핵심 특성:\n"
            prompt += ", ".join(core_traits) + "\n\n"
        
        quote = mbti_info.get('quote', '')
        quote_author = mbti_info.get('quote_author', '')
        if quote and quote_author:
            prompt += "대표 명언:\n"
            prompt += f"\"{quote}\" - {quote_author}\n\n"
        
        themes = mbti_info.get('themes', {})
        if themes:
            prompt += "주요 성격 테마:\n"
            for theme_name, theme_data in themes.items():
                prompt += f"- {theme_name}: {theme_data.get('summary', '')}\n"
            prompt += "\n"

    # 종족 특성 섹션
    if species_info:
        prompt += "[종족 특성]\n"
        if species_info.get("summary"):
            prompt += f"{species_info.get('summary')}\n\n"
        
        traits = species_info.get("traits", [])
        if traits:
            prompt += "주요 특징:\n"
            for trait in traits:
                prompt += f"- {trait}\n"
            prompt += "\n"
        
        speech_pattern = species_info.get("speech_pattern", {})
        if speech_pattern:
            prompt += "말투 특성:\n"
            prompt += f"- 스타일: {speech_pattern.get('스타일', '')}\n"
            prompt += f"- 주요 종결어미: {speech_pattern.get('종결어미', '')}\n"
            if speech_pattern.get('예시'):
                prompt += f"- 예시: {speech_pattern.get('예시', '')}\n"
            prompt += "\n"

    # 인사말이 있는 경우 추가
    if greeting:
        prompt += "[인사말]\n"
        prompt += f"{greeting}\n\n"

    prompt += "[답변 형식]\n"
    prompt += "당신은 반드시 2문장 내외로만 답변해야합니다.\n\n"

    return prompt

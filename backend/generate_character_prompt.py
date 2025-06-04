# ✅ 라이브러리 불러오기
import os
import json
from species_summary_generator import get_or_generate_species_summary
import datetime

# ✅ 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CHARACTER_PATH = os.path.join(DATA_DIR, "character.json")
MBTI_PATH = os.path.join(DATA_DIR, "MBTI.json")
FINAL_SPECIES_PATH = os.path.join(DATA_DIR, "species", "final_species.json")
PROMPTS_DIR = os.path.join(DATA_DIR, "prompts")

# ✅ prompts 디렉토리가 없으면 생성
os.makedirs(PROMPTS_DIR, exist_ok=True)

# ✅ JSON 로드 함수
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# ✅ 캐릭터 목록 불러오기
def load_characters():
    return load_json(CHARACTER_PATH)

# ✅ 캐릭터 이름으로 하나 가져오기
def get_character_by_name(name):
    characters = load_characters()
    for char in characters:
        if char["name"] == name:
            return char
    print(f"❌ 캐릭터 '{name}'를 찾을 수 없습니다.")
    return None

# ✅ 종족 요약 불러오기 또는 생성하기
def get_species_data(species_name):
    species_list = load_json(FINAL_SPECIES_PATH)
    for entry in species_list:
        if entry.get("종족") == species_name:
            return entry  # 전체 반환
    # ✅ 없으면 생성
    print(f"⚠️ 종족 '{species_name}' 없음 → 새로 생성합니다")
    return get_or_generate_species_summary(species_name)

# ✅ MBTI 정보 불러오기 (리스트 탐색 기반)
def get_mbti_data(mbti_type):
    mbti_data = load_json(MBTI_PATH)
    for item in mbti_data.get("types", []):
        if item["name"].upper() == mbti_type.upper():
            return item
    return {}

# ✅ 프롬프트 생성기
def create_prompt(character):
    name = character["name"]
    species = character["species"]
    mbti = character["mbti"]

    species_data = get_species_data(species)
    species_summary = json.dumps(species_data, ensure_ascii=False, indent=2)
    mbti_info = get_mbti_data(mbti)
    mbti_summary = json.dumps(mbti_info, ensure_ascii=False, indent=2)

    # ✅ 프롬프트 생성
    prompt = f"""
[System Prompt]
이름: {name}
종족 정보:
{species_summary}

MBTI 정보:
{mbti_summary}

스타일 태그: {character['hashtag']}
시작 인사: {character['greeting']}
주로 다루는 콘텐츠: {character['content']}
말투: {character['voice']}

[Instruction]
- 제공된 캐릭터 정보를 기반으로 캐릭터의 화법과 성격을 반영합니다.
- 사용자의 질문이나 대화 주제에 적절히 반응합니다.
"""
    return prompt.strip()

# ✅ 프롬프트를 JSON 파일로 저장
def save_prompt_to_json(character_name, prompt):
    """
    모든 캐릭터의 프롬프트를 하나의 JSON 파일(character_prompts.json)에 dict 형태로 저장합니다.
    """
    prompts_path = os.path.join(PROMPTS_DIR, "character_prompts.json")

    # 기존 데이터 불러오기
    if os.path.exists(prompts_path):
        with open(prompts_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {}

    # 새로운 캐릭터 프롬프트 추가
    data[character_name] = {
        "prompt": prompt,
        "generated_at": datetime.datetime.now().isoformat()
    }

    # 다시 저장
    with open(prompts_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return prompts_path


# ✅ 프롬프트 생성 및 저장
def generate_and_save_prompt(character_name):
    """
    캐릭터의 프롬프트를 생성하고 JSON 파일로 저장합니다.
    
    Args:
        character_name (str): 캐릭터 이름
    
    Returns:
        tuple: (프롬프트 문자열, 저장된 파일 경로)
    """
    character = get_character_by_name(character_name)
    if not character:
        return None, None
    
    prompt = create_prompt(character)
    file_path = save_prompt_to_json(character_name, prompt)
    
    return prompt, file_path

# ✅ character_prompts.json에서 이미 처리된 캐릭터를 확인하고,
# 새로운 캐릭터만 프롬프트 생성
def generate_all_character_prompts():
    characters = load_characters()
    prompts_path = os.path.join(PROMPTS_DIR, "character_prompts.json")

    # ✅ 기존 프롬프트 로드
    if os.path.exists(prompts_path):
        with open(prompts_path, "r", encoding="utf-8") as f:
            existing_prompts = json.load(f)
    else:
        existing_prompts = {}

    # ✅ 캐릭터 순회하며 새로 추가된 것만 처리
    for char in characters:
        name = char["name"]
        if name in existing_prompts:
            print(f"⏩ '{name}' 이미 존재함 (스킵)")
            continue

        print(f"🛠️ '{name}' 프롬프트 생성 중...")
        prompt, path = generate_and_save_prompt(name)
        if prompt:
            print(f"✅ 저장 완료: {path}")
        else:
            print(f"❌ 실패: {name}")

if __name__ == "__main__":
    generate_all_character_prompts()
    
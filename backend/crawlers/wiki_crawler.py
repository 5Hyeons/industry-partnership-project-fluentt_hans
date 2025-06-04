import os
import json
import wikipedia
from wikipedia.exceptions import DisambiguationError, PageError

# ✅ 언어 설정
wikipedia.set_lang("ko")

# ✅ 파일 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # backend/ 까지 상위 이동
DATA_PATH = os.path.join(BASE_DIR, "data", "species", "wiki_species.json")

# ✅ JSON 로드 및 저장 함수
def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ✅ 기존 종족 있는지 확인
def exists_species(data, species_name):
    return any(entry.get("종족") == species_name for entry in data)

# ✅ 저장된 종족 내용 가져오기
def get_species_content(data, species_name):
    for entry in data:
        if entry.get("종족") == species_name:
            return entry.get("위키_내용")
    return None

# ✅ 유효성 검사 함수
def is_valid(content: str, species_name: str) -> bool:
    if not (300 <= len(content) <= 20000):
        return False
    blacklist_phrases = [
        "검색 결과", "다음은", "다음과 같은 문서가 있습니다",
        "제목이", "문서를 새로 만들 수 있습니다",
        "동음이의어", "문서 목록", "분류:",
        "는(은) 다음을 가리킬 수 있습니다"
    ]
    if any(phrase in content for phrase in blacklist_phrases):
        return False 
    if species_name not in content:
        return False
    return True

# ✅ 종족 정보 위키에서 가져오기
def get_wiki_species(species_name):
    data = load_json(DATA_PATH, [])

    if exists_species(data, species_name):
        print(f"⚠️ 이미 수집된 종족 (위키): {species_name}")
        return get_species_content(data, species_name)

    try:
        try:
            # 정확한 제목으로만 시도
            page = wikipedia.page(species_name, auto_suggest=False)
            content = page.content.strip()

            # ✅ 유효성 검사 없이 바로 저장
            data.append({"종족": species_name, "위키_내용": content})
            save_json(DATA_PATH, data)
            print(f"✅ 저장 완료 (위키): {species_name} ← 정확 제목")
            return content

        except (DisambiguationError, PageError) as e:
            print(f"⚠️ 직접 호출 실패 ({species_name}): {e}")
            return None

    except Exception as e:
        print(f"❌ 전체 예외 발생: {str(e)}")
        return None

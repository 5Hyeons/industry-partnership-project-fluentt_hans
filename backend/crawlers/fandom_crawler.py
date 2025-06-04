import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from deep_translator import GoogleTranslator

# ✅ 현재 스크립트 기준 경로
base_path = os.path.dirname(os.path.abspath(__file__))  # ← 이 줄 추가
BASE_DIR = os.path.abspath(os.path.join(base_path, ".."))
SAVE_PATH = os.path.join(BASE_DIR, "data", "species", "fandom_species.json")

# ✅ JSON 로드 및 저장 함수
def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ✅ 이미 수집한 종족 확인
def exists_species(data, species_name):
    return any(entry["종족"] == species_name for entry in data)

# ✅ 한글 → 영어 번역기 (띄어쓰기 → 언더스코어)
def translate_ko_to_en(text: str) -> str:
    try:
        translated = GoogleTranslator(source='ko', target='en').translate(text)
        return translated.replace(" ", "_")
    except Exception as e:
        print(f"❌ 번역 실패: {text} → {e}")
        return text.replace(" ", "_")

# ✅ Fandom 크롤링 함수
def crawl_fandom(species_name_ko):
    species_name_en = translate_ko_to_en(species_name_ko)
    print(f"🌐 번역됨: '{species_name_ko}' → '{species_name_en}'")

    url = f"https://fiction.fandom.com/wiki/{quote_plus(species_name_en)}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200:
            print(f"❌ 요청 실패: {species_name_en} ({res.status_code})")
            return None

        soup = BeautifulSoup(res.text, "html.parser")
        content_div = soup.find("div", class_="mw-parser-output")
        if not content_div:
            print(f"❌ 본문 없음: {species_name_en}")
            return None

        paragraphs = content_div.find_all("p")
        text = "\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
        if len(text) < 300:
            print(f"⚠️ 너무 짧음 (건너뜀): {species_name_en}")
            return None

        return text

    except Exception as e:
        print(f"❌ 예외 발생: {species_name_en} → {e}")
        return None

# ✅ 단일 종족 처리 함수
def process_species(species_name_ko):
    data = load_json(SAVE_PATH, [])

    if exists_species(data, species_name_ko):
        print(f"⚠️ 이미 수집됨: {species_name_ko}")
        return

    content = crawl_fandom(species_name_ko)
    if content:
        data.append({"종족": species_name_ko, "팬덤_내용": content})
        save_json(SAVE_PATH, data)
        print(f"✅ 저장 완료: {species_name_ko}")
    else:
        print(f"❌ 저장 실패: {species_name_ko}")
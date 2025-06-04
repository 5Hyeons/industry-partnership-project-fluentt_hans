# 📦 라이브러리 불러오기
import os
import re
import json
from dotenv import load_dotenv
from openai import OpenAI

# ✅ 환경 변수 로드
load_dotenv(os.path.join(os.path.abspath(".."), ".env"))
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ✅ 경로 설정
BASE_PATH = os.path.dirname(os.path.abspath(__file__))  # 현재 파일 기준으로 고정
DATA_PATH = os.path.join(BASE_PATH, "data", "species")
FINAL_PATH = os.path.join(DATA_PATH, "final_species.json")
FANDOM_PATH = os.path.join(DATA_PATH, "fandom_species.json")
NAMU_PATH = os.path.join(DATA_PATH, "namuwiki_species.json")
WIKI_PATH = os.path.join(DATA_PATH, "wiki_species.json")

# ✅ 크롤러 함수
from crawlers.wiki_crawler import get_wiki_species
from crawlers.fandom_crawler import crawl_fandom

# ✅ JSON 입출력 함수
def load_json(path, default=[]):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ✅ GPT 응답에서 JSON 추출
def extract_json_block(text):
    match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        return match.group(1)
    return text.strip()

# ✅ 각 출처 요약
def summarize_each_source(sources):
    if not sources:
        print("⚠️ 요약할 출처가 없습니다 (빈 리스트)")
        return []

    summaries = []
    for i, src in enumerate(sources):
        if not src.strip():
            print(f"⚠️ 출처 {i+1}가 비어 있음 → 건너뜀")
            continue

        try:
            print(f"📄 출처 {i+1} 요약 중...")
            res = client.chat.completions.create(
                model="gpt-4o",
                temperature=0.5,
                messages=[
                    {"role": "system", "content": "아래 글을 한국어로 500자 이내로 요약해줘."},
                    {"role": "user", "content": src}
                ]
            )
            summary = res.choices[0].message.content.strip()
            summaries.append(summary)
        except Exception as e:
            print(f"❌ 출처 {i+1} 요약 실패: {e}")
    return summaries

# ✅ 요약 합치기
def reduce_summaries_to_final_json(species_name, summaries):
    if not summaries:
        print("❌ 요약할 내용 없음")
        return None

    joined = "\n".join(summaries)
    final_prompt = (
        f"다음은 '{species_name}' 종족에 대한 여러 출처 요약입니다. "
        f"이를 종합하여 아래 JSON 형식으로 요약해주세요:\n\n{joined}\n\n"
        f"{{\n"
        f"    \"종족명\": \"{species_name}\",\n"
        f"    \"요약\": \"<5000자 이내 요약문>\",\n"
        f"    \"특징\": [\"<특징1>\", \"<특징2>\", \"...\"],\n"
        f"    \"말투\": {{\n"
        f"        \"스타일\": \"<말투 스타일 설명>\",\n"
        f"        \"종결어미\": \"<예: ~냥, ~다옹 등>\",\n"
        f"        \"예시\": \"<말투 예시 문장>\"\n"
        f"    }}\n"
        f"}}"
    )

    try:
        final_res = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.6,
            messages=[
                {"role": "system", "content": "너는 친절하고 체계적인 백과사전 편집자야. 반드시 JSON 형식을 지켜."},
                {"role": "user", "content": final_prompt}
            ]
        )
        content = final_res.choices[0].message.content.strip()
        json_text = extract_json_block(content)
        return json.loads(json_text)
    except Exception as e:
        print(f"❌ 최종 요약 실패: {e}")
        return None

# ✅ 종족 요약 실행
def get_or_generate_species_summary(species_name):
    final_data = load_json(FINAL_PATH)

    for entry in final_data:
        if entry["종족"] == species_name:
            print(f"✅ 종족 '{species_name}' 요약이 이미 존재합니다.")
            return entry["요약"]

    print(f"🔍 종족 '{species_name}' 요약이 없음 → 크롤링 및 데이터 조회 시작")

    sources = []

    fandom = crawl_fandom(species_name)
    if fandom:
        print(f"⭐ 팬덤 크롤링 성공")
        sources.append(fandom)
    else:
        print(f"❌ 팬덤 크롤링 실패")

    wiki = get_wiki_species(species_name)
    if wiki:
        print(f"📘 위키 크롤링 성공")
        sources.append(wiki)
    else:
        print(f"❌ 위키 크롤링 실패")

    namu_dict = load_json(NAMU_PATH, {})
    if species_name in namu_dict:
        print(f"🌿 나무위키 저장본 수집 완료")
        sources.append(namu_dict[species_name])
    else:
        print(f"❌ 나무위키 저장본 없음")

    if sources:
        print(f"🧠 GPT 요약 시작 (출처 수: {len(sources)})")
        partials = summarize_each_source(sources)

        if partials:
            summary = reduce_summaries_to_final_json(species_name, partials)
        else:
            print("❌ 부분 요약 모두 실패 또는 출처 없음")
            return None
    else:
        print("📭 출처 없음 → 이름만으로 요약 시도")
        summary = reduce_summaries_to_final_json(species_name, [f"'{species_name}'이라는 이름만으로 요약을 생성해주세요."])

    if not summary:
        print(f"❌ GPT 요약 실패: {species_name}")
        return None

    final_data.append({"종족": species_name, "요약": summary})
    save_json(FINAL_PATH, final_data)
    print(f"💾 저장 완료: {species_name}")
    return summary

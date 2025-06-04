# ✅ 라이브러리 불러오기
import os
import re
import json
import requests
from dotenv import load_dotenv
from supabase import create_client
from datasets import load_dataset
import wikipedia
from wikipedia.exceptions import DisambiguationError, PageError
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from deep_translator import GoogleTranslator
from openai import OpenAI
from typing import Dict, Any, List
from .supabase_client import supabase

# ✅ 환경 설정
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
client = OpenAI(api_key=OPENAI_KEY)

namuwiki_dataset = None

# ✅ 나무위키 단일 검색 함수
def get_namuwiki_text(species_name):
    print(f"\U0001F4E5 [get_namuwiki_text] 종족명: {species_name}")
    global namuwiki_dataset
    if namuwiki_dataset is None:
        namuwiki_dataset = load_dataset("heegyu/namuwiki", split="train")
    for entry in namuwiki_dataset:
        if entry["title"] == species_name:
            return entry["text"]
    print("❌ 나무위키 본문 없음")
    return None

# ✅ 위키피디아 크롤러
def get_wiki_species(species_name):
    print(f"\U0001F4E5 [get_wiki_species] 종족명: {species_name}")
    try:
        page = wikipedia.page(species_name, auto_suggest=False)
        return page.content.strip()
    except (DisambiguationError, PageError):
        return None
    except Exception as e:
        print(f"❌ 위키 예외 발생: {e}")
        return None

# ✅ 팬덤 크롤러
def translate_ko_to_en(text: str) -> str:
    print(f"\U0001F310 [translate_ko_to_en] 번역 시도: {text}")
    try:
        translated = GoogleTranslator(source='ko', target='en').translate(text)
        result = translated.replace(" ", "_")
        return result
    except Exception as e:
        return text.replace(" ", "_")

def crawl_fandom(species_name_ko):
    print(f"\U0001F4E5 [crawl_fandom] 종족명: {species_name_ko}")
    species_name_en = translate_ko_to_en(species_name_ko)
    url = f"https://fiction.fandom.com/wiki/{quote_plus(species_name_en)}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200:
            return None
        soup = BeautifulSoup(res.text, "html.parser")
        content_div = soup.find("div", class_="mw-parser-output")
        if not content_div:
            return None
        paragraphs = content_div.find_all("p")
        text = "\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
        if len(text) < 300:
            return None
        return text
    except Exception as e:
        return None

# ✅ GPT 요약 함수
def extract_json_block(text):
    print("🔍 [extract_json_block] JSON 블록 추출 시도")
    match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
    return match.group(1) if match else text.strip()

def summarize_each_source(sources):
    summaries = []
    for i, src in enumerate(sources):
        try:
            res = client.chat.completions.create(
                model="gpt-4o",
                temperature=0.5,
                messages=[
                    {"role": "system", "content": "당신은 판타지 세계의 종족들에 대한 백과사전 편집자입니다. 주어진 텍스트에서 해당 종족의 특징, 문화, 능력, 말투 등을 추출하여 요약해주세요."},
                    {"role": "user", "content": f"다음 텍스트를 5000자 이내로 요약해주세요. 특히 종족의 특징적인 면을 잘 담아주세요:\n\n{src}"}
                ]
            )
            summary = res.choices[0].message.content.strip()
            summaries.append(summary)
        except Exception as e:
            print(f"❌ GPT 요약 중 오류 발생: {str(e)}")
            continue
    return summaries

def reduce_summaries_to_final_json(species_name, summaries):
    if not summaries:
        return None
    joined = "\n\n=== 다음 출처 ===\n\n".join(summaries)
    prompt = (
        f"다음은 '{species_name}' 종족에 대한 여러 출처의 요약문입니다. "
        f"이를 종합하여 해당 종족의 특징을 추출하고, 아래 JSON 형식으로 정리해주세요. "
        f"특히 이 종족만의 독특한 특징과 말투를 잘 표현해주세요.\n\n"
        f"=== 주의사항 ===\n"
        f"1. 반드시 아래 JSON 형식을 정확히 따라주세요.\n"
        f"2. JSON 형식에서 벗어난 다른 텍스트를 포함하지 마세요.\n"
        f"3. 모든 문자열은 쌍따옴표(\")로 감싸주세요.\n"
        f"4. 특징은 정확히 5개를 작성해주세요.\n\n"
        f"=== 요약문 ===\n{joined}\n\n"
        f"=== JSON 형식 ===\n"
        f"""{{
            "종족명": "{species_name}",
            "요약": "이 종족의 핵심적인 특징을 설명하는 5000자 이내의 텍스트",
            "특징": [
                "이 종족만의 대표적인 특징 1",
                "이 종족만의 대표적인 특징 2",
                "이 종족만의 대표적인 특징 3",
                "이 종족만의 대표적인 특징 4",
                "이 종족만의 대표적인 특징 5"
            ],
            "말투": {{
                "스타일": "이 종족이 주로 사용하는 말투나 대화 스타일 설명",
                "종결어미": "이 종족이 주로 사용하는 특징적인 종결어미나 표현",
                "예시": "이 종족의 전형적인 대화 예시"
            }}
        }}"""
    )
    try:
        final_res = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.6,
            messages=[
                {"role": "system", "content": "당신은 판타지 세계의 종족들에 대한 백과사전 편집자입니다. 주어진 정보를 바탕으로 해당 종족의 특징을 정확한 JSON 형식으로 정리해주세요. 반드시 제시된 JSON 형식을 정확히 따라야 하며, JSON 형식에서 벗어난 다른 텍스트를 포함해서는 안 됩니다."},
                {"role": "user", "content": prompt}
            ]
        )
        raw = final_res.choices[0].message.content.strip()
        json_text = extract_json_block(raw)
        return json.loads(json_text)
    except Exception as e:
        print(f"❌ 최종 요약 생성 중 오류 발생: {str(e)}")
        return None

# ✅ Supabase에 저장
def save_to_supabase(species_name, summary):
    res = supabase.table("species").insert({
        "name": species_name,
        "summary": summary
    }).execute()

    if res.data:
        print("✅ Supabase 저장 성공")
        return True
    else:
        print(f"❌ Supabase 저장 실패: {res.error}")
        return False

# ✅ Supabase 중복 확인 함수
def exists_in_supabase(species_name):
    try:
        res = supabase.table("species").select("name").eq("name", species_name).execute()
        return bool(res.data)
    except Exception as e:
        print(f"❌ Supabase 조회 실패: {e}")
        return False

# ✅ 전체 실행 함수
def process_species(species_name):
    print(f"\n🚀 [process_species] 종족 '{species_name}' 처리 시작")

    if exists_in_supabase(species_name):
        print(f"⚠️ 이미 존재: {species_name} → 처리 건너뜀")
        return

    sources = []

    fandom = crawl_fandom(species_name)
    if fandom:
        print("✅ 팬덤 크롤링 성공")
        sources.append(fandom)
    else:
        print("❌ 팬덤 크롤링 실패")

    wiki = get_wiki_species(species_name)
    if wiki:
        print("✅ 위키 크롤링 성공")
        sources.append(wiki)
    else:
        print("❌ 위키 크롤링 실패")

    namu = get_namuwiki_text(species_name)
    if namu:
        print("✅ 나무위키 검색 성공")
        sources.append(namu)
    else:
        print("❌ 나무위키 검색 실패")

    if not sources:
        print(f"❌ 출처 없음: {species_name}")
        return

    print(f"🧠 GPT 요약 시작 (출처 수: {len(sources)})")
    partials = summarize_each_source(sources)
    print("📄 부분 요약 리스트:")
    for i, p in enumerate(partials):
        print(f"--- 요약 {i+1} ---\n{p}\n")

    summary = reduce_summaries_to_final_json(species_name, partials)

    if summary:
        success = save_species_to_supabase(summary)
        if success:
            print(f"✅ 저장 완료: {species_name}")
        else:
            print(f"❌ 저장 실패: {species_name}")
    else:
        print(f"❌ 요약 생성 실패: {species_name}")

def save_species_to_supabase(species_data: Dict[str, Any]) -> bool:
    """종족 정보를 Supabase에 저장합니다.
    
    Args:
        species_data: {
            "종족명": str,
            "요약": str,
            "특징": List[str],
            "말투": {
                "스타일": str,
                "종결어미": str,
                "예시": str
            }
        }
    """
    try:
        # 기존 데이터가 있는지 확인
        existing = supabase.table("species").select("id").eq("name", species_data["종족명"]).execute()
        
        if existing.data:
            print(f"⚠️ 기존 데이터 업데이트: {species_data['종족명']}")
            response = supabase.table("species").update({
                "summary": species_data["요약"],
                "traits": species_data["특징"],
                "speech_pattern": species_data["말투"]
            }).eq("name", species_data["종족명"]).execute()
        else:
            print(f"✨ 새 데이터 추가: {species_data['종족명']}")
            response = supabase.table("species").insert({
                "name": species_data["종족명"],
                "summary": species_data["요약"],
                "traits": species_data["특징"],
                "speech_pattern": species_data["말투"]
            }).execute()
        
        if not response.data:
            print(f"❌ 종족 정보 저장 실패: {species_data['종족명']}")
            return False
            
        print(f"✅ 종족 정보 저장 완료: {species_data['종족명']}")
        return True
        
    except Exception as e:
        print(f"❌ 저장 중 오류 발생: {str(e)}")
        return False

def get_species_info(species_name: str) -> Dict[str, Any]:
    """종족 정보를 Supabase에서 가져옵니다."""
    try:
        response = supabase.table("species").select("*").eq("name", species_name).execute()
        
        if not response.data:
            print(f"⚠️ 종족 정보 없음: {species_name}")
            return {}
            
        data = response.data[0]
        return {
            "name": data["name"],
            "summary": data["summary"],
            "traits": data.get("traits", []),
            "speech_pattern": data.get("speech_pattern", {
                "스타일": "",
                "종결어미": "",
                "예시": ""
            })
        }
        
    except Exception as e:
        print(f"❌ 정보 조회 중 오류 발생: {str(e)}")
        return {}

import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from backend.utils.supabase_client import insert_character_prompt
from backend.utils.prompt_generator import generate_character_prompt
from backend.agents.character_loader import map_voice, map_tone

def character_creation_view():
    st.title("🎨 캐릭터 생성")

    name = st.text_input("이름", placeholder="예: 하루")
    alias = st.text_input("별칭 (alias)", placeholder="예: haru")
    gender = st.selectbox("성별", ["남자", "여자", "기타"])
    species = st.text_input("종족", placeholder="예: 인간")
    nation = st.text_input("국가", placeholder="예: 한국")
    mbti = st.selectbox("MBTI", [
        "ISTJ", "ISFJ", "INFJ", "INTJ",
        "ISTP", "ISFP", "INFP", "INTP",
        "ESTP", "ESFP", "ENFP", "ENTP",
        "ESTJ", "ESFJ", "ENFJ", "ENTJ"
    ])
    personality = st.text_area("성격 요약", placeholder="예: 조용하고 사랑스러운 형")
    tone = st.text_area("말투 스타일", placeholder="예: 부드럽고 차분한 말투 (자동 추천 가능, 수정 가능)")
    content = st.text_area("콘텐츠 주제", placeholder="예: 호그와트에서의 모험")
    greeting = st.text_input("인사말", placeholder="예: 안녕... 오늘도 무사히 마치면서")
    hashtag = st.text_input("해시태그", placeholder="예: #운명을 지닌 소녀")

    if st.button("✅ 캐릭터 생성"):
        if not name or not alias:
            st.error("⚠️ 이름과 별칭은 필수입니다.")
            return

        user = st.session_state.get("user", {})
        user_id = user.get("id", None)

        # 자동 voice / tone 매핑
        auto_voice = map_voice(gender, mbti)
        auto_tone = tone if tone else map_tone(mbti)

        # 캐릭터 정보 구성
        character_info = {
            "name": name,
            "mbti": mbti,
            "species": species,
            "type": personality,
            "greeting": greeting
        }

        # 새로운 프롬프트 생성
        system_prompt = generate_character_prompt(character_info)

        character_data = {
            "user_id": user_id,
            "name": name,
            "alias": alias,
            "species": species,
            "nation": nation,
            "mbti": mbti,
            "type": personality,
            "system_prompt": system_prompt,
            "voice": auto_voice,
            "tone": auto_tone,
            "gender": gender,
            "content": content,
            "greeting": greeting,
            "hashtag": hashtag,
            "is_default": False
        }

        try:
            insert_character_prompt(character_data)
            st.success(f"🎉 '{name}' 캐릭터가 성공적으로 생성되었습니다!")
            st.session_state["view"] = "select_character"
        except Exception as e:
            st.error(f"❌ 캐릭터 생성 중 오류: {e}")

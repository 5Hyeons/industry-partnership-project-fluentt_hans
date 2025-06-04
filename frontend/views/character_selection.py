# 📁 frontend/views/character_selection.py

import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from backend.utils.supabase_client import fetch_all_characters

def character_selection_view():
    st.title("🎭 캐릭터 선택")

    try:
        characters = fetch_all_characters()
        if not characters:
            st.warning("⚠️ 등록된 캐릭터가 없습니다.")
            return
    except Exception as e:
        st.error(f"❌ 캐릭터 불러오기 실패: {e}")
        return

    for character in characters:
        with st.expander(f"🧙 {character['name']} ({character['alias']})"):
            st.write(f"🌍 종족: {character.get('species', 'N/A')}")
            st.write(f"🏳️ 국가: {character.get('nation', 'N/A')}")
            st.write(f"🧠 MBTI: {character.get('mbti', 'N/A')}")
            st.write(f"💬 성격 요약: {character.get('type', 'N/A')}")
            st.write(f"🔊 목소리: {character.get('voice', 'N/A')}")

            if st.button(f"✅ 이 캐릭터로 시작", key=character['id']):
                st.session_state["selected_character"] = character
                st.session_state["view"] = "chat"
                st.success(f"🎙️ '{character['name']}' 캐릭터로 대화를 시작합니다!")

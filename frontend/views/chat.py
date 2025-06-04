import streamlit as st
import subprocess
import sys
import os

def chat_view():
    character = st.session_state.get("selected_character")
    if not character:
        st.error("⚠️ 선택된 캐릭터가 없습니다.")
        return

    st.title(f"🎙️ {character['name']}와 음성 대화 시작")

    # ✅ agent 실행 여부 체크 (중복 방지)
    # if not st.session_state.get("agent_started"):
    #     alias = character["alias"]
    #     try:
    #         subprocess.Popen(
    #             # [sys.executable, "main.py", "dev", "--character", alias],
    #             [sys.executable, "main.py", "connect", "--room", "upstage_dev_room1", "--character", alias],
    #             cwd=os.path.abspath("backend"),
    #             stdout=None,
    #             stderr=None
    #         )
    #         st.session_state["agent_started"] = True
    #         st.success(f"🎧 LiveKit 에이전트 '{alias}' 실행됨 (서버 터미널 확인)")
    #     except Exception as e:
    #         st.error(f"에이전트 실행 실패: {e}")
    #         return

    st.info("에이전트가 음성 대화를 기다리고 있습니다. 브라우저 마이크 권한을 허용해주세요.")

import streamlit as st
import sys
import os

# ✅ backend 경로 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from backend.utils.supabase_client import get_user_by_nickname

def login_view():
    st.title("🔐 닉네임으로 로그인")
    nickname = st.text_input("닉네임을 입력하세요")

    if st.button("로그인"):
        if not nickname:
            st.error("⚠️ 닉네임을 입력해주세요.")
            return

        user = get_user_by_nickname(nickname)

        if user:
            st.session_state["user"] = user
            st.session_state["view"] = "post_login"
            st.success(f"🎉 {nickname}님 환영합니다!")
        else:
            st.error("❌ 해당 닉네임의 사용자가 존재하지 않습니다.")

import streamlit as st

def post_login_view():
    st.title("🎮 캐릭터로 시작하기")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧙 기존 캐릭터 선택"):
            st.session_state["view"] = "select_character"

    with col2:
        if st.button("🎨 새 캐릭터 생성"):
            st.session_state["view"] = "create_character"

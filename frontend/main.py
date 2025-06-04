import streamlit as st

# View 모듈 불러오기
from views.login import login_view
from views.post_login import post_login_view
from views.character_selection import character_selection_view
from views.character_creation import character_creation_view
from views.chat import chat_view

def main():
    # 초기 상태 설정
    if "view" not in st.session_state:
        st.session_state["view"] = "login"

    if st.session_state["view"] == "login":
        login_view()

    elif st.session_state["view"] == "post_login":
        post_login_view()

    elif st.session_state["view"] == "select_character":
        character_selection_view()

    elif st.session_state["view"] == "create_character":
        character_creation_view()

    elif st.session_state["view"] == "chat":
        chat_view()

# 메인 함수 실행
if __name__ == "__main__":
    main()

import streamlit as st


DEFAULT_OPEN_TABS = [
    {
        "MENU_KEY": "dashboard",
        "MENU_NAME": "Dashboard",
    }
]


SESSION_DEFAULTS = {
    "IS_LOGGED_IN": False,
    "COMPANY_ID": None,
    "COMPANY_CODE": "",
    "COMPANY_NAME": "",
    "USER_ID": None,
    "LOGIN_ID": "",
    "USER_NAME": "",
    "ROLE_ID": None,
    "ROLE_CODE": "",
    "ROLE_NAME": "",
    "ACTIVE_TAB": "dashboard",
    "OPEN_TABS": DEFAULT_OPEN_TABS,
}


def is_logged_in() -> bool:
    """
    현재 로그인 여부 확인
    """
    return st.session_state.get("IS_LOGGED_IN", False)


def init_session() -> None:
    """
    세션 기본값 초기화
    - 이미 값이 있는 경우 유지
    - 없는 키만 기본값 세팅
    """
    for key, value in SESSION_DEFAULTS.items():
        if key not in st.session_state:
            if key == "OPEN_TABS":
                st.session_state[key] = [tab.copy() for tab in DEFAULT_OPEN_TABS]
            else:
                st.session_state[key] = value


def login(
    company_id,
    company_code,
    company_name,
    user_id,
    login_id,
    user_name,
    role_id=None,
    role_code=None,
    role_name=None,
) -> None:
    """
    로그인 성공 시 사용자 세션 저장
    """
    st.session_state["IS_LOGGED_IN"] = True
    st.session_state["COMPANY_ID"] = company_id
    st.session_state["COMPANY_CODE"] = company_code
    st.session_state["COMPANY_NAME"] = company_name
    st.session_state["USER_ID"] = user_id
    st.session_state["LOGIN_ID"] = login_id
    st.session_state["USER_NAME"] = user_name
    st.session_state["ROLE_ID"] = role_id
    st.session_state["ROLE_CODE"] = role_code
    st.session_state["ROLE_NAME"] = role_name

    # 로그인 시 기본 탭 상태 초기화
    st.session_state["OPEN_TABS"] = [tab.copy() for tab in DEFAULT_OPEN_TABS]
    st.session_state["ACTIVE_TAB"] = "dashboard"


def logout() -> None:
    """
    로그아웃 시 세션 상태 초기화
    """
    for key in list(SESSION_DEFAULTS.keys()):
        if key == "OPEN_TABS":
            st.session_state[key] = [tab.copy() for tab in DEFAULT_OPEN_TABS]
        else:
            st.session_state[key] = SESSION_DEFAULTS[key]
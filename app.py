import streamlit as st

from common.auth import init_session, is_logged_in
from common.logger import setup_logger
from pages.login import render_login_page
from pages.main import render_main_page

setup_logger()

st.set_page_config(
    page_title="D-Lab",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


def apply_global_css(logged_in: bool) -> None:
    """
    로그인 여부에 따라 전역 CSS 적용
    - 로그인 전: 사이드바 숨김
    - 로그인 후: 사이드바 토글 버튼 표시
    """
    if logged_in:
        state_css = """
        /* 로그인 후 사이드바 토글 버튼 표시 */
        [data-testid="collapsedControl"] {
            display: block !important;
            visibility: visible !important;
        }
        """
    else:
        state_css = """
        /* 로그인 화면에서는 좌측 사이드바 숨김 */
        [data-testid="stSidebar"] {
            display: none !important;
        }

        /* 로그인 화면에서는 사이드바 토글 버튼 숨김 */
        [data-testid="collapsedControl"] {
            display: none !important;
        }
        """

    st.markdown(
        f"""
        <style>
            /* =========================
               기본 Streamlit 네비게이션 숨김
            ========================= */
            [data-testid="stSidebarNav"] {{
                display: none !important;
            }}

            /* =========================
               전체 앱 외곽 여백 제거
            ========================= */
            .stApp {{
                margin: 0 !important;
                padding: 0 !important;
            }}

            html, body, [class*="css"] {{
                margin: 0 !important;
                padding: 0 !important;
            }}

            /* =========================
               메인 영역 상단 공백 최소화
            ========================= */
            .main {{
                padding-top: 0 !important;
                margin-top: 0 !important;
            }}

            [data-testid="stAppViewContainer"] {{
                padding-top: 0 !important;
                margin-top: 0 !important;
            }}

            [data-testid="stMain"] {{
                padding-top: 0 !important;
                margin-top: 0 !important;
            }}

            /* 실제 본문 컨테이너 */
            .block-container {{
                padding-top: 0.15rem !important;
                padding-bottom: 0.4rem !important;
                padding-left: 0.75rem !important;
                padding-right: 0.75rem !important;
                margin-top: 0 !important;
                max-width: 100% !important;
            }}

            .stAppViewContainer .main .block-container {{
                padding-top: 0.15rem !important;
            }}

            /* =========================
               상단 기본 헤더 완전 축소
            ========================= */
            header {{
                height: auto !important;
            }}

            [data-testid="stHeader"] {{
                height: 2.2rem !important;
                min-height: 2.2rem !important;
                background: transparent !important;
                border-bottom: none !important;
            }}

            [data-testid="stToolbar"] {{
                height: 2.2rem !important;
                min-height: 2.2rem !important;
                padding-top: 0 !important;
                padding-bottom: 0 !important;
            }}

            /* 좌측 상단 토글 버튼 위치/크기 보정 */
            [data-testid="collapsedControl"] {{
                margin-top: 0.15rem !important;
                margin-left: 0.15rem !important;
                z-index: 999 !important;
            }}

            [data-testid="stDecoration"] {{
                display: none !important;
            }}

            /* =========================
               블록 간 세로/가로 간격 축소
            ========================= */
            div[data-testid="stVerticalBlock"] {{
                gap: 0.5rem !important;
            }}

            div[data-testid="stHorizontalBlock"] {{
                gap: 0.6rem !important;
                align-items: flex-start !important;
            }}

            div[data-testid="stContainer"] {{
                padding-top: 0.1rem !important;
                padding-bottom: 0.1rem !important;
                margin-top: 0 !important;
                margin-bottom: 0 !important;
            }}

            div.element-container {{
                margin-top: 0.05rem !important;
                margin-bottom: 0.05rem !important;
            }}

            /* =========================
               제목/문단/라벨 여백 축소
            ========================= */
            h1 {{
                margin-top: 0rem !important;
                margin-bottom: 0.35rem !important;
                padding-top: 0rem !important;
            }}

            h2, h3 {{
                margin-top: 0.1rem !important;
                margin-bottom: 0.25rem !important;
                padding-top: 0 !important;
            }}

            h4, h5, h6 {{
                margin-top: 0.05rem !important;
                margin-bottom: 0.2rem !important;
                padding-top: 0 !important;
            }}

            p {{
                margin-top: 0 !important;
                margin-bottom: 0.2rem !important;
            }}

            label {{
                margin-bottom: 0.1rem !important;
            }}

            /* =========================
               Divider 여백 축소
            ========================= */
            hr {{
                margin-top: 0.2rem !important;
                margin-bottom: 0.4rem !important;
            }}

            /* =========================
               버튼/입력/셀렉트 여백 축소
            ========================= */
            div[data-testid="stButton"] {{
                margin-top: 0 !important;
                margin-bottom: 0 !important;
            }}

            button {{
                margin-top: 0 !important;
                margin-bottom: 0 !important;
            }}

            div[data-testid="stTextInput"],
            div[data-testid="stSelectbox"],
            div[data-testid="stDateInput"],
            div[data-testid="stTextArea"] {{
                margin-top: 0 !important;
                margin-bottom: 0 !important;
            }}

            div[data-baseweb="input"],
            div[data-baseweb="select"],
            div[data-baseweb="textarea"] {{
                margin-top: 0 !important;
                margin-bottom: 0 !important;
            }}

            /* =========================
               탭 영역 여백 축소
            ========================= */
            div[role="tablist"] {{
                margin-top: 0 !important;
                margin-bottom: 0.15rem !important;
                gap: 0.35rem !important;
            }}

            div[role="tab"] {{
                padding-top: 0.45rem !important;
                padding-bottom: 0.45rem !important;
            }}

            /* =========================
               expander / sidebar 여백
            ========================= */
            .streamlit-expanderHeader {{
                padding-top: 0.35rem !important;
                padding-bottom: 0.35rem !important;
            }}

            [data-testid="stSidebar"] {{
                padding-top: 0 !important;
            }}

            section[data-testid="stSidebar"] .block-container {{
                padding-top: 0.6rem !important;
                padding-left: 0.6rem !important;
                padding-right: 0.6rem !important;
                padding-bottom: 0.5rem !important;
            }}

            /* =========================
               선택된 메뉴 스타일
            ========================= */
            .menu-selected {{
                width: 100%;
                background: #2f6fed;
                color: white;
                font-weight: 700;
                border-radius: 10px;
                padding: 0.68rem 0.9rem;
                margin-bottom: 0.35rem;
                border: 1px solid #2f6fed;
                box-sizing: border-box;
            }}

            .sub-menu-selected {{
                width: 100%;
                background: #e8f0ff;
                color: #1f4fbf;
                font-weight: 700;
                border-radius: 10px;
                padding: 0.68rem 0.9rem 0.68rem 1.2rem;
                margin-bottom: 0.35rem;
                border: 1px solid #b8cdfc;
                box-sizing: border-box;
            }}

            /* =========================
               빈 markdown / 빈 element로 인한 공백 축소
            ========================= */
            div.element-container:has(div[data-testid="stMarkdownContainer"]:empty) {{
                display: none !important;
            }}

            {state_css}
        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    init_session()

    logged_in = is_logged_in()
    apply_global_css(logged_in)

    if logged_in:
        render_main_page()
    else:
        render_login_page()


if __name__ == "__main__":
    main()
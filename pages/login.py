import streamlit as st

from common.auth import login
from common.exceptions import AuthenticationError, DatabaseError, ValidationError
from services.auth_service import AuthService


def render_login_page():
    """
    로그인 화면 렌더링
    - 로그인 입력 UI 표시
    - 인증 처리
    - 성공 시 세션 저장 후 메인 화면으로 이동
    """
    auth_service = AuthService()

    # 로그인 화면 전용 스타일
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(135deg, #EAF1FB 0%, #DCE7F7 50%, #EDF3FB 100%);
        }

        .login-title {
            text-align: center;
            font-size: 30px;
            font-weight: 800;
            color: #0F172A;
            letter-spacing: 1px;
            margin-bottom: 4px;
        }

        .login-subtitle {
            text-align: center;
            font-size: 14px;
            color: #64748B;
            margin-bottom: 22px;
        }

        .login-footer {
            text-align: center;
            font-size: 11px;
            color: #94A3B8;
            margin-top: 12px;
        }

        div[data-testid="stForm"] {
            border: none !important;
            background: transparent !important;
            box-shadow: none !important;
            padding: 0 !important;
        }

        div[data-testid="stFormSubmitButton"] > button {
            width: 100%;
            height: 44px;
            border-radius: 10px;
            font-weight: 600;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(255, 255, 255, 0.96);
            border: 1px solid #E5E7EB !important;
            border-radius: 16px !important;
            box-shadow: 0 14px 30px rgba(30, 41, 59, 0.12);
            padding: 30px 24px 22px 24px;
            backdrop-filter: blur(4px);
        }
        </style>
    """, unsafe_allow_html=True)

    left, center, right = st.columns([1.45, 1, 1.45])

    with center:
        st.markdown("<div style='height:70px;'></div>", unsafe_allow_html=True)

        card = st.container(border=True)

        with card:
            st.markdown('<div class="login-title">D-Lab</div>', unsafe_allow_html=True)
            st.markdown('<div class="login-subtitle">Sign In</div>', unsafe_allow_html=True)

            with st.form("login_form"):
                company_code = st.text_input("Company Code", value="ILHOS").strip().upper()
                login_id = st.text_input("Login ID").strip().upper()
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Sign In")

            if submitted:
                try:
                    user_info = auth_service.validate_user(
                        company_code=company_code,
                        login_id=login_id,
                        password=password,
                    )

                    login(
                        company_id=user_info["COMPANY_ID"],
                        company_code=user_info["COMPANY_CODE"],
                        company_name=user_info["COMPANY_NAME"],
                        user_id=user_info["USER_ID"],
                        login_id=user_info["LOGIN_ID"],
                        user_name=user_info["USER_NAME"],
                        role_id=user_info["ROLE_ID"],
                        role_code=user_info["ROLE_CODE"],
                        role_name=user_info["ROLE_NAME"],
                    )

                    st.success("Sign in successful.")
                    st.rerun()

                except ValidationError as e:
                    st.error(e.message)
                except AuthenticationError as e:
                    st.error(e.message)
                except DatabaseError as e:
                    st.error(e.message)

            st.markdown('<div class="login-footer">© ILHOS</div>', unsafe_allow_html=True)
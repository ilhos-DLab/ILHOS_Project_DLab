import streamlit as st
from common.auth import logout


def render_header() -> None:
    company_name = st.session_state.get("COMPANY_NAME", "")
    user_name = st.session_state.get("USER_NAME", "")

    st.markdown(
        """
        <style>
        .top-header-title {
            font-size: 22px;
            font-weight: 800;
            color: #0f172a;
            line-height: 1;
            margin: 0;
            padding: 0;
        }

        .top-header-right {
            display: flex;
            justify-content: flex-end;
            align-items: center;
            gap: 10px;
            font-size: 12px;
            font-weight: 600;
            color: #334155;
            white-space: nowrap;
            margin: 0;
            padding: 0;
            line-height: 1;
        }

        .top-header-divider {
            margin-top: 0.15rem;
            margin-bottom: 0.2rem;
            border-bottom: 1px solid #e5e7eb;
        }

        div[data-testid="stButton"] {
            margin-top: 0 !important;
            margin-bottom: 0 !important;
        }

        div[data-testid="stButton"] > button {
            height: 34px !important;
            min-height: 34px !important;
            padding-top: 0 !important;
            padding-bottom: 0 !important;
            border-radius: 10px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([7.2, 3.2], gap="small")

    with left:
        st.markdown(
            '<div class="top-header-title">D-Lab</div>',
            unsafe_allow_html=True,
        )

    with right:
        info_col, btn_col = st.columns([4.6, 1.6], gap="small")

        with info_col:
            st.markdown(
                f"""
                <div class="top-header-right">
                    <span>Company: {company_name}</span>
                    <span>User: {user_name}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with btn_col:
            if st.button("Sign Out", key="HEADER_SIGNOUT", use_container_width=True):
                logout()
                st.rerun()

    st.markdown('<div class="top-header-divider"></div>', unsafe_allow_html=True)
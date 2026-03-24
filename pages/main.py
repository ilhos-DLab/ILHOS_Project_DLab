import streamlit as st

from common.exceptions import DatabaseError, ValidationError
from components.header import render_header
from components.sidebar import render_sidebar
from pages.system.company_management import render_company_management
from pages.analysis.sales_analysis import render_sales_analysis
from services.menu_service import MenuService
from pages.invest.invest_management import render_invest_management

def get_tab_icon(menu_key: str) -> str:
    icon_map = {
        "dashboard": "📊",
        "customer_management": "🏢",
        "item_management": "📦",
        "purchase_order": "📝",
        "purchase_receipt": "📥",
        "user_management": "👤",
        "role_management": "🛡️",
        "menu_management": "📁",
        "company_management": "🏭",
        "sales_analysis": "📊",
        "invest_management": "💹",
        "invest_analysis": "📈",
        "invest_stats": "📊",
    }
    return icon_map.get(menu_key, "📄")


def render_page_title(title: str) -> None:
    st.markdown(
        f"""
        <h2 style="
            margin: 0.05rem 0 0.35rem 0;
            padding: 0;
            line-height: 1.2;
            font-weight: 700;
        ">
            {title}
        </h2>
        """,
        unsafe_allow_html=True,
    )


def set_active_tab(menu_key: str) -> None:
    st.session_state["ACTIVE_TAB"] = menu_key


def close_tab(menu_key: str) -> None:
    """
    현재 열린 탭 닫기
    - dashboard 탭은 항상 유지
    """
    if menu_key == "dashboard":
        return

    open_tabs = st.session_state.get("OPEN_TABS", [])
    active_tab = st.session_state.get("ACTIVE_TAB", "dashboard")

    new_tabs = [tab for tab in open_tabs if tab["MENU_KEY"] != menu_key]
    st.session_state["OPEN_TABS"] = new_tabs

    if active_tab == menu_key:
        if new_tabs:
            st.session_state["ACTIVE_TAB"] = new_tabs[-1]["MENU_KEY"]
        else:
            st.session_state["ACTIVE_TAB"] = "dashboard"


def render_tabs() -> None:
    """
    상단 열림 탭 UI 렌더링
    """
    open_tabs = st.session_state.get("OPEN_TABS", [])
    active_tab = st.session_state.get("ACTIVE_TAB", "dashboard")

    if not open_tabs:
        return

    st.markdown(
        """
        <style>
        .erp-tab-wrap {
            margin-top: 0.1rem;
            margin-bottom: 0.25rem;
        }

        .erp-tab-bar .stButton {
            margin-top: 0 !important;
            margin-bottom: 0 !important;
        }

        .erp-tab-bar .stButton > button {
            height: 36px;
            min-height: 36px;
            border-radius: 10px;
            font-weight: 600;
            white-space: nowrap;
            box-shadow: none;
            padding-top: 0 !important;
            padding-bottom: 0 !important;
        }

        .erp-tab-bar button[kind="primary"] {
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            border: 1px solid #1d4ed8;
            color: #ffffff;
        }

        .erp-tab-bar button[kind="primary"]:hover {
            background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
            border: 1px solid #1e40af;
            color: #ffffff;
        }

        .erp-tab-bar button[kind="secondary"] {
            background: #ffffff;
            border: 1px solid #d1d5db;
            color: #111827;
        }

        .erp-tab-bar button[kind="secondary"]:hover {
            background: #f8fafc;
            border: 1px solid #94a3b8;
            color: #0f172a;
        }

        .erp-close-row {
            margin-top: 0.1rem;
            margin-bottom: 0.15rem;
        }

        .erp-close-row .stButton > button {
            height: 34px;
            min-height: 34px;
            border-radius: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="erp-tab-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="erp-tab-bar">', unsafe_allow_html=True)

    tab_cols = st.columns(len(open_tabs), gap="small")

    for idx, tab in enumerate(open_tabs):
        with tab_cols[idx]:
            is_active = tab["MENU_KEY"] == active_tab
            button_type = "primary" if is_active else "secondary"
            icon = get_tab_icon(tab["MENU_KEY"])

            if st.button(
                f"{icon} {tab['MENU_NAME']}",
                key=f"TAB_{tab['MENU_KEY']}",
                use_container_width=True,
                type=button_type,
            ):
                set_active_tab(tab["MENU_KEY"])
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    if active_tab != "dashboard":
        st.markdown('<div class="erp-close-row">', unsafe_allow_html=True)
        left, right = st.columns([9, 1.7], gap="small")
        with right:
            if st.button(
                "Close Current Tab",
                key="BTN_CLOSE_CURRENT_TAB",
                use_container_width=True,
            ):
                close_tab(active_tab)
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def render_main_page() -> None:
    """
    메인 페이지 렌더링
    - 헤더 표시
    - 메뉴 조회 및 사이드바 렌더링
    - 활성 탭에 따라 화면 분기
    """
    render_header()

    company_id = st.session_state.get("COMPANY_ID")
    role_id = st.session_state.get("ROLE_ID")

    menu_service = MenuService()

    try:
        menu_list = menu_service.get_menu_list(company_id, role_id)
    except ValidationError as e:
        st.error(str(e))
        return
    except DatabaseError as e:
        st.error(str(e))
        return

    render_sidebar(menu_list)
    render_tabs()

    active_tab = st.session_state.get("ACTIVE_TAB", "dashboard")

    if active_tab == "dashboard":
        render_page_title("Dashboard")
        render_dashboard_content()

    elif active_tab == "customer_management":
        render_page_title("Customer Management")
        render_customer_management()

    elif active_tab == "item_management":
        render_page_title("Item Management")
        render_item_management()

    elif active_tab == "purchase_order":
        render_page_title("Purchase Orders")
        render_purchase_order()

    elif active_tab == "purchase_receipt":
        render_page_title("Purchase Receipts")
        render_purchase_receipt()

    elif active_tab == "user_management":
        render_page_title("User Management")
        render_user_management()

    elif active_tab == "role_management":
        render_page_title("Role Management")
        render_role_management()

    elif active_tab == "menu_management":
        render_page_title("Menu Management")
        render_menu_management()

    elif active_tab == "company_management":        
        render_company_management()

    elif active_tab == "sales_analysis":
        render_page_title("Sales Analysis")
        render_sales_analysis()
     
    elif active_tab == "invest_management":
        render_page_title("Investment Management")
        render_invest_management()

    elif active_tab == "invest_analysis":
        render_page_title("Investment Analysis")
        st.info("This page is under preparation.")

    elif active_tab == "invest_stats":
        render_page_title("Investment Statistics")
        st.info("This page is under preparation.")

    else:
        render_page_title("Page")
        st.info("This page is under preparation.")
       
def render_dashboard_content() -> None:
    st.write("Welcome to D-Lab ERP System.")

    col1, col2, col3 = st.columns(3, gap="small")
    with col1:
        st.metric("Customers", "0")
    with col2:
        st.metric("Items", "0")
    with col3:
        st.metric("Open Orders", "0")


def render_customer_management() -> None:
    st.write("This page will be implemented in the next step.")


def render_item_management() -> None:
    st.write("This page will be implemented in the next step.")


def render_purchase_order() -> None:
    st.write("This page will be implemented in the next step.")


def render_purchase_receipt() -> None:
    st.write("This page will be implemented in the next step.")


def render_user_management() -> None:
    st.write("This page will be implemented in the next step.")


def render_role_management() -> None:
    st.write("This page will be implemented in the next step.")


def render_menu_management() -> None:
    st.write("This page will be implemented in the next step.")
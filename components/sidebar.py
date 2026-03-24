import streamlit as st


def open_tab(menu_key, menu_name):
    # 탭이 이미 열려 있는지 확인 후 없으면 추가
    open_tabs = st.session_state.get("OPEN_TABS", [])

    exists = any(tab["MENU_KEY"] == menu_key for tab in open_tabs)

    if not exists:
        open_tabs.append({
            "MENU_KEY": menu_key,
            "MENU_NAME": menu_name
        })

    st.session_state["OPEN_TABS"] = open_tabs
    st.session_state["ACTIVE_TAB"] = menu_key


def render_menu_button(menu_key, menu_name, button_key):
    active_tab = st.session_state.get("ACTIVE_TAB", "dashboard")

    if active_tab == menu_key:
        st.markdown(
            f'<div class="sub-menu-selected">{menu_name}</div>',
            unsafe_allow_html=True
        )
    else:
        if st.button(
            menu_name,
            key=button_key,
            use_container_width=True
        ):
            open_tab(menu_key, menu_name)
            st.rerun()


def render_sidebar(menu_list):
    # 좌측 메뉴 표시
    with st.sidebar:
        st.markdown("## Navigation")

        company_id = st.session_state.get("COMPANY_ID")
        role_id = st.session_state.get("ROLE_ID")

        # 메뉴가 없으면 원인 파악용 메시지 표시
        if not menu_list:
            st.warning("No menu is available.")
            st.caption(f"COMPANY_ID = {company_id}")
            st.caption(f"ROLE_ID = {role_id}")
            return

        parent_menus = [
            menu for menu in menu_list
            if menu["PARENT_MENU_ID"] == 0
        ]

        for parent in parent_menus:
            children = [
                menu for menu in menu_list
                if menu["PARENT_MENU_ID"] == parent["MENU_ID"]
            ]

            if children:
                with st.expander(parent["MENU_NAME"], expanded=False):
                    for child in children:
                        render_menu_button(
                            child["PAGE_KEY"],
                            child["MENU_NAME"],
                            f"MENU_{child['MENU_ID']}"
                        )
            else:
                render_menu_button(
                    parent["PAGE_KEY"],
                    parent["MENU_NAME"],
                    f"MENU_{parent['MENU_ID']}"
                )
import pandas as pd
import streamlit as st
from datetime import date
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

from services.invest.invest_service import InvestService
from common.exceptions import ValidationError, NotFoundError, DatabaseError
from common.utils import format_number, to_float
from common.export_utils import (
    prepare_export_dataframe,
    get_excel_download_data,
    get_pdf_download_data,
)

service = InvestService()


def _format_invest_amount_input():
    """
    Investment Amount 입력창에서 포커스를 벗어났을 때
    숫자형 표시(천단위 콤마)로 변환한다.
    """
    raw_value = st.session_state.get("INVEST_AMOUNT_INPUT", "")
    amount_value = to_float(raw_value)

    st.session_state["INVEST_AMOUNT"] = amount_value
    st.session_state["INVEST_AMOUNT_INPUT"] = format_number(
        amount_value,
        digits=0,
        default="",
    )


def init_invest_state():
    # 화면 상태 초기화
    defaults = {
        "INVEST_FORM_MODE": "NEW",
        "INVEST_SELECTED_ID": None,
        "INVEST_SEARCH_NAME": "",
        "INVEST_SEARCH_USE_YN": "Y",
        "INVEST_LIST": [],
        "INVEST_CODE": "",
        "INVEST_NAME": "",
        "INVEST_TICKER_SYMBOL": "",
        "INVEST_TYPE": "Stock",
        "INVEST_AMOUNT": 0.0,
        "INVEST_AMOUNT_INPUT": "",
        "INVEST_DATE": date.today(),
        "INVEST_REMARK": "",
        "INVEST_USE_YN": "Y",
        "INVEST_MARKET_NAME": "",
        "INVEST_CURRENT_PRICE": "",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if not st.session_state["INVEST_AMOUNT_INPUT"]:
        st.session_state["INVEST_AMOUNT_INPUT"] = format_number(
            st.session_state["INVEST_AMOUNT"],
            digits=0,
            default="",
        )


def clear_form():
    # 입력 폼 초기화
    st.session_state["INVEST_FORM_MODE"] = "NEW"
    st.session_state["INVEST_SELECTED_ID"] = None
    st.session_state["INVEST_CODE"] = ""
    st.session_state["INVEST_NAME"] = ""
    st.session_state["INVEST_TICKER_SYMBOL"] = ""
    st.session_state["INVEST_TYPE"] = "Stock"
    st.session_state["INVEST_AMOUNT"] = 0.0
    st.session_state["INVEST_AMOUNT_INPUT"] = ""
    st.session_state["INVEST_DATE"] = date.today()
    st.session_state["INVEST_REMARK"] = ""
    st.session_state["INVEST_USE_YN"] = "Y"
    st.session_state["INVEST_MARKET_NAME"] = ""
    st.session_state["INVEST_CURRENT_PRICE"] = ""


def load_list():
    # 조회 조건으로 목록 조회
    st.session_state["INVEST_LIST"] = service.get_invest_list(
        invest_name=st.session_state["INVEST_SEARCH_NAME"],
        use_yn=st.session_state["INVEST_SEARCH_USE_YN"],
    )


def load_detail(invest_id: int):
    # 상세 데이터 조회 후 폼 바인딩
    item = service.get_invest_detail(invest_id)

    amount_value = to_float(item["INVEST_AMOUNT"])

    st.session_state["INVEST_FORM_MODE"] = "EDIT"
    st.session_state["INVEST_SELECTED_ID"] = item["INVEST_ID"]
    st.session_state["INVEST_CODE"] = item["INVEST_CODE"]
    st.session_state["INVEST_NAME"] = item["INVEST_NAME"]
    st.session_state["INVEST_TICKER_SYMBOL"] = item.get("TICKER_SYMBOL", "") or ""
    st.session_state["INVEST_TYPE"] = item["INVEST_TYPE"]
    st.session_state["INVEST_AMOUNT"] = amount_value
    st.session_state["INVEST_AMOUNT_INPUT"] = format_number(
        amount_value,
        digits=0,
        default="",
    )
    st.session_state["INVEST_DATE"] = item["INVEST_DATE"]
    st.session_state["INVEST_REMARK"] = item["REMARK"] or ""
    st.session_state["INVEST_USE_YN"] = item["USE_YN"]

    st.session_state["INVEST_MARKET_NAME"] = ""
    st.session_state["INVEST_CURRENT_PRICE"] = ""


def collect_form_data():
    # 입력값 보정 후 폼 데이터 수집
    st.session_state["INVEST_AMOUNT"] = to_float(
        st.session_state["INVEST_AMOUNT_INPUT"]
    )

    return {
        "invest_code": st.session_state["INVEST_CODE"].strip(),
        "invest_name": st.session_state["INVEST_NAME"].strip(),
        "ticker_symbol": st.session_state["INVEST_TICKER_SYMBOL"].strip(),
        "invest_type": st.session_state["INVEST_TYPE"],
        "invest_amount": to_float(st.session_state["INVEST_AMOUNT"]),
        "invest_date": st.session_state["INVEST_DATE"],
        "remark": st.session_state["INVEST_REMARK"].strip(),
        "use_yn": st.session_state["INVEST_USE_YN"],
        "user_id": st.session_state.get("USER_ID", 1),
    }


def render_search_area():
    # 조회 조건 영역
    with st.container(border=True):
        st.subheader("Search")

        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            st.text_input(
                "Investment Name",
                key="INVEST_SEARCH_NAME",
                placeholder="Enter investment name",
            )

        with col2:
            st.selectbox(
                "Use Status",
                options=["", "Y", "N"],
                format_func=lambda x: {"": "All", "Y": "Yes", "N": "No"}[x],
                key="INVEST_SEARCH_USE_YN",
            )

        with col3:
            st.write("")
            st.write("")
            if st.button("Search", use_container_width=True):
                load_list()
                clear_form()
                st.rerun()


def render_invest_list():
    # 목록 그리드 영역
    with st.container(border=True):
        st.subheader("Investment List")

        df = pd.DataFrame(st.session_state["INVEST_LIST"])

        if df.empty:
            st.info("No data found.")
            return

        display_df = df[
            [
                "INVEST_ID",
                "INVEST_CODE",
                "INVEST_NAME",
                "TICKER_SYMBOL",
                "INVEST_TYPE",
                "INVEST_AMOUNT",
                "INVEST_DATE",
                "USE_YN",
            ]
        ].copy()

        display_df["INVEST_DATE"] = display_df["INVEST_DATE"].astype(str)
        display_df["INVEST_AMOUNT"] = display_df["INVEST_AMOUNT"].apply(
            lambda x: format_number(x, digits=0, default="")
        )

        gb = GridOptionsBuilder.from_dataframe(display_df)
        gb.configure_default_column(
            editable=False,
            sortable=True,
            filter=True,
            resizable=True,
        )

        gb.configure_selection(
            selection_mode="single",
            use_checkbox=False,
        )

        gb.configure_column("INVEST_ID", header_name="ID", hide=True)
        gb.configure_column("INVEST_CODE", header_name="Code", width=120)
        gb.configure_column("INVEST_NAME", header_name="Investment Name", width=220)
        gb.configure_column("TICKER_SYMBOL", header_name="Ticker", width=140)
        gb.configure_column("INVEST_TYPE", header_name="Type", width=120)
        gb.configure_column("INVEST_AMOUNT", header_name="Amount", width=140)
        gb.configure_column("INVEST_DATE", header_name="Date", width=130)
        gb.configure_column("USE_YN", header_name="Use", width=90)

        grid_options = gb.build()

        grid_response = AgGrid(
            display_df,
            gridOptions=grid_options,
            height=260,
            width="100%",
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            fit_columns_on_grid_load=False,
            allow_unsafe_jscode=True,
            theme="streamlit",
            reload_data=False,
        )

        export_df = prepare_export_dataframe(
            df=df,
            columns=[
                "INVEST_CODE",
                "INVEST_NAME",
                "TICKER_SYMBOL",
                "INVEST_TYPE",
                "INVEST_AMOUNT",
                "INVEST_DATE",
                "USE_YN",
                "REMARK",
            ],
            rename_map={
                "INVEST_CODE": "Code",
                "INVEST_NAME": "Investment Name",
                "TICKER_SYMBOL": "Ticker",
                "INVEST_TYPE": "Type",
                "INVEST_AMOUNT": "Amount",
                "INVEST_DATE": "Date",
                "USE_YN": "Use",
                "REMARK": "Remark",
            },
            number_columns=["INVEST_AMOUNT"],
            date_columns=["INVEST_DATE"],
        )

        download_col1, download_col2, _ = st.columns([1, 1, 4])

        with download_col1:
            excel_data = get_excel_download_data(
                export_df,
                sheet_name="Investment List",
            )
            st.download_button(
                label="📊 Excel Download",
                data=excel_data,
                file_name="investment_list.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

        with download_col2:
            pdf_data = get_pdf_download_data(
                export_df,
                title="Investment List",
            )
            st.download_button(
                label="📄 PDF Download",
                data=pdf_data,
                file_name="investment_list.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

        selected_rows = grid_response.get("selected_rows", [])

        if selected_rows is not None and len(selected_rows) > 0:
            selected_row = None

            if isinstance(selected_rows, pd.DataFrame):
                selected_row = selected_rows.iloc[0].to_dict()
            elif isinstance(selected_rows, list):
                selected_row = selected_rows[0]

            if selected_row:
                selected_id = selected_row.get("INVEST_ID")
                current_selected_id = st.session_state.get("INVEST_SELECTED_ID")

                if selected_id is not None and current_selected_id != selected_id:
                    load_detail(int(selected_id))
                    st.rerun()


def render_form_area():
    # 입력/상세 폼 영역
    with st.container(border=True):
        form_title = (
            "New Investment"
            if st.session_state["INVEST_FORM_MODE"] == "NEW"
            else "Edit Investment"
        )
        st.subheader(form_title)

        left_col, right_col = st.columns(2)

        with left_col:
            st.text_input("Investment Code", key="INVEST_CODE")
            st.text_input("Investment Name", key="INVEST_NAME")
            st.text_input("Ticker Symbol", key="INVEST_TICKER_SYMBOL")

            st.selectbox(
                "Investment Type",
                options=["Stock", "ETF", "Cash", "Bond", "Fund", "Other"],
                key="INVEST_TYPE",
            )

            st.text_input(
                "Investment Amount",
                key="INVEST_AMOUNT_INPUT",
                placeholder="Enter amount",
                on_change=_format_invest_amount_input,
            )

            st.date_input("Investment Date", key="INVEST_DATE")

        with right_col:
            st.selectbox(
                "Use Status",
                options=["Y", "N"],
                format_func=lambda x: {"Y": "Yes", "N": "No"}[x],
                key="INVEST_USE_YN",
            )

            st.text_area("Remark", key="INVEST_REMARK", height=120)

            market_btn_col1, market_btn_col2 = st.columns([1, 1])

            with market_btn_col1:
                if st.button("Get Market Price", use_container_width=True):
                    ticker_symbol = st.session_state["INVEST_TICKER_SYMBOL"].strip()

                    if not ticker_symbol:
                        st.warning("Please enter a ticker symbol first.")
                    else:
                        market_info = service.get_market_price(ticker_symbol)
                        st.session_state["INVEST_MARKET_NAME"] = (
                            market_info.get("name", "") or ""
                        )

                        current_price = market_info.get("current_price")
                        st.session_state["INVEST_CURRENT_PRICE"] = format_number(
                            current_price,
                            digits=0,
                            default="",
                        )

                        if market_info.get("name"):
                            st.success("Market data has been retrieved.")
                        else:
                            st.warning("No market data was found for this ticker.")

            with market_btn_col2:
                if st.button("Clear Market Data", use_container_width=True):
                    st.session_state["INVEST_MARKET_NAME"] = ""
                    st.session_state["INVEST_CURRENT_PRICE"] = ""
                    st.rerun()

            st.text_input(
                "Market Name",
                key="INVEST_MARKET_NAME",
                disabled=True,
            )

            st.text_input(
                "Current Price",
                key="INVEST_CURRENT_PRICE",
                disabled=True,
            )

        btn1, btn2, btn3 = st.columns(3)

        with btn1:
            if st.button("New", use_container_width=True):
                clear_form()
                st.rerun()

        with btn2:
            if st.button("Save", use_container_width=True):
                form_data = collect_form_data()

                if st.session_state["INVEST_FORM_MODE"] == "NEW":
                    service.create_invest(form_data)
                    st.success("Investment has been created.")
                else:
                    service.modify_invest(
                        st.session_state["INVEST_SELECTED_ID"],
                        form_data,
                    )
                    st.success("Investment has been updated.")

                load_list()
                clear_form()
                st.rerun()

        with btn3:
            if st.button("Delete", use_container_width=True):
                invest_id = st.session_state["INVEST_SELECTED_ID"]

                if not invest_id:
                    st.warning("Please select an investment first.")
                    return

                service.remove_invest(
                    invest_id=invest_id,
                    user_id=st.session_state.get("USER_ID", 1),
                )
                st.success("Investment has been deleted.")
                load_list()
                clear_form()
                st.rerun()


def render_invest_management():
    # 투자관리 메인 렌더링
    init_invest_state()

    if not st.session_state["INVEST_LIST"]:
        load_list()

    try:
        render_search_area()
        render_invest_list()
        render_form_area()

    except ValidationError as e:
        st.warning(str(e))
    except NotFoundError as e:
        st.error(str(e))
    except DatabaseError as e:
        st.error(str(e))
    except Exception as e:
        st.error(f"Unexpected error: {e}")
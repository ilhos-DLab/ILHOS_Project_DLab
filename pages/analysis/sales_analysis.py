import streamlit as st
import pandas as pd
from datetime import date

from common.exceptions import ValidationError, DatabaseError
from services.sales_analysis_service import SalesAnalysisService

service = SalesAnalysisService()


def init_sales_analysis_state():
    # 매출분석 화면 상태 초기화
    today = date.today()

    defaults = {
        "SALES_ANALYSIS_FROM_DATE": today.replace(day=1),
        "SALES_ANALYSIS_TO_DATE": today,
        "SALES_ANALYSIS_RESULT": [],
        "SALES_ANALYSIS_SEARCHED": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def search_sales_analysis():
    # 매출분석 데이터 조회
    result = service.get_monthly_sales_summary(
        st.session_state["SALES_ANALYSIS_FROM_DATE"],
        st.session_state["SALES_ANALYSIS_TO_DATE"],
    )

    st.session_state["SALES_ANALYSIS_RESULT"] = result
    st.session_state["SALES_ANALYSIS_SEARCHED"] = True


def render_search_area():
    # 조회조건 영역 렌더링
    col1, col2, col3 = st.columns([1, 1, 4])

    with col1:
        st.date_input(
            "From Date",
            key="SALES_ANALYSIS_FROM_DATE",
        )

    with col2:
        st.date_input(
            "To Date",
            key="SALES_ANALYSIS_TO_DATE",
        )

    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Search", key="SALES_ANALYSIS_SEARCH_BUTTON"):
            try:
                search_sales_analysis()
                st.success("Search completed successfully.")
            except ValidationError as e:
                st.warning(str(e))
            except DatabaseError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"Unexpected error occurred. {e}")


def render_kpi_area(data):
    # KPI 영역 렌더링
    total_qty = 0
    total_amount = 0
    avg_amount = 0

    if data:
        total_qty = sum((row.get("TOTAL_QTY") or 0) for row in data)
        total_amount = sum((row.get("TOTAL_AMOUNT") or 0) for row in data)
        avg_amount = total_amount / len(data) if len(data) > 0 else 0

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Quantity", f"{int(total_qty):,}")

    with col2:
        st.metric("Total Sales Amount", f"{int(total_amount):,}")

    with col3:
        st.metric("Average Monthly Sales", f"{int(avg_amount):,}")


def render_grid_area(data):
    # 그리드 영역 렌더링
    st.subheader("Monthly Sales Summary")

    if not data:
        if st.session_state["SALES_ANALYSIS_SEARCHED"]:
            st.info("No data found.")
        return

    display_rows = []
    for row in data:
        display_rows.append(
            {
                "Sale Month": row.get("SALE_MONTH"),
                "Total Quantity": f"{int(row.get('TOTAL_QTY') or 0):,}",
                "Total Sales Amount": f"{int(row.get('TOTAL_AMOUNT') or 0):,}",
            }
        )

    display_df = pd.DataFrame(display_rows)

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )


def render_chart_area(data):
    # 차트 영역 렌더링
    st.subheader("Sales Trend")

    if not data:
        if st.session_state["SALES_ANALYSIS_SEARCHED"]:
            st.info("No chart data available.")
        return

    chart_rows = []
    for row in data:
        chart_rows.append(
            {
                "SALE_MONTH": row.get("SALE_MONTH"),
                "TOTAL_AMOUNT": float(row.get("TOTAL_AMOUNT") or 0),
            }
        )

    chart_df = pd.DataFrame(chart_rows)

    if chart_df.empty:
        st.info("No chart data available.")
        return

    chart_df = chart_df.sort_values("SALE_MONTH")
    chart_df = chart_df.set_index("SALE_MONTH")

    st.line_chart(chart_df)


def render_sales_analysis():
    # 매출분석 메인 화면 렌더링
    init_sales_analysis_state()

    render_search_area()

    data = st.session_state["SALES_ANALYSIS_RESULT"]

    st.divider()
    render_kpi_area(data)

    st.divider()
    render_grid_area(data)

    st.divider()
    render_chart_area(data)
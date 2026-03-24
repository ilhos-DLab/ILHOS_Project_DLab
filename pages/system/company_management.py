import os
import streamlit as st
import pandas as pd
from datetime import date

from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

from common.exceptions import (
    ValidationError,
    NotFoundError,
    BusinessError,
    DatabaseError,
)
from common.export_utils import (
    prepare_export_dataframe,
    get_excel_download_data,
    get_pdf_download_data,
)
from common.file_utils import (
    normalize_file_path,
    delete_file_if_exists,
    save_uploaded_file,
)
from services.company_service import CompanyService

service = CompanyService()

LOGO_UPLOAD_DIR = "uploads/company_logo"
MAX_LOGO_FILE_SIZE_MB = 3
ALLOWED_LOGO_CONTENT_TYPES = {"image/png", "image/jpeg", "image/jpg"}
ALLOWED_LOGO_EXTENSIONS = {".png", ".jpg", ".jpeg"}


def render_section_title(
    title: str,
    margin_top: str = "0rem",
    margin_bottom: str = "0.30rem",
    font_size: str = "1.00rem",
) -> None:
    st.markdown(
        f"""
        <div style="
            margin: {margin_top} 0 {margin_bottom} 0;
            padding: 0;
            line-height: 1.2;
            font-size: {font_size};
            font-weight: 700;
            color: #1e293b;
        ">
            {title}
        </div>
        """,
        unsafe_allow_html=True,
    )


def init_company_state() -> None:
    defaults = {
        "COMPANY_FORM_MODE": "NEW",
        "COMPANY_FORM_SELECTED_ID": None,
        "COMPANY_SEARCH_NAME": "",
        "COMPANY_SEARCH_USE_YN": "",
        "COMPANY_LIST": [],
        "COMPANY_LIST_LOADED": False,
        "COMPANY_FORM_CODE": "",
        "COMPANY_FORM_NAME": "",
        "COMPANY_FORM_BUSINESS_NO": "",
        "COMPANY_FORM_CEO_NAME": "",
        "COMPANY_FORM_TEL_NO": "",
        "COMPANY_FORM_ADDRESS": "",
        "COMPANY_FORM_SERVICE_START_DATE": date.today(),
        "COMPANY_FORM_SERVICE_END_DATE": date.today(),
        "COMPANY_FORM_REMARK": "",
        "COMPANY_FORM_USE_YN": "Y",
        "COMPANY_FORM_LOGO_PATH": "",
        "COMPANY_FORM_LOGO_FILE_NAME": "",
        "COMPANY_FORM_LOGO_DELETE_YN": "N",
        "COMPANY_FORM_LOGO_UPLOADER_VERSION": 0,
        "COMPANY_FORM_LOGO_UPLOAD_FILE": None,
        "POPUP_OPEN": False,
        "POPUP_TYPE": "info",
        "POPUP_MESSAGE": "",
        "SAVE_CONFIRM_OPEN": False,
        "DELETE_CONFIRM_OPEN": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def clear_logo_upload_state() -> None:
    st.session_state["COMPANY_FORM_LOGO_UPLOADER_VERSION"] = (
        st.session_state.get("COMPANY_FORM_LOGO_UPLOADER_VERSION", 0) + 1
    )
    st.session_state["COMPANY_FORM_LOGO_UPLOAD_FILE"] = None

    if "COMPANY_FORM_LOGO_DELETE_CHECK" in st.session_state:
        st.session_state["COMPANY_FORM_LOGO_DELETE_CHECK"] = False


def open_popup(message: str, popup_type: str = "info") -> None:
    st.session_state["POPUP_OPEN"] = True
    st.session_state["POPUP_TYPE"] = popup_type
    st.session_state["POPUP_MESSAGE"] = message


def close_popup() -> None:
    st.session_state["POPUP_OPEN"] = False
    st.session_state["POPUP_TYPE"] = "info"
    st.session_state["POPUP_MESSAGE"] = ""


def open_save_confirm() -> None:
    st.session_state["SAVE_CONFIRM_OPEN"] = True


def close_save_confirm() -> None:
    st.session_state["SAVE_CONFIRM_OPEN"] = False


def open_delete_confirm() -> None:
    st.session_state["DELETE_CONFIRM_OPEN"] = True


def close_delete_confirm() -> None:
    st.session_state["DELETE_CONFIRM_OPEN"] = False


@st.dialog("Notification")
def show_popup_dialog():
    popup_type = st.session_state.get("POPUP_TYPE", "info")
    message = st.session_state.get("POPUP_MESSAGE", "")

    if popup_type == "success":
        st.success(message)
    elif popup_type == "warning":
        st.warning(message)
    elif popup_type == "error":
        st.error(message)
    else:
        st.info(message)

    if st.button("OK", key="POPUP_OK", use_container_width=True):
        close_popup()
        st.rerun()


@st.dialog("Save Confirmation")
def show_save_confirm_dialog():
    form_mode = st.session_state.get("COMPANY_FORM_MODE", "NEW")

    if form_mode == "NEW":
        st.info("Do you want to create this company?")
    else:
        st.info("Do you want to save changes to this company?")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Cancel", key="SAVE_CONFIRM_CANCEL", use_container_width=True):
            close_save_confirm()
            st.rerun()

    with col2:
        if st.button(
            "Save",
            key="SAVE_CONFIRM_OK",
            type="primary",
            use_container_width=True,
        ):
            old_logo_path = st.session_state.get("COMPANY_FORM_LOGO_PATH", "") or ""
            old_logo_file_name = st.session_state.get("COMPANY_FORM_LOGO_FILE_NAME", "") or ""
            delete_logo_yn = st.session_state.get("COMPANY_FORM_LOGO_DELETE_YN", "N")
            uploaded_logo_file = st.session_state.get("COMPANY_FORM_LOGO_UPLOAD_FILE")

            new_logo_path = old_logo_path
            new_logo_file_name = old_logo_file_name

            try:
                current_form_mode = st.session_state.get("COMPANY_FORM_MODE", "NEW")
                selected_id = st.session_state.get("COMPANY_FORM_SELECTED_ID")
                company_code = st.session_state.get("COMPANY_FORM_CODE", "").strip()

                if uploaded_logo_file is not None:
                    new_logo_path, new_logo_file_name = save_uploaded_file(
                        uploaded_file=uploaded_logo_file,
                        upload_dir=LOGO_UPLOAD_DIR,
                        prefix=company_code or "company",
                        allowed_content_types=ALLOWED_LOGO_CONTENT_TYPES,
                        allowed_extensions=ALLOWED_LOGO_EXTENSIONS,
                        max_size_mb=MAX_LOGO_FILE_SIZE_MB,
                        field_label="Logo file",
                    )
                elif delete_logo_yn == "Y":
                    new_logo_path = ""
                    new_logo_file_name = ""

                payload = {
                    "company_code": company_code,
                    "company_name": st.session_state.get("COMPANY_FORM_NAME", "").strip(),
                    "business_no": st.session_state.get("COMPANY_FORM_BUSINESS_NO", "").strip(),
                    "ceo_name": st.session_state.get("COMPANY_FORM_CEO_NAME", "").strip(),
                    "tel_no": st.session_state.get("COMPANY_FORM_TEL_NO", "").strip(),
                    "address": st.session_state.get("COMPANY_FORM_ADDRESS", "").strip(),
                    "service_start_date": st.session_state.get("COMPANY_FORM_SERVICE_START_DATE"),
                    "service_end_date": st.session_state.get("COMPANY_FORM_SERVICE_END_DATE"),
                    "remark": st.session_state.get("COMPANY_FORM_REMARK", "").strip(),
                    "use_yn": st.session_state.get("COMPANY_FORM_USE_YN", "Y"),
                    "logo_path": new_logo_path or None,
                    "logo_file_name": new_logo_file_name or None,
                }

                if current_form_mode == "NEW":
                    payload["created_by"] = st.session_state.get("USER_ID")
                    service.create_company(payload)

                    reset_form()
                    load_company_list()
                    open_popup("Company created successfully.", "success")

                elif current_form_mode == "EDIT":
                    if not selected_id:
                        if uploaded_logo_file is not None and new_logo_path:
                            delete_file_if_exists(new_logo_path)
                        open_popup("Please select a company to update.", "warning")
                    else:
                        payload["updated_by"] = st.session_state.get("USER_ID")
                        service.update_company(selected_id, payload)

                        if uploaded_logo_file is not None and old_logo_path and old_logo_path != new_logo_path:
                            delete_file_if_exists(old_logo_path)

                        if delete_logo_yn == "Y" and old_logo_path:
                            delete_file_if_exists(old_logo_path)

                        load_company_list()
                        load_company_detail(selected_id)
                        open_popup("Company updated successfully.", "success")

                clear_logo_upload_state()

            except ValidationError as e:
                if uploaded_logo_file is not None and new_logo_path and new_logo_path != old_logo_path:
                    delete_file_if_exists(new_logo_path)
                open_popup(e.message, "warning")
            except BusinessError as e:
                if uploaded_logo_file is not None and new_logo_path and new_logo_path != old_logo_path:
                    delete_file_if_exists(new_logo_path)
                open_popup(e.message, "warning")
            except NotFoundError as e:
                if uploaded_logo_file is not None and new_logo_path and new_logo_path != old_logo_path:
                    delete_file_if_exists(new_logo_path)
                open_popup(e.message, "warning")
            except DatabaseError as e:
                if uploaded_logo_file is not None and new_logo_path and new_logo_path != old_logo_path:
                    delete_file_if_exists(new_logo_path)
                open_popup(e.message, "error")
            except Exception:
                if uploaded_logo_file is not None and new_logo_path and new_logo_path != old_logo_path:
                    delete_file_if_exists(new_logo_path)
                open_popup("An unexpected error occurred while saving company.", "error")

            close_save_confirm()
            st.rerun()


@st.dialog("Delete Confirmation")
def show_delete_confirm_dialog():
    st.warning("Are you sure you want to delete this company?")
    st.caption("This action performs a logical delete.")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Cancel", key="DELETE_CONFIRM_CANCEL", use_container_width=True):
            close_delete_confirm()
            st.rerun()

    with col2:
        if st.button(
            "Delete",
            key="DELETE_CONFIRM_OK",
            type="primary",
            use_container_width=True,
        ):
            try:
                company_id = st.session_state.get("COMPANY_FORM_SELECTED_ID")

                if not company_id:
                    open_popup("Please select a company to delete.", "warning")
                else:
                    service.delete_company(
                        company_id=company_id,
                        deleted_by=st.session_state.get("USER_ID"),
                    )
                    reset_form()
                    load_company_list()
                    open_popup("Company deleted successfully.", "success")

            except ValidationError as e:
                open_popup(e.message, "warning")
            except BusinessError as e:
                open_popup(e.message, "warning")
            except NotFoundError as e:
                open_popup(e.message, "warning")
            except DatabaseError as e:
                open_popup(e.message, "error")
            except Exception:
                open_popup("An unexpected error occurred while deleting company.", "error")

            close_delete_confirm()
            st.rerun()


def reset_form() -> None:
    try:
        next_code = service.get_next_company_code()
    except DatabaseError:
        next_code = ""
    except Exception:
        next_code = ""

    st.session_state["COMPANY_FORM_MODE"] = "NEW"
    st.session_state["COMPANY_FORM_SELECTED_ID"] = None
    st.session_state["COMPANY_FORM_CODE"] = next_code
    st.session_state["COMPANY_FORM_NAME"] = ""
    st.session_state["COMPANY_FORM_BUSINESS_NO"] = ""
    st.session_state["COMPANY_FORM_CEO_NAME"] = ""
    st.session_state["COMPANY_FORM_TEL_NO"] = ""
    st.session_state["COMPANY_FORM_ADDRESS"] = ""
    st.session_state["COMPANY_FORM_SERVICE_START_DATE"] = date.today()
    st.session_state["COMPANY_FORM_SERVICE_END_DATE"] = date.today()
    st.session_state["COMPANY_FORM_REMARK"] = ""
    st.session_state["COMPANY_FORM_USE_YN"] = "Y"
    st.session_state["COMPANY_FORM_LOGO_PATH"] = ""
    st.session_state["COMPANY_FORM_LOGO_FILE_NAME"] = ""
    st.session_state["COMPANY_FORM_LOGO_DELETE_YN"] = "N"
    clear_logo_upload_state()


def load_company_list() -> None:
    search_name = st.session_state.get("COMPANY_SEARCH_NAME", "")
    search_use_yn = st.session_state.get("COMPANY_SEARCH_USE_YN", "")
    use_yn = search_use_yn if search_use_yn in ("Y", "N") else None

    company_list = service.get_company_list(
        search_name=search_name,
        use_yn=use_yn,
    )
    st.session_state["COMPANY_LIST"] = company_list
    st.session_state["COMPANY_LIST_LOADED"] = True


def load_company_detail(company_id: int) -> None:
    company = service.get_company_detail(company_id)

    st.session_state["COMPANY_FORM_MODE"] = "EDIT"
    st.session_state["COMPANY_FORM_SELECTED_ID"] = company["COMPANY_ID"]
    st.session_state["COMPANY_FORM_CODE"] = company["COMPANY_CODE"] or ""
    st.session_state["COMPANY_FORM_NAME"] = company["COMPANY_NAME"] or ""
    st.session_state["COMPANY_FORM_BUSINESS_NO"] = company["BUSINESS_NO"] or ""
    st.session_state["COMPANY_FORM_CEO_NAME"] = company["CEO_NAME"] or ""
    st.session_state["COMPANY_FORM_TEL_NO"] = company["TEL_NO"] or ""
    st.session_state["COMPANY_FORM_ADDRESS"] = company["ADDRESS"] or ""
    st.session_state["COMPANY_FORM_SERVICE_START_DATE"] = company["SERVICE_START_DATE"]
    st.session_state["COMPANY_FORM_SERVICE_END_DATE"] = company["SERVICE_END_DATE"]
    st.session_state["COMPANY_FORM_REMARK"] = company["REMARK"] or ""
    st.session_state["COMPANY_FORM_USE_YN"] = company["USE_YN"] or "Y"
    st.session_state["COMPANY_FORM_LOGO_PATH"] = normalize_file_path(company.get("LOGO_PATH") or "") or ""
    st.session_state["COMPANY_FORM_LOGO_FILE_NAME"] = company.get("LOGO_FILE_NAME") or ""
    st.session_state["COMPANY_FORM_LOGO_DELETE_YN"] = "N"
    clear_logo_upload_state()


def save_company() -> None:
    open_save_confirm()


def render_search_area() -> None:
    render_section_title(
        "Company Search",
        margin_top="0rem",
        margin_bottom="0.22rem",
        font_size="1.00rem",
    )

    col1, col2, col3 = st.columns([3.4, 2.0, 1.9], gap="small")

    with col1:
        st.text_input(
            "Company Name",
            key="COMPANY_SEARCH_NAME",
            placeholder="Enter company name",
        )

    with col2:
        st.selectbox(
            "Use Status",
            options=["", "Y", "N"],
            key="COMPANY_SEARCH_USE_YN",
            format_func=lambda x: {
                "": "All",
                "Y": "Active",
                "N": "Inactive",
            }.get(x, x),
        )

    with col3:
        st.markdown("<div style='height: 1.35rem;'></div>", unsafe_allow_html=True)
        btn_col1, btn_col2 = st.columns(2, gap="small")

        with btn_col1:
            if st.button("Search", key="COMPANY_SEARCH_BTN", use_container_width=True):
                try:
                    load_company_list()
                    st.rerun()
                except ValidationError as e:
                    open_popup(e.message, "warning")
                    st.rerun()
                except DatabaseError as e:
                    open_popup(e.message, "error")
                    st.rerun()
                except Exception:
                    open_popup("An unexpected error occurred while searching.", "error")
                    st.rerun()

        with btn_col2:
            if st.button("New", key="COMPANY_NEW_BTN", use_container_width=True):
                reset_form()
                st.rerun()


def render_grid_area() -> None:
    render_section_title(
        "Company List",
        margin_top="0rem",
        margin_bottom="0.35rem",
        font_size="1.00rem",
    )

    company_list = st.session_state.get("COMPANY_LIST", [])
    df = pd.DataFrame(company_list)

    if df.empty:
        st.info("No company data found.")
        return

    display_columns = [
        "COMPANY_ID",
        "COMPANY_CODE",
        "COMPANY_NAME",
        "BUSINESS_NO",
        "CEO_NAME",
        "TEL_NO",
        "SERVICE_START_DATE",
        "SERVICE_END_DATE",
        "USE_YN",
    ]

    existing_columns = [col for col in display_columns if col in df.columns]
    display_df = df[existing_columns].copy()

    for col in ["SERVICE_START_DATE", "SERVICE_END_DATE"]:
        if col in display_df.columns:
            display_df[col] = pd.to_datetime(display_df[col], errors="coerce").dt.strftime("%Y-%m-%d")
            display_df[col] = display_df[col].fillna("")

    gb = GridOptionsBuilder.from_dataframe(display_df)
    gb.configure_default_column(
        editable=False,
        sortable=True,
        filter=True,
        resizable=True,
    )
    gb.configure_selection("single", use_checkbox=False)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=10)

    if "COMPANY_ID" in display_df.columns:
        gb.configure_column("COMPANY_ID", header_name="ID", width=80)
    if "COMPANY_CODE" in display_df.columns:
        gb.configure_column("COMPANY_CODE", header_name="Code", width=95)
    if "COMPANY_NAME" in display_df.columns:
        gb.configure_column("COMPANY_NAME", header_name="Company Name", width=150)
    if "BUSINESS_NO" in display_df.columns:
        gb.configure_column("BUSINESS_NO", header_name="Business No", width=130)
    if "CEO_NAME" in display_df.columns:
        gb.configure_column("CEO_NAME", header_name="CEO Name", width=100)
    if "TEL_NO" in display_df.columns:
        gb.configure_column("TEL_NO", header_name="Tel No", width=115)
    if "SERVICE_START_DATE" in display_df.columns:
        gb.configure_column("SERVICE_START_DATE", header_name="Start Date", width=115)
    if "SERVICE_END_DATE" in display_df.columns:
        gb.configure_column("SERVICE_END_DATE", header_name="End Date", width=115)
    if "USE_YN" in display_df.columns:
        gb.configure_column("USE_YN", header_name="Use", width=80)

    grid_options = gb.build()

    grid_response = AgGrid(
        display_df,
        gridOptions=grid_options,
        height=430,
        width="100%",
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        fit_columns_on_grid_load=False,
        allow_unsafe_jscode=False,
        theme="streamlit",
    )

    export_df = prepare_export_dataframe(
        df=pd.DataFrame(company_list),
        columns=[
            "COMPANY_CODE",
            "COMPANY_NAME",
            "BUSINESS_NO",
            "CEO_NAME",
            "TEL_NO",
            "ADDRESS",
            "SERVICE_START_DATE",
            "SERVICE_END_DATE",
            "USE_YN",
            "REMARK",
        ],
        rename_map={
            "COMPANY_CODE": "Code",
            "COMPANY_NAME": "Company Name",
            "BUSINESS_NO": "Business No",
            "CEO_NAME": "CEO Name",
            "TEL_NO": "Tel No",
            "ADDRESS": "Address",
            "SERVICE_START_DATE": "Service Start Date",
            "SERVICE_END_DATE": "Service End Date",
            "USE_YN": "Use",
            "REMARK": "Remark",
        },
        date_columns=["SERVICE_START_DATE", "SERVICE_END_DATE"],
    )

    download_col1, download_col2, _ = st.columns([1, 1, 3])

    with download_col1:
        excel_data = get_excel_download_data(
            export_df,
            sheet_name="Company List",
        )
        st.download_button(
            label="📊 Excel",
            data=excel_data,
            file_name="company_list.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="COMPANY_EXCEL_DOWNLOAD",
        )

    with download_col2:
        pdf_data = get_pdf_download_data(
            export_df,
            title="Company List",
        )
        st.download_button(
            label="📄 PDF",
            data=pdf_data,
            file_name="company_list.pdf",
            mime="application/pdf",
            use_container_width=True,
            key="COMPANY_PDF_DOWNLOAD",
        )

    selected_rows = grid_response.get("selected_rows", [])
    selected_row = None

    if selected_rows is not None:
        if isinstance(selected_rows, pd.DataFrame):
            if not selected_rows.empty:
                selected_row = selected_rows.iloc[0].to_dict()
        elif isinstance(selected_rows, list):
            if len(selected_rows) > 0:
                selected_row = selected_rows[0]
        elif isinstance(selected_rows, dict):
            selected_row = selected_rows

    if selected_row:
        company_id = selected_row.get("COMPANY_ID")
        current_selected_id = st.session_state.get("COMPANY_FORM_SELECTED_ID")

        if company_id and current_selected_id != company_id:
            try:
                load_company_detail(int(company_id))
                st.rerun()
            except ValidationError as e:
                open_popup(e.message, "warning")
                st.rerun()
            except NotFoundError as e:
                open_popup(e.message, "warning")
                st.rerun()
            except DatabaseError as e:
                open_popup(e.message, "error")
                st.rerun()
            except Exception:
                open_popup(
                    "An unexpected error occurred while loading company detail.",
                    "error",
                )
                st.rerun()


def render_logo_area():
    st.markdown("##### Company Logo")

    current_logo_path = st.session_state.get("COMPANY_FORM_LOGO_PATH", "") or ""
    current_logo_file_name = st.session_state.get("COMPANY_FORM_LOGO_FILE_NAME", "") or ""
    delete_logo_yn = st.session_state.get("COMPANY_FORM_LOGO_DELETE_YN", "N")

    uploader_version = st.session_state.get("COMPANY_FORM_LOGO_UPLOADER_VERSION", 0)
    uploader_key = f"COMPANY_FORM_LOGO_UPLOAD_{uploader_version}"

    uploaded_logo_file = st.file_uploader(
        "Upload Logo",
        type=["png", "jpg", "jpeg"],
        key=uploader_key,
        help=f"PNG/JPG only, max {MAX_LOGO_FILE_SIZE_MB}MB",
    )

    if uploaded_logo_file is not None:
        st.image(uploaded_logo_file, width=180)
        st.caption(f"New file: {uploaded_logo_file.name}")
    elif current_logo_path and delete_logo_yn != "Y" and os.path.exists(current_logo_path):
        st.image(current_logo_path, width=180)
        if current_logo_file_name:
            st.caption(f"Current file: {current_logo_file_name}")
    else:
        st.info("No logo image registered.")

    checkbox_value = delete_logo_yn == "Y"
    remove_logo_checked = st.checkbox(
        "Delete existing logo",
        value=checkbox_value,
        key="COMPANY_FORM_LOGO_DELETE_CHECK",
    )
    st.session_state["COMPANY_FORM_LOGO_DELETE_YN"] = "Y" if remove_logo_checked else "N"

    return uploaded_logo_file


def render_form_area() -> None:
    render_section_title(
        "Company Detail",
        margin_top="0rem",
        margin_bottom="0.40rem",
        font_size="1.00rem",
    )

    form_mode = st.session_state.get("COMPANY_FORM_MODE", "NEW")
    is_new = form_mode == "NEW"

    with st.container(border=True):
        row1_col1, row1_col2 = st.columns(2, gap="small")
        row2_col1, row2_col2 = st.columns(2, gap="small")
        row3_col1, row3_col2 = st.columns(2, gap="small")
        row4_col1, row4_col2 = st.columns(2, gap="small")

        with row1_col1:
            st.text_input(
                "Company Code",
                key="COMPANY_FORM_CODE",
                disabled=not is_new,
            )

        with row1_col2:
            st.text_input(
                "Company Name",
                key="COMPANY_FORM_NAME",
            )

        with row2_col1:
            st.text_input(
                "Business Number",
                key="COMPANY_FORM_BUSINESS_NO",
            )

        with row2_col2:
            st.text_input(
                "CEO Name",
                key="COMPANY_FORM_CEO_NAME",
            )

        with row3_col1:
            st.text_input(
                "Telephone Number",
                key="COMPANY_FORM_TEL_NO",
            )

        with row3_col2:
            st.selectbox(
                "Use Status",
                options=["Y", "N"],
                key="COMPANY_FORM_USE_YN",
                format_func=lambda x: {
                    "Y": "Active",
                    "N": "Inactive",
                }.get(x, x),
            )

        with row4_col1:
            st.date_input(
                "Service Start Date",
                key="COMPANY_FORM_SERVICE_START_DATE",
            )

        with row4_col2:
            st.date_input(
                "Service End Date",
                key="COMPANY_FORM_SERVICE_END_DATE",
            )

        st.text_input(
            "Address",
            key="COMPANY_FORM_ADDRESS",
        )

        st.text_area(
            "Remark",
            key="COMPANY_FORM_REMARK",
            height=65,
        )

        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
        uploaded_logo_file = render_logo_area()
        st.session_state["COMPANY_FORM_LOGO_UPLOAD_FILE"] = uploaded_logo_file
        st.markdown("<div style='height: 0.6rem;'></div>", unsafe_allow_html=True)

        btn_col1, btn_col2 = st.columns(2, gap="small")

        with btn_col1:
            if st.button(
                "Save",
                key="COMPANY_SAVE_BTN",
                type="primary",
                use_container_width=True,
            ):
                save_company()
                st.rerun()

        with btn_col2:
            if st.button("Delete", key="COMPANY_DELETE_BTN", use_container_width=True):
                if not st.session_state.get("COMPANY_FORM_SELECTED_ID"):
                    open_popup("Please select a company to delete.", "warning")
                    st.rerun()
                else:
                    open_delete_confirm()
                    st.rerun()


def render_company_management() -> None:
    init_company_state()

    st.markdown(
        """
        <style>
        div[data-testid="stVerticalBlockBorderWrapper"] {
            padding-top: 0.45rem !important;
            padding-bottom: 0.45rem !important;
        }

        div[data-testid="stTextInput"] label,
        div[data-testid="stDateInput"] label,
        div[data-testid="stSelectbox"] label,
        div[data-testid="stTextArea"] label,
        div[data-testid="stFileUploader"] label {
            font-size: 0.84rem !important;
            margin-bottom: 0.16rem !important;
        }

        .stTextInput input,
        .stDateInput input {
            height: 2.15rem !important;
        }

        div[data-testid="stTextArea"] textarea {
            min-height: 65px !important;
        }

        .company-section-gap {
            height: 0.65rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if not st.session_state.get("COMPANY_FORM_CODE"):
        reset_form()

    if not st.session_state.get("COMPANY_LIST_LOADED", False):
        try:
            load_company_list()
        except Exception:
            st.session_state["COMPANY_LIST"] = []
        st.session_state["COMPANY_LIST_LOADED"] = True

    render_search_area()
    st.markdown('<div class="company-section-gap"></div>', unsafe_allow_html=True)

    left_col, right_col = st.columns([1.45, 1.0], gap="small")

    with left_col:
        render_grid_area()

    with right_col:
        render_form_area()

    if st.session_state.get("POPUP_OPEN"):
        show_popup_dialog()

    if st.session_state.get("SAVE_CONFIRM_OPEN"):
        show_save_confirm_dialog()

    if st.session_state.get("DELETE_CONFIRM_OPEN"):
        show_delete_confirm_dialog()
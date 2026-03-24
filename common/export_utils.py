import io
import pandas as pd

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


def _format_number_for_export(value):
    if value is None or value == "":
        return ""
    try:
        return f"{float(value):,.0f}"
    except Exception:
        return value


def prepare_export_dataframe(
    df: pd.DataFrame,
    columns: list[str] | None = None,
    rename_map: dict | None = None,
    number_columns: list[str] | None = None,
    date_columns: list[str] | None = None,
) -> pd.DataFrame:
    """
    공통 다운로드용 데이터프레임 가공
    """
    if df is None or df.empty:
        return pd.DataFrame()

    export_df = df.copy()

    if columns:
        existing_columns = [col for col in columns if col in export_df.columns]
        export_df = export_df[existing_columns].copy()

    if rename_map:
        export_df.rename(columns=rename_map, inplace=True)

    if number_columns:
        renamed_number_columns = [
            rename_map.get(col, col) if rename_map else col for col in number_columns
        ]
        for col in renamed_number_columns:
            if col in export_df.columns:
                export_df[col] = export_df[col].apply(_format_number_for_export)

    if date_columns:
        renamed_date_columns = [
            rename_map.get(col, col) if rename_map else col for col in date_columns
        ]
        for col in renamed_date_columns:
            if col in export_df.columns:
                export_df[col] = export_df[col].astype(str)

    return export_df


def get_excel_download_data(
    df: pd.DataFrame,
    sheet_name: str = "Sheet1",
) -> bytes:
    """
    데이터프레임을 엑셀 bytes로 변환
    """
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)

        workbook = writer.book
        worksheet = writer.sheets[sheet_name]

        header_format = workbook.add_format({
            "bold": True,
            "align": "center",
            "valign": "vcenter",
            "border": 1,
        })

        cell_format = workbook.add_format({
            "border": 1,
        })

        for col_num, value in enumerate(df.columns):
            worksheet.write(0, col_num, value, header_format)

        for row_idx in range(len(df)):
            for col_idx in range(len(df.columns)):
                worksheet.write(
                    row_idx + 1,
                    col_idx,
                    df.iloc[row_idx, col_idx],
                    cell_format,
                )

        for idx, col in enumerate(df.columns):
            max_length = max(
                df[col].astype(str).map(len).max() if not df.empty else 0,
                len(str(col)),
            )
            worksheet.set_column(idx, idx, min(max_length + 2, 35))

    output.seek(0)
    return output.getvalue()


def get_pdf_download_data(
    df: pd.DataFrame,
    title: str = "List",
) -> bytes:
    """
    데이터프레임을 PDF bytes로 변환
    """
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=10 * mm,
        rightMargin=10 * mm,
        topMargin=10 * mm,
        bottomMargin=10 * mm,
    )

    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(title, styles["Title"]))
    elements.append(Spacer(1, 6 * mm))

    if df is None or df.empty:
        elements.append(Paragraph("No data found.", styles["Normal"]))
    else:
        data = [df.columns.tolist()] + df.fillna("").values.tolist()

        available_width = landscape(A4)[0] - (20 * mm)
        col_count = len(df.columns)
        col_width = available_width / col_count if col_count > 0 else available_width
        col_widths = [col_width] * col_count

        table = Table(data, colWidths=col_widths, repeatRows=1)

        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9E2F3")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7F7F7")]),
            ("WORDWRAP", (0, 0), (-1, -1), "CJK"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))

        elements.append(table)

    doc.build(elements)
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data
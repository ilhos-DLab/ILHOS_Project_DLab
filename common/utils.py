from datetime import datetime
from decimal import Decimal, InvalidOperation
import re
from typing import Optional, Union


NumberLike = Union[int, float, Decimal, str, None]


def nvl(value, default=""):
    return default if value is None else value


def safe_strip(value) -> str:
    if value is None:
        return ""
    return str(value).strip()


def only_numeric_string(value: NumberLike) -> str:
    """
    숫자/문자 입력값에서 숫자 관련 문자만 정리
    허용: 0-9, -, .
    예)
        "50,000원" -> "50000"
        "  -1,234.56 " -> "-1234.56"
    """
    text = safe_strip(value)
    if not text:
        return ""

    text = text.replace(",", "")
    text = re.sub(r"[^0-9\.\-]", "", text)

    # '-'가 여러 개 들어간 경우 첫 번째만 허용
    if text.count("-") > 1:
        text = text.replace("-", "")
        text = "-" + text

    # '.'이 여러 개 들어간 경우 첫 번째만 허용
    if text.count(".") > 1:
        first_dot = text.find(".")
        text = text[: first_dot + 1] + text[first_dot + 1 :].replace(".", "")

    return text


def to_int_or_none(value: NumberLike) -> Optional[int]:
    """
    콤마 포함 문자열 등을 int로 변환
    변환 불가하면 None
    """
    text = only_numeric_string(value)
    if text in ("", "-", ".", "-."):
        return None

    try:
        return int(Decimal(text))
    except (InvalidOperation, ValueError):
        return None


def to_decimal_or_none(value: NumberLike) -> Optional[Decimal]:
    """
    콤마 포함 문자열 등을 Decimal로 변환
    변환 불가하면 None
    """
    text = only_numeric_string(value)
    if text in ("", "-", ".", "-."):
        return None

    try:
        return Decimal(text)
    except InvalidOperation:
        return None


def format_int_display(value: NumberLike) -> str:
    """
    화면 표시용 정수 포맷
    예)
        50000 -> "50,000"
        "50000" -> "50,000"
        None -> ""
    """
    num = to_int_or_none(value)
    if num is None:
        return ""
    return f"{num:,}"


def format_decimal_display(value: NumberLike, scale: int = 2) -> str:
    """
    화면 표시용 소수 포맷
    예)
        1234.5 -> "1,234.50"
    """
    num = to_decimal_or_none(value)
    if num is None:
        return ""

    quantized = num.quantize(Decimal("1." + ("0" * scale)))
    return f"{quantized:,.{scale}f}"


def normalize_integer_input_in_session(session_key: str) -> None:
    """
    Streamlit session_state 값에 대해
    사용자가 입력을 마치고 포커스를 벗어났을 때
    정수형 표시 포맷으로 바꿔준다.
    """
    import streamlit as st

    raw_value = st.session_state.get(session_key, "")
    if safe_strip(raw_value) == "":
        st.session_state[session_key] = ""
        return

    converted = to_int_or_none(raw_value)
    if converted is None:
        # 숫자 변환 불가 시 원본 유지 또는 공백 처리 중 선택 가능
        # 여기서는 원본 유지
        st.session_state[session_key] = safe_strip(raw_value)
        return

    st.session_state[session_key] = f"{converted:,}"


def normalize_decimal_input_in_session(session_key: str, scale: int = 2) -> None:
    """
    Streamlit session_state 값에 대해
    소수형 표시 포맷으로 바꿔준다.
    """
    import streamlit as st

    raw_value = st.session_state.get(session_key, "")
    if safe_strip(raw_value) == "":
        st.session_state[session_key] = ""
        return

    converted = to_decimal_or_none(raw_value)
    if converted is None:
        st.session_state[session_key] = safe_strip(raw_value)
        return

    st.session_state[session_key] = format_decimal_display(converted, scale=scale)




def to_float(value, default: float = 0.0) -> float:
    """
    숫자/문자 값을 float으로 안전하게 변환
    - None, 빈문자, 변환 실패 시 default 반환
    """
    if value is None:
        return default

    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip().replace(",", "")
    if text == "":
        return default

    try:
        return float(text)
    except (ValueError, TypeError):
        return default


def to_int(value, default: int = 0) -> int:
    """
    숫자/문자 값을 int로 안전하게 변환
    - None, 빈문자, 변환 실패 시 default 반환
    """
    if value is None:
        return default

    if isinstance(value, int):
        return value

    if isinstance(value, float):
        return int(value)

    text = str(value).strip().replace(",", "")
    if text == "":
        return default

    try:
        return int(float(text))
    except (ValueError, TypeError):
        return default


def format_number(value, digits: int = 0, default: str = "") -> str:
    """
    숫자를 천단위 콤마 형식 문자열로 변환
    예)
    - format_number(1000000) -> '1,000,000'
    - format_number(186600.5, 1) -> '186,600.5'
    """
    if value is None:
        return default

    try:
        number = Decimal(str(value).replace(",", "").strip())
    except (InvalidOperation, AttributeError):
        return default

    if digits <= 0:
        return f"{int(number):,}"

    return f"{float(number):,.{digits}f}"


def format_currency(value, symbol: str = "", digits: int = 0, default: str = "") -> str:
    """
    통화 표시용 문자열 반환
    예)
    - format_currency(1000000, "₩") -> '₩ 1,000,000'
    - format_currency(1234.56, "$", 2) -> '$ 1,234.56'
    """
    formatted = format_number(value, digits=digits, default=default)
    if formatted == "":
        return default

    return f"{symbol} {formatted}".strip()


def parse_number(value, default: float = 0.0) -> float:
    """
    format_number와 반대로 콤마 포함 문자열을 숫자로 변환
    예)
    - parse_number('1,000,000') -> 1000000.0
    """
    return to_float(value, default=default)

def get_today_str():
    return datetime.now().strftime("%Y-%m-%d")

def nvl(value, default=""):
    return value if value is not None else default
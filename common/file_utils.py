import os
import uuid
from typing import Iterable, Optional, Tuple

from common.exceptions import ValidationError


def ensure_directory(directory: str) -> None:
    os.makedirs(directory, exist_ok=True)


def normalize_file_path(file_path: Optional[str]) -> Optional[str]:
    if not file_path:
        return None
    return file_path.replace("\\", "/")


def delete_file_if_exists(file_path: Optional[str]) -> None:
    normalized_path = normalize_file_path(file_path)
    if not normalized_path:
        return

    if os.path.exists(normalized_path):
        try:
            os.remove(normalized_path)
        except Exception:
            pass


def validate_uploaded_file(
    uploaded_file,
    allowed_content_types: Optional[Iterable[str]] = None,
    allowed_extensions: Optional[Iterable[str]] = None,
    max_size_mb: Optional[int] = None,
    field_label: str = "File",
) -> None:
    if uploaded_file is None:
        return

    if allowed_content_types:
        allowed_content_types = set(allowed_content_types)
        if getattr(uploaded_file, "type", None) not in allowed_content_types:
            raise ValidationError(
                f"{field_label} type is not allowed."
            )

    if allowed_extensions:
        allowed_extensions = {ext.lower() for ext in allowed_extensions}
        ext = os.path.splitext(uploaded_file.name)[1].lower()
        if ext not in allowed_extensions:
            allowed_text = ", ".join(sorted(allowed_extensions))
            raise ValidationError(
                f"{field_label} extension must be one of: {allowed_text}"
            )

    if max_size_mb is not None:
        file_size = getattr(uploaded_file, "size", 0)
        if file_size > max_size_mb * 1024 * 1024:
            raise ValidationError(
                f"{field_label} size must be less than or equal to {max_size_mb}MB."
            )


def save_uploaded_file(
    uploaded_file,
    upload_dir: str,
    prefix: str = "",
    allowed_content_types: Optional[Iterable[str]] = None,
    allowed_extensions: Optional[Iterable[str]] = None,
    max_size_mb: Optional[int] = None,
    field_label: str = "File",
) -> Tuple[str, str]:
    if uploaded_file is None:
        return "", ""

    validate_uploaded_file(
        uploaded_file=uploaded_file,
        allowed_content_types=allowed_content_types,
        allowed_extensions=allowed_extensions,
        max_size_mb=max_size_mb,
        field_label=field_label,
    )

    ensure_directory(upload_dir)

    original_name = uploaded_file.name
    ext = os.path.splitext(original_name)[1].lower()

    safe_prefix = (prefix or "file").strip()
    safe_prefix = safe_prefix.replace(" ", "_").replace("/", "_").replace("\\", "_")

    unique_name = f"{safe_prefix}_{uuid.uuid4().hex}{ext}"
    saved_path = os.path.join(upload_dir, unique_name)

    with open(saved_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    normalized_path = normalize_file_path(saved_path) or ""
    return normalized_path, original_name


def is_image_file(file_path: Optional[str]) -> bool:
    normalized_path = normalize_file_path(file_path)
    if not normalized_path:
        return False

    ext = os.path.splitext(normalized_path)[1].lower()
    return ext in {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}
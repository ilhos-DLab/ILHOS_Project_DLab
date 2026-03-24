from sqlalchemy.exc import SQLAlchemyError

from common.db import get_session
from common.exceptions import ValidationError, AuthenticationError, DatabaseError
from repositories.auth_repository import AuthRepository


class AuthService:
    """
    인증 관련 서비스
    - 입력값 검증
    - 사용자 인증 처리
    - 예외 변환 처리
    """

    def __init__(self):
        self.repo = AuthRepository()

    def _normalize_required_string(self, value, field_name: str) -> str:
        """
        필수 문자열 입력값 정리
        - None 불가
        - 공백 제거
        - 빈 문자열 불가
        """
        if value is None:
            raise ValidationError(f"{field_name} is required.")

        value = str(value).strip()

        if value == "":
            raise ValidationError(f"{field_name} is required.")

        return value

    def validate_user(self, company_code: str, login_id: str, password: str) -> dict:
        """
        로그인 사용자 검증
        - 유효한 사용자 정보가 있으면 사용자/권한 정보를 반환
        - 없으면 AuthenticationError 발생
        """
        company_code = self._normalize_required_string(company_code, "Company code")
        login_id = self._normalize_required_string(login_id, "Login ID")
        password = self._normalize_required_string(password, "Password")

        try:
            with get_session() as session:
                user = self.repo.get_user_for_login(
                    session=session,
                    company_code=company_code,
                    login_id=login_id,
                    password=password,
                )

                if not user:
                    raise AuthenticationError("Invalid login credentials.")

                return user

        except (ValidationError, AuthenticationError):
            raise
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to validate user. Detail: {str(e)}") from e
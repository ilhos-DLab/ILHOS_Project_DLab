from sqlalchemy.exc import SQLAlchemyError

from common.db import get_session
from common.exceptions import ValidationError, DatabaseError
from repositories.menu_repository import MenuRepository


class MenuService:
    """
    메뉴 관련 서비스
    - 입력값 검증
    - 권한 기준 메뉴 조회
    - 예외 변환 처리
    """

    def __init__(self):
        self.repo = MenuRepository()

    def _validate_company_id(self, company_id) -> int:
        """
        회사 ID 검증
        """
        if company_id is None or str(company_id).strip() == "":
            raise ValidationError("Company ID is required.")

        try:
            return int(company_id)
        except (TypeError, ValueError) as e:
            raise ValidationError("Company ID must be a valid integer.") from e

    def _normalize_role_id(self, role_id) -> int | None:
        """
        권한 ID 정리
        - 없으면 None 허용
        - 값이 있으면 정수로 변환
        """
        if role_id is None or str(role_id).strip() == "":
            return None

        try:
            return int(role_id)
        except (TypeError, ValueError) as e:
            raise ValidationError("Role ID must be a valid integer.") from e

    def get_menu_list(self, company_id, role_id=None) -> list[dict]:
        """
        메뉴 목록 조회
        - role_id 가 있으면 권한 기준 메뉴 우선 조회
        - 권한 메뉴가 없으면 회사 기준 전체 메뉴 조회
        """
        company_id = self._validate_company_id(company_id)
        role_id = self._normalize_role_id(role_id)

        try:
            with get_session() as session:
                rows = []

                if role_id is not None:
                    rows = self.repo.get_menu_list_with_role(
                        session=session,
                        company_id=company_id,
                        role_id=role_id,
                    )

                if not rows:
                    rows = self.repo.get_menu_list_without_role(
                        session=session,
                        company_id=company_id,
                    )

                return rows

        except ValidationError:
            raise
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to retrieve menu list.") from e
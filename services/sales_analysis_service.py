from datetime import date, datetime

from sqlalchemy.exc import SQLAlchemyError

from common.db import get_session
from common.exceptions import ValidationError, DatabaseError
from common.logger import get_logger
from repositories.sales_analysis_repository import SalesAnalysisRepository

logger = get_logger(__name__)


class SalesAnalysisService:
    def __init__(self):
        self.repo = SalesAnalysisRepository()

    def _parse_date(self, value, field_name: str) -> date:
        """
        날짜값 검증 및 date 타입 변환
        """
        if value is None or value == "":
            raise ValidationError(f"{field_name} is required.")

        if isinstance(value, date) and not isinstance(value, datetime):
            return value

        if isinstance(value, datetime):
            return value.date()

        if isinstance(value, str):
            try:
                return datetime.strptime(value.strip(), "%Y-%m-%d").date()
            except ValueError as e:
                raise ValidationError(f"{field_name} must be in YYYY-MM-DD format.") from e

        raise ValidationError(f"{field_name} has an invalid format.")

    def get_monthly_sales_summary(self, from_date, to_date):
        try:
            validated_from_date = self._parse_date(from_date, "From date")
            validated_to_date = self._parse_date(to_date, "To date")

            if validated_from_date > validated_to_date:
                raise ValidationError("From date cannot be later than to date.")

            with get_session() as session:
                return self.repo.get_monthly_sales_summary(
                    session,
                    validated_from_date,
                    validated_to_date,
                )

        except ValidationError:
            raise
        except SQLAlchemyError as e:
            logger.exception("Database error occurred while retrieving monthly sales summary.")
            raise DatabaseError("Failed to retrieve monthly sales summary.") from e
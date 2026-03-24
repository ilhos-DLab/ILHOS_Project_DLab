from datetime import date, datetime

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from common.db import get_session
from common.exceptions import ValidationError, NotFoundError, BusinessError, DatabaseError
from common.logger import get_logger
from repositories.company_repository import CompanyRepository

logger = get_logger(__name__)


class CompanyService:
    def __init__(self):
        self.repo = CompanyRepository()

    def _normalize_string(self, value, max_length: int | None = None, field_name: str = "Field"):
        if value is None:
            return None

        if not isinstance(value, str):
            value = str(value)

        value = value.strip()

        if value == "":
            return None

        if max_length is not None and len(value) > max_length:
            raise ValidationError(f"{field_name} must be {max_length} characters or fewer.")

        return value

    def _parse_date(self, value, field_name: str) -> date:
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

    def _validate_use_yn(self, use_yn: str | None) -> str:
        value = (use_yn or "Y").strip().upper()
        if value not in ("Y", "N"):
            raise ValidationError("Use flag must be 'Y' or 'N'.")
        return value

    def _validate_company_code(self, company_code: str) -> str:
        company_code = self._normalize_string(company_code, 30, "Company code")
        if not company_code:
            raise ValidationError("Company code is required.")
        return company_code

    def _validate_company_name(self, company_name: str) -> str:
        company_name = self._normalize_string(company_name, 200, "Company name")
        if not company_name:
            raise ValidationError("Company name is required.")
        return company_name

    def _validate_company_data(self, data: dict, is_create: bool = True) -> dict:
        validated = {}

        if is_create:
            validated["company_code"] = self._validate_company_code(data.get("company_code"))

        validated["company_name"] = self._validate_company_name(data.get("company_name"))
        validated["business_no"] = self._normalize_string(data.get("business_no"), 20, "Business number")
        validated["ceo_name"] = self._normalize_string(data.get("ceo_name"), 100, "CEO name")
        validated["tel_no"] = self._normalize_string(data.get("tel_no"), 30, "Telephone number")
        validated["address"] = self._normalize_string(data.get("address"), 500, "Address")
        validated["remark"] = self._normalize_string(data.get("remark"), 1000, "Remark")
        validated["use_yn"] = self._validate_use_yn(data.get("use_yn"))

        service_start_date = self._parse_date(data.get("service_start_date"), "Service start date")
        service_end_date = self._parse_date(data.get("service_end_date"), "Service end date")

        if service_start_date > service_end_date:
            raise ValidationError("Service start date cannot be later than service end date.")

        validated["service_start_date"] = service_start_date
        validated["service_end_date"] = service_end_date
        validated["logo_path"] = self._normalize_string(data.get("logo_path"), 500, "Logo path")
        validated["logo_file_name"] = self._normalize_string(data.get("logo_file_name"), 255, "Logo file name")

        return validated

    def get_company_list(self, search_name: str | None = None, use_yn: str | None = None):
        try:
            normalized_search_name = self._normalize_string(search_name, 200, "Search name")
            normalized_use_yn = None

            if use_yn is not None and str(use_yn).strip() != "":
                normalized_use_yn = self._validate_use_yn(use_yn)

            with get_session() as session:
                return self.repo.get_list(session, normalized_search_name, normalized_use_yn)

        except ValidationError:
            raise
        except SQLAlchemyError as e:
            logger.exception("Database error occurred while retrieving company list.")
            raise DatabaseError("Failed to retrieve company list.") from e

    def get_company_detail(self, company_id: int):
        try:
            if not company_id:
                raise ValidationError("Company ID is required.")

            with get_session() as session:
                company = self.repo.get_by_id(session, company_id)
                if not company:
                    raise NotFoundError("Company not found.")

                return company

        except (ValidationError, NotFoundError):
            raise
        except SQLAlchemyError as e:
            logger.exception("Database error occurred while retrieving company detail.")
            raise DatabaseError("Failed to retrieve company detail.") from e

    def get_next_company_code(self):
        try:
            with get_session() as session:
                return self.repo.get_next_company_code(session)

        except SQLAlchemyError as e:
            logger.exception("Database error occurred while generating next company code.")
            raise DatabaseError("Failed to generate company code.") from e

    def create_company(self, data: dict):
        try:
            validated = self._validate_company_data(data, is_create=True)
            created_by = data.get("created_by")

            logger.info("Company creation started | company_code=%s", validated["company_code"])

            with get_session() as session:
                if self.repo.exists_company_code(session, validated["company_code"]):
                    raise BusinessError("Company code already exists.")

                self.repo.insert(session, {
                    "company_code": validated["company_code"],
                    "company_name": validated["company_name"],
                    "business_no": validated["business_no"],
                    "ceo_name": validated["ceo_name"],
                    "tel_no": validated["tel_no"],
                    "address": validated["address"],
                    "service_start_date": validated["service_start_date"],
                    "service_end_date": validated["service_end_date"],
                    "remark": validated["remark"],
                    "use_yn": validated["use_yn"],
                    "logo_path": validated["logo_path"],
                    "logo_file_name": validated["logo_file_name"],
                    "created_by": created_by,
                })

            logger.info("Company creation completed | company_code=%s", validated["company_code"])
            return True

        except (ValidationError, NotFoundError, BusinessError):
            raise
        except IntegrityError as e:
            logger.exception("Integrity error occurred during company creation.")
            raise DatabaseError("Failed to create company due to database constraints.") from e
        except SQLAlchemyError as e:
            logger.exception("Database error occurred during company creation.")
            raise DatabaseError("Failed to create company.") from e

    def update_company(self, company_id: int, data: dict):
        try:
            if not company_id:
                raise ValidationError("Company ID is required.")

            validated = self._validate_company_data(data, is_create=False)
            updated_by = data.get("updated_by")

            logger.info("Company update started | company_id=%s", company_id)

            with get_session() as session:
                company = self.repo.get_by_id(session, company_id)
                if not company:
                    raise NotFoundError("Company not found.")

                rowcount = self.repo.update(session, company_id, {
                    "company_name": validated["company_name"],
                    "business_no": validated["business_no"],
                    "ceo_name": validated["ceo_name"],
                    "tel_no": validated["tel_no"],
                    "address": validated["address"],
                    "service_start_date": validated["service_start_date"],
                    "service_end_date": validated["service_end_date"],
                    "remark": validated["remark"],
                    "use_yn": validated["use_yn"],
                    "logo_path": validated["logo_path"],
                    "logo_file_name": validated["logo_file_name"],
                    "updated_by": updated_by,
                })

                if rowcount == 0:
                    raise BusinessError("No company record was updated.")

            logger.info("Company update completed | company_id=%s", company_id)
            return True

        except (ValidationError, NotFoundError, BusinessError):
            raise
        except IntegrityError as e:
            logger.exception("Integrity error occurred during company update.")
            raise DatabaseError("Failed to update company due to database constraints.") from e
        except SQLAlchemyError as e:
            logger.exception("Database error occurred during company update.")
            raise DatabaseError("Failed to update company.") from e

    def delete_company(self, company_id: int, deleted_by: int | None = None):
        try:
            if not company_id:
                raise ValidationError("Company ID is required.")

            logger.info("Company deletion started | company_id=%s", company_id)

            with get_session() as session:
                company = self.repo.get_by_id(session, company_id)
                if not company:
                    raise NotFoundError("Company not found.")

                rowcount = self.repo.delete(session, company_id, deleted_by)

                if rowcount == 0:
                    raise BusinessError("No company record was deleted.")

            logger.info("Company deletion completed | company_id=%s", company_id)
            return True

        except (ValidationError, NotFoundError, BusinessError):
            raise
        except SQLAlchemyError as e:
            logger.exception("Database error occurred during company deletion.")
            raise DatabaseError("Failed to delete company.") from e
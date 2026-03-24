from sqlalchemy import text
from sqlalchemy.orm import Session


class CompanyRepository:
    """
    업체 정보에 대한 DB 접근 전용 Repository
    - SQL 실행만 담당
    - commit / rollback 은 service 계층에서 처리
    """

    def get_list(
        self,
        session: Session,
        search_name: str | None = None,
        use_yn: str | None = None,
    ) -> list[dict]:
        sql = """
        SELECT
            COMPANY_ID,
            COMPANY_CODE,
            COMPANY_NAME,
            BUSINESS_NO,
            CEO_NAME,
            TEL_NO,
            ADDRESS,
            SERVICE_START_DATE,
            SERVICE_END_DATE,
            REMARK,
            LOGO_PATH,
            LOGO_FILE_NAME,
            CREATED_AT,
            CREATED_BY,
            UPDATED_AT,
            UPDATED_BY,
            USE_YN,
            DEL_YN
        FROM dbo.TB_COMPANY
        WHERE DEL_YN = 'N'
        """

        params = {}

        if search_name:
            sql += " AND COMPANY_NAME LIKE :search_name "
            params["search_name"] = f"%{search_name}%"

        if use_yn:
            sql += " AND USE_YN = :use_yn "
            params["use_yn"] = use_yn

        sql += " ORDER BY COMPANY_ID DESC "

        result = session.execute(text(sql), params).mappings().all()
        return [dict(row) for row in result]

    def get_by_id(self, session: Session, company_id: int) -> dict | None:
        sql = """
        SELECT
            COMPANY_ID,
            COMPANY_CODE,
            COMPANY_NAME,
            BUSINESS_NO,
            CEO_NAME,
            TEL_NO,
            ADDRESS,
            SERVICE_START_DATE,
            SERVICE_END_DATE,
            REMARK,
            LOGO_PATH,
            LOGO_FILE_NAME,
            CREATED_AT,
            CREATED_BY,
            UPDATED_AT,
            UPDATED_BY,
            USE_YN,
            DEL_YN
        FROM dbo.TB_COMPANY
        WHERE COMPANY_ID = :company_id
          AND DEL_YN = 'N'
        """

        row = session.execute(
            text(sql),
            {"company_id": company_id},
        ).mappings().first()

        return dict(row) if row else None

    def exists_company_code(
        self,
        session: Session,
        company_code: str,
        exclude_company_id: int | None = None,
    ) -> bool:
        sql = """
        SELECT COUNT(1) AS CNT
        FROM dbo.TB_COMPANY
        WHERE COMPANY_CODE = :company_code
          AND DEL_YN = 'N'
        """

        params = {"company_code": company_code}

        if exclude_company_id is not None:
            sql += " AND COMPANY_ID <> :exclude_company_id "
            params["exclude_company_id"] = exclude_company_id

        count = session.execute(text(sql), params).scalar_one()
        return count > 0

    def get_next_company_code(self, session: Session) -> str:
        sql = """
        SELECT ISNULL(MAX(COMPANY_ID), 0) + 1 AS NEXT_ID
        FROM dbo.TB_COMPANY
        """

        next_id = session.execute(text(sql)).scalar_one()
        return f"C{str(next_id).zfill(4)}"

    def insert(self, session: Session, data: dict) -> None:
        sql = """
        INSERT INTO dbo.TB_COMPANY
        (
            COMPANY_CODE,
            COMPANY_NAME,
            BUSINESS_NO,
            CEO_NAME,
            TEL_NO,
            ADDRESS,
            SERVICE_START_DATE,
            SERVICE_END_DATE,
            REMARK,
            LOGO_PATH,
            LOGO_FILE_NAME,
            CREATED_BY,
            USE_YN,
            DEL_YN
        )
        VALUES
        (
            :company_code,
            :company_name,
            :business_no,
            :ceo_name,
            :tel_no,
            :address,
            :service_start_date,
            :service_end_date,
            :remark,
            :logo_path,
            :logo_file_name,
            :created_by,
            :use_yn,
            'N'
        )
        """

        params = {
            "company_code": data["company_code"],
            "company_name": data["company_name"],
            "business_no": data.get("business_no"),
            "ceo_name": data.get("ceo_name"),
            "tel_no": data.get("tel_no"),
            "address": data.get("address"),
            "service_start_date": data.get("service_start_date"),
            "service_end_date": data.get("service_end_date"),
            "remark": data.get("remark"),
            "logo_path": data.get("logo_path"),
            "logo_file_name": data.get("logo_file_name"),
            "created_by": data.get("created_by"),
            "use_yn": data.get("use_yn", "Y"),
        }

        session.execute(text(sql), params)

    def update(self, session: Session, company_id: int, data: dict) -> int:
        sql = """
        UPDATE dbo.TB_COMPANY
           SET COMPANY_NAME       = :company_name,
               BUSINESS_NO        = :business_no,
               CEO_NAME           = :ceo_name,
               TEL_NO             = :tel_no,
               ADDRESS            = :address,
               SERVICE_START_DATE = :service_start_date,
               SERVICE_END_DATE   = :service_end_date,
               REMARK             = :remark,
               LOGO_PATH          = :logo_path,
               LOGO_FILE_NAME     = :logo_file_name,
               UPDATED_AT         = GETDATE(),
               UPDATED_BY         = :updated_by,
               USE_YN             = :use_yn
         WHERE COMPANY_ID         = :company_id
           AND DEL_YN             = 'N'
        """

        params = {
            "company_id": company_id,
            "company_name": data["company_name"],
            "business_no": data.get("business_no"),
            "ceo_name": data.get("ceo_name"),
            "tel_no": data.get("tel_no"),
            "address": data.get("address"),
            "service_start_date": data.get("service_start_date"),
            "service_end_date": data.get("service_end_date"),
            "remark": data.get("remark"),
            "logo_path": data.get("logo_path"),
            "logo_file_name": data.get("logo_file_name"),
            "updated_by": data.get("updated_by"),
            "use_yn": data.get("use_yn", "Y"),
        }

        result = session.execute(text(sql), params)
        return result.rowcount

    def delete(
        self,
        session: Session,
        company_id: int,
        deleted_by: int | None = None,
    ) -> int:
        sql = """
        UPDATE dbo.TB_COMPANY
           SET DEL_YN     = 'Y',
               UPDATED_AT = GETDATE(),
               UPDATED_BY = :deleted_by
         WHERE COMPANY_ID = :company_id
           AND DEL_YN     = 'N'
        """

        result = session.execute(
            text(sql),
            {
                "company_id": company_id,
                "deleted_by": deleted_by,
            },
        )
        return result.rowcount
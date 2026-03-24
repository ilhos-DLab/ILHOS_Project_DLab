from sqlalchemy import text
from sqlalchemy.orm import Session


class AuthRepository:
    """
    인증 관련 DB 조회 전용 Repository
    - SQL 실행만 담당
    - commit / rollback 은 service 계층에서 처리
    """

    def get_user_for_login(
        self,
        session: Session,
        company_code: str,
        login_id: str,
        password: str,
    ) -> dict | None:
        sql = text("""
            SELECT
                C.COMPANY_ID,
                C.COMPANY_CODE,
                C.COMPANY_NAME,
                U.USER_ID,
                U.LOGIN_ID,
                U.USER_NAME,
                R.ROLE_ID,
                R.ROLE_CODE,
                R.ROLE_NAME
            FROM dbo.TB_COMPANY C
            INNER JOIN dbo.TB_USER U
                ON C.COMPANY_ID = U.COMPANY_ID
            LEFT JOIN dbo.TB_USER_ROLE UR
                ON U.COMPANY_ID = UR.COMPANY_ID
               AND U.USER_ID = UR.USER_ID
               AND UR.USE_YN = 'Y'
               AND UR.DEL_YN = 'N'
            LEFT JOIN dbo.TB_ROLE R
                ON UR.ROLE_ID = R.ROLE_ID
               AND R.USE_YN = 'Y'
               AND R.DEL_YN = 'N'
            WHERE C.COMPANY_CODE = :company_code
              AND U.LOGIN_ID = :login_id
              AND U.PASSWORD = :password
              AND C.USE_YN = 'Y'
              AND C.DEL_YN = 'N'
              AND U.USE_YN = 'Y'
              AND U.DEL_YN = 'N'
              AND CAST(GETDATE() AS DATE) BETWEEN C.SERVICE_START_DATE AND C.SERVICE_END_DATE
        """)

        row = session.execute(
            sql,
            {
                "company_code": company_code,
                "login_id": login_id,
                "password": password,
            },
        ).mappings().first()

        return dict(row) if row else None
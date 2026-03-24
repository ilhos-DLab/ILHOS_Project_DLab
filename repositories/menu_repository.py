from sqlalchemy import text
from sqlalchemy.orm import Session


class MenuRepository:
    """
    메뉴 조회 전용 Repository
    - SQL 실행만 담당
    - commit / rollback 은 service 계층에서 처리
    """

    def get_menu_list_with_role(
        self,
        session: Session,
        company_id: int,
        role_id: int,
    ) -> list[dict]:
        sql = text("""
            SELECT
                M.MENU_ID,
                M.MENU_CODE,
                M.MENU_NAME,
                M.PARENT_MENU_ID,
                M.MENU_LEVEL,
                M.SORT_NO,
                M.PAGE_KEY,
                M.MENU_TYPE
            FROM dbo.TB_MENU M
            INNER JOIN dbo.TB_COMPANY_MENU CM
                ON M.MENU_ID = CM.MENU_ID
               AND CM.COMPANY_ID = :company_id
               AND CM.USE_YN = 'Y'
               AND CM.DEL_YN = 'N'
            INNER JOIN dbo.TB_ROLE_MENU_PERMISSION RMP
                ON M.MENU_ID = RMP.MENU_ID
               AND RMP.COMPANY_ID = :company_id
               AND RMP.ROLE_ID = :role_id
               AND RMP.READ_YN = 'Y'
               AND RMP.USE_YN = 'Y'
               AND RMP.DEL_YN = 'N'
            WHERE M.USE_YN = 'Y'
              AND M.DEL_YN = 'N'
            ORDER BY M.MENU_LEVEL, M.PARENT_MENU_ID, M.SORT_NO, M.MENU_ID
        """)

        result = session.execute(
            sql,
            {
                "company_id": company_id,
                "role_id": role_id,
            },
        ).mappings().all()

        return [dict(row) for row in result]

    def get_menu_list_without_role(
        self,
        session: Session,
        company_id: int,
    ) -> list[dict]:
        sql = text("""
            SELECT
                M.MENU_ID,
                M.MENU_CODE,
                M.MENU_NAME,
                M.PARENT_MENU_ID,
                M.MENU_LEVEL,
                M.SORT_NO,
                M.PAGE_KEY,
                M.MENU_TYPE
            FROM dbo.TB_MENU M
            INNER JOIN dbo.TB_COMPANY_MENU CM
                ON M.MENU_ID = CM.MENU_ID
               AND CM.COMPANY_ID = :company_id
               AND CM.USE_YN = 'Y'
               AND CM.DEL_YN = 'N'
            WHERE M.USE_YN = 'Y'
              AND M.DEL_YN = 'N'
            ORDER BY M.MENU_LEVEL, M.PARENT_MENU_ID, M.SORT_NO, M.MENU_ID
        """)

        result = session.execute(
            sql,
            {
                "company_id": company_id,
            },
        ).mappings().all()

        return [dict(row) for row in result]
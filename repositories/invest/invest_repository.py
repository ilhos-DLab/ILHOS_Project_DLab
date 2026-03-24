from sqlalchemy import text


class InvestRepository:
    # 투자 목록 조회
    def get_invest_list(self, session, invest_name: str = "", use_yn: str = "Y"):
        sql = text("""
            SELECT
                INVEST_ID,
                INVEST_CODE,
                INVEST_NAME,
                TICKER_SYMBOL,
                INVEST_TYPE,
                INVEST_AMOUNT,
                INVEST_DATE,
                REMARK,
                USE_YN
            FROM DLAB.dbo.TB_INVESTMENT
            WHERE DEL_YN = 'N'
              AND (:invest_name = '' OR INVEST_NAME LIKE '%' + :invest_name + '%')
              AND (:use_yn = '' OR USE_YN = :use_yn)
            ORDER BY INVEST_ID DESC
        """)

        result = session.execute(sql, {
            "invest_name": invest_name,
            "use_yn": use_yn,
        })

        return [dict(row._mapping) for row in result]

    # 투자 상세 조회
    def get_invest_detail(self, session, invest_id: int):
        sql = text("""
            SELECT
                INVEST_ID,
                INVEST_CODE,
                INVEST_NAME,
                TICKER_SYMBOL,
                INVEST_TYPE,
                INVEST_AMOUNT,
                INVEST_DATE,
                REMARK,
                USE_YN
            FROM DLAB.dbo.TB_INVESTMENT
            WHERE INVEST_ID = :invest_id
              AND DEL_YN = 'N'
        """)

        row = session.execute(sql, {"invest_id": invest_id}).mappings().first()
        return dict(row) if row else None

    # 투자 코드 중복 확인
    def exists_invest_code(self, session, invest_code: str, exclude_id: int | None = None):
        sql = text("""
            SELECT COUNT(*) AS CNT
            FROM DLAB.dbo.TB_INVESTMENT
            WHERE INVEST_CODE = :invest_code
              AND DEL_YN = 'N'
              AND (:exclude_id IS NULL OR INVEST_ID <> :exclude_id)
        """)

        row = session.execute(sql, {
            "invest_code": invest_code,
            "exclude_id": exclude_id,
        }).mappings().first()

        return row["CNT"] > 0

    # 투자 등록
    def insert_invest(self, session, data: dict):
        sql = text("""
            INSERT INTO DLAB.dbo.TB_INVESTMENT
            (
                INVEST_CODE,
                INVEST_NAME,
                TICKER_SYMBOL,
                INVEST_TYPE,
                INVEST_AMOUNT,
                INVEST_DATE,
                REMARK,
                USE_YN,
                DEL_YN,
                CREATED_AT,
                CREATED_BY
            )
            VALUES
            (
                :invest_code,
                :invest_name,
                :ticker_symbol,
                :invest_type,
                :invest_amount,
                :invest_date,
                :remark,
                :use_yn,
                'N',
                GETDATE(),
                :user_id
            )
        """)

        session.execute(sql, data)

    # 투자 수정
    def update_invest(self, session, invest_id: int, data: dict):
        params = dict(data)
        params["invest_id"] = invest_id

        sql = text("""
            UPDATE DLAB.dbo.TB_INVESTMENT
               SET INVEST_CODE   = :invest_code,
                   INVEST_NAME   = :invest_name,
                   TICKER_SYMBOL = :ticker_symbol,
                   INVEST_TYPE   = :invest_type,
                   INVEST_AMOUNT = :invest_amount,
                   INVEST_DATE   = :invest_date,
                   REMARK        = :remark,
                   USE_YN        = :use_yn,
                   UPDATED_AT    = GETDATE(),
                   UPDATED_BY    = :user_id
             WHERE INVEST_ID     = :invest_id
               AND DEL_YN        = 'N'
        """)

        session.execute(sql, params)

    # 투자 삭제
    def delete_invest(self, session, invest_id: int, user_id: int):
        sql = text("""
            UPDATE DLAB.dbo.TB_INVESTMENT
               SET DEL_YN = 'Y',
                   UPDATED_AT = GETDATE(),
                   UPDATED_BY = :user_id
             WHERE INVEST_ID = :invest_id
               AND DEL_YN = 'N'
        """)

        session.execute(sql, {
            "invest_id": invest_id,
            "user_id": user_id,
        })
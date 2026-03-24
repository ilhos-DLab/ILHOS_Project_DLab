from sqlalchemy import text


class SalesAnalysisRepository:
    def get_monthly_sales_summary(self, session, from_date, to_date):
        # 월별 매출 집계 데이터 조회
        sql = text("""
            SELECT
                CONVERT(VARCHAR(7), SALE_DATE, 120) AS SALE_MONTH,
                SUM(SALE_QTY) AS TOTAL_QTY,
                SUM(SALE_AMOUNT) AS TOTAL_AMOUNT
            FROM dbo.TB_SALES
            WHERE SALE_DATE BETWEEN :from_date AND :to_date
            GROUP BY CONVERT(VARCHAR(7), SALE_DATE, 120)
            ORDER BY SALE_MONTH
        """)

        result = session.execute(
            sql,
            {
                "from_date": from_date,
                "to_date": to_date,
            }
        )

        return [dict(row._mapping) for row in result]
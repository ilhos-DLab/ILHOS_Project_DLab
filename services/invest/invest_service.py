from config.database import SessionLocal
from common.exceptions import ValidationError, NotFoundError, DatabaseError
from repositories.invest.invest_repository import InvestRepository
from services.invest.market_data_service import MarketDataService


class InvestService:
    def __init__(self):
        self.repo = InvestRepository()
        self.market_service = MarketDataService()

    # 투자 목록 조회
    def get_invest_list(self, invest_name: str = "", use_yn: str = "Y"):
        try:
            with SessionLocal() as session:
                return self.repo.get_invest_list(
                    session=session,
                    invest_name=invest_name,
                    use_yn=use_yn,
                )
        except Exception as e:
            raise DatabaseError(f"Failed to retrieve investment list. {e}")

    # 투자 상세 조회
    def get_invest_detail(self, invest_id: int):
        try:
            with SessionLocal() as session:
                item = self.repo.get_invest_detail(session=session, invest_id=invest_id)
                if not item:
                    raise NotFoundError("Investment data was not found.")
                return item
        except NotFoundError:
            raise
        except Exception as e:
            raise DatabaseError(f"Failed to retrieve investment detail. {e}")

    # 티커 정보 조회
    def get_market_price(self, ticker_symbol: str):
        try:
            return self.market_service.get_current_price(ticker_symbol)
        except Exception as e:
            raise DatabaseError(f"Failed to retrieve market data. {e}")

    # 입력값 검증
    def validate_invest_data(
        self,
        session,
        data: dict,
        mode: str = "NEW",
        invest_id: int | None = None,
    ) -> None:
        if not str(data.get("invest_code", "")).strip():
            raise ValidationError("Investment code is required.")

        if not str(data.get("invest_name", "")).strip():
            raise ValidationError("Investment name is required.")

        if not str(data.get("ticker_symbol", "")).strip():
            raise ValidationError("Ticker symbol is required.")

        if not str(data.get("invest_type", "")).strip():
            raise ValidationError("Investment type is required.")

        if data.get("invest_amount") is None:
            raise ValidationError("Investment amount is required.")

        if float(data["invest_amount"]) < 0:
            raise ValidationError("Investment amount must be 0 or greater.")

        if not data.get("invest_date"):
            raise ValidationError("Investment date is required.")

        exists = self.repo.exists_invest_code(
            session=session,
            invest_code=str(data["invest_code"]).strip(),
            exclude_id=invest_id if mode == "EDIT" else None,
        )

        if exists:
            raise ValidationError("Investment code already exists.")

    # 투자 등록
    def create_invest(self, data: dict):
        try:
            with SessionLocal() as session:
                self.validate_invest_data(session=session, data=data, mode="NEW")
                self.repo.insert_invest(session=session, data=data)
                session.commit()
        except ValidationError:
            raise
        except Exception as e:
            raise DatabaseError(f"Failed to create investment data. {e}")

    # 투자 수정
    def modify_invest(self, invest_id: int, data: dict):
        try:
            with SessionLocal() as session:
                current = self.repo.get_invest_detail(session=session, invest_id=invest_id)
                if not current:
                    raise NotFoundError("Investment data was not found.")

                self.validate_invest_data(
                    session=session,
                    data=data,
                    mode="EDIT",
                    invest_id=invest_id,
                )

                self.repo.update_invest(session=session, invest_id=invest_id, data=data)
                session.commit()
        except ValidationError:
            raise
        except NotFoundError:
            raise
        except Exception as e:
            raise DatabaseError(f"Failed to update investment data. {e}")

    # 투자 삭제
    def remove_invest(self, invest_id: int, user_id: int):
        try:
            with SessionLocal() as session:
                current = self.repo.get_invest_detail(session=session, invest_id=invest_id)
                if not current:
                    raise NotFoundError("Investment data was not found.")

                self.repo.delete_invest(session=session, invest_id=invest_id, user_id=user_id)
                session.commit()
        except NotFoundError:
            raise
        except Exception as e:
            raise DatabaseError(f"Failed to delete investment data. {e}")
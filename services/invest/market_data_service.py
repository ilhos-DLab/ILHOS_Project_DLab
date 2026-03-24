import yfinance as yf


class MarketDataService:
    # 티커 유효성 및 현재가 조회
    def get_current_price(self, ticker_symbol: str) -> dict:
        ticker = str(ticker_symbol).strip().upper()

        if not ticker:
            return {
                "ticker_symbol": "",
                "name": "",
                "current_price": None,
                "currency": "",
                "market": "",
            }

        stock = yf.Ticker(ticker)
        info = stock.info if stock else {}

        return {
            "ticker_symbol": ticker,
            "name": info.get("shortName", ""),
            "current_price": info.get("currentPrice", None),
            "currency": info.get("currency", ""),
            "market": info.get("exchange", ""),
        }
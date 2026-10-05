from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, Any, List
from src.domain.policies.portfolio_pnl_policy import PortfolioPnLPolicy
from src.repositories.portfolio_repository import PortfolioRepository
from src.repositories.stock_repository import StockRepository


class PortfolioService:
    def __init__(self, portfolio_repo: PortfolioRepository, stock_repo: StockRepository):
        self.portfolio_repo = portfolio_repo
        self.stock_repo = stock_repo

    def get_statistics(self, user_id: int) -> Dict[str, Any]:
        """AC-09: Exact fixed-point decimal portfolio valuation."""
        holdings = self.portfolio_repo.get_holdings(user_id)
        holdings_data = []
        for h in holdings:
            stock = self.stock_repo.get_by_symbol(h.symbol, include_delisted=True)
            curr_price = stock.current_price if stock else h.average_buy_price
            holdings_data.append({
                "symbol": h.symbol,
                "shares_held": h.shares_held,
                "average_buy_price": h.average_buy_price,
                "current_price": curr_price
            })

        summary = PortfolioPnLPolicy.calculate_summary(holdings_data)
        return {
            "user_id": user_id,
            "total_invested": str(summary["total_invested"]),
            "current_value": str(summary["current_value"]),
            "absolute_pnl": str(summary["absolute_pnl"]),
            "percent_pnl": str(summary["percent_pnl"]),
            "currency": "USD",
            "calculated_at": datetime.now(timezone.utc).isoformat()
        }

    def get_holdings_breakdown(self, user_id: int) -> List[Dict[str, Any]]:
        holdings = self.portfolio_repo.get_holdings(user_id)
        results = []
        for h in holdings:
            stock = self.stock_repo.get_by_symbol(h.symbol, include_delisted=True)
            curr_price = stock.current_price if stock else h.average_buy_price
            pos_pnl = PortfolioPnLPolicy.calculate_position_pnl(
                shares_held=h.shares_held,
                avg_price=h.average_buy_price,
                current_price=curr_price
            )
            results.append({
                "symbol": h.symbol,
                "name": stock.name if stock else h.symbol,
                "shares_held": str(h.shares_held),
                "average_buy_price": str(h.average_buy_price),
                "current_price": str(curr_price),
                "total_invested": str(pos_pnl["total_invested"]),
                "current_value": str(pos_pnl["current_value"]),
                "absolute_pnl": str(pos_pnl["absolute_pnl"]),
                "percent_pnl": str(pos_pnl["percent_pnl"])
            })
        return results

    def get_cash_balance(self, user_id: int) -> Dict[str, Any]:
        cash = self.portfolio_repo.get_cash(user_id)
        return {
            "user_id": user_id,
            "available_cash": str(cash),
            "currency": "USD"
        }

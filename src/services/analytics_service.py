from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, List
from src.domain.policies.gainer_loser_policy import GainerLoserPolicy
from src.repositories.portfolio_repository import PortfolioRepository
from src.repositories.stock_repository import StockRepository
from src.repositories.order_repository import OrderRepository


class AnalyticsService:
    def __init__(
        self,
        portfolio_repo: PortfolioRepository,
        stock_repo: StockRepository,
        order_repo: OrderRepository
    ):
        self.portfolio_repo = portfolio_repo
        self.stock_repo = stock_repo
        self.order_repo = order_repo

    def get_daily_performance(self, user_id: int) -> Dict[str, Any]:
        """AC-10: Top 5 gainers and losers from customer's active holdings."""
        holdings = self.portfolio_repo.get_holdings(user_id)
        if not holdings:
            return {
                "user_id": user_id,
                "top_gainers": [],
                "top_losers": [],
                "calculated_at": datetime.now(timezone.utc).isoformat()
            }

        holdings_data = []
        for h in holdings:
            stock = self.stock_repo.get_by_symbol(h.symbol, include_delisted=True)
            if stock:
                curr_price = stock.current_price
                open_price = stock.open_price
                name = stock.name
            else:
                curr_price = h.average_buy_price
                open_price = h.average_buy_price
                name = h.symbol

            holdings_data.append({
                "symbol": h.symbol,
                "name": name,
                "shares_held": h.shares_held,
                "current_price": curr_price,
                "open_price": open_price
            })

        movers = GainerLoserPolicy.rank_movers(holdings_data)

        # Format DTO strings
        def _format_items(items: List[Dict]) -> List[Dict]:
            formatted = []
            for item in items:
                pct = item["change_percent"]
                pct_str = f"{'+' if pct >= 0 else ''}{pct}%"
                formatted.append({
                    "symbol": item["symbol"],
                    "name": item["name"],
                    "shares_held": str(item["shares_held"]),
                    "current_price": str(item["current_price"]),
                    "open_price": str(item["open_price"]),
                    "change_amount": str(item["change_amount"]),
                    "change_percent": pct_str
                })
            return formatted

        return {
            "user_id": user_id,
            "top_gainers": _format_items(movers["top_gainers"]),
            "top_losers": _format_items(movers["top_losers"]),
            "calculated_at": datetime.now(timezone.utc).isoformat()
        }

    def get_sector_exposure(self, user_id: int) -> Dict[str, Any]:
        """Aggregates market value and percentage weight by sector."""
        holdings = self.portfolio_repo.get_holdings(user_id)
        sector_totals = {}
        total_market_value = Decimal("0.0000")

        for h in holdings:
            stock = self.stock_repo.get_by_symbol(h.symbol, include_delisted=True)
            sector = stock.sector if stock else "Unknown"
            curr_price = stock.current_price if stock else h.average_buy_price
            val = (h.shares_held * curr_price).quantize(Decimal("0.0001"))

            total_market_value += val
            sector_totals[sector] = sector_totals.get(sector, Decimal("0.0000")) + val

        breakdown = []
        for sec, val in sector_totals.items():
            if total_market_value > Decimal("0.0000"):
                weight = ((val / total_market_value) * Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            else:
                weight = Decimal("0.00")
            breakdown.append({
                "sector": sec,
                "market_value": str(val),
                "weight_percent": f"{weight}%"
            })

        return {
            "user_id": user_id,
            "total_market_value": str(total_market_value.quantize(Decimal("0.0001"))),
            "sectors": sorted(breakdown, key=lambda x: float(x["weight_percent"].replace("%", "")), reverse=True)
        }

    def get_admin_order_statistics(self) -> Dict[str, Any]:
        """Admin telemetry for platform-wide order stats."""
        return self.order_repo.get_admin_order_statistics()

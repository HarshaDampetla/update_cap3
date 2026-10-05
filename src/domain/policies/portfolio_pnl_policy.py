from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Any


class PortfolioPnLPolicy:
    """Enforces mathematical precision and zero floating-point error (NFR-01, AC-09)."""

    PRECISION = Decimal("0.0001")

    @classmethod
    def calculate_summary(cls, holdings: List[Dict[str, Any]]) -> Dict[str, Decimal]:
        total_invested = Decimal("0.0000")
        current_value = Decimal("0.0000")

        for h in holdings:
            shares = Decimal(str(h["shares_held"]))
            avg_price = Decimal(str(h["average_buy_price"]))
            curr_price = Decimal(str(h["current_price"]))

            total_invested += (shares * avg_price)
            current_value += (shares * curr_price)

        total_invested = total_invested.quantize(cls.PRECISION, rounding=ROUND_HALF_UP)
        current_value = current_value.quantize(cls.PRECISION, rounding=ROUND_HALF_UP)
        absolute_pnl = (current_value - total_invested).quantize(cls.PRECISION, rounding=ROUND_HALF_UP)

        if total_invested > Decimal("0.0000"):
            percent_pnl = ((absolute_pnl / total_invested) * Decimal("100")).quantize(cls.PRECISION, rounding=ROUND_HALF_UP)
        else:
            percent_pnl = Decimal("0.0000")

        return {
            "total_invested": total_invested,
            "current_value": current_value,
            "absolute_pnl": absolute_pnl,
            "percent_pnl": percent_pnl
        }

    @classmethod
    def calculate_position_pnl(cls, shares_held: Decimal, avg_price: Decimal, current_price: Decimal) -> Dict[str, Decimal]:
        shares = Decimal(str(shares_held))
        cost = (shares * Decimal(str(avg_price))).quantize(cls.PRECISION, rounding=ROUND_HALF_UP)
        mkt_val = (shares * Decimal(str(current_price))).quantize(cls.PRECISION, rounding=ROUND_HALF_UP)
        abs_pnl = (mkt_val - cost).quantize(cls.PRECISION, rounding=ROUND_HALF_UP)
        if cost > Decimal("0.0000"):
            pct_pnl = ((abs_pnl / cost) * Decimal("100")).quantize(cls.PRECISION, rounding=ROUND_HALF_UP)
        else:
            pct_pnl = Decimal("0.0000")
        return {
            "total_invested": cost,
            "current_value": mkt_val,
            "absolute_pnl": abs_pnl,
            "percent_pnl": pct_pnl
        }

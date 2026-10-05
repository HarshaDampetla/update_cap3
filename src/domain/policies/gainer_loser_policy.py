from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Any


class GainerLoserPolicy:
    """Ranks top 5 gainers and losers from active holdings using fixed-point math (AC-10, NFR-01)."""

    PRECISION = Decimal("0.0001")

    @classmethod
    def rank_movers(cls, holdings_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        if not holdings_data:
            return {
                "top_gainers": [],
                "top_losers": []
            }

        calculated = []
        for item in holdings_data:
            curr = Decimal(str(item["current_price"]))
            open_p = Decimal(str(item["open_price"]))
            diff = curr - open_p
            if open_p > Decimal("0.0000"):
                pct = ((diff / open_p) * Decimal("100")).quantize(cls.PRECISION, rounding=ROUND_HALF_UP)
            else:
                pct = Decimal("0.0000")

            calculated.append({
                **item,
                "change_amount": diff.quantize(cls.PRECISION, rounding=ROUND_HALF_UP),
                "change_percent": pct
            })

        # Sort for gainers (highest positive first)
        gainers = sorted(calculated, key=lambda x: x["change_percent"], reverse=True)[:5]

        # Sort for losers (lowest / most negative first)
        losers = sorted(calculated, key=lambda x: x["change_percent"])[:5]

        return {
            "top_gainers": gainers,
            "top_losers": losers
        }

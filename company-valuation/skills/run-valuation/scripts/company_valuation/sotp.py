"""
Sum-of-the-Parts (SOTP) Analysis.

This module implements:
- Segment valuation with different methodologies
- Corporate overhead capitalization
- Conglomerate discount application

SOTP is used for conglomerates where different business units
have vastly different risk profiles and peer groups.
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum


class ValuationMethod(Enum):
    """Valuation methodology for segment."""
    EV_EBITDA = "ev_ebitda"
    EV_EBIT = "ev_ebit"
    EV_REVENUE = "ev_revenue"
    PE = "pe"
    PRICE_TO_BOOK = "price_to_book"
    DCF = "dcf"
    DDM = "ddm"


@dataclass
class Segment:
    """
    Business segment for SOTP analysis.

    Attributes:
        name: Segment name
        method: Valuation methodology
        metric_value: Value of the metric (EBITDA, Revenue, etc.)
        multiple: Multiple to apply
        segment_value: Pre-calculated value (if using DCF/DDM)
        description: Optional description
    """
    name: str
    method: ValuationMethod
    metric_value: float = 0.0
    multiple: float = 0.0
    segment_value: Optional[float] = None
    description: str = ""

    @property
    def calculated_value(self) -> float:
        """
        Calculate segment value.

        If segment_value is provided (e.g., from DCF), use it.
        Otherwise, calculate as metric × multiple.
        """
        if self.segment_value is not None:
            return self.segment_value
        return self.metric_value * self.multiple


@dataclass
class SOTPResult:
    """Result of SOTP analysis."""
    segment_values: dict[str, float]
    gross_enterprise_value: float
    corporate_overhead_value: float
    enterprise_value_pre_discount: float
    conglomerate_discount: float
    discount_amount: float
    net_enterprise_value: float
    equity_value: float
    equity_value_per_share: Optional[float]


@dataclass
class SOTPModel:
    """
    Sum-of-the-Parts Valuation Model.

    Calculates total enterprise value by summing individually
    valued business segments, then applying adjustments.

    Methodology:
    1. Value each segment using appropriate methodology/peers
    2. Sum segment values
    3. Subtract capitalized corporate overhead
    4. Apply conglomerate discount (typically 10-20%)

    Attributes:
        segments: List of business segments
        corporate_overhead: Annual corporate overhead costs
        overhead_multiple: Multiple to capitalize overhead
        conglomerate_discount: Discount for conglomerate structure (0.10 = 10%)
        net_debt: Net debt for equity bridge
        shares_outstanding: Diluted shares for per-share value
    """
    segments: list[Segment]
    corporate_overhead: float = 0.0
    overhead_multiple: float = 8.0  # Typical 8-10x for overhead
    conglomerate_discount: float = 0.15  # 15% typical discount
    net_debt: float = 0.0
    shares_outstanding: Optional[float] = None

    @property
    def corporate_overhead_value(self) -> float:
        """
        Capitalized value of corporate overhead.

        Corporate overhead reduces value as it's a cost not
        attributed to any segment.
        """
        return self.corporate_overhead * self.overhead_multiple

    def calculate(self) -> SOTPResult:
        """
        Perform SOTP valuation.

        Returns:
            SOTPResult with detailed breakdown
        """
        # Calculate each segment's value
        segment_values = {s.name: s.calculated_value for s in self.segments}

        # Gross EV is sum of segments
        gross_ev = sum(segment_values.values())

        # Subtract corporate overhead
        overhead_value = self.corporate_overhead_value
        ev_pre_discount = gross_ev - overhead_value

        # Apply conglomerate discount
        discount_amount = ev_pre_discount * self.conglomerate_discount
        net_ev = ev_pre_discount - discount_amount

        # Bridge to equity
        equity_value = net_ev - self.net_debt

        per_share = None
        if self.shares_outstanding and self.shares_outstanding > 0:
            per_share = equity_value / self.shares_outstanding

        return SOTPResult(
            segment_values=segment_values,
            gross_enterprise_value=gross_ev,
            corporate_overhead_value=overhead_value,
            enterprise_value_pre_discount=ev_pre_discount,
            conglomerate_discount=self.conglomerate_discount,
            discount_amount=discount_amount,
            net_enterprise_value=net_ev,
            equity_value=equity_value,
            equity_value_per_share=per_share
        )

    def sensitivity_to_discount(self, discounts: list[float]) -> dict[float, float]:
        """
        Calculate sensitivity of equity value to conglomerate discount.

        Args:
            discounts: List of discount rates to test

        Returns:
            Dictionary mapping discount rate to equity value
        """
        original_discount = self.conglomerate_discount
        results = {}

        for discount in discounts:
            self.conglomerate_discount = discount
            result = self.calculate()
            results[discount] = result.equity_value

        self.conglomerate_discount = original_discount
        return results

    def segment_contribution(self) -> dict[str, float]:
        """
        Calculate each segment's contribution to total value.

        Returns:
            Dictionary mapping segment name to percentage contribution
        """
        result = self.calculate()
        total = result.gross_enterprise_value

        if total == 0:
            return {s.name: 0.0 for s in self.segments}

        return {
            name: value / total
            for name, value in result.segment_values.items()
        }

    @classmethod
    def from_dict(cls, segment_data: list[dict],
                  corporate_overhead: float = 0.0,
                  overhead_multiple: float = 8.0,
                  conglomerate_discount: float = 0.15,
                  net_debt: float = 0.0,
                  shares_outstanding: Optional[float] = None) -> "SOTPModel":
        """
        Create SOTP model from dictionary data.

        Convenience method for creating model from structured data.

        Args:
            segment_data: List of dicts with keys:
                - name: Segment name
                - method: Valuation method string
                - metric_value: Metric value (optional)
                - multiple: Multiple to apply (optional)
                - segment_value: Pre-calculated value (optional)
            corporate_overhead: Annual corporate overhead
            overhead_multiple: Multiple for overhead capitalization
            conglomerate_discount: Discount rate
            net_debt: Net debt
            shares_outstanding: Diluted shares

        Returns:
            SOTPModel instance
        """
        segments = []
        for data in segment_data:
            method = ValuationMethod(data.get("method", "ev_ebitda"))
            segments.append(Segment(
                name=data["name"],
                method=method,
                metric_value=data.get("metric_value", 0.0),
                multiple=data.get("multiple", 0.0),
                segment_value=data.get("segment_value"),
                description=data.get("description", "")
            ))

        return cls(
            segments=segments,
            corporate_overhead=corporate_overhead,
            overhead_multiple=overhead_multiple,
            conglomerate_discount=conglomerate_discount,
            net_debt=net_debt,
            shares_outstanding=shares_outstanding
        )

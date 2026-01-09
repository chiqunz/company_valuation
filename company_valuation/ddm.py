"""
Dividend Discount Model (DDM).

This module implements:
- Two-stage DDM for financial institutions
- Gordon Growth Model
- Dividend forecasting from EPS and payout ratio

DDM is the standard valuation approach for banks and insurance companies
where traditional DCF metrics (FCF, working capital) are not meaningful.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class DividendProjection:
    """
    Single period dividend projection.

    Attributes:
        year: Projection year
        eps: Earnings per share
        payout_ratio: Dividend payout ratio (DPS/EPS)
        dps: Dividend per share (calculated or explicit)
    """
    year: int
    eps: float
    payout_ratio: float = 0.0
    dps: Optional[float] = None

    def __post_init__(self):
        """Calculate DPS if not provided."""
        if self.dps is None:
            self.dps = self.eps * self.payout_ratio


@dataclass
class DDMResult:
    """Result of DDM valuation."""
    pv_explicit_dividends: float
    terminal_value_undiscounted: float
    pv_terminal_value: float
    equity_value_per_share: float
    terminal_method: str
    implied_growth_rate: Optional[float] = None


@dataclass
class DDMModel:
    """
    Two-Stage Dividend Discount Model.

    Stage 1: Explicit dividend forecast (derived from EPS × Payout Ratio)
    Stage 2: Terminal value via Gordon Growth or P/E multiple

    Formula:
    V0 = Σ DPS_t / (1 + ke)^t + P_n / (1 + ke)^n

    Where P_n is terminal stock price from Gordon Growth or P/E.

    Attributes:
        projections: List of DividendProjection objects
        cost_of_equity: Required return on equity (ke)
        terminal_growth: Perpetual dividend growth rate
        terminal_pe: Terminal P/E multiple (alternative to growth)
    """
    projections: list[DividendProjection]
    cost_of_equity: float
    terminal_growth: float = 0.03
    terminal_pe: Optional[float] = None

    def _discount_factor(self, period: int) -> float:
        """Calculate discount factor for a given period."""
        return 1 / ((1 + self.cost_of_equity) ** period)

    def calculate_pv_dividends(self) -> tuple[float, list[float]]:
        """
        Calculate present value of explicit dividend forecasts.

        Returns:
            Tuple of (total PV, list of discounted dividends)
        """
        discounted_divs = []
        for proj in self.projections:
            df = self._discount_factor(proj.year)
            discounted = proj.dps * df
            discounted_divs.append(discounted)

        return sum(discounted_divs), discounted_divs

    def terminal_value_gordon_growth(self) -> float:
        """
        Calculate terminal stock price using Gordon Growth Model.

        P_n = DPS_n+1 / (ke - g) = DPS_n × (1 + g) / (ke - g)

        Returns:
            Terminal stock price (undiscounted)
        """
        if self.cost_of_equity <= self.terminal_growth:
            raise ValueError(
                f"Terminal growth ({self.terminal_growth:.2%}) must be less than "
                f"cost of equity ({self.cost_of_equity:.2%})"
            )

        final_dps = self.projections[-1].dps
        terminal_dps = final_dps * (1 + self.terminal_growth)
        return terminal_dps / (self.cost_of_equity - self.terminal_growth)

    def terminal_value_pe_multiple(self) -> float:
        """
        Calculate terminal stock price using P/E multiple.

        P_n = EPS_n × P/E Multiple

        Returns:
            Terminal stock price (undiscounted)
        """
        if self.terminal_pe is None:
            raise ValueError("Terminal P/E not specified")

        final_eps = self.projections[-1].eps
        return final_eps * self.terminal_pe

    def _discount_terminal_value(self, terminal_price: float) -> float:
        """Discount terminal stock price to present."""
        n = len(self.projections)
        return terminal_price * self._discount_factor(n)

    def value_gordon_growth(self) -> DDMResult:
        """
        Calculate equity value using Gordon Growth terminal value.

        Returns:
            DDMResult with valuation details
        """
        pv_divs, _ = self.calculate_pv_dividends()
        terminal_price = self.terminal_value_gordon_growth()
        pv_terminal = self._discount_terminal_value(terminal_price)

        equity_value = pv_divs + pv_terminal

        return DDMResult(
            pv_explicit_dividends=pv_divs,
            terminal_value_undiscounted=terminal_price,
            pv_terminal_value=pv_terminal,
            equity_value_per_share=equity_value,
            terminal_method="gordon_growth"
        )

    def value_pe_multiple(self) -> DDMResult:
        """
        Calculate equity value using P/E terminal value.

        Returns:
            DDMResult with valuation details
        """
        if self.terminal_pe is None:
            raise ValueError("Terminal P/E not specified")

        pv_divs, _ = self.calculate_pv_dividends()
        terminal_price = self.terminal_value_pe_multiple()
        pv_terminal = self._discount_terminal_value(terminal_price)

        equity_value = pv_divs + pv_terminal

        # Calculate implied growth rate
        implied_g = self._implied_growth_from_pe(terminal_price)

        return DDMResult(
            pv_explicit_dividends=pv_divs,
            terminal_value_undiscounted=terminal_price,
            pv_terminal_value=pv_terminal,
            equity_value_per_share=equity_value,
            terminal_method="pe_multiple",
            implied_growth_rate=implied_g
        )

    def _implied_growth_from_pe(self, terminal_price: float) -> float:
        """
        Calculate implied growth rate from P/E terminal value.

        Given P = DPS × (1+g) / (ke - g), solve for g.
        """
        final_dps = self.projections[-1].dps
        if final_dps == 0 or terminal_price == 0:
            return 0

        # From Gordon Growth: P = DPS(1+g)/(ke-g)
        # P(ke-g) = DPS(1+g)
        # Pke - Pg = DPS + DPSg
        # Pke - DPS = Pg + DPSg
        # Pke - DPS = g(P + DPS)
        # g = (Pke - DPS) / (P + DPS)
        numerator = terminal_price * self.cost_of_equity - final_dps
        denominator = terminal_price + final_dps
        return numerator / denominator if denominator != 0 else 0

    def value(self, method: str = "gordon_growth") -> DDMResult:
        """
        Calculate DDM value using specified method.

        Args:
            method: "gordon_growth" or "pe_multiple"

        Returns:
            DDMResult with valuation details
        """
        if method == "gordon_growth":
            return self.value_gordon_growth()
        elif method == "pe_multiple":
            return self.value_pe_multiple()
        else:
            raise ValueError(f"Unknown method: {method}")

    @classmethod
    def from_eps_forecast(cls, eps_forecasts: list[float],
                          payout_ratio: float,
                          cost_of_equity: float,
                          terminal_growth: float = 0.03,
                          terminal_pe: Optional[float] = None) -> "DDMModel":
        """
        Create DDM model from EPS forecasts and payout ratio.

        Convenience method for common use case where dividends
        are derived from earnings.

        Args:
            eps_forecasts: List of EPS by year
            payout_ratio: Constant dividend payout ratio
            cost_of_equity: Required return on equity
            terminal_growth: Perpetual dividend growth rate
            terminal_pe: Optional terminal P/E multiple

        Returns:
            DDMModel instance
        """
        projections = [
            DividendProjection(year=i+1, eps=eps, payout_ratio=payout_ratio)
            for i, eps in enumerate(eps_forecasts)
        ]

        return cls(
            projections=projections,
            cost_of_equity=cost_of_equity,
            terminal_growth=terminal_growth,
            terminal_pe=terminal_pe
        )

    @classmethod
    def from_dividend_forecast(cls, dps_forecasts: list[float],
                               cost_of_equity: float,
                               terminal_growth: float = 0.03) -> "DDMModel":
        """
        Create DDM model from explicit dividend forecasts.

        Args:
            dps_forecasts: List of DPS by year
            cost_of_equity: Required return on equity
            terminal_growth: Perpetual dividend growth rate

        Returns:
            DDMModel instance
        """
        projections = [
            DividendProjection(year=i+1, eps=0, payout_ratio=0, dps=dps)
            for i, dps in enumerate(dps_forecasts)
        ]

        return cls(
            projections=projections,
            cost_of_equity=cost_of_equity,
            terminal_growth=terminal_growth
        )

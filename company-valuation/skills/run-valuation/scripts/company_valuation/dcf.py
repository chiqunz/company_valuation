"""
Discounted Cash Flow (DCF) Model.

This module implements:
- UFCF (Unlevered Free Cash Flow) calculation
- Discount factor calculation with mid-year convention
- Stub period handling
- Terminal Value via Perpetuity Growth and Exit Multiple methods
- Enterprise Value to Equity Value bridge
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class UFCFProjection:
    """
    Single period UFCF (Unlevered Free Cash Flow) projection.

    UFCF = EBIT × (1 - Tax Rate) + D&A - CapEx - ΔNWC

    Note on SBC: Can be treated as cash expense (not added back) or non-cash
    (added back). Use add_back_sbc=False for buy-side/economic view.

    Attributes:
        year: Projection year (1, 2, 3, etc.)
        revenue: Projected revenue
        ebit: Operating income (EBIT)
        tax_rate: Marginal tax rate
        depreciation_amortization: D&A (non-cash expense)
        capex: Capital expenditures (cash outflow, positive number)
        delta_nwc: Change in net working capital (increase = outflow, positive)
        sbc: Stock-based compensation (if tracking separately)
        add_back_sbc: Whether to add back SBC (sell-side convention)
        ebitda: EBITDA for exit multiple terminal value (optional)
    """
    year: int
    revenue: float
    ebit: float
    tax_rate: float
    depreciation_amortization: float
    capex: float
    delta_nwc: float
    sbc: float = 0.0
    add_back_sbc: bool = False
    ebitda: Optional[float] = None

    @property
    def nopat(self) -> float:
        """Net Operating Profit After Tax."""
        return self.ebit * (1 - self.tax_rate)

    @property
    def ufcf(self) -> float:
        """Calculate Unlevered Free Cash Flow."""
        fcf = (self.nopat
               + self.depreciation_amortization
               - self.capex
               - self.delta_nwc)
        if self.add_back_sbc:
            fcf += self.sbc
        return fcf

    def __post_init__(self):
        """Set EBITDA if not provided."""
        if self.ebitda is None:
            self.ebitda = self.ebit + self.depreciation_amortization


@dataclass
class DCFResult:
    """Result of DCF valuation."""
    pv_explicit_cashflows: float
    terminal_value_undiscounted: float
    pv_terminal_value: float
    enterprise_value: float
    equity_value: float
    equity_value_per_share: Optional[float]
    terminal_method: str
    implied_perpetual_growth: Optional[float] = None


@dataclass
class DCFModel:
    """
    Institutional DCF Model.

    Supports:
    - Mid-year convention
    - Stub periods
    - Perpetuity growth terminal value
    - Exit multiple terminal value
    - Enterprise to equity bridge

    Attributes:
        projections: List of UFCFProjection objects
        wacc: Weighted Average Cost of Capital
        terminal_growth: Perpetual growth rate (g) for Gordon Growth
        exit_multiple: Exit EBITDA multiple (optional)
        net_debt: Net debt for equity bridge
        shares_outstanding: Diluted shares for per-share value
        mid_year_convention: Whether to use mid-year discounting
        stub_fraction: Fraction of first year if starting mid-period
    """
    projections: list[UFCFProjection]
    wacc: float
    terminal_growth: float = 0.025
    exit_multiple: Optional[float] = None
    net_debt: float = 0.0
    shares_outstanding: Optional[float] = None
    mid_year_convention: bool = True
    stub_fraction: float = 1.0  # 1.0 = full year, 0.5 = half year stub

    def _get_discount_periods(self) -> list[float]:
        """
        Calculate discount periods accounting for mid-year and stub.

        Returns:
            List of discount periods for each projection year
        """
        periods = []
        for i in range(len(self.projections)):
            if i == 0:
                base_period = self.stub_fraction
                mid_year_adjustment = self.stub_fraction / 2
            else:
                base_period = self.stub_fraction + i
                mid_year_adjustment = 0.5

            if self.mid_year_convention:
                period = base_period - mid_year_adjustment
            else:
                period = base_period

            periods.append(period)
        return periods

    def _discount_factor(self, period: float) -> float:
        """Calculate discount factor for a given period."""
        return 1 / ((1 + self.wacc) ** period)

    def calculate_pv_explicit(self) -> tuple[float, list[float]]:
        """
        Calculate present value of explicit forecast period.

        Returns:
            Tuple of (total PV, list of discounted cash flows)
        """
        periods = self._get_discount_periods()
        discounted_cfs = []

        for proj, period in zip(self.projections, periods):
            df = self._discount_factor(period)
            discounted_cf = proj.ufcf * df
            discounted_cfs.append(discounted_cf)

        return sum(discounted_cfs), discounted_cfs

    def calculate_terminal_value_perpetuity(self) -> float:
        """
        Calculate terminal value using Gordon Growth Model.

        TV = UFCF_n × (1 + g) / (WACC - g)

        Returns:
            Terminal value (undiscounted)
        """
        if self.wacc <= self.terminal_growth:
            raise ValueError(
                f"Terminal growth ({self.terminal_growth:.2%}) must be less than "
                f"WACC ({self.wacc:.2%})"
            )

        final_ufcf = self.projections[-1].ufcf
        tv = final_ufcf * (1 + self.terminal_growth) / (self.wacc - self.terminal_growth)
        return tv

    def calculate_terminal_value_exit_multiple(self) -> float:
        """
        Calculate terminal value using exit EBITDA multiple.

        TV = EBITDA_n × Multiple

        Returns:
            Terminal value (undiscounted)
        """
        if self.exit_multiple is None:
            raise ValueError("Exit multiple not specified")

        final_ebitda = self.projections[-1].ebitda
        return final_ebitda * self.exit_multiple

    def calculate_implied_growth_from_multiple(self, tv: float) -> float:
        """
        Calculate implied perpetual growth rate from exit multiple.

        Used as sanity check - if implied g > GDP growth, multiple may be aggressive.

        Simplified formula: g = (TV × WACC - UFCF_n+1) / (TV + UFCF_n+1)

        Args:
            tv: Terminal value from exit multiple

        Returns:
            Implied perpetual growth rate
        """
        final_ufcf = self.projections[-1].ufcf
        ufcf_next = final_ufcf * (1 + self.terminal_growth)  # Proxy using terminal_growth

        # Derived from Gordon Growth: TV = UFCF × (1+g) / (WACC - g)
        # Solving for g: g = (TV × WACC - UFCF) / (TV + UFCF)
        numerator = tv * self.wacc - final_ufcf
        denominator = tv + final_ufcf
        return numerator / denominator if denominator != 0 else 0

    def _discount_terminal_value(self, tv: float) -> float:
        """
        Discount terminal value to present.

        TV is always discounted from end of period n (not mid-year).
        """
        n = len(self.projections)
        # For stub periods, adjust the terminal discount period
        terminal_period = self.stub_fraction + (n - 1) if self.stub_fraction < 1 else n
        return tv * self._discount_factor(terminal_period)

    def value_perpetuity_method(self) -> DCFResult:
        """
        Calculate DCF value using perpetuity growth method.

        Returns:
            DCFResult with valuation details
        """
        pv_explicit, _ = self.calculate_pv_explicit()
        tv = self.calculate_terminal_value_perpetuity()
        pv_tv = self._discount_terminal_value(tv)

        ev = pv_explicit + pv_tv
        equity_value = ev - self.net_debt

        per_share = None
        if self.shares_outstanding and self.shares_outstanding > 0:
            per_share = equity_value / self.shares_outstanding

        return DCFResult(
            pv_explicit_cashflows=pv_explicit,
            terminal_value_undiscounted=tv,
            pv_terminal_value=pv_tv,
            enterprise_value=ev,
            equity_value=equity_value,
            equity_value_per_share=per_share,
            terminal_method="perpetuity_growth"
        )

    def value_exit_multiple_method(self) -> DCFResult:
        """
        Calculate DCF value using exit multiple method.

        Returns:
            DCFResult with valuation details
        """
        if self.exit_multiple is None:
            raise ValueError("Exit multiple not specified")

        pv_explicit, _ = self.calculate_pv_explicit()
        tv = self.calculate_terminal_value_exit_multiple()
        pv_tv = self._discount_terminal_value(tv)
        implied_g = self.calculate_implied_growth_from_multiple(tv)

        ev = pv_explicit + pv_tv
        equity_value = ev - self.net_debt

        per_share = None
        if self.shares_outstanding and self.shares_outstanding > 0:
            per_share = equity_value / self.shares_outstanding

        return DCFResult(
            pv_explicit_cashflows=pv_explicit,
            terminal_value_undiscounted=tv,
            pv_terminal_value=pv_tv,
            enterprise_value=ev,
            equity_value=equity_value,
            equity_value_per_share=per_share,
            terminal_method="exit_multiple",
            implied_perpetual_growth=implied_g
        )

    def value(self, method: str = "perpetuity") -> DCFResult:
        """
        Calculate DCF value using specified method.

        Args:
            method: "perpetuity" or "exit_multiple"

        Returns:
            DCFResult with valuation details
        """
        if method == "perpetuity":
            return self.value_perpetuity_method()
        elif method == "exit_multiple":
            return self.value_exit_multiple_method()
        else:
            raise ValueError(f"Unknown method: {method}")

    def terminal_value_percentage(self, method: str = "perpetuity") -> float:
        """
        Calculate what percentage of EV comes from terminal value.

        Per report: TV often accounts for 60-80% of total EV.

        Args:
            method: "perpetuity" or "exit_multiple"

        Returns:
            Percentage of EV from terminal value
        """
        result = self.value(method)
        if result.enterprise_value == 0:
            return 0
        return result.pv_terminal_value / result.enterprise_value

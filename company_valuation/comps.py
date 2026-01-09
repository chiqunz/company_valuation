"""
Comparable Company Analysis (Trading Comps).

This module implements:
- LTM (Last Twelve Months) metric calculation
- Enterprise Value calculation
- Multiple calculations: EV/EBITDA, EV/EBIT, P/E, EV/Revenue, P/BV
- Peer group statistics
"""

from dataclasses import dataclass, field
from typing import Optional
import numpy as np


@dataclass
class PeerCompany:
    """
    Comparable peer company data.

    Attributes:
        ticker: Stock ticker symbol
        name: Company name
        price: Current stock price
        shares_outstanding: Diluted shares outstanding (millions)
        net_debt: Net debt (cash negative, debt positive)

        For LTM calculations:
        fy_revenue: Last fiscal year revenue
        ytd_revenue: Current year-to-date revenue
        prior_ytd_revenue: Prior year YTD revenue

        fy_ebitda: Last fiscal year EBITDA
        ytd_ebitda: Current YTD EBITDA
        prior_ytd_ebitda: Prior year YTD EBITDA

        fy_ebit: Last fiscal year EBIT
        ytd_ebit: Current YTD EBIT
        prior_ytd_ebit: Prior YTD EBIT

        fy_net_income: Last fiscal year net income
        ytd_net_income: Current YTD net income
        prior_ytd_net_income: Prior YTD net income

        book_value: Book value of equity (for P/BV)

        Alternatively, pre-calculated LTM metrics:
        ltm_revenue: LTM Revenue (if pre-calculated)
        ltm_ebitda: LTM EBITDA (if pre-calculated)
        ltm_ebit: LTM EBIT (if pre-calculated)
        ltm_net_income: LTM Net Income (if pre-calculated)

        Forward estimates:
        ntm_revenue: Next twelve months revenue estimate
        ntm_ebitda: NTM EBITDA estimate
        ntm_eps: NTM EPS estimate
    """
    ticker: str
    name: str
    price: float
    shares_outstanding: float
    net_debt: float

    # Fiscal year data for LTM calculation
    fy_revenue: Optional[float] = None
    ytd_revenue: Optional[float] = None
    prior_ytd_revenue: Optional[float] = None

    fy_ebitda: Optional[float] = None
    ytd_ebitda: Optional[float] = None
    prior_ytd_ebitda: Optional[float] = None

    fy_ebit: Optional[float] = None
    ytd_ebit: Optional[float] = None
    prior_ytd_ebit: Optional[float] = None

    fy_net_income: Optional[float] = None
    ytd_net_income: Optional[float] = None
    prior_ytd_net_income: Optional[float] = None

    book_value: Optional[float] = None

    # Pre-calculated LTM (if available)
    ltm_revenue: Optional[float] = None
    ltm_ebitda: Optional[float] = None
    ltm_ebit: Optional[float] = None
    ltm_net_income: Optional[float] = None

    # Forward estimates
    ntm_revenue: Optional[float] = None
    ntm_ebitda: Optional[float] = None
    ntm_eps: Optional[float] = None

    def _calc_ltm(self, fy: Optional[float], ytd: Optional[float],
                  prior_ytd: Optional[float]) -> Optional[float]:
        """Calculate LTM metric: FY + Current YTD - Prior YTD"""
        if all(v is not None for v in [fy, ytd, prior_ytd]):
            return fy + ytd - prior_ytd
        return None

    @property
    def market_cap(self) -> float:
        """Market capitalization."""
        return self.price * self.shares_outstanding

    @property
    def enterprise_value(self) -> float:
        """Enterprise value = Market Cap + Net Debt."""
        return self.market_cap + self.net_debt

    def get_ltm_revenue(self) -> Optional[float]:
        """Get LTM Revenue (pre-calculated or calculated)."""
        if self.ltm_revenue is not None:
            return self.ltm_revenue
        return self._calc_ltm(self.fy_revenue, self.ytd_revenue, self.prior_ytd_revenue)

    def get_ltm_ebitda(self) -> Optional[float]:
        """Get LTM EBITDA."""
        if self.ltm_ebitda is not None:
            return self.ltm_ebitda
        return self._calc_ltm(self.fy_ebitda, self.ytd_ebitda, self.prior_ytd_ebitda)

    def get_ltm_ebit(self) -> Optional[float]:
        """Get LTM EBIT."""
        if self.ltm_ebit is not None:
            return self.ltm_ebit
        return self._calc_ltm(self.fy_ebit, self.ytd_ebit, self.prior_ytd_ebit)

    def get_ltm_net_income(self) -> Optional[float]:
        """Get LTM Net Income."""
        if self.ltm_net_income is not None:
            return self.ltm_net_income
        return self._calc_ltm(self.fy_net_income, self.ytd_net_income,
                              self.prior_ytd_net_income)

    @property
    def ltm_eps(self) -> Optional[float]:
        """LTM Earnings per Share."""
        ni = self.get_ltm_net_income()
        if ni is not None and self.shares_outstanding > 0:
            return ni / self.shares_outstanding
        return None

    def ev_ebitda(self, use_ntm: bool = False) -> Optional[float]:
        """EV/EBITDA multiple."""
        if use_ntm and self.ntm_ebitda:
            ebitda = self.ntm_ebitda
        else:
            ebitda = self.get_ltm_ebitda()
        if ebitda and ebitda > 0:
            return self.enterprise_value / ebitda
        return None

    def ev_ebit(self) -> Optional[float]:
        """EV/EBIT multiple."""
        ebit = self.get_ltm_ebit()
        if ebit and ebit > 0:
            return self.enterprise_value / ebit
        return None

    def ev_revenue(self, use_ntm: bool = False) -> Optional[float]:
        """EV/Revenue multiple."""
        if use_ntm and self.ntm_revenue:
            revenue = self.ntm_revenue
        else:
            revenue = self.get_ltm_revenue()
        if revenue and revenue > 0:
            return self.enterprise_value / revenue
        return None

    def pe_ratio(self, use_ntm: bool = False) -> Optional[float]:
        """P/E ratio."""
        if use_ntm and self.ntm_eps:
            eps = self.ntm_eps
        else:
            eps = self.ltm_eps
        if eps and eps > 0:
            return self.price / eps
        return None

    def price_to_book(self) -> Optional[float]:
        """Price to Book Value."""
        if self.book_value and self.book_value > 0:
            return self.market_cap / self.book_value
        return None


@dataclass
class ComparableAnalysis:
    """
    Comparable Company Analysis for a peer group.

    Calculates and summarizes valuation multiples across peer companies.
    """
    peers: list[PeerCompany]

    def _filter_valid(self, values: list[Optional[float]]) -> list[float]:
        """Filter out None values and return valid floats."""
        return [v for v in values if v is not None]

    def _statistics(self, values: list[float]) -> dict:
        """Calculate statistics for a list of values."""
        if not values:
            return {
                "mean": None,
                "median": None,
                "min": None,
                "max": None,
                "p25": None,
                "p75": None
            }

        arr = np.array(values)
        return {
            "mean": float(np.mean(arr)),
            "median": float(np.median(arr)),
            "min": float(np.min(arr)),
            "max": float(np.max(arr)),
            "p25": float(np.percentile(arr, 25)),
            "p75": float(np.percentile(arr, 75))
        }

    def ev_ebitda_multiples(self, use_ntm: bool = False) -> dict:
        """
        Get EV/EBITDA multiples for all peers with statistics.

        Args:
            use_ntm: Use NTM EBITDA instead of LTM

        Returns:
            Dictionary with peer multiples and statistics
        """
        multiples = {p.ticker: p.ev_ebitda(use_ntm) for p in self.peers}
        valid = self._filter_valid(list(multiples.values()))
        stats = self._statistics(valid)
        return {"multiples": multiples, "statistics": stats}

    def ev_ebit_multiples(self) -> dict:
        """Get EV/EBIT multiples for all peers with statistics."""
        multiples = {p.ticker: p.ev_ebit() for p in self.peers}
        valid = self._filter_valid(list(multiples.values()))
        stats = self._statistics(valid)
        return {"multiples": multiples, "statistics": stats}

    def ev_revenue_multiples(self, use_ntm: bool = False) -> dict:
        """Get EV/Revenue multiples for all peers with statistics."""
        multiples = {p.ticker: p.ev_revenue(use_ntm) for p in self.peers}
        valid = self._filter_valid(list(multiples.values()))
        stats = self._statistics(valid)
        return {"multiples": multiples, "statistics": stats}

    def pe_ratios(self, use_ntm: bool = False) -> dict:
        """Get P/E ratios for all peers with statistics."""
        multiples = {p.ticker: p.pe_ratio(use_ntm) for p in self.peers}
        valid = self._filter_valid(list(multiples.values()))
        stats = self._statistics(valid)
        return {"multiples": multiples, "statistics": stats}

    def price_to_book_ratios(self) -> dict:
        """Get P/BV ratios for all peers with statistics."""
        multiples = {p.ticker: p.price_to_book() for p in self.peers}
        valid = self._filter_valid(list(multiples.values()))
        stats = self._statistics(valid)
        return {"multiples": multiples, "statistics": stats}

    def implied_value(self, target_metric: float, multiple_type: str = "ev_ebitda",
                      use_median: bool = True, use_ntm: bool = False) -> dict:
        """
        Calculate implied enterprise/equity value based on peer multiples.

        Args:
            target_metric: Target company's metric (e.g., EBITDA)
            multiple_type: "ev_ebitda", "ev_ebit", "ev_revenue", "pe"
            use_median: Use median multiple (vs mean)
            use_ntm: Use NTM multiples

        Returns:
            Dictionary with implied value and range (25th-75th percentile)
        """
        if multiple_type == "ev_ebitda":
            data = self.ev_ebitda_multiples(use_ntm)
        elif multiple_type == "ev_ebit":
            data = self.ev_ebit_multiples()
        elif multiple_type == "ev_revenue":
            data = self.ev_revenue_multiples(use_ntm)
        elif multiple_type == "pe":
            data = self.pe_ratios(use_ntm)
        else:
            raise ValueError(f"Unknown multiple type: {multiple_type}")

        stats = data["statistics"]
        ref_multiple = stats["median"] if use_median else stats["mean"]

        if ref_multiple is None:
            return {"implied_value": None, "low": None, "high": None}

        implied = target_metric * ref_multiple
        low = target_metric * stats["p25"] if stats["p25"] else None
        high = target_metric * stats["p75"] if stats["p75"] else None

        return {
            "implied_value": implied,
            "low": low,
            "high": high,
            "multiple_used": ref_multiple,
            "p25_multiple": stats["p25"],
            "p75_multiple": stats["p75"]
        }

    def summary(self, use_ntm: bool = False) -> dict:
        """
        Generate summary of all multiples across peer group.

        Args:
            use_ntm: Use NTM multiples where available

        Returns:
            Dictionary with all multiple statistics
        """
        return {
            "ev_ebitda": self.ev_ebitda_multiples(use_ntm),
            "ev_ebit": self.ev_ebit_multiples(),
            "ev_revenue": self.ev_revenue_multiples(use_ntm),
            "pe": self.pe_ratios(use_ntm),
            "price_to_book": self.price_to_book_ratios()
        }

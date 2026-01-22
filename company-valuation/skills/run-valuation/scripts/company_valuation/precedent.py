"""
Precedent Transaction Analysis.

This module implements:
- Transaction multiple calculation
- Control premium analysis
- Time-decay filtering for relevance
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional

from company_valuation.utils import filter_valid_values, calculate_statistics


@dataclass
class Transaction:
    """
    M&A transaction data for precedent analysis.

    Attributes:
        target_name: Name of acquired company
        acquirer_name: Name of acquirer
        announce_date: Transaction announcement date
        close_date: Transaction close date (optional)
        deal_value: Total transaction value (equity + assumed debt)
        equity_value: Equity portion of deal value
        target_ltm_revenue: Target's LTM revenue at announcement
        target_ltm_ebitda: Target's LTM EBITDA at announcement
        target_ltm_ebit: Target's LTM EBIT at announcement
        target_ltm_net_income: Target's LTM net income
        pre_announcement_price: Target's stock price before announcement
        deal_price_per_share: Price paid per share
        is_strategic: True if strategic buyer, False if financial (PE)
        deal_type: "strategic", "financial", "mixed"
        sector: Industry sector
        geography: Region/country
    """
    target_name: str
    acquirer_name: str
    announce_date: date
    deal_value: float  # Enterprise Value paid
    equity_value: float

    target_ltm_revenue: Optional[float] = None
    target_ltm_ebitda: Optional[float] = None
    target_ltm_ebit: Optional[float] = None
    target_ltm_net_income: Optional[float] = None

    pre_announcement_price: Optional[float] = None
    deal_price_per_share: Optional[float] = None

    close_date: Optional[date] = None
    is_strategic: bool = True
    deal_type: str = "strategic"
    sector: Optional[str] = None
    geography: Optional[str] = None

    @property
    def control_premium(self) -> Optional[float]:
        """
        Calculate control premium paid over pre-announcement price.

        Control Premium = (Deal Price - Pre-Announcement Price) / Pre-Announcement Price

        Typical range: 20-40%
        """
        if self.pre_announcement_price and self.deal_price_per_share:
            if self.pre_announcement_price > 0:
                return ((self.deal_price_per_share - self.pre_announcement_price)
                        / self.pre_announcement_price)
        return None

    @property
    def ev_revenue(self) -> Optional[float]:
        """EV/Revenue transaction multiple."""
        if self.target_ltm_revenue and self.target_ltm_revenue > 0:
            return self.deal_value / self.target_ltm_revenue
        return None

    @property
    def ev_ebitda(self) -> Optional[float]:
        """EV/EBITDA transaction multiple."""
        if self.target_ltm_ebitda and self.target_ltm_ebitda > 0:
            return self.deal_value / self.target_ltm_ebitda
        return None

    @property
    def ev_ebit(self) -> Optional[float]:
        """EV/EBIT transaction multiple."""
        if self.target_ltm_ebit and self.target_ltm_ebit > 0:
            return self.deal_value / self.target_ltm_ebit
        return None

    @property
    def pe_ratio(self) -> Optional[float]:
        """P/E based on equity value and net income."""
        if self.target_ltm_net_income and self.target_ltm_net_income > 0:
            return self.equity_value / self.target_ltm_net_income
        return None

    def years_since(self, reference_date: Optional[date] = None) -> float:
        """Calculate years since transaction announcement."""
        ref = reference_date or date.today()
        delta = ref - self.announce_date
        return delta.days / 365.25


@dataclass
class PrecedentAnalysis:
    """
    Precedent Transaction Analysis for valuation.

    Analyzes historical M&A transactions to derive valuation multiples.
    Includes time-decay filtering to ensure relevance.
    """
    transactions: list[Transaction]

    def filter_by_recency(self, max_years: float = 3.0,
                          reference_date: Optional[date] = None) -> "PrecedentAnalysis":
        """
        Filter transactions to only include recent deals.

        Per report: Transactions from different rate environments (e.g., 2021 ZIRP)
        may be irrelevant in 2025 higher-rate environment.

        Args:
            max_years: Maximum years since announcement
            reference_date: Date to calculate from (default: today)

        Returns:
            New PrecedentAnalysis with filtered transactions
        """
        filtered = [
            t for t in self.transactions
            if t.years_since(reference_date) <= max_years
        ]
        return PrecedentAnalysis(filtered)

    def filter_by_deal_type(self, deal_type: str) -> "PrecedentAnalysis":
        """
        Filter by deal type (strategic, financial, or mixed).

        Args:
            deal_type: "strategic", "financial", or "mixed"

        Returns:
            New PrecedentAnalysis with filtered transactions
        """
        filtered = [t for t in self.transactions if t.deal_type == deal_type]
        return PrecedentAnalysis(filtered)

    def filter_by_sector(self, sector: str) -> "PrecedentAnalysis":
        """Filter transactions by sector."""
        filtered = [t for t in self.transactions if t.sector == sector]
        return PrecedentAnalysis(filtered)

    def filter_by_size(self, min_value: Optional[float] = None,
                       max_value: Optional[float] = None) -> "PrecedentAnalysis":
        """
        Filter transactions by deal value range.

        Args:
            min_value: Minimum deal value
            max_value: Maximum deal value

        Returns:
            New PrecedentAnalysis with filtered transactions
        """
        filtered = []
        for t in self.transactions:
            if min_value is not None and t.deal_value < min_value:
                continue
            if max_value is not None and t.deal_value > max_value:
                continue
            filtered.append(t)
        return PrecedentAnalysis(filtered)

    def control_premium_statistics(self) -> dict:
        """
        Calculate control premium statistics.

        Returns:
            Statistics on control premiums paid
        """
        premiums = filter_valid_values([t.control_premium for t in self.transactions])
        return calculate_statistics(premiums)

    def ev_ebitda_multiples(self) -> dict:
        """Get EV/EBITDA transaction multiples with statistics."""
        multiples = {t.target_name: t.ev_ebitda for t in self.transactions}
        valid = filter_valid_values(list(multiples.values()))
        return {"multiples": multiples, "statistics": calculate_statistics(valid)}

    def ev_ebit_multiples(self) -> dict:
        """Get EV/EBIT transaction multiples with statistics."""
        multiples = {t.target_name: t.ev_ebit for t in self.transactions}
        valid = filter_valid_values(list(multiples.values()))
        return {"multiples": multiples, "statistics": calculate_statistics(valid)}

    def ev_revenue_multiples(self) -> dict:
        """Get EV/Revenue transaction multiples with statistics."""
        multiples = {t.target_name: t.ev_revenue for t in self.transactions}
        valid = filter_valid_values(list(multiples.values()))
        return {"multiples": multiples, "statistics": calculate_statistics(valid)}

    def implied_value(self, target_metric: float, multiple_type: str = "ev_ebitda",
                      use_median: bool = True) -> dict:
        """
        Calculate implied value based on precedent multiples.

        Note: Precedent multiples typically higher than trading multiples
        due to control premium.

        Args:
            target_metric: Target company's metric (e.g., EBITDA)
            multiple_type: "ev_ebitda", "ev_ebit", "ev_revenue"
            use_median: Use median multiple (vs mean)

        Returns:
            Dictionary with implied value and range
        """
        if multiple_type == "ev_ebitda":
            data = self.ev_ebitda_multiples()
        elif multiple_type == "ev_ebit":
            data = self.ev_ebit_multiples()
        elif multiple_type == "ev_revenue":
            data = self.ev_revenue_multiples()
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
            "transaction_count": stats["count"]
        }

    def summary(self) -> dict:
        """
        Generate summary of precedent transaction analysis.

        Returns:
            Dictionary with all multiple statistics and control premiums
        """
        return {
            "ev_ebitda": self.ev_ebitda_multiples(),
            "ev_ebit": self.ev_ebit_multiples(),
            "ev_revenue": self.ev_revenue_multiples(),
            "control_premium": self.control_premium_statistics(),
            "transaction_count": len(self.transactions)
        }

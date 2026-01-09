"""
WACC (Weighted Average Cost of Capital) and CAPM calculations.

This module implements:
- Cost of Equity via CAPM
- Beta unlevering and relevering
- WACC calculation
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class CostOfEquity:
    """
    Cost of Equity calculation using CAPM.

    CAPM: Re = Rf + β × (Rm - Rf)

    Attributes:
        risk_free_rate: 10-year government bond yield (e.g., 0.04 for 4%)
        beta: Levered beta of the stock
        equity_risk_premium: Market risk premium (Rm - Rf), typically 4.5%-5.5%
    """
    risk_free_rate: float
    beta: float
    equity_risk_premium: float

    def calculate(self) -> float:
        """Calculate cost of equity using CAPM."""
        return self.risk_free_rate + self.beta * self.equity_risk_premium

    @classmethod
    def from_market_return(cls, risk_free_rate: float, beta: float,
                          market_return: float) -> "CostOfEquity":
        """Create from market return instead of ERP."""
        erp = market_return - risk_free_rate
        return cls(risk_free_rate=risk_free_rate, beta=beta,
                  equity_risk_premium=erp)


@dataclass
class BetaCalculator:
    """
    Beta unlevering and relevering calculations.

    Used to strip out capital structure effects from peer betas
    and relever at the target's capital structure.

    Formulas:
        Unlever: βU = βL / (1 + (1-T) × D/E)
        Relever: βL = βU × (1 + (1-T) × D/E)
    """

    @staticmethod
    def unlever(levered_beta: float, debt: float, equity: float,
                tax_rate: float) -> float:
        """
        Unlever a levered beta to get asset beta.

        Args:
            levered_beta: Observed levered beta
            debt: Total debt value
            equity: Total equity value
            tax_rate: Marginal tax rate

        Returns:
            Unlevered (asset) beta
        """
        if equity == 0:
            raise ValueError("Equity cannot be zero")
        de_ratio = debt / equity
        return levered_beta / (1 + (1 - tax_rate) * de_ratio)

    @staticmethod
    def relever(unlevered_beta: float, debt: float, equity: float,
                tax_rate: float) -> float:
        """
        Relever an unlevered beta at target capital structure.

        Args:
            unlevered_beta: Asset beta
            debt: Target debt value
            equity: Target equity value
            tax_rate: Marginal tax rate

        Returns:
            Relevered beta at target capital structure
        """
        if equity == 0:
            raise ValueError("Equity cannot be zero")
        de_ratio = debt / equity
        return unlevered_beta * (1 + (1 - tax_rate) * de_ratio)

    @classmethod
    def from_peers(cls, peer_betas: list[float], peer_debts: list[float],
                   peer_equities: list[float], tax_rate: float,
                   target_debt: float, target_equity: float) -> float:
        """
        Calculate target beta from peer group.

        Unlevers each peer beta, takes median, then relevers at target structure.

        Args:
            peer_betas: List of peer levered betas
            peer_debts: List of peer debt values
            peer_equities: List of peer equity values
            tax_rate: Marginal tax rate
            target_debt: Target company debt
            target_equity: Target company equity

        Returns:
            Relevered beta for target company
        """
        if len(peer_betas) != len(peer_debts) or len(peer_betas) != len(peer_equities):
            raise ValueError("All peer lists must have same length")

        # Unlever each peer beta
        unlevered_betas = []
        for beta, debt, equity in zip(peer_betas, peer_debts, peer_equities):
            unlevered = cls.unlever(beta, debt, equity, tax_rate)
            unlevered_betas.append(unlevered)

        # Take median unlevered beta
        sorted_betas = sorted(unlevered_betas)
        n = len(sorted_betas)
        if n % 2 == 0:
            median_unlevered = (sorted_betas[n//2 - 1] + sorted_betas[n//2]) / 2
        else:
            median_unlevered = sorted_betas[n//2]

        # Relever at target structure
        return cls.relever(median_unlevered, target_debt, target_equity, tax_rate)


@dataclass
class WACC:
    """
    Weighted Average Cost of Capital calculation.

    WACC = (E/V × Re) + (D/V × Rd × (1-T))

    Attributes:
        equity_value: Market value of equity
        debt_value: Market value of debt
        cost_of_equity: Required return on equity
        cost_of_debt: Marginal cost of debt (YTM on new debt)
        tax_rate: Marginal tax rate
    """
    equity_value: float
    debt_value: float
    cost_of_equity: float
    cost_of_debt: float
    tax_rate: float

    @property
    def total_value(self) -> float:
        """Total firm value (D + E)."""
        return self.equity_value + self.debt_value

    @property
    def equity_weight(self) -> float:
        """Weight of equity in capital structure."""
        return self.equity_value / self.total_value if self.total_value > 0 else 0

    @property
    def debt_weight(self) -> float:
        """Weight of debt in capital structure."""
        return self.debt_value / self.total_value if self.total_value > 0 else 0

    @property
    def after_tax_cost_of_debt(self) -> float:
        """After-tax cost of debt."""
        return self.cost_of_debt * (1 - self.tax_rate)

    def calculate(self) -> float:
        """
        Calculate WACC.

        Returns:
            Weighted average cost of capital
        """
        equity_component = self.equity_weight * self.cost_of_equity
        debt_component = self.debt_weight * self.after_tax_cost_of_debt
        return equity_component + debt_component

    @classmethod
    def from_capm(cls, equity_value: float, debt_value: float,
                  risk_free_rate: float, beta: float, equity_risk_premium: float,
                  cost_of_debt: float, tax_rate: float) -> "WACC":
        """
        Create WACC calculator with CAPM-derived cost of equity.

        Args:
            equity_value: Market cap
            debt_value: Total debt (market value)
            risk_free_rate: 10-year government bond yield
            beta: Levered beta
            equity_risk_premium: ERP (Rm - Rf)
            cost_of_debt: Marginal cost of debt
            tax_rate: Marginal tax rate

        Returns:
            WACC instance
        """
        coe = CostOfEquity(risk_free_rate, beta, equity_risk_premium)
        return cls(
            equity_value=equity_value,
            debt_value=debt_value,
            cost_of_equity=coe.calculate(),
            cost_of_debt=cost_of_debt,
            tax_rate=tax_rate
        )

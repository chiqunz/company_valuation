"""
Leveraged Buyout (LBO) Model.

This module implements:
- Sources & Uses analysis
- Debt schedule with mandatory amortization
- Cash sweep mechanism
- Revolver logic (draw/repay)
- IRR and MOIC calculation
- Circularity resolution through iteration
"""

from dataclasses import dataclass, field
from typing import Optional
import numpy as np


@dataclass
class DebtTranche:
    """
    Individual debt tranche in the capital structure.

    Attributes:
        name: Tranche name (e.g., "Term Loan A", "Unitranche", "Revolver")
        amount: Initial amount drawn
        interest_rate: Annual interest rate (e.g., 0.09 for 9%)
        amortization_rate: Annual mandatory amortization as % of original (e.g., 0.01 for 1%)
        is_revolver: Whether this is a revolving facility
        revolver_commitment: Total available commitment for revolver
        cash_sweep_priority: Priority for cash sweep (lower = higher priority)
    """
    name: str
    amount: float
    interest_rate: float
    amortization_rate: float = 0.0
    is_revolver: bool = False
    revolver_commitment: float = 0.0
    cash_sweep_priority: int = 1

    def annual_amortization(self, original_amount: float) -> float:
        """Calculate mandatory annual amortization."""
        return original_amount * self.amortization_rate

    def interest_expense(self, balance: float) -> float:
        """Calculate interest expense on current balance."""
        return balance * self.interest_rate


@dataclass
class LBOProjection:
    """
    Single year projection for LBO model.

    Attributes:
        year: Projection year (1, 2, 3, etc.)
        ebitda: EBITDA for the year
        capex: Capital expenditures
        delta_nwc: Change in net working capital
        tax_rate: Cash tax rate
        depreciation: D&A (for tax shield calculation)
    """
    year: int
    ebitda: float
    capex: float = 0.0
    delta_nwc: float = 0.0
    tax_rate: float = 0.25
    depreciation: float = 0.0


@dataclass
class LBOResult:
    """Result of LBO analysis."""
    entry_equity: float
    exit_equity: float
    moic: float
    irr: float
    exit_enterprise_value: float
    exit_net_debt: float
    total_debt_paydown: float
    yearly_results: list[dict]


@dataclass
class SourcesAndUses:
    """Sources and Uses of funds in LBO transaction."""
    # Sources
    term_loan: float = 0.0
    revolver_draw: float = 0.0
    other_debt: float = 0.0
    sponsor_equity: float = 0.0
    rollover_equity: float = 0.0

    # Uses
    equity_purchase: float = 0.0
    refinance_debt: float = 0.0
    transaction_fees: float = 0.0
    financing_fees: float = 0.0

    @property
    def total_sources(self) -> float:
        return (self.term_loan + self.revolver_draw + self.other_debt +
                self.sponsor_equity + self.rollover_equity)

    @property
    def total_uses(self) -> float:
        return (self.equity_purchase + self.refinance_debt +
                self.transaction_fees + self.financing_fees)

    @property
    def total_debt(self) -> float:
        return self.term_loan + self.revolver_draw + self.other_debt

    def is_balanced(self, tolerance: float = 0.01) -> bool:
        """Check if sources equal uses."""
        return abs(self.total_sources - self.total_uses) < tolerance


@dataclass
class LBOModel:
    """
    Institutional LBO Model.

    Solves for: "What is the maximum price to achieve target IRR
    given available debt financing?"

    Features:
    - Multiple debt tranches with different terms
    - Mandatory amortization
    - Cash sweep mechanism
    - Revolver draw/repay logic
    - Iterative circularity resolution

    Attributes:
        entry_ebitda: EBITDA at acquisition
        entry_multiple: EV/EBITDA entry multiple
        debt_tranches: List of debt tranches
        projections: Yearly EBITDA and cash flow projections
        exit_multiple: EV/EBITDA exit multiple
        transaction_fees_pct: Transaction fees as % of EV
        financing_fees_pct: Financing fees as % of debt
        min_cash: Minimum cash to maintain
    """
    entry_ebitda: float
    entry_multiple: float
    debt_tranches: list[DebtTranche]
    projections: list[LBOProjection]
    exit_multiple: float
    transaction_fees_pct: float = 0.02
    financing_fees_pct: float = 0.02
    min_cash: float = 0.0

    @property
    def purchase_price(self) -> float:
        """Total enterprise value at entry."""
        return self.entry_ebitda * self.entry_multiple

    @property
    def total_initial_debt(self) -> float:
        """Total debt at closing."""
        return sum(t.amount for t in self.debt_tranches)

    @property
    def transaction_fees(self) -> float:
        """Transaction advisory fees."""
        return self.purchase_price * self.transaction_fees_pct

    @property
    def financing_fees(self) -> float:
        """Debt financing fees."""
        return self.total_initial_debt * self.financing_fees_pct

    @property
    def initial_equity(self) -> float:
        """Sponsor equity check at close."""
        return (self.purchase_price + self.transaction_fees +
                self.financing_fees - self.total_initial_debt)

    def sources_and_uses(self) -> SourcesAndUses:
        """Generate Sources & Uses table."""
        # Separate debt by type
        term_loan = sum(t.amount for t in self.debt_tranches if not t.is_revolver)
        revolver = sum(t.amount for t in self.debt_tranches if t.is_revolver)

        return SourcesAndUses(
            term_loan=term_loan,
            revolver_draw=revolver,
            sponsor_equity=self.initial_equity,
            equity_purchase=self.purchase_price,
            transaction_fees=self.transaction_fees,
            financing_fees=self.financing_fees
        )

    def _calculate_free_cash_flow(self, proj: LBOProjection,
                                  interest_expense: float) -> float:
        """
        Calculate free cash flow available for debt paydown.

        FCF = EBITDA - Interest - Taxes - CapEx - ΔNWC

        Note: Uses iterative approach since interest depends on debt
        which depends on paydown which depends on FCF.
        """
        # Calculate taxable income (EBITDA - D&A - Interest)
        taxable_income = proj.ebitda - proj.depreciation - interest_expense
        taxes = max(0, taxable_income * proj.tax_rate)

        # FCF available for debt service
        fcf = proj.ebitda - interest_expense - taxes - proj.capex - proj.delta_nwc
        return fcf

    def run_model(self, max_iterations: int = 10,
                  convergence_threshold: float = 0.01) -> LBOResult:
        """
        Run the LBO model with iterative circularity resolution.

        The model has circular reference:
        Interest → Debt Balance → Paydown → FCF → Interest

        Uses iteration to resolve.

        Args:
            max_iterations: Maximum iterations for convergence
            convergence_threshold: Threshold for convergence check

        Returns:
            LBOResult with IRR, MOIC, and yearly details
        """
        years = len(self.projections)

        # Initialize debt balances
        debt_balances = {t.name: t.amount for t in self.debt_tranches}
        original_amounts = {t.name: t.amount for t in self.debt_tranches}
        yearly_results = []
        total_paydown = 0.0

        for proj in self.projections:
            # Iterative calculation for this year
            prev_interest = 0.0

            for iteration in range(max_iterations):
                # Calculate interest expense
                total_interest = sum(
                    t.interest_expense(debt_balances[t.name])
                    for t in self.debt_tranches
                )

                # Calculate FCF
                fcf = self._calculate_free_cash_flow(proj, total_interest)

                # Check convergence
                if abs(total_interest - prev_interest) < convergence_threshold:
                    break
                prev_interest = total_interest

            # Apply mandatory amortization
            mandatory_paydown = 0.0
            for t in self.debt_tranches:
                if not t.is_revolver:
                    amort = min(t.annual_amortization(original_amounts[t.name]),
                               debt_balances[t.name])
                    debt_balances[t.name] -= amort
                    mandatory_paydown += amort

            # Cash available after mandatory amortization
            cash_for_sweep = fcf - mandatory_paydown

            # Cash sweep - pay down debt in priority order
            sweep_paydown = 0.0
            if cash_for_sweep > 0:
                # Sort tranches by priority
                sorted_tranches = sorted(
                    [t for t in self.debt_tranches if not t.is_revolver],
                    key=lambda x: x.cash_sweep_priority
                )

                remaining_cash = cash_for_sweep
                for t in sorted_tranches:
                    if remaining_cash <= 0:
                        break
                    paydown = min(remaining_cash, debt_balances[t.name])
                    debt_balances[t.name] -= paydown
                    sweep_paydown += paydown
                    remaining_cash -= paydown

            # Handle revolver (draw if FCF negative, repay if positive)
            revolver_change = 0.0
            for t in self.debt_tranches:
                if t.is_revolver:
                    if cash_for_sweep < 0:
                        # Draw on revolver
                        draw = min(-cash_for_sweep,
                                  t.revolver_commitment - debt_balances[t.name])
                        debt_balances[t.name] += draw
                        revolver_change = draw
                    elif cash_for_sweep > 0 and sweep_paydown == 0:
                        # Repay revolver if no term debt
                        repay = min(cash_for_sweep, debt_balances[t.name])
                        debt_balances[t.name] -= repay
                        revolver_change = -repay

            year_paydown = mandatory_paydown + sweep_paydown - revolver_change
            total_paydown += year_paydown

            yearly_results.append({
                "year": proj.year,
                "ebitda": proj.ebitda,
                "interest_expense": total_interest,
                "fcf": fcf,
                "mandatory_amortization": mandatory_paydown,
                "cash_sweep": sweep_paydown,
                "revolver_change": revolver_change,
                "ending_debt": sum(debt_balances.values())
            })

        # Exit calculation
        final_ebitda = self.projections[-1].ebitda
        exit_ev = final_ebitda * self.exit_multiple
        exit_debt = sum(debt_balances.values())
        exit_equity = exit_ev - exit_debt

        # Return calculations
        moic = exit_equity / self.initial_equity if self.initial_equity > 0 else 0
        irr = (moic ** (1 / years)) - 1 if moic > 0 and years > 0 else 0

        return LBOResult(
            entry_equity=self.initial_equity,
            exit_equity=exit_equity,
            moic=moic,
            irr=irr,
            exit_enterprise_value=exit_ev,
            exit_net_debt=exit_debt,
            total_debt_paydown=total_paydown,
            yearly_results=yearly_results
        )

    def solve_for_entry_multiple(self, target_irr: float,
                                 min_multiple: float = 5.0,
                                 max_multiple: float = 15.0,
                                 tolerance: float = 0.001) -> Optional[float]:
        """
        Solve for maximum entry multiple to achieve target IRR.

        Uses binary search to find the entry multiple that yields
        the target IRR.

        Args:
            target_irr: Target IRR (e.g., 0.20 for 20%)
            min_multiple: Minimum multiple to consider
            max_multiple: Maximum multiple to consider
            tolerance: IRR tolerance for convergence

        Returns:
            Entry multiple that achieves target IRR, or None if not achievable
        """
        original_multiple = self.entry_multiple

        low, high = min_multiple, max_multiple

        for _ in range(50):  # Max iterations
            mid = (low + high) / 2
            self.entry_multiple = mid

            # Recalculate debt based on new multiple
            # Assuming debt scales with purchase price
            scale = mid / original_multiple
            for t in self.debt_tranches:
                t.amount = t.amount * scale / (self.entry_multiple / original_multiple)

            result = self.run_model()

            if abs(result.irr - target_irr) < tolerance:
                self.entry_multiple = original_multiple
                return mid

            if result.irr > target_irr:
                low = mid  # Can pay more
            else:
                high = mid  # Need to pay less

        self.entry_multiple = original_multiple
        return None

    @classmethod
    def simple_lbo(cls, entry_ebitda: float, entry_multiple: float,
                   leverage_turns: float, interest_rate: float,
                   exit_multiple: float, hold_years: int = 5,
                   ebitda_growth: float = 0.05, capex_pct: float = 0.20,
                   tax_rate: float = 0.25) -> "LBOModel":
        """
        Create a simplified LBO model with single debt tranche.

        Convenience method for quick analysis.

        Args:
            entry_ebitda: Entry EBITDA
            entry_multiple: Entry EV/EBITDA
            leverage_turns: Debt / EBITDA at entry
            interest_rate: Interest rate on debt
            exit_multiple: Exit EV/EBITDA
            hold_years: Investment hold period
            ebitda_growth: Annual EBITDA growth rate
            capex_pct: CapEx as % of EBITDA
            tax_rate: Cash tax rate

        Returns:
            LBOModel instance
        """
        # Create single unitranche debt
        debt_amount = entry_ebitda * leverage_turns
        debt = DebtTranche(
            name="Unitranche",
            amount=debt_amount,
            interest_rate=interest_rate,
            amortization_rate=0.01  # 1% mandatory amortization
        )

        # Create projections
        projections = []
        for year in range(1, hold_years + 1):
            ebitda = entry_ebitda * ((1 + ebitda_growth) ** year)
            projections.append(LBOProjection(
                year=year,
                ebitda=ebitda,
                capex=ebitda * capex_pct,
                tax_rate=tax_rate,
                depreciation=ebitda * 0.10  # Simplified D&A assumption
            ))

        return cls(
            entry_ebitda=entry_ebitda,
            entry_multiple=entry_multiple,
            debt_tranches=[debt],
            projections=projections,
            exit_multiple=exit_multiple
        )

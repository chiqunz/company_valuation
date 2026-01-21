"""Tests for LBO Model."""

import pytest
from company_valuation.lbo import LBOModel, LBOProjection, DebtTranche, SourcesAndUses


class TestDebtTranche:
    """Tests for DebtTranche calculations."""

    def test_annual_amortization(self):
        """Test mandatory amortization calculation."""
        tranche = DebtTranche(
            name="Term Loan",
            amount=500,
            interest_rate=0.08,
            amortization_rate=0.01  # 1% per year
        )
        # Amortization = 500 × 0.01 = 5 per year
        assert tranche.annual_amortization(500) == pytest.approx(5.0, rel=1e-6)

    def test_interest_expense(self):
        """Test interest expense calculation."""
        tranche = DebtTranche(
            name="Term Loan",
            amount=500,
            interest_rate=0.08
        )
        # Interest = 500 × 0.08 = 40
        assert tranche.interest_expense(500) == pytest.approx(40.0, rel=1e-6)

    def test_revolver_tranche(self):
        """Test revolver tranche configuration."""
        revolver = DebtTranche(
            name="Revolver",
            amount=0,  # Start undrawn
            interest_rate=0.07,
            is_revolver=True,
            revolver_commitment=100
        )
        assert revolver.is_revolver
        assert revolver.revolver_commitment == 100


class TestSourcesAndUses:
    """Tests for Sources and Uses."""

    def test_balanced_sources_uses(self):
        """Test balanced sources and uses."""
        sau = SourcesAndUses(
            term_loan=600,
            sponsor_equity=500,
            equity_purchase=1000,
            transaction_fees=50,
            financing_fees=50
        )
        assert sau.is_balanced()
        assert sau.total_sources == 1100
        assert sau.total_uses == 1100

    def test_unbalanced_sources_uses(self):
        """Test detection of unbalanced S&U."""
        sau = SourcesAndUses(
            term_loan=600,
            sponsor_equity=400,  # Short 100
            equity_purchase=1000,
            transaction_fees=50,
            financing_fees=50
        )
        assert not sau.is_balanced()


class TestLBOModel:
    """Tests for LBO Model."""

    @pytest.fixture
    def simple_lbo(self):
        """Create simple LBO model for testing."""
        return LBOModel.simple_lbo(
            entry_ebitda=100,
            entry_multiple=10.0,
            leverage_turns=6.0,
            interest_rate=0.08,
            exit_multiple=10.0,
            hold_years=5,
            ebitda_growth=0.05,
            capex_pct=0.15,
            tax_rate=0.25
        )

    def test_purchase_price(self, simple_lbo):
        """Test purchase price calculation."""
        # Entry EBITDA × Multiple = 100 × 10 = 1000
        assert simple_lbo.purchase_price == pytest.approx(1000, rel=1e-6)

    def test_initial_debt(self, simple_lbo):
        """Test initial debt calculation."""
        # 6x EBITDA leverage = 100 × 6 = 600
        assert simple_lbo.total_initial_debt == pytest.approx(600, rel=1e-6)

    def test_initial_equity(self, simple_lbo):
        """Test sponsor equity calculation."""
        # Equity = Purchase - Debt - Fees
        expected = 1000 - 600 + simple_lbo.transaction_fees + simple_lbo.financing_fees
        # Fees are additional, so: 1000 + fees - 600 = 400 + fees
        assert simple_lbo.initial_equity > 0

    def test_sources_and_uses(self, simple_lbo):
        """Test sources and uses table generation."""
        sau = simple_lbo.sources_and_uses()

        assert sau.total_debt > 0
        assert sau.sponsor_equity > 0
        assert sau.is_balanced()

    def test_run_model_returns_positive(self, simple_lbo):
        """Test that model runs and returns positive returns."""
        result = simple_lbo.run_model()

        assert result.moic > 0
        assert result.irr > 0
        assert result.exit_equity > 0
        assert len(result.yearly_results) == 5

    def test_debt_paydown_occurs(self, simple_lbo):
        """Test that debt gets paid down over time."""
        result = simple_lbo.run_model()

        # Ending debt should be less than starting debt
        assert result.exit_net_debt < simple_lbo.total_initial_debt
        assert result.total_debt_paydown > 0

    def test_irr_moic_relationship(self, simple_lbo):
        """Test IRR and MOIC relationship: IRR = MOIC^(1/years) - 1."""
        result = simple_lbo.run_model()

        # Recalculate IRR from MOIC
        expected_irr = (result.moic ** (1/5)) - 1
        assert result.irr == pytest.approx(expected_irr, rel=1e-4)

    def test_yearly_results_structure(self, simple_lbo):
        """Test yearly results contain expected fields."""
        result = simple_lbo.run_model()

        for yearly in result.yearly_results:
            assert "year" in yearly
            assert "ebitda" in yearly
            assert "interest_expense" in yearly
            assert "fcf" in yearly
            assert "ending_debt" in yearly

    def test_ebitda_growth(self, simple_lbo):
        """Test EBITDA grows at specified rate."""
        result = simple_lbo.run_model()

        # Year 1 EBITDA = 100 × 1.05 = 105
        assert result.yearly_results[0]["ebitda"] == pytest.approx(105, rel=1e-2)

        # Year 5 EBITDA = 100 × 1.05^5 ≈ 127.6
        expected_y5 = 100 * (1.05 ** 5)
        assert result.yearly_results[4]["ebitda"] == pytest.approx(expected_y5, rel=1e-2)

    def test_higher_leverage_higher_irr(self):
        """Test that higher leverage increases IRR (with constant EBITDA)."""
        low_leverage = LBOModel.simple_lbo(
            entry_ebitda=100, entry_multiple=10.0,
            leverage_turns=4.0, interest_rate=0.08,
            exit_multiple=10.0
        )
        high_leverage = LBOModel.simple_lbo(
            entry_ebitda=100, entry_multiple=10.0,
            leverage_turns=6.0, interest_rate=0.08,
            exit_multiple=10.0
        )

        low_result = low_leverage.run_model()
        high_result = high_leverage.run_model()

        # Higher leverage = higher IRR (assuming company can service debt)
        assert high_result.irr > low_result.irr

    def test_exit_multiple_impact(self):
        """Test exit multiple expansion increases returns."""
        base = LBOModel.simple_lbo(
            entry_ebitda=100, entry_multiple=10.0,
            leverage_turns=5.0, interest_rate=0.08,
            exit_multiple=10.0  # Flat multiple
        )
        expanded = LBOModel.simple_lbo(
            entry_ebitda=100, entry_multiple=10.0,
            leverage_turns=5.0, interest_rate=0.08,
            exit_multiple=12.0  # Multiple expansion
        )

        base_result = base.run_model()
        expanded_result = expanded.run_model()

        assert expanded_result.irr > base_result.irr
        assert expanded_result.moic > base_result.moic

    def test_custom_debt_structure(self):
        """Test LBO with custom multi-tranche debt structure."""
        projections = [
            LBOProjection(year=i, ebitda=100*(1.05**i), capex=15*(1.05**i),
                         tax_rate=0.25, depreciation=10*(1.05**i))
            for i in range(1, 6)
        ]

        model = LBOModel(
            entry_ebitda=100,
            entry_multiple=10.0,
            debt_tranches=[
                DebtTranche(name="Senior", amount=400, interest_rate=0.07,
                           amortization_rate=0.01, cash_sweep_priority=1),
                DebtTranche(name="Mezz", amount=150, interest_rate=0.12,
                           amortization_rate=0.0, cash_sweep_priority=2)
            ],
            projections=projections,
            exit_multiple=10.0
        )

        result = model.run_model()

        assert result.moic > 0
        assert len(result.yearly_results) == 5

"""Tests for WACC and CAPM calculations."""

import pytest
from company_valuation.wacc import WACC, CostOfEquity, BetaCalculator


class TestCostOfEquity:
    """Tests for Cost of Equity (CAPM) calculation."""

    def test_basic_capm(self):
        """Test basic CAPM calculation: Re = Rf + β × ERP"""
        coe = CostOfEquity(
            risk_free_rate=0.04,  # 4%
            beta=1.2,
            equity_risk_premium=0.05  # 5%
        )
        # Re = 0.04 + 1.2 × 0.05 = 0.04 + 0.06 = 0.10
        assert coe.calculate() == pytest.approx(0.10, rel=1e-6)

    def test_beta_one(self):
        """Test with market beta (β=1)."""
        coe = CostOfEquity(
            risk_free_rate=0.04,
            beta=1.0,
            equity_risk_premium=0.055
        )
        # Re = 0.04 + 1.0 × 0.055 = 0.095
        assert coe.calculate() == pytest.approx(0.095, rel=1e-6)

    def test_low_beta(self):
        """Test with defensive stock (low beta)."""
        coe = CostOfEquity(
            risk_free_rate=0.035,
            beta=0.6,
            equity_risk_premium=0.05
        )
        # Re = 0.035 + 0.6 × 0.05 = 0.035 + 0.03 = 0.065
        assert coe.calculate() == pytest.approx(0.065, rel=1e-6)

    def test_high_beta(self):
        """Test with high-growth stock (high beta)."""
        coe = CostOfEquity(
            risk_free_rate=0.04,
            beta=1.8,
            equity_risk_premium=0.05
        )
        # Re = 0.04 + 1.8 × 0.05 = 0.04 + 0.09 = 0.13
        assert coe.calculate() == pytest.approx(0.13, rel=1e-6)

    def test_from_market_return(self):
        """Test creating from market return instead of ERP."""
        coe = CostOfEquity.from_market_return(
            risk_free_rate=0.04,
            beta=1.2,
            market_return=0.09
        )
        # ERP = 0.09 - 0.04 = 0.05
        # Re = 0.04 + 1.2 × 0.05 = 0.10
        assert coe.calculate() == pytest.approx(0.10, rel=1e-6)


class TestBetaCalculator:
    """Tests for beta unlevering and relevering."""

    def test_unlever_beta(self):
        """Test beta unlevering calculation."""
        # βU = βL / (1 + (1-T) × D/E)
        # βU = 1.5 / (1 + (1-0.25) × 0.5) = 1.5 / 1.375 ≈ 1.091
        unlevered = BetaCalculator.unlever(
            levered_beta=1.5,
            debt=500,
            equity=1000,
            tax_rate=0.25
        )
        expected = 1.5 / (1 + 0.75 * 0.5)
        assert unlevered == pytest.approx(expected, rel=1e-6)

    def test_relever_beta(self):
        """Test beta relevering calculation."""
        # βL = βU × (1 + (1-T) × D/E)
        # βL = 1.0 × (1 + (1-0.25) × 0.6) = 1.0 × 1.45 = 1.45
        relevered = BetaCalculator.relever(
            unlevered_beta=1.0,
            debt=600,
            equity=1000,
            tax_rate=0.25
        )
        expected = 1.0 * (1 + 0.75 * 0.6)
        assert relevered == pytest.approx(expected, rel=1e-6)

    def test_unlever_relever_roundtrip(self):
        """Unlevering then relevering at same structure should return original."""
        original_beta = 1.3
        debt = 400
        equity = 800
        tax_rate = 0.21

        unlevered = BetaCalculator.unlever(original_beta, debt, equity, tax_rate)
        relevered = BetaCalculator.relever(unlevered, debt, equity, tax_rate)

        assert relevered == pytest.approx(original_beta, rel=1e-6)

    def test_from_peers(self):
        """Test calculating target beta from peer group."""
        peer_betas = [1.2, 1.4, 1.3, 1.5, 1.1]
        peer_debts = [200, 300, 250, 400, 150]
        peer_equities = [1000, 1000, 1000, 1000, 1000]
        tax_rate = 0.25

        target_beta = BetaCalculator.from_peers(
            peer_betas=peer_betas,
            peer_debts=peer_debts,
            peer_equities=peer_equities,
            tax_rate=tax_rate,
            target_debt=500,
            target_equity=800
        )

        # Should be positive and reasonable
        assert target_beta > 0
        assert target_beta < 3.0

    def test_zero_equity_raises(self):
        """Zero equity should raise ValueError."""
        with pytest.raises(ValueError):
            BetaCalculator.unlever(1.2, 500, 0, 0.25)

        with pytest.raises(ValueError):
            BetaCalculator.relever(1.0, 500, 0, 0.25)


class TestWACC:
    """Tests for WACC calculation."""

    def test_basic_wacc(self):
        """Test basic WACC calculation."""
        wacc = WACC(
            equity_value=1000,
            debt_value=500,
            cost_of_equity=0.10,
            cost_of_debt=0.06,
            tax_rate=0.25
        )
        # E/V = 1000/1500 = 0.667
        # D/V = 500/1500 = 0.333
        # After-tax Rd = 0.06 × 0.75 = 0.045
        # WACC = 0.667 × 0.10 + 0.333 × 0.045 = 0.0667 + 0.015 = 0.0817
        result = wacc.calculate()
        expected = (1000/1500) * 0.10 + (500/1500) * 0.06 * 0.75
        assert result == pytest.approx(expected, rel=1e-6)

    def test_all_equity(self):
        """Test WACC with no debt (all equity firm)."""
        wacc = WACC(
            equity_value=1000,
            debt_value=0,
            cost_of_equity=0.12,
            cost_of_debt=0.06,
            tax_rate=0.25
        )
        # WACC = Cost of Equity when no debt
        assert wacc.calculate() == pytest.approx(0.12, rel=1e-6)

    def test_weights(self):
        """Test equity and debt weight calculations."""
        wacc = WACC(
            equity_value=700,
            debt_value=300,
            cost_of_equity=0.10,
            cost_of_debt=0.05,
            tax_rate=0.21
        )
        assert wacc.equity_weight == pytest.approx(0.7, rel=1e-6)
        assert wacc.debt_weight == pytest.approx(0.3, rel=1e-6)
        assert wacc.total_value == 1000

    def test_after_tax_cost_of_debt(self):
        """Test after-tax cost of debt calculation."""
        wacc = WACC(
            equity_value=500,
            debt_value=500,
            cost_of_equity=0.10,
            cost_of_debt=0.08,
            tax_rate=0.25
        )
        # After-tax = 0.08 × (1 - 0.25) = 0.06
        assert wacc.after_tax_cost_of_debt == pytest.approx(0.06, rel=1e-6)

    def test_from_capm(self):
        """Test creating WACC with CAPM-derived cost of equity."""
        wacc = WACC.from_capm(
            equity_value=1000,
            debt_value=400,
            risk_free_rate=0.04,
            beta=1.2,
            equity_risk_premium=0.05,
            cost_of_debt=0.06,
            tax_rate=0.25
        )
        # Cost of equity = 0.04 + 1.2 × 0.05 = 0.10
        assert wacc.cost_of_equity == pytest.approx(0.10, rel=1e-6)

        # WACC should be calculated correctly
        result = wacc.calculate()
        assert result > 0
        assert result < wacc.cost_of_equity  # Tax shield reduces WACC

"""Tests for utility functions."""

import pytest
from company_valuation.utils import (
    treasury_stock_method, diluted_shares, OptionGrant,
    enterprise_value, equity_value_from_ev, net_debt,
    ltm_calculation, implied_perpetual_growth, rule_of_40,
    ev_to_equity_bridge
)


class TestTreasuryStockMethod:
    """Tests for Treasury Stock Method."""

    def test_basic_tsm(self):
        """Test basic TSM calculation."""
        options = [
            OptionGrant(quantity=100, strike_price=50)
        ]
        current_price = 100

        # New Shares = 100 × (1 - 50/100) = 100 × 0.5 = 50
        dilution = treasury_stock_method(options, current_price)
        assert dilution == pytest.approx(50, rel=1e-6)

    def test_multiple_grants(self):
        """Test TSM with multiple option grants."""
        options = [
            OptionGrant(quantity=100, strike_price=50),   # 50 net shares
            OptionGrant(quantity=200, strike_price=80),   # 40 net shares
        ]
        current_price = 100

        dilution = treasury_stock_method(options, current_price)
        # Grant 1: 100 × (1 - 50/100) = 50
        # Grant 2: 200 × (1 - 80/100) = 40
        assert dilution == pytest.approx(90, rel=1e-6)

    def test_out_of_money_options(self):
        """Test that OTM options are not dilutive."""
        options = [
            OptionGrant(quantity=100, strike_price=50),   # ITM
            OptionGrant(quantity=100, strike_price=120),  # OTM
        ]
        current_price = 100

        dilution = treasury_stock_method(options, current_price)
        # Only ITM grant creates dilution
        assert dilution == pytest.approx(50, rel=1e-6)

    def test_at_the_money_options(self):
        """Test ATM options create no dilution."""
        options = [
            OptionGrant(quantity=100, strike_price=100)  # ATM
        ]
        current_price = 100

        dilution = treasury_stock_method(options, current_price)
        assert dilution == pytest.approx(0, rel=1e-6)

    def test_zero_price(self):
        """Test handling of zero stock price."""
        options = [OptionGrant(quantity=100, strike_price=50)]
        dilution = treasury_stock_method(options, current_price=0)
        assert dilution == 0

    def test_diluted_shares(self):
        """Test fully diluted share count."""
        options = [
            OptionGrant(quantity=100, strike_price=50)
        ]
        shares = diluted_shares(
            basic_shares=1000,
            options=options,
            current_price=100,
            rsus=25
        )
        # Basic + TSM + RSUs = 1000 + 50 + 25 = 1075
        assert shares == pytest.approx(1075, rel=1e-6)


class TestEnterpriseValue:
    """Tests for EV calculations."""

    def test_enterprise_value(self):
        """Test EV calculation."""
        ev = enterprise_value(
            equity_value=1000,
            total_debt=500,
            cash=200
        )
        # EV = 1000 + 500 - 200 = 1300
        assert ev == pytest.approx(1300, rel=1e-6)

    def test_enterprise_value_with_minority_interest(self):
        """Test EV with minority interest and preferred."""
        ev = enterprise_value(
            equity_value=1000,
            total_debt=500,
            cash=200,
            minority_interest=50,
            preferred_stock=30
        )
        # EV = 1000 + 500 - 200 + 50 + 30 = 1380
        assert ev == pytest.approx(1380, rel=1e-6)

    def test_equity_value_from_ev(self):
        """Test equity value from EV."""
        equity = equity_value_from_ev(
            enterprise_value=1300,
            total_debt=500,
            cash=200
        )
        # Equity = 1300 - 500 + 200 = 1000
        assert equity == pytest.approx(1000, rel=1e-6)

    def test_net_debt(self):
        """Test net debt calculation."""
        nd = net_debt(total_debt=500, cash=200)
        assert nd == pytest.approx(300, rel=1e-6)

    def test_net_cash(self):
        """Test net cash (negative net debt)."""
        nd = net_debt(total_debt=200, cash=500)
        assert nd == pytest.approx(-300, rel=1e-6)


class TestLTMCalculation:
    """Tests for LTM metric calculation."""

    def test_ltm_calculation(self):
        """Test LTM = FY + Current YTD - Prior YTD."""
        ltm = ltm_calculation(
            fiscal_year=1000,
            ytd_current=300,
            ytd_prior=250
        )
        # LTM = 1000 + 300 - 250 = 1050
        assert ltm == pytest.approx(1050, rel=1e-6)

    def test_ltm_with_growth(self):
        """Test LTM shows growth when YTD > Prior YTD."""
        ltm = ltm_calculation(
            fiscal_year=1000,
            ytd_current=400,
            ytd_prior=300
        )
        # LTM = 1000 + 400 - 300 = 1100 (10% growth implied)
        assert ltm > 1000

    def test_ltm_with_decline(self):
        """Test LTM shows decline when YTD < Prior YTD."""
        ltm = ltm_calculation(
            fiscal_year=1000,
            ytd_current=200,
            ytd_prior=300
        )
        # LTM = 1000 + 200 - 300 = 900 (decline)
        assert ltm < 1000


class TestImpliedGrowth:
    """Tests for implied perpetual growth rate."""

    def test_implied_growth(self):
        """Test implied growth calculation."""
        # Given TV = FCF(1+g)/(r-g), derive g
        g = implied_perpetual_growth(
            terminal_value=1000,
            final_fcf=70,
            discount_rate=0.10
        )
        # With TV=1000, FCF=70, r=10%: g ≈ 2.3%
        assert 0.02 < g < 0.03

    def test_high_implied_growth_warning(self):
        """Test detecting unreasonably high implied growth."""
        g = implied_perpetual_growth(
            terminal_value=2000,  # High TV relative to FCF
            final_fcf=50,
            discount_rate=0.10
        )
        # If implied g > GDP growth (~3%), multiple may be aggressive
        # This should return high implied growth
        assert g > 0.05


class TestRuleOf40:
    """Tests for Rule of 40."""

    def test_rule_of_40_healthy(self):
        """Test healthy SaaS company (score > 40%)."""
        score = rule_of_40(revenue_growth=0.30, profit_margin=0.15)
        assert score == pytest.approx(0.45, rel=1e-6)
        assert score >= 0.40

    def test_rule_of_40_unhealthy(self):
        """Test struggling SaaS company (score < 40%)."""
        score = rule_of_40(revenue_growth=0.20, profit_margin=0.10)
        assert score == pytest.approx(0.30, rel=1e-6)
        assert score < 0.40

    def test_rule_of_40_profitable_slow_growth(self):
        """Test mature profitable but slow-growing company."""
        score = rule_of_40(revenue_growth=0.05, profit_margin=0.35)
        assert score == pytest.approx(0.40, rel=1e-6)


class TestEVToEquityBridge:
    """Tests for EV to Equity bridge."""

    def test_basic_bridge(self):
        """Test basic EV to equity per share bridge."""
        result = ev_to_equity_bridge(
            enterprise_value=1500,
            net_debt=500,
            diluted_shares=100
        )

        assert result["enterprise_value"] == 1500
        assert result["net_debt"] == 500
        assert result["equity_value"] == pytest.approx(1000, rel=1e-6)
        assert result["equity_value_per_share"] == pytest.approx(10.0, rel=1e-6)

    def test_bridge_with_net_cash(self):
        """Test bridge when company has net cash."""
        result = ev_to_equity_bridge(
            enterprise_value=1000,
            net_debt=-200,  # Net cash
            diluted_shares=100
        )

        # Equity = 1000 - (-200) = 1200
        assert result["equity_value"] == pytest.approx(1200, rel=1e-6)
        assert result["equity_value_per_share"] == pytest.approx(12.0, rel=1e-6)

    def test_bridge_zero_shares(self):
        """Test bridge with zero shares."""
        result = ev_to_equity_bridge(
            enterprise_value=1000,
            net_debt=500,
            diluted_shares=0
        )

        assert result["equity_value_per_share"] == 0

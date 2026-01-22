"""Tests for Dividend Discount Model."""

import pytest
from company_valuation.ddm import DDMModel, DividendProjection


class TestDividendProjection:
    """Tests for DividendProjection."""

    def test_dps_from_eps_and_payout(self):
        """Test DPS calculation from EPS and payout ratio."""
        proj = DividendProjection(
            year=1,
            eps=5.0,
            payout_ratio=0.40
        )
        # DPS = 5.0 × 0.40 = 2.0
        assert proj.dps == pytest.approx(2.0, rel=1e-6)

    def test_explicit_dps(self):
        """Test explicit DPS overrides calculation."""
        proj = DividendProjection(
            year=1,
            eps=5.0,
            payout_ratio=0.40,
            dps=2.5  # Explicit
        )
        assert proj.dps == 2.5

    def test_zero_payout(self):
        """Test zero payout ratio."""
        proj = DividendProjection(
            year=1,
            eps=5.0,
            payout_ratio=0.0
        )
        assert proj.dps == 0.0


class TestDDMModel:
    """Tests for DDM Model."""

    @pytest.fixture
    def sample_projections(self):
        """Create sample dividend projections."""
        return [
            DividendProjection(year=1, eps=5.0, payout_ratio=0.40),   # DPS = 2.0
            DividendProjection(year=2, eps=5.5, payout_ratio=0.40),   # DPS = 2.2
            DividendProjection(year=3, eps=6.0, payout_ratio=0.40),   # DPS = 2.4
            DividendProjection(year=4, eps=6.5, payout_ratio=0.40),   # DPS = 2.6
            DividendProjection(year=5, eps=7.0, payout_ratio=0.40),   # DPS = 2.8
        ]

    def test_pv_dividends(self, sample_projections):
        """Test present value of dividends calculation."""
        model = DDMModel(
            projections=sample_projections,
            cost_of_equity=0.10,
            terminal_growth=0.03
        )
        pv_total, pv_list = model.calculate_pv_dividends()

        # PV of Year 1: 2.0 / 1.10 ≈ 1.818
        assert pv_list[0] == pytest.approx(2.0 / 1.10, rel=1e-4)

        # Total PV should be sum of all discounted dividends
        assert pv_total == pytest.approx(sum(pv_list), rel=1e-6)
        assert pv_total > 0

    def test_terminal_value_gordon_growth(self, sample_projections):
        """Test terminal value using Gordon Growth."""
        model = DDMModel(
            projections=sample_projections,
            cost_of_equity=0.10,
            terminal_growth=0.03
        )
        tv = model.terminal_value_gordon_growth()

        # TV = DPS_5 × (1 + g) / (ke - g) = 2.8 × 1.03 / (0.10 - 0.03)
        expected = 2.8 * 1.03 / 0.07
        assert tv == pytest.approx(expected, rel=1e-4)

    def test_terminal_value_pe(self, sample_projections):
        """Test terminal value using P/E multiple."""
        model = DDMModel(
            projections=sample_projections,
            cost_of_equity=0.10,
            terminal_growth=0.03,
            terminal_pe=15.0
        )
        tv = model.terminal_value_pe_multiple()

        # TV = EPS_5 × P/E = 7.0 × 15 = 105
        assert tv == pytest.approx(105.0, rel=1e-6)

    def test_terminal_growth_exceeds_ke_raises(self, sample_projections):
        """Terminal growth >= cost of equity should raise ValueError."""
        model = DDMModel(
            projections=sample_projections,
            cost_of_equity=0.08,
            terminal_growth=0.10  # Higher than ke
        )
        with pytest.raises(ValueError):
            model.terminal_value_gordon_growth()

    def test_full_valuation_gordon(self, sample_projections):
        """Test complete DDM valuation with Gordon Growth."""
        model = DDMModel(
            projections=sample_projections,
            cost_of_equity=0.10,
            terminal_growth=0.03
        )
        result = model.value_gordon_growth()

        assert result.pv_explicit_dividends > 0
        assert result.terminal_value_undiscounted > 0
        assert result.pv_terminal_value > 0
        assert result.equity_value_per_share > 0
        assert result.terminal_method == "gordon_growth"

        # Equity value = PV dividends + PV terminal
        expected = result.pv_explicit_dividends + result.pv_terminal_value
        assert result.equity_value_per_share == pytest.approx(expected, rel=1e-6)

    def test_full_valuation_pe(self, sample_projections):
        """Test complete DDM valuation with P/E terminal."""
        model = DDMModel(
            projections=sample_projections,
            cost_of_equity=0.10,
            terminal_growth=0.03,
            terminal_pe=15.0
        )
        result = model.value_pe_multiple()

        assert result.equity_value_per_share > 0
        assert result.terminal_method == "pe_multiple"
        assert result.implied_growth_rate is not None

    def test_from_eps_forecast(self):
        """Test creating DDM from EPS forecast."""
        model = DDMModel.from_eps_forecast(
            eps_forecasts=[5.0, 5.5, 6.0, 6.5, 7.0],
            payout_ratio=0.40,
            cost_of_equity=0.10,
            terminal_growth=0.03
        )

        assert len(model.projections) == 5
        assert model.projections[0].dps == pytest.approx(2.0, rel=1e-6)
        assert model.projections[4].dps == pytest.approx(2.8, rel=1e-6)

    def test_from_dividend_forecast(self):
        """Test creating DDM from explicit dividend forecast."""
        model = DDMModel.from_dividend_forecast(
            dps_forecasts=[2.0, 2.2, 2.4, 2.6, 2.8],
            cost_of_equity=0.10,
            terminal_growth=0.03
        )

        assert len(model.projections) == 5
        assert model.projections[0].dps == 2.0
        assert model.projections[4].dps == 2.8

    def test_value_method_selector(self, sample_projections):
        """Test value() method selects correct approach."""
        model = DDMModel(
            projections=sample_projections,
            cost_of_equity=0.10,
            terminal_growth=0.03,
            terminal_pe=15.0
        )

        gordon_result = model.value("gordon_growth")
        pe_result = model.value("pe_multiple")

        assert gordon_result.terminal_method == "gordon_growth"
        assert pe_result.terminal_method == "pe_multiple"

    def test_bank_valuation_example(self):
        """Test realistic bank valuation scenario."""
        # Bank with ROE of 12%, growing dividends
        model = DDMModel.from_eps_forecast(
            eps_forecasts=[4.50, 4.80, 5.10, 5.40, 5.70],
            payout_ratio=0.35,  # Banks typically 30-40% payout
            cost_of_equity=0.11,  # Higher for banks
            terminal_growth=0.03
        )

        result = model.value_gordon_growth()

        # Should produce reasonable bank valuation
        assert result.equity_value_per_share > 0
        # Terminal value typically dominates
        tv_pct = result.pv_terminal_value / result.equity_value_per_share
        assert 0.50 < tv_pct < 0.90

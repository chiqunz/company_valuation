"""Tests for DCF model."""

import pytest
from company_valuation.dcf import DCFModel, UFCFProjection


class TestUFCFProjection:
    """Tests for Unlevered Free Cash Flow calculation."""

    def test_basic_ufcf(self):
        """Test basic UFCF calculation."""
        proj = UFCFProjection(
            year=1,
            revenue=1000,
            ebit=200,
            tax_rate=0.25,
            depreciation_amortization=50,
            capex=60,
            delta_nwc=20
        )
        # NOPAT = 200 × 0.75 = 150
        # UFCF = 150 + 50 - 60 - 20 = 120
        assert proj.nopat == pytest.approx(150, rel=1e-6)
        assert proj.ufcf == pytest.approx(120, rel=1e-6)

    def test_ufcf_with_sbc_not_added_back(self):
        """Test UFCF when SBC is treated as real expense (buy-side view)."""
        proj = UFCFProjection(
            year=1,
            revenue=1000,
            ebit=200,
            tax_rate=0.25,
            depreciation_amortization=50,
            capex=60,
            delta_nwc=20,
            sbc=30,
            add_back_sbc=False
        )
        # UFCF should not include SBC add-back
        assert proj.ufcf == pytest.approx(120, rel=1e-6)

    def test_ufcf_with_sbc_added_back(self):
        """Test UFCF when SBC is added back (sell-side view)."""
        proj = UFCFProjection(
            year=1,
            revenue=1000,
            ebit=200,
            tax_rate=0.25,
            depreciation_amortization=50,
            capex=60,
            delta_nwc=20,
            sbc=30,
            add_back_sbc=True
        )
        # UFCF = 150 + 50 - 60 - 20 + 30 = 150
        assert proj.ufcf == pytest.approx(150, rel=1e-6)

    def test_ebitda_calculated(self):
        """Test EBITDA is calculated from EBIT + D&A."""
        proj = UFCFProjection(
            year=1,
            revenue=1000,
            ebit=200,
            tax_rate=0.25,
            depreciation_amortization=50,
            capex=60,
            delta_nwc=20
        )
        # EBITDA = EBIT + D&A = 200 + 50 = 250
        assert proj.ebitda == pytest.approx(250, rel=1e-6)

    def test_ebitda_explicit(self):
        """Test explicit EBITDA overrides calculation."""
        proj = UFCFProjection(
            year=1,
            revenue=1000,
            ebit=200,
            tax_rate=0.25,
            depreciation_amortization=50,
            capex=60,
            delta_nwc=20,
            ebitda=300  # Explicit
        )
        assert proj.ebitda == 300


class TestDCFModel:
    """Tests for DCF Model."""

    @pytest.fixture
    def sample_projections(self):
        """Create sample 5-year projections."""
        return [
            UFCFProjection(year=1, revenue=1000, ebit=200, tax_rate=0.25,
                          depreciation_amortization=50, capex=60, delta_nwc=10),
            UFCFProjection(year=2, revenue=1100, ebit=220, tax_rate=0.25,
                          depreciation_amortization=55, capex=65, delta_nwc=10),
            UFCFProjection(year=3, revenue=1210, ebit=242, tax_rate=0.25,
                          depreciation_amortization=60, capex=70, delta_nwc=10),
            UFCFProjection(year=4, revenue=1331, ebit=266, tax_rate=0.25,
                          depreciation_amortization=65, capex=75, delta_nwc=10),
            UFCFProjection(year=5, revenue=1464, ebit=293, tax_rate=0.25,
                          depreciation_amortization=70, capex=80, delta_nwc=10),
        ]

    def test_terminal_value_perpetuity(self, sample_projections):
        """Test terminal value using perpetuity growth method."""
        model = DCFModel(
            projections=sample_projections,
            wacc=0.10,
            terminal_growth=0.025
        )
        tv = model.calculate_terminal_value_perpetuity()

        # TV = UFCF_5 × (1 + g) / (WACC - g)
        final_ufcf = sample_projections[-1].ufcf
        expected_tv = final_ufcf * 1.025 / (0.10 - 0.025)
        assert tv == pytest.approx(expected_tv, rel=1e-6)

    def test_terminal_value_exit_multiple(self, sample_projections):
        """Test terminal value using exit multiple method."""
        model = DCFModel(
            projections=sample_projections,
            wacc=0.10,
            terminal_growth=0.025,
            exit_multiple=10.0
        )
        tv = model.calculate_terminal_value_exit_multiple()

        # TV = EBITDA_5 × Multiple
        final_ebitda = sample_projections[-1].ebitda
        expected_tv = final_ebitda * 10.0
        assert tv == pytest.approx(expected_tv, rel=1e-6)

    def test_terminal_growth_exceeds_wacc_raises(self, sample_projections):
        """Terminal growth >= WACC should raise ValueError."""
        model = DCFModel(
            projections=sample_projections,
            wacc=0.08,
            terminal_growth=0.10  # Higher than WACC
        )
        with pytest.raises(ValueError):
            model.calculate_terminal_value_perpetuity()

    def test_mid_year_convention(self, sample_projections):
        """Test mid-year convention increases value vs year-end."""
        model_mid = DCFModel(
            projections=sample_projections,
            wacc=0.10,
            terminal_growth=0.025,
            mid_year_convention=True
        )
        model_end = DCFModel(
            projections=sample_projections,
            wacc=0.10,
            terminal_growth=0.025,
            mid_year_convention=False
        )

        result_mid = model_mid.value_perpetuity_method()
        result_end = model_end.value_perpetuity_method()

        # Mid-year should give higher value (cash received earlier)
        assert result_mid.enterprise_value > result_end.enterprise_value

    def test_equity_bridge(self, sample_projections):
        """Test enterprise to equity value bridge."""
        model = DCFModel(
            projections=sample_projections,
            wacc=0.10,
            terminal_growth=0.025,
            net_debt=500,
            shares_outstanding=100
        )
        result = model.value_perpetuity_method()

        # Equity = EV - Net Debt
        expected_equity = result.enterprise_value - 500
        assert result.equity_value == pytest.approx(expected_equity, rel=1e-6)

        # Per share = Equity / Shares
        expected_per_share = expected_equity / 100
        assert result.equity_value_per_share == pytest.approx(expected_per_share, rel=1e-6)

    def test_implied_growth_from_multiple(self, sample_projections):
        """Test implied perpetual growth calculation."""
        model = DCFModel(
            projections=sample_projections,
            wacc=0.10,
            terminal_growth=0.025,
            exit_multiple=10.0
        )
        result = model.value_exit_multiple_method()

        # Implied growth should be calculated
        assert result.implied_perpetual_growth is not None
        # Should be reasonable (not >10% or negative)
        assert -0.05 < result.implied_perpetual_growth < 0.10

    def test_terminal_value_percentage(self, sample_projections):
        """Test terminal value typically 60-80% of EV per report."""
        model = DCFModel(
            projections=sample_projections,
            wacc=0.10,
            terminal_growth=0.025
        )
        tv_pct = model.terminal_value_percentage("perpetuity")

        # Per report: TV often 60-80% of total EV
        assert 0.50 < tv_pct < 0.90

    def test_full_dcf_valuation(self, sample_projections):
        """Test complete DCF produces reasonable results."""
        model = DCFModel(
            projections=sample_projections,
            wacc=0.10,
            terminal_growth=0.025,
            net_debt=300,
            shares_outstanding=50
        )

        result = model.value_perpetuity_method()

        # Sanity checks
        assert result.pv_explicit_cashflows > 0
        assert result.terminal_value_undiscounted > 0
        assert result.pv_terminal_value > 0
        assert result.enterprise_value > 0
        assert result.equity_value > 0
        assert result.equity_value_per_share > 0

        # EV should be sum of explicit + terminal PV
        expected_ev = result.pv_explicit_cashflows + result.pv_terminal_value
        assert result.enterprise_value == pytest.approx(expected_ev, rel=1e-6)

    def test_stub_period(self, sample_projections):
        """Test stub period handling (partial first year)."""
        model_full = DCFModel(
            projections=sample_projections,
            wacc=0.10,
            terminal_growth=0.025,
            stub_fraction=1.0
        )
        model_stub = DCFModel(
            projections=sample_projections,
            wacc=0.10,
            terminal_growth=0.025,
            stub_fraction=0.5  # Half year stub
        )

        result_full = model_full.value_perpetuity_method()
        result_stub = model_stub.value_perpetuity_method()

        # With stub, first year cash flow is closer, value should be higher
        assert result_stub.enterprise_value > result_full.enterprise_value

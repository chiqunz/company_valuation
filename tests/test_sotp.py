"""Tests for Sum-of-the-Parts Analysis."""

import pytest
from company_valuation.sotp import SOTPModel, Segment, ValuationMethod


class TestSegment:
    """Tests for Segment calculations."""

    def test_calculated_value(self):
        """Test segment value calculation from metric × multiple."""
        segment = Segment(
            name="Media",
            method=ValuationMethod.EV_EBITDA,
            metric_value=500,
            multiple=10.0
        )
        # Value = 500 × 10 = 5000
        assert segment.calculated_value == pytest.approx(5000, rel=1e-6)

    def test_explicit_segment_value(self):
        """Test explicit segment value (e.g., from DCF)."""
        segment = Segment(
            name="Finance",
            method=ValuationMethod.DDM,
            segment_value=3000  # Pre-calculated via DDM
        )
        assert segment.calculated_value == 3000

    def test_explicit_overrides_calculation(self):
        """Test that explicit value overrides metric × multiple."""
        segment = Segment(
            name="Tech",
            method=ValuationMethod.EV_EBITDA,
            metric_value=500,
            multiple=10.0,
            segment_value=6000  # Override
        )
        assert segment.calculated_value == 6000


class TestSOTPModel:
    """Tests for SOTPModel."""

    @pytest.fixture
    def conglomerate_segments(self):
        """Create sample conglomerate segments."""
        return [
            Segment(name="Media", method=ValuationMethod.EV_EBITDA,
                   metric_value=500, multiple=10.0),  # 5000
            Segment(name="Finance", method=ValuationMethod.PRICE_TO_BOOK,
                   metric_value=2000, multiple=1.5),  # 3000
            Segment(name="Tech", method=ValuationMethod.EV_REVENUE,
                   metric_value=1000, multiple=4.0),  # 4000
        ]

    def test_gross_enterprise_value(self, conglomerate_segments):
        """Test gross EV is sum of segment values."""
        model = SOTPModel(segments=conglomerate_segments)
        result = model.calculate()

        # Gross EV = 5000 + 3000 + 4000 = 12000
        assert result.gross_enterprise_value == pytest.approx(12000, rel=1e-6)

    def test_corporate_overhead_deduction(self, conglomerate_segments):
        """Test corporate overhead is deducted."""
        model = SOTPModel(
            segments=conglomerate_segments,
            corporate_overhead=50,  # Annual overhead
            overhead_multiple=8.0  # Capitalize at 8x
        )
        result = model.calculate()

        # Overhead value = 50 × 8 = 400
        assert result.corporate_overhead_value == pytest.approx(400, rel=1e-6)
        # EV pre-discount = 12000 - 400 = 11600
        assert result.enterprise_value_pre_discount == pytest.approx(11600, rel=1e-6)

    def test_conglomerate_discount(self, conglomerate_segments):
        """Test conglomerate discount application."""
        model = SOTPModel(
            segments=conglomerate_segments,
            corporate_overhead=50,
            overhead_multiple=8.0,
            conglomerate_discount=0.15  # 15% discount
        )
        result = model.calculate()

        # EV pre-discount = 11600
        # Discount = 11600 × 0.15 = 1740
        expected_discount = 11600 * 0.15
        assert result.discount_amount == pytest.approx(expected_discount, rel=1e-6)

        # Net EV = 11600 - 1740 = 9860
        assert result.net_enterprise_value == pytest.approx(9860, rel=1e-6)

    def test_equity_value_bridge(self, conglomerate_segments):
        """Test bridge from EV to equity value."""
        model = SOTPModel(
            segments=conglomerate_segments,
            corporate_overhead=50,
            overhead_multiple=8.0,
            conglomerate_discount=0.15,
            net_debt=1000,
            shares_outstanding=100
        )
        result = model.calculate()

        # Net EV = 9860
        # Equity = 9860 - 1000 = 8860
        expected_equity = result.net_enterprise_value - 1000
        assert result.equity_value == pytest.approx(expected_equity, rel=1e-6)

        # Per share = 8860 / 100 = 88.60
        assert result.equity_value_per_share == pytest.approx(88.60, rel=1e-6)

    def test_segment_contribution(self, conglomerate_segments):
        """Test segment contribution percentages."""
        model = SOTPModel(segments=conglomerate_segments)
        contributions = model.segment_contribution()

        # Media: 5000 / 12000 = 41.67%
        assert contributions["Media"] == pytest.approx(5000/12000, rel=1e-4)
        # Finance: 3000 / 12000 = 25%
        assert contributions["Finance"] == pytest.approx(0.25, rel=1e-4)
        # Tech: 4000 / 12000 = 33.33%
        assert contributions["Tech"] == pytest.approx(4000/12000, rel=1e-4)

        # Should sum to 1.0
        assert sum(contributions.values()) == pytest.approx(1.0, rel=1e-6)

    def test_sensitivity_to_discount(self, conglomerate_segments):
        """Test sensitivity to conglomerate discount."""
        model = SOTPModel(
            segments=conglomerate_segments,
            conglomerate_discount=0.15,
            net_debt=1000
        )

        discounts = [0.0, 0.10, 0.15, 0.20, 0.25]
        sensitivity = model.sensitivity_to_discount(discounts)

        # Higher discount = lower equity value
        assert sensitivity[0.0] > sensitivity[0.10] > sensitivity[0.25]

        # At 0% discount, equity should be highest
        assert sensitivity[0.0] == max(sensitivity.values())

    def test_from_dict(self):
        """Test creating model from dictionary data."""
        segment_data = [
            {"name": "Division A", "method": "ev_ebitda",
             "metric_value": 100, "multiple": 8.0},
            {"name": "Division B", "method": "ev_revenue",
             "metric_value": 500, "multiple": 2.0},
        ]

        model = SOTPModel.from_dict(
            segment_data=segment_data,
            corporate_overhead=20,
            conglomerate_discount=0.10,
            net_debt=200
        )

        result = model.calculate()
        assert len(model.segments) == 2
        assert result.gross_enterprise_value == pytest.approx(1800, rel=1e-6)

    def test_no_discount_scenario(self, conglomerate_segments):
        """Test with no conglomerate discount."""
        model = SOTPModel(
            segments=conglomerate_segments,
            conglomerate_discount=0.0,
            net_debt=500
        )
        result = model.calculate()

        assert result.discount_amount == 0
        assert result.net_enterprise_value == result.enterprise_value_pre_discount

    def test_net_cash_company(self, conglomerate_segments):
        """Test company with net cash (negative net debt)."""
        model = SOTPModel(
            segments=conglomerate_segments,
            conglomerate_discount=0.15,
            net_debt=-500  # Net cash
        )
        result = model.calculate()

        # Equity = EV + cash (since net_debt is negative)
        assert result.equity_value > result.net_enterprise_value

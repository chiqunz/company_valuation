"""Tests for Sensitivity Analysis."""

import pytest
from company_valuation.sensitivity import (
    SensitivityAnalysis, SensitivityTable, FootballField, FootballFieldBar
)


class TestSensitivityTable:
    """Tests for SensitivityTable."""

    def test_basic_table(self):
        """Test basic sensitivity table creation."""
        table = SensitivityTable(
            row_variable="WACC",
            col_variable="Growth",
            row_values=[0.08, 0.10, 0.12],
            col_values=[0.02, 0.025, 0.03],
            results=[
                [150, 140, 130],
                [120, 110, 100],
                [100, 90, 80]
            ],
            base_row_idx=1,
            base_col_idx=1
        )

        assert table.base_value == 110
        assert table.min_value() == 80
        assert table.max_value() == 150
        assert table.range() == (80, 150)

    def test_to_dict(self):
        """Test serialization to dictionary."""
        table = SensitivityTable(
            row_variable="WACC",
            col_variable="Growth",
            row_values=[0.08, 0.10],
            col_values=[0.02, 0.03],
            results=[[100, 90], [80, 70]]
        )

        d = table.to_dict()
        assert d["row_variable"] == "WACC"
        assert d["col_variable"] == "Growth"
        assert d["range"] == (70, 100)


class TestSensitivityAnalysis:
    """Tests for SensitivityAnalysis utility functions."""

    def test_create_table(self):
        """Test creating sensitivity table from function."""
        def calc_func(x, y):
            return x * y

        table = SensitivityAnalysis.create_table(
            calc_func=calc_func,
            row_variable="X",
            col_variable="Y",
            row_values=[1, 2, 3],
            col_values=[10, 20, 30],
            base_row_value=2,
            base_col_value=20
        )

        # Check dimensions
        assert len(table.row_values) == 3
        assert len(table.col_values) == 3
        assert len(table.results) == 3
        assert len(table.results[0]) == 3

        # Check values
        assert table.results[0][0] == 10  # 1 × 10
        assert table.results[1][1] == 40  # 2 × 20
        assert table.results[2][2] == 90  # 3 × 30

        # Check base case
        assert table.base_row_idx == 1
        assert table.base_col_idx == 1
        assert table.base_value == 40

    def test_create_table_with_errors(self):
        """Test that calculation errors result in NaN."""
        def calc_func(x, y):
            if y == 0:
                raise ValueError("Division by zero")
            return x / y

        table = SensitivityAnalysis.create_table(
            calc_func=calc_func,
            row_variable="X",
            col_variable="Y",
            row_values=[10, 20],
            col_values=[0, 5, 10]  # 0 will cause error
        )

        # First column should be NaN
        import math
        assert math.isnan(table.results[0][0])
        assert math.isnan(table.results[1][0])

        # Other values should be correct
        assert table.results[0][1] == 2.0  # 10 / 5
        assert table.results[1][2] == 2.0  # 20 / 10


class TestFootballField:
    """Tests for Football Field visualization."""

    def test_football_field_bar(self):
        """Test FootballFieldBar properties."""
        bar = FootballFieldBar(
            method="DCF",
            low=80,
            mid=100,
            high=120
        )

        assert bar.range_width == 40

    def test_create_football_field(self):
        """Test creating football field from ranges."""
        ff = SensitivityAnalysis.create_football_field(
            dcf_range=(80, 100, 120),
            comps_range=(85, 105, 125),
            lbo_range=(70, 85, 100),
            fifty_two_week=(75, 110),
            current_price=95
        )

        assert len(ff.bars) == 3
        assert ff.fifty_two_week_low == 75
        assert ff.fifty_two_week_high == 110
        assert ff.current_price == 95

    def test_overall_range(self):
        """Test overall range calculation."""
        ff = SensitivityAnalysis.create_football_field(
            dcf_range=(80, 100, 120),
            comps_range=(90, 110, 130),
            lbo_range=(70, 85, 100)
        )

        low, high = ff.overall_range()
        assert low == 70  # LBO low
        assert high == 130  # Comps high

    def test_overall_range_with_52_week(self):
        """Test overall range includes 52-week range."""
        ff = SensitivityAnalysis.create_football_field(
            dcf_range=(80, 100, 120),
            fifty_two_week=(60, 140)  # Wider than DCF
        )

        low, high = ff.overall_range()
        assert low == 60
        assert high == 140

    def test_consensus_range(self):
        """Test consensus (overlap) range calculation."""
        ff = SensitivityAnalysis.create_football_field(
            dcf_range=(80, 100, 120),
            comps_range=(90, 105, 115),
            lbo_range=(85, 95, 110)
        )

        low, high = ff.consensus_range()
        # Overlap: max(80,90,85)=90 to min(120,115,110)=110
        assert low == 90
        assert high == 110

    def test_no_consensus_range(self):
        """Test when there's no overlap between methods."""
        ff = SensitivityAnalysis.create_football_field(
            dcf_range=(100, 110, 120),
            lbo_range=(70, 80, 90)  # No overlap with DCF
        )

        low, high = ff.consensus_range()
        import math
        assert math.isnan(low)
        assert math.isnan(high)

    def test_to_dict(self):
        """Test serialization."""
        ff = SensitivityAnalysis.create_football_field(
            dcf_range=(80, 100, 120),
            comps_range=(85, 105, 125),
            current_price=95
        )

        d = ff.to_dict()
        assert len(d["bars"]) == 2
        assert d["current_price"] == 95
        assert "overall_range" in d
        assert "consensus_range" in d

    def test_partial_football_field(self):
        """Test football field with only some methodologies."""
        ff = SensitivityAnalysis.create_football_field(
            dcf_range=(80, 100, 120)
            # Only DCF, no other methods
        )

        assert len(ff.bars) == 1
        assert ff.bars[0].method == "DCF"

    def test_empty_football_field(self):
        """Test empty football field."""
        ff = SensitivityAnalysis.create_football_field()

        assert len(ff.bars) == 0
        # Should still work but return empty ranges

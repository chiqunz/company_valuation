"""
Sensitivity Analysis and Football Field Visualization.

This module implements:
- Two-variable sensitivity tables
- Football Field data generation for valuation ranges
"""

from dataclasses import dataclass
from typing import Callable, Optional, Any
import numpy as np


@dataclass
class SensitivityTable:
    """
    Two-dimensional sensitivity analysis table.

    Attributes:
        row_variable: Name of row variable
        col_variable: Name of column variable
        row_values: Values for row variable
        col_values: Values for column variable
        results: 2D array of results
        base_row_idx: Index of base case row
        base_col_idx: Index of base case column
    """
    row_variable: str
    col_variable: str
    row_values: list[float]
    col_values: list[float]
    results: list[list[float]]
    base_row_idx: Optional[int] = None
    base_col_idx: Optional[int] = None

    @property
    def base_value(self) -> Optional[float]:
        """Get base case value."""
        if self.base_row_idx is not None and self.base_col_idx is not None:
            return self.results[self.base_row_idx][self.base_col_idx]
        return None

    def min_value(self) -> float:
        """Get minimum value in table."""
        return min(min(row) for row in self.results)

    def max_value(self) -> float:
        """Get maximum value in table."""
        return max(max(row) for row in self.results)

    def range(self) -> tuple[float, float]:
        """Get value range (min, max)."""
        return self.min_value(), self.max_value()

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "row_variable": self.row_variable,
            "col_variable": self.col_variable,
            "row_values": self.row_values,
            "col_values": self.col_values,
            "results": self.results,
            "base_value": self.base_value,
            "range": self.range()
        }


@dataclass
class FootballFieldBar:
    """
    Single bar in a football field chart.

    Attributes:
        method: Valuation method name
        low: Low end of range (e.g., 25th percentile)
        mid: Midpoint value (e.g., median)
        high: High end of range (e.g., 75th percentile)
    """
    method: str
    low: float
    mid: float
    high: float

    @property
    def range_width(self) -> float:
        """Width of the valuation range."""
        return self.high - self.low


@dataclass
class FootballField:
    """
    Football Field valuation summary.

    Combines multiple valuation methodologies to show
    valuation range across approaches.
    """
    bars: list[FootballFieldBar]
    fifty_two_week_low: Optional[float] = None
    fifty_two_week_high: Optional[float] = None
    current_price: Optional[float] = None

    def overall_range(self) -> tuple[float, float]:
        """Get overall valuation range across all methods."""
        all_lows = [b.low for b in self.bars]
        all_highs = [b.high for b in self.bars]

        if self.fifty_two_week_low:
            all_lows.append(self.fifty_two_week_low)
        if self.fifty_two_week_high:
            all_highs.append(self.fifty_two_week_high)

        return min(all_lows), max(all_highs)

    def consensus_range(self) -> tuple[float, float]:
        """
        Get consensus range (overlap of all methods).

        Returns range where all valuation methods agree.
        May return (nan, nan) if no overlap exists.
        """
        max_low = max(b.low for b in self.bars)
        min_high = min(b.high for b in self.bars)

        if max_low <= min_high:
            return max_low, min_high
        return float('nan'), float('nan')

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization/visualization."""
        return {
            "bars": [
                {"method": b.method, "low": b.low, "mid": b.mid, "high": b.high}
                for b in self.bars
            ],
            "fifty_two_week": {
                "low": self.fifty_two_week_low,
                "high": self.fifty_two_week_high
            },
            "current_price": self.current_price,
            "overall_range": self.overall_range(),
            "consensus_range": self.consensus_range()
        }


class SensitivityAnalysis:
    """
    Sensitivity analysis utilities for valuation models.

    Generates sensitivity tables and football field data.
    """

    @staticmethod
    def create_table(
        calc_func: Callable[[float, float], float],
        row_variable: str,
        col_variable: str,
        row_values: list[float],
        col_values: list[float],
        base_row_value: Optional[float] = None,
        base_col_value: Optional[float] = None
    ) -> SensitivityTable:
        """
        Create a two-variable sensitivity table.

        Args:
            calc_func: Function that takes (row_val, col_val) and returns result
            row_variable: Name of row variable (e.g., "WACC")
            col_variable: Name of column variable (e.g., "Terminal Growth")
            row_values: List of row variable values to test
            col_values: List of column variable values to test
            base_row_value: Base case row value (for highlighting)
            base_col_value: Base case column value

        Returns:
            SensitivityTable with results
        """
        results = []
        for row_val in row_values:
            row_results = []
            for col_val in col_values:
                try:
                    result = calc_func(row_val, col_val)
                except Exception:
                    result = float('nan')
                row_results.append(result)
            results.append(row_results)

        # Find base case indices
        base_row_idx = None
        base_col_idx = None
        if base_row_value is not None:
            try:
                base_row_idx = row_values.index(base_row_value)
            except ValueError:
                pass
        if base_col_value is not None:
            try:
                base_col_idx = col_values.index(base_col_value)
            except ValueError:
                pass

        return SensitivityTable(
            row_variable=row_variable,
            col_variable=col_variable,
            row_values=row_values,
            col_values=col_values,
            results=results,
            base_row_idx=base_row_idx,
            base_col_idx=base_col_idx
        )

    @staticmethod
    def dcf_sensitivity(
        base_dcf: Any,
        wacc_range: list[float],
        growth_range: list[float]
    ) -> SensitivityTable:
        """
        Create WACC vs Terminal Growth sensitivity for DCF.

        Standard DCF sensitivity analysis.

        Args:
            base_dcf: DCFModel instance
            wacc_range: List of WACC values to test
            growth_range: List of terminal growth rates to test

        Returns:
            SensitivityTable with enterprise values
        """
        base_wacc = base_dcf.wacc
        base_growth = base_dcf.terminal_growth

        def calc_ev(wacc: float, growth: float) -> float:
            base_dcf.wacc = wacc
            base_dcf.terminal_growth = growth
            try:
                result = base_dcf.value_perpetuity_method()
                return result.enterprise_value
            finally:
                base_dcf.wacc = base_wacc
                base_dcf.terminal_growth = base_growth

        return SensitivityAnalysis.create_table(
            calc_func=calc_ev,
            row_variable="WACC",
            col_variable="Terminal Growth",
            row_values=wacc_range,
            col_values=growth_range,
            base_row_value=base_wacc,
            base_col_value=base_growth
        )

    @staticmethod
    def lbo_sensitivity(
        base_lbo: Any,
        entry_multiples: list[float],
        exit_multiples: list[float]
    ) -> SensitivityTable:
        """
        Create Entry Multiple vs Exit Multiple sensitivity for LBO.

        Standard LBO sensitivity analysis.

        Args:
            base_lbo: LBOModel instance
            entry_multiples: List of entry multiples to test
            exit_multiples: List of exit multiples to test

        Returns:
            SensitivityTable with IRR values
        """
        base_entry = base_lbo.entry_multiple
        base_exit = base_lbo.exit_multiple

        def calc_irr(entry: float, exit_mult: float) -> float:
            base_lbo.entry_multiple = entry
            base_lbo.exit_multiple = exit_mult
            # Also need to adjust debt for entry multiple
            try:
                result = base_lbo.run_model()
                return result.irr
            finally:
                base_lbo.entry_multiple = base_entry
                base_lbo.exit_multiple = base_exit

        return SensitivityAnalysis.create_table(
            calc_func=calc_irr,
            row_variable="Entry Multiple",
            col_variable="Exit Multiple",
            row_values=entry_multiples,
            col_values=exit_multiples,
            base_row_value=base_entry,
            base_col_value=base_exit
        )

    @staticmethod
    def create_football_field(
        dcf_range: Optional[tuple[float, float, float]] = None,
        comps_range: Optional[tuple[float, float, float]] = None,
        precedent_range: Optional[tuple[float, float, float]] = None,
        lbo_range: Optional[tuple[float, float, float]] = None,
        fifty_two_week: Optional[tuple[float, float]] = None,
        current_price: Optional[float] = None
    ) -> FootballField:
        """
        Create football field from valuation ranges.

        Args:
            dcf_range: (low, mid, high) from DCF analysis
            comps_range: (low, mid, high) from Trading Comps
            precedent_range: (low, mid, high) from Precedent Transactions
            lbo_range: (low, mid, high) from LBO analysis
            fifty_two_week: (low, high) 52-week trading range
            current_price: Current stock price

        Returns:
            FootballField instance
        """
        bars = []

        if dcf_range:
            bars.append(FootballFieldBar(
                method="DCF",
                low=dcf_range[0],
                mid=dcf_range[1],
                high=dcf_range[2]
            ))

        if comps_range:
            bars.append(FootballFieldBar(
                method="Trading Comps",
                low=comps_range[0],
                mid=comps_range[1],
                high=comps_range[2]
            ))

        if precedent_range:
            bars.append(FootballFieldBar(
                method="Precedent Transactions",
                low=precedent_range[0],
                mid=precedent_range[1],
                high=precedent_range[2]
            ))

        if lbo_range:
            bars.append(FootballFieldBar(
                method="LBO",
                low=lbo_range[0],
                mid=lbo_range[1],
                high=lbo_range[2]
            ))

        return FootballField(
            bars=bars,
            fifty_two_week_low=fifty_two_week[0] if fifty_two_week else None,
            fifty_two_week_high=fifty_two_week[1] if fifty_two_week else None,
            current_price=current_price
        )
